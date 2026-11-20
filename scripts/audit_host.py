#!/usr/bin/env python3
"""Read-only containment audit. Emit fixed checks, never raw Docker/host data."""
import argparse
import json
from pathlib import Path, PurePosixPath
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def command_json(args):
    completed = subprocess.run(args, capture_output=True, text=True, timeout=20)
    if completed.returncode:
        raise RuntimeError('Inspection unavailable; check local access privately.')
    return json.loads(completed.stdout)


def overlap(left, right):
    """Docker bind sources are absolute host paths; handle path boundaries exactly."""
    a, b = PurePosixPath(left), PurePosixPath(right)
    if not a.is_absolute() or not b.is_absolute():
        raise ValueError('Expected absolute bind paths')
    return a == b or a in b.parents or b in a.parents


def summarize_containers(streaming, downloader, gateway):
    sm = streaming.get('Mounts') or []
    dm = downloader.get('Mounts') or []
    media = [m for m in sm if m.get('Destination', '').startswith('/media/')]
    download_mounts = [m for m in dm if m.get('Destination') == '/downloads']
    gateway_ids = {gateway.get('Id'), gateway.get('Name', '').lstrip('/')}
    gateway_ids.discard(None)
    gateway_ids.discard('')
    mode = (downloader.get('HostConfig') or {}).get('NetworkMode', '')
    shared = mode.startswith('container:') and mode[10:] in gateway_ids
    readonly = bool(media) and all(m.get('RW') is False for m in media)
    # Fail when a writable downloader bind can reach a library through a parent.
    library_writable = any(
        m.get('Type') == d.get('Type') == 'bind' and d.get('RW') is True
        and overlap(m['Source'], d['Source']) for m in media for d in dm
    )
    staging_visible = any(
        s.get('Type') == d.get('Type') == 'bind' and overlap(s['Source'], d['Source'])
        for s in sm for d in download_mounts
    )
    return {
        'streaming_running': streaming.get('State', {}).get('Running') is True,
        'streaming_healthy': streaming.get('State', {}).get('Health', {}).get('Status') == 'healthy',
        'downloader_running': downloader.get('State', {}).get('Running') is True,
        'gateway_running': gateway.get('State', {}).get('Running') is True,
        'gateway_healthy': gateway.get('State', {}).get('Health', {}).get('Status') == 'healthy',
        'shared_vpn_namespace': shared,
        'downloader_ports_absent': not bool((downloader.get('HostConfig') or {}).get('PortBindings')),
        'media_read_only': readonly,
        'staging_hidden_from_streamer': bool(download_mounts) and not staging_visible,
        'library_hidden_from_downloader': bool(media) and not library_writable,
    }


def collect_live(args):
    # Full inspect results remain in process memory. Do not print/store them.
    containers = [command_json(['docker', 'inspect', name])[0]
                  for name in [args.streaming, args.downloader, args.gateway]]
    data = summarize_containers(*containers)
    mount = command_json(['findmnt', '--json', '--target', args.storage,
                          '--output', 'TARGET,OPTIONS'])['filesystems'][0]
    options = set(mount['options'].split(','))
    # A mount of '/' does not establish that the selected data mount is present.
    target = Path(mount['target']).resolve()
    storage = Path(args.storage).resolve()
    data['data_mount_present'] = target != Path('/') and (target == storage or target in storage.parents)
    data.update({flag: flag in options for flag in ['noexec', 'nosuid', 'nodev']})
    data['scanner_installed'] = bool(shutil.which('clamdscan') or shutil.which('clamscan'))
    daemon = subprocess.run(['systemctl', 'is-active', '--quiet', 'tailscaled.service'],
                            capture_output=True, timeout=10)
    data['private_access_daemon_active'] = daemon.returncode == 0
    return data


CHECKS = [
    ('streaming_running', 'Streaming container is running'),
    ('streaming_healthy', 'Streaming healthcheck is healthy'),
    ('downloader_running', 'Download client is running'),
    ('gateway_running', 'VPN gateway is running'),
    ('gateway_healthy', 'VPN gateway healthcheck is healthy'),
    ('shared_vpn_namespace', 'Downloader shares the VPN gateway network namespace'),
    ('downloader_ports_absent', 'Downloader has no independent published ports'),
    ('media_read_only', 'Media bind mounts are read-only inside the streamer'),
    ('staging_hidden_from_streamer', 'Download staging is not mounted into the streamer'),
    ('library_hidden_from_downloader', 'Downloader has no writable bind reaching media libraries'),
    ('data_mount_present', 'A separate data mount is present'),
    ('noexec', 'Data mount has noexec'),
    ('nosuid', 'Data mount has nosuid'),
    ('nodev', 'Data mount has nodev'),
    ('private_access_daemon_active', 'Private-access daemon is active'),
    ('scanner_installed', 'An antivirus scan client is installed'),
]
MANUAL = [
    ('firewall_and_client_access', 'Effective firewall rules and allowed/denied client access'),
    ('vpn_binding_dns_ipv6', 'Application interface binding, DNS path and IPv6 handling'),
    ('vpn_failure_and_recovery', 'Controlled tunnel-failure, egress and recovery test'),
    ('media_integrity_and_scan', 'Selected item completion, integrity and complete antivirus coverage'),
    ('playback_and_gpu', 'Direct play, subtitles and actual GPU transcode session'),
    ('backup_restore_and_boot', 'Consistent restore, reboot and power recovery'),
]


def evaluate(data, demo=False):
    checks = []
    for key, label in CHECKS:
        value = data.get(key)
        status = 'pass' if value is True else 'fail' if value is False else 'not_checked'
        checks.append({'id': key, 'description': label, 'status': status})
    checks.extend({'id': key, 'description': label, 'status': 'not_checked'} for key, label in MANUAL)
    counts = {status: sum(c['status'] == status for c in checks)
              for status in ['pass', 'fail', 'not_checked']}
    return {'schema_version': 1, 'mode': 'fictional_demo' if demo else 'read_only_snapshot',
            'checks': checks, 'counts': counts,
            'static_controls_passed': all(data.get(key) is True for key, _ in CHECKS),
            'scope': 'Snapshot only; manual checks remain. Not a certification of security or VPN privacy.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--fixture', type=Path, default=None)
    source.add_argument('--live', action='store_true')
    parser.add_argument('--streaming', default='media-streaming')
    parser.add_argument('--downloader', default='media-downloads')
    parser.add_argument('--gateway', default='media-vpn')
    parser.add_argument('--storage', default='/srv/example-media-data')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        data = collect_live(args) if args.live else json.loads((args.fixture or ROOT / 'demo/inventory.json').read_text())
        if not isinstance(data, dict):
            raise ValueError('Expected object')
        report = evaluate(data, demo=not args.live)
    except (OSError, ValueError, KeyError, IndexError, TypeError, RuntimeError, subprocess.SubprocessError):
        # Exception messages may include local paths, config or raw command output.
        parser.exit(2, 'Inspection failed. Check dependencies, arguments and permissions locally; no raw details emitted.\n')
    rendered = json.dumps(report, indent=2) + '\n'
    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered)
        except OSError:
            parser.exit(2, 'Could not write the report. Check the destination privately.\n')
    else:
        print(rendered, end='')
    return 0 if report['static_controls_passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
