# HP ENVY 17-ch0xxx audio investigation — 2026-09-27

This record documents the speaker investigation and one unsuccessful temporary HDA reconfiguration attempt. It does not establish a working repair.

## Confirmed hardware and baseline

- Machine: HP ENVY Laptop 17-ch0xxx; board: HP 88B5.
- PCI audio subsystem ID: `103c:88b5`.
- Codec: Realtek ALC245; codec subsystem ID: `103c:88b5`.
- Audio path: `sof-audio-pci-intel-tgl`, using `skl_hda_dsp_generic`.
- Clean pin configuration: node `0x14` init pin config `0x411111f0`; node `0x17` init pin config `0x90170180`.
- `user_pin_configs` and `driver_pin_configs` were empty at baseline.
- PipeWire exposed `HiFi__Speaker__sink` as the default speaker sink. Bottom/bass speakers audibly worked; top B&O speakers were silent.

## Runtime observations before the sysfs experiment

| Node | Pin widget control | AMP | EAPD | Connection select | Default pin config |
| --- | --- | --- | --- | --- | --- |
| `0x14` | `0x00` | `0x00` | `0x02` | `0x00` | `0x411111f0` |
| `0x17` | `0x40` | `0x00` | `0x00` | `0x01` | `0x90170180` |

A runtime attempt to set node `0x14` PIN_WIDGET_CONTROL to `0x40` read back as `0x00` immediately.

## Temporary sysfs experiment and recovery

The temporary `user_pin_configs` values `0x14 0x90170110` and `0x17 0x90170111` were accepted. PipeWire, WirePlumber, pipewire-pulse, and their activation sockets were stopped; `/dev/snd` had no remaining `fuser` holders.

Writing `1` to `/sys/class/sound/hwC0D0/reconfig` did not complete. The `tee` process entered D-state while the kernel was in this teardown path:

```text
reconfig_store
reconfig_codec
snd_hda_codec_reset
snd_soc_unregister_component_by_driver
soc_cleanup_card_resources
snd_card_free
```

During partial teardown, HDMI PCM nodes disappeared while analog and DMIC/deep-buffer PCMs remained. The experiment was stopped and the machine was rebooted rather than attempting another reconfiguration.

After reboot, `user_pin_configs` was empty, pin configs were restored to `0x411111f0` (`0x14`) and `0x90170180` (`0x17`), the complete ALSA PCM inventory had returned, PipeWire/WirePlumber were normal, `HiFi__Speaker__sink` was default, and bottom speakers audibly worked. No persistent damage occurred.

## Conclusions and constraints

- Do not repeat live HDA sysfs reconfiguration on this machine unless new evidence establishes a safe method. See the repository [agent safety guidance](../../AGENTS.md#hp-envy-audio-research).
- The proposed `0x14`/`0x17` overrides were never applied successfully; this experiment provides no evidence that they work.
- A previous live-image recollection that the top speakers once produced audio is historical, user-reported evidence only. The repository has insufficient information to establish which action caused it.
- This record captures observations and constraints; it does not recommend runtime codec writes, pin overrides, or boot parameter changes.
