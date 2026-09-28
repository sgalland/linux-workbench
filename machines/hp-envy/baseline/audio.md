# Audio baseline

The later speaker investigation and sysfs reconfiguration experiment are recorded in [`audio-investigation-2026-09-27.md`](../audio-investigation-2026-09-27.md). Read that safety record before any further machine-specific audio work.

This records the observed state without attempting diagnosis or repair. The known report that the Bang & Olufsen internal speakers do not work correctly under Linux is preserved as user-provided context. Other audio functionality has worked in previous testing, also per user report.

## Kernel and hardware path

- PCI audio controller: Intel 500-series on-package HDA controller, bound to `sof-audio-pci-intel-tgl`.
- The SOF stack selected the `skl_hda_dsp_generic` machine driver and reported two digital microphones in platform tables.
- `/sys/class/sound` exposed one `sof-hda-dsp` card with analog, HDMI, microphone, and deep-buffer PCM endpoints.
- `/proc/asound/cards` exposed one SOF HDA DSP card. `/proc/asound/pcm` listed analog playback/capture, three HDMI playback PCMs, two digital-microphone capture PCMs, and analog deep-buffer playback.
- HDA codec nodes included Realtek ALC245 (kernel codec module `snd_hda_codec_alc269`) and Intel HDMI (`snd_hda_codec_intelhdmi`). The kernel log reported the analog line output classified as speaker, one headphone output, and a microphone input; this is topology enumeration, not a playback test.
- Kernel messages showed SOF firmware/topology loading and an HDMI topology warning that no PCM was available for one HDMI converter.

## Related buses

- ACPI exposed an HDAS SoundWire controller path and child paths `SWD0` through `SWD7`; the inspected `/sys/bus/soundwire/devices` directory had no device entries.
- No audio-specific I2C endpoint was identified in the inspected I2C device entries. The platform has Intel LPSS I2C controllers; graphics-related I2C buses were also present.
- No speaker fixup or configuration was attempted.

## User-session audio state

- `systemctl --user` could not connect to the user service bus from the Codex execution environment.
- `wpctl status` and `pactl` sink/source/card queries could not reach PipeWire from that environment. These results are access limitations of this run, not evidence that PipeWire or WirePlumber is failing in the CachyOS user session.
- `aplay -l` and `arecord -l` reported no soundcards from the Codex execution environment despite readable ALSA proc and sysfs card information. This mismatch does not establish that ALSA devices are absent from the host session.
- Active sinks, sources, and profiles could not be reliably enumerated from the Codex execution environment. No independent host-session evidence was collected for those facilities.

## Kernel messages

Relevant readable boot messages described SOF/HDA initialization, codec enumeration, analog output/headphone/microphone topology, digital microphone detection, and the HDMI topology warning summarized above. Unrelated messages and raw log output were not retained.
