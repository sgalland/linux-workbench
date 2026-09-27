import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from workbenchlib import inspect


class ParserTests(unittest.TestCase):
    def test_uname_field_order(self):
        observation, facts = inspect._parse_uname("Linux 7.2.8-1-cachyos x86_64\n")
        self.assertEqual(observation, "present")
        self.assertEqual(facts["kernel"], "Linux")
        self.assertEqual(facts["kernel_release"], "7.2.8-1-cachyos")
        self.assertEqual(facts["architecture"], "x86_64")

    def test_os_release_uses_allowlisted_fields(self):
        text = 'NAME="CachyOS"\nID=cachyos\nBUILD_SECRET="do-not-keep"\n'
        observation, facts = inspect._parse_os_release(text)
        self.assertEqual(observation, "present")
        self.assertEqual(facts, {"distribution": {"name": "CachyOS", "id": "cachyos"}})
        self.assertNotIn("do-not-keep", json.dumps(facts))

    def test_lsblk_omits_names_and_mount_paths(self):
        source = json.dumps({"blockdevices": [{"name": "nvme0n1", "type": "disk", "size": "1T", "fstype": None, "mountpoint": "/home/private", "rota": False, "tran": "nvme", "uuid": "secret"}]})
        observation, facts = inspect._parse_lsblk(source)
        self.assertEqual(observation, "present")
        encoded = json.dumps(facts)
        for private in ("nvme0n1", "/home/private", "secret"):
            self.assertNotIn(private, encoded)
        self.assertEqual(facts["devices"][0]["type"], "disk")

    def test_pci_omits_addresses_and_ids_but_keeps_driver(self):
        text = "00:02.0 VGA compatible controller [0300]: Example GPU [1234:abcd]\n\tKernel driver in use: i915\n"
        _, facts = inspect._parse_pci(text)
        encoded = json.dumps(facts)
        self.assertNotIn("00:02.0", encoded)
        self.assertNotIn("1234:abcd", encoded)
        self.assertIn("i915", encoded)

    def test_usb_omits_bus_and_device_numbers(self):
        _, facts = inspect._parse_lsusb("Bus 001 Device 004: ID 1234:abcd Example USB device\n")
        self.assertEqual(facts, {"devices": ["Example USB device"]})

    def test_pw_dump_keeps_endpoint_relationships_and_discards_private_props(self):
        text = json.dumps([
            {"id": 9, "info": {"props": {"media.class": "Audio/Device", "device.name": "secret device", "device.description": "Sensitive model"}}},
            {"id": 17, "info": {"props": {"media.class": "Audio/Sink", "node.name": "private-client-name", "device.id": 9, "device.category": "Speaker", "secret.property": "credential"}, "params": [{"id": "Props", "param": {"mute": True, "volume": 0.5, "channelVolumes": [0.5, 0.6]}}]}}
        ])
        _, facts = inspect._parse_pw_dump(text)
        encoded = json.dumps(facts)
        self.assertIn('"muted": true', encoded)
        self.assertIn('"volume": 0.5', encoded)
        sink = next(item for item in facts["endpoints"] if item["kind"] == "sink")
        self.assertEqual(sink["device_ref"], 9)
        self.assertEqual(sink["category"], "Speaker")
        self.assertNotIn("credential", encoded)
        self.assertNotIn("Sensitive model", encoded)
        self.assertNotIn("private-client-name", encoded)
        self.assertNotIn("secret device", encoded)

    def test_wpctl_default_is_snapshot_local_id(self):
        raw = "Audio\n ├─ Sinks:\n │  * 42. Built-in Audio Analog Stereo [vol: 0.50]\n │   43. HDMI [vol: 1.00]\n ├─ Sources:\n │   51. Mic [vol: 0.80]\n"
        _, facts = inspect._parse_wpctl(raw)
        self.assertEqual(facts["default_markers"], {"sink": 42})
        self.assertEqual(facts["sink_count"], 2)

    def test_alsa_pcm_splits_playback_and_capture_directions(self):
        _, facts = inspect._parse_alsa_pcm("00-00: HDA Analog: playback 1 : capture 1\n00-03: HDMI 0: playback 1\n")
        self.assertEqual([row["direction"] for row in facts["devices"]], ["playback", "capture", "playback"])
        self.assertEqual(facts["devices"][0]["role"], "analog")
        self.assertEqual(facts["devices"][2]["role"], "hdmi")

    def test_alsa_card_names_are_sanitized(self):
        _, facts = inspect._parse_alsa_cards(" 0 [sof-hda-dsp   ]: HDA-Intel - SOF Audio\n")
        self.assertEqual(facts["cards"][0]["driver"], "HDA-Intel")
        self.assertEqual(facts["cards"][0]["name"], "sof-hda-dsp")

    def test_alsa_listings_keep_direction_and_subdevice_capabilities(self):
        _, facts = inspect._parse_alsa_listing("card 0: PCH [HDA], device 3: HDMI 0 [HDMI 0], subdevices: 1/1\n", "playback")
        self.assertEqual(facts["devices"][0]["direction"], "playback")
        self.assertEqual(facts["devices"][0]["role"], "hdmi")
        self.assertEqual(facts["devices"][0]["available_subdevices"], 1)
        self.assertEqual(facts["devices"][0]["subdevices"], 1)

    def test_usb_tree_removes_separator_punctuation(self):
        _, facts = inspect._parse_usb_tree("/: Bus 01.Port 1: Dev 1, Class=root_hub, Driver=xhci_hcd/1p, 480M\n |__ Port 2: Dev 2, If 0, Class=Hub, Driver=hub/4p, 5000M\n")
        self.assertEqual(facts["topology"][0]["class"], "root_hub")
        self.assertEqual(facts["topology"][1]["driver"], "hub/4p")

    def test_audio_sysfs_records_sanitized_direct_child_driver(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            node = root / "codec with secret!"
            node.mkdir()
            (node / "driver").symlink_to("/sys/bus/hdaudio/drivers/realtek")
            probe = inspect._probe_audio_sysfs("hda", root)
        self.assertEqual(probe["facts"]["devices"], [{"name": "codec with secret", "driver": "realtek"}])

    def test_missing_alsa_file_is_unknown_not_absent(self):
        result = inspect._probe_file("cards", Path("/this/path/does/not/exist"), inspect._parse_alsa_cards)
        self.assertEqual((result["status"], result["observation"]), ("unavailable", "unknown"))

    def test_unit_state_parser_keeps_only_named_service_state(self):
        raw = "Id=pipewire.service\nLoadState=loaded\nActiveState=active\nSubState=running\n\nId=wireplumber.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\n"
        _, facts = inspect._parse_unit_states(raw)
        self.assertEqual(facts["units"]["pipewire"]["activestate"], "active")
        self.assertEqual(facts["units"]["wireplumber"]["substate"], "dead")


class CollectionTests(unittest.TestCase):
    def test_failed_probe_does_not_abort_and_snapshot_marks_unknown(self):
        def runner(argv, timeout):
            if argv[0] == "uname":
                return "", "private diagnostic", 1
            if argv[0] == "pw-dump":
                raise RuntimeError("do not serialize this failure detail")
            return "", "", 0

        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            etc = base / "etc"
            proc = base / "proc"
            sysfs = base / "sys"
            etc.mkdir()
            proc.mkdir()
            sysfs.mkdir()
            (etc / "os-release").write_text('ID=cachyos\nNAME="CachyOS"\n')
            with patch.object(inspect.shutil, "which", return_value="/fixture/tool"), patch.dict("os.environ", {}, clear=True):
                snapshot = inspect.collect(runner, proc=proc, sysfs=sysfs, etc=etc)

        probes = {p["id"]: p for p in snapshot["probes"]}
        self.assertEqual(probes["kernel"]["status"], "command_error")
        self.assertEqual(probes["pipewire_snapshot"]["status"], "probe_error")
        self.assertEqual(probes["kscreen"]["status"], "not_collected")
        self.assertIn("kernel", snapshot["completeness"]["incomplete_probe_ids"])
        self.assertFalse(snapshot["completeness"]["complete"])
        self.assertNotIn("private diagnostic", json.dumps(snapshot))
        self.assertNotIn("do not serialize", json.dumps(snapshot))

    def test_write_snapshot_stays_under_requested_output_directory(self):
        inspect.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=inspect.OUTPUT_DIR) as directory:
            target = Path(directory)
            path = inspect.write_snapshot({"safe": True}, target)
            self.assertEqual(path.parent, target)
            self.assertEqual(json.loads(path.read_text()), {"safe": True})

    def test_write_snapshot_rejects_paths_outside_repository_output(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                inspect.write_snapshot({"safe": True}, Path(directory))

    def test_write_snapshot_does_not_follow_broken_filename_symlink(self):
        class FixedDatetime:
            @staticmethod
            def now(tz=None):
                return datetime(2026, 1, 2, tzinfo=timezone.utc)

        inspect.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=inspect.OUTPUT_DIR) as directory, tempfile.TemporaryDirectory() as outside:
            target = Path(directory)
            (target / "20260102T000000Z.json").symlink_to(Path(outside) / "unexpected.json")
            with patch.object(inspect, "datetime", FixedDatetime):
                path = inspect.write_snapshot({"safe": True}, target)
            self.assertEqual(path.name, "20260102T000000Z-1.json")
            self.assertFalse((Path(outside) / "unexpected.json").exists())


if __name__ == "__main__":
    unittest.main()
