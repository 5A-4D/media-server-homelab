import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit_host', ROOT / 'scripts/audit_host.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def fixture():
    # Fabricated topology with no host data or credentials.
    streamer = {'State': {'Running': True, 'Health': {'Status': 'healthy'}}, 'Mounts': [
        {'Type': 'bind', 'Source': '/example/library/movies', 'Destination': '/media/movies', 'RW': False}]}
    downloader = {'State': {'Running': True}, 'HostConfig': {'NetworkMode': 'container:example-gateway'}, 'Mounts': [
        {'Type': 'bind', 'Source': '/example/staging', 'Destination': '/downloads', 'RW': True}]}
    gateway = {'Id': 'example-gateway', 'Name': '/media-vpn',
               'State': {'Running': True, 'Health': {'Status': 'healthy'}}}
    return streamer, downloader, gateway


class ContainmentTests(unittest.TestCase):
    def test_separate_staging_and_readonly_library(self):
        data = audit.summarize_containers(*fixture())
        self.assertTrue(all(data.values()))

    def test_downloader_outside_gateway_fails(self):
        s, d, g = fixture()
        for mode in ['host', 'bridge', 'container:other-gateway']:
            d['HostConfig']['NetworkMode'] = mode
            self.assertFalse(audit.summarize_containers(s, d, g)['shared_vpn_namespace'])

    def test_gateway_name_is_supported(self):
        s, d, g = fixture()
        d['HostConfig']['NetworkMode'] = 'container:media-vpn'
        self.assertTrue(audit.summarize_containers(s, d, g)['shared_vpn_namespace'])

    def test_writable_media_fails(self):
        s, d, g = fixture()
        s['Mounts'][0]['RW'] = True
        self.assertFalse(audit.summarize_containers(s, d, g)['media_read_only'])

    def test_missing_media_is_not_readonly_success(self):
        s, d, g = fixture()
        s['Mounts'] = []
        data = audit.summarize_containers(s, d, g)
        self.assertFalse(data['media_read_only'])
        self.assertFalse(data['library_hidden_from_downloader'])

    def test_parent_mount_into_downloader_reaches_library(self):
        s, d, g = fixture()
        d['Mounts'].append({'Type': 'bind', 'Source': '/example', 'Destination': '/host', 'RW': True})
        self.assertFalse(audit.summarize_containers(s, d, g)['library_hidden_from_downloader'])

    def test_staging_parent_exposed_to_streamer_fails(self):
        s, d, g = fixture()
        s['Mounts'].append({'Type': 'bind', 'Source': '/example', 'Destination': '/extra', 'RW': False})
        self.assertFalse(audit.summarize_containers(s, d, g)['staging_hidden_from_streamer'])

    def test_path_prefix_without_directory_boundary_is_distinct(self):
        self.assertFalse(audit.overlap('/example/media', '/example/media-downloads'))
        self.assertTrue(audit.overlap('/example/media', '/example/media/movies'))

    def test_independent_downloader_ports_fail(self):
        s, d, g = fixture()
        d['HostConfig']['PortBindings'] = {'8080/tcp': [{'HostIp': '127.0.0.1', 'HostPort': '8080'}]}
        self.assertFalse(audit.summarize_containers(s, d, g)['downloader_ports_absent'])


class PrivacyAndReportTests(unittest.TestCase):
    def test_unknown_input_fields_never_appear_in_report(self):
        data = json.loads((ROOT / 'demo/inventory.json').read_text())
        sentinel = 'DO_NOT_EMIT_SYNTHETIC_PRIVATE_VALUE'
        data.update({'environment': {'private_value': sentinel}, 'hostname': sentinel, 'media_titles': [sentinel]})
        self.assertNotIn(sentinel, json.dumps(audit.evaluate(data)))

    def test_truthy_strings_and_missing_fields_do_not_pass(self):
        report = audit.evaluate({'shared_vpn_namespace': 'true'})
        self.assertFalse(report['static_controls_passed'])
        self.assertTrue(all(c['status'] == 'not_checked' for c in report['checks']))

    def test_failed_mount_flag_blocks_static_pass(self):
        data = json.loads((ROOT / 'demo/inventory.json').read_text())
        data['noexec'] = False
        report = audit.evaluate(data)
        self.assertFalse(report['static_controls_passed'])
        self.assertEqual(report['counts']['fail'], 1)

    def test_manual_checks_remain_unverified_even_for_good_fixture(self):
        data = json.loads((ROOT / 'demo/inventory.json').read_text())
        report = audit.evaluate(data, demo=True)
        self.assertEqual(report['mode'], 'fictional_demo')
        self.assertTrue(report['static_controls_passed'])
        self.assertEqual(report['counts'], {'pass': 16, 'fail': 0, 'not_checked': 6})

    def test_cli_defaults_to_offline_demo(self):
        process = subprocess.run([sys.executable, str(ROOT / 'scripts/audit_host.py')], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(process.stdout)['mode'], 'fictional_demo')

    def test_missing_input_does_not_disclose_path(self):
        name = '/SYNTHETIC_PRIVATE_LOCATION/missing.json'
        process = subprocess.run([sys.executable, str(ROOT / 'scripts/audit_host.py'), '--fixture', name], capture_output=True, text=True)
        self.assertEqual(process.returncode, 2)
        self.assertNotIn(name, process.stderr)

    def test_unwritable_output_does_not_disclose_path(self):
        name = '/dev/null/SYNTHETIC_PRIVATE_LOCATION/report.json'
        process = subprocess.run([sys.executable, str(ROOT / 'scripts/audit_host.py'), '--output', name], capture_output=True, text=True)
        self.assertEqual(process.returncode, 2)
        self.assertNotIn(name, process.stderr)


if __name__ == '__main__':
    unittest.main()
