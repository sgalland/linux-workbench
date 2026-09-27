# Hardware baseline

Summarized from unprivileged `lspci -nnk`, `lsusb`, and `lsusb -t` output. No network addresses or nearby network identifiers were collected.

## PCI devices and bound drivers

- Host bridge: Intel Tiger Lake-UP3/H35; module candidate `igen6_edac` (no active driver reported).
- Integrated graphics: Intel Tiger Lake Iris Xe; active kernel driver `i915`.
- Thermal controller: Intel Dynamic Tuning; active driver `proc_thermal`.
- PCIe bridges: Intel; active driver `pcieport`.
- Intel GNA accelerator: enumerated; no active driver reported.
- Intel telemetry controller: active driver `intel_vsec`.
- USB controllers: Intel xHCI bound to `xhci_hcd`; Thunderbolt NHI bound to `thunderbolt`.
- Intel VMD controller: active driver `vmd`.
- Wireless network controller: Intel Wi-Fi 6 AX201; active driver `iwlwifi`.
- Intel LPSS I2C controllers: active driver `intel-lpss`.
- Intel management engine interface: active driver `mei_me`.
- Intel HDA audio controller: active driver `sof-audio-pci-intel-tgl`; details are in [`audio.md`](audio.md).
- Intel SMBus controller: active driver `i801_smbus`.
- Intel SPI controller: active driver `intel-spi`.
- Realtek PCIe SD card reader: active driver `rtsx_pci`.
- Samsung NVMe controller: active driver `nvme`.

## USB

- `lsusb` device enumeration was unavailable because libusb initialization failed in the Codex execution environment. This is not evidence of a CachyOS USB failure.
- `lsusb -t` showed Intel xHCI root hubs, a Bluetooth-class interface bound to `btusb`, and one vendor-specific interface with no driver shown.
- Bus/device numbers and other transient identifiers are not retained.

## Network privacy

Only adapter model and driver are recorded. IP addresses, MAC addresses, SSIDs, connection names, and other network state were not queried or recorded.
