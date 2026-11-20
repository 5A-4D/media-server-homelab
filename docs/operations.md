# Operations and recovery

## Routine health without exposing private state

The audit defaults to a fictional offline fixture. To inspect a reviewed local
installation, explicitly select live mode and provide local container names and
the data path. This example uses the repository's generic names:

```sh
python3 scripts/audit_host.py --live \
  --streaming media-streaming --downloader media-downloads \
  --gateway media-vpn --storage /srv/example-media-data \
  --output reports/local-audit.json
```

The report folder is ignored. The helper reads Docker metadata, mount options,
private-access daemon status and scanner-client availability. It does not read
VPN profile contents, application databases, media files, torrent state,
calendars or logs. It does not issue network probes, restart containers or
change configuration. Access to Docker inspection must already be available.

A zero exit code means the selected static controls passed. Six manual checks
still appear as `not_checked`; do not label the host fully verified based on
that exit code. A missing observation does not become a pass. Raw input fields
outside the fixed report schema are never copied into output.

## Playback and GPU validation

Use generated test-pattern video and a synthetic audio tone, stored in a
dedicated test area outside a real library until approved. The original helper
used FFmpeg's `testsrc2` and `sine` inputs to create an H.264/AAC sample; no
copyrighted movie is needed for a playback check.

Check direct play, subtitle behavior and an intentional transcode separately.
Inspect the actual session/FFmpeg diagnostics privately to establish which
device and encoder were used. `vainfo` support and a visible device node are
prerequisites, not proof that a session used hardware acceleration. Do not
publish library screenshots, user sessions or real viewing history.

## Controlled VPN outage procedure

This is an active maintenance test and is intentionally absent from the audit
script and CI. Preserve an independent administration path first.

1. Use authorized synthetic/test transfer traffic, record the intended tunnel
   interface and privately establish host/client egress behavior.
2. Confirm application binding, gateway firewall, DNS and IPv6 expectations.
3. Introduce a controlled tunnel failure while leaving the relevant client
   process observable. Check that transfers cannot bypass the tunnel.
4. Test direct/bypass paths and new connections; distinguish routing failures
   from a test that simply terminated the application.
5. Restore the gateway/client relationship, confirm health and intended egress,
   and verify that recovery did not disrupt Jellyfin or private administration.
6. Record timestamped results and limitations privately, without addresses,
   account data, traffic payloads or media titles in portfolio evidence.

The original diagnostic helper included gateway stop/restart recovery logic.
It is not copied into a default runnable command here because publication must
not interrupt the active installation. A current green healthcheck does not
stand in for this outage test.

## Backup and restore

| State | Treatment |
| --- | --- |
| Jellyfin configuration/database | Take an application-consistent backup, commonly by stopping writes during an approved window; retain ownership and version context. |
| Jellyfin cache/transcodes | Usually rebuildable; distinguish it from required configuration. |
| qBittorrent profile/resume state | Back up consistently if transfer/seeding continuity matters; keep private. |
| WireGuard profile and application credentials | Restricted, encrypted backup; exclude from source control and shared reports. |
| Service/Compose/firewall configuration | Back up local reviewed versions privately; repository examples lack real targets. |
| Media library | Separate capacity/retention decision; a configuration backup does not back up the media. |

Restore to an isolated location first. Verify service identities, file access,
image compatibility and library paths before reconnecting clients. Keep the
previous configuration/image available until the restored service is validated.
Do not claim a working backup until a restore has actually been exercised.

## Startup, reboot and power

The original services were observed enabled and active. Systemd mount
dependencies protect startup ordering; container health remains a separate
check. The original Jellyfin container had no Docker restart policy, while the
download stack used `unless-stopped`. The reference Jellyfin template adds that
policy; the live policy was not changed during publication.

Before an approved reboot, establish private/local recovery access and confirm
mount persistence. Afterward check the actual mount, service state, container
health, private reachability and a synthetic playback item. Disk encryption,
firmware AC-power recovery, lid/suspend settings and physical restart behavior
need their own review. No power-loss or reboot result is claimed here.

## Update procedure

Record current image IDs and configuration privately, read upstream release
notes, back up state consistently, and stage an approved update. Revalidate GPU
access, library permissions, application interface binding and gateway behavior
after changes. Roll back image/configuration together when needed, accounting
for database migrations that may not support downgrade.

The pinned example digests identify a snapshot, not an automatic update policy.
This repository has no deployment workflow or ongoing synchronization.

## Troubleshooting map

| Symptom | Investigate first |
| --- | --- |
| Service active but unavailable | Actual container state/health, mount presence and effective bind/firewall path. |
| Empty library after boot | Correct data mount, container bind sources and service read permissions; avoid creating replacement root-disk paths. |
| GPU transcode fails | Selected render node, device group, container identity, driver capability and actual session diagnostics. |
| Downloader cannot transfer | Gateway health, tunnel interface binding, DNS and routing; do not bypass the VPN to make a test pass. |
| Private client denied | Approved identity/address, input versus forwarding path, existing rules and IPv4/IPv6 behavior. |
| Scanner says clean unusually fast | Limits, skipped/unreadable files, database status and real byte coverage. |
| Item copied but absent in Jellyfin | Exact destination, library membership, naming, refresh result and indexed path. |

Keep troubleshooting output private by default. Share selected sanitized facts,
not raw logs, cookies, environment dumps, VPN configuration or account exports.
