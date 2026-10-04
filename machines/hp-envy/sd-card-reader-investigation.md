# HP Envy SD card reader investigation

Collected 2026-10-04 with unprivileged, read-only commands on the HP ENVY
Laptop 17-ch0xxx. An SD card was inserted during inspection. No card contents,
filesystem identifiers, storage serials, or unrelated device identifiers are
retained in this record, and no host or media configuration was changed.

## Controller and driver

- PCI function `0000:2b:00.0` is a Realtek RTS5288 PCIe SD UHS-I Card Reader
  controller, vendor/device **`10ec:5228`**, revision `01`, with HP subsystem
  **`103c:88b5`**. The PCI class is `ff00`. The PCI address can change between
  boots; the vendor/device and subsystem IDs identify the hardware more
  reliably.
- Sysfs and udev agree that `rtsx_pci` is bound to the PCI function. Its child
  platform device is bound to `rtsx_pci_sdmmc` and exposes `/sys/class/mmc_host/mmc0`.
  `lsmod` shows `rtsx_pci`, `rtsx_pci_sdmmc`, and `mmc_core` loaded. This is a
  PCIe Realtek reader feeding the MMC subsystem, not a USB reader or a generic
  SDHCI controller.
- The current-boot kernel journal records `rtsx_pci` enabling the controller.
  No targeted `rtsx_pci` error appeared in the inspected messages.

## Card and block-device state

- `/sys/bus/mmc/devices` currently contains one card under `mmc0`; its sysfs
  `type` is `SD`. Udev reports `MMC_TYPE=SD` and `MODALIAS=mmc:block`.
- The current-boot kernel journal records SDXC UHS-I SDR104 detection, then
  removal and redetection. Thus the controller and host **do detect inserted
  media**. These events do not establish that sectors can be read.
- The detected card has no bound MMC device driver. `mmc_block` is absent from
  `lsmod` and `/sys/module`, and no `mmcblk*` device appears in `/sys/class/block`
  or `lsblk`. No filesystem exposure can be assessed without a block device.
- The running kernel is `7.2.8-1-cachyos`, but
  `/usr/lib/modules/7.2.8-1-cachyos` is absent. `modinfo mmc_block` for that
  running kernel fails with “Module mmc_block not found.” Its readable kernel
  configuration says `CONFIG_MMC_BLOCK=m`, so this driver was configured as a
  module, not built into the running kernel. The installed `linux-cachyos`
  package is `7.2.9-1`; that version's module tree contains `mmc_block.ko.zst`,
  and `modinfo -k 7.2.9-1-cachyos` reports the `mmc:block` alias.

**Observed classification:** controller enumerated and bound; media detected;
no MMC block driver bound and no card block device. The running-kernel/module-tree
mismatch is the strongest local explanation for the missing `mmc_block` driver.
The inspected journal contains no `mmc_block` or `mmcblk` message, so the exact
autoload failure path is unconfirmed. There is no evidence here of a Realtek
controller quirk, firmware dependency, or card filesystem problem.

## Evidence and commands

Relevant output was retained from these read-only checks (the card's transient
MMC address is omitted here):

```text
lspci -Dnnk                 # inspected only the Realtek card-reader function
cat /sys/bus/pci/devices/0000:2b:00.0/{vendor,device,subsystem_vendor,subsystem_device,class,modalias}
readlink /sys/bus/pci/devices/0000:2b:00.0/driver
readlink /sys/bus/platform/devices/rtsx_pci_sdmmc.0/driver
udevadm info --query=property --path=/sys/bus/pci/devices/0000:2b:00.0
lsmod                      # inspected rtsx, mmc, and sdhci entries only
find /sys/class/mmc_host /sys/bus/mmc/devices /sys/class/block -maxdepth 2
cat /sys/bus/mmc/devices/<card>/type
readlink /sys/bus/mmc/devices/<card>/driver
udevadm info --query=property --path=/sys/bus/mmc/devices/<card>
lsblk -dn -o NAME,TYPE,TRAN,RM,SIZE
journalctl -k -b -o cat --no-pager -g 'mmc0:|mmcblk|rtsx_pci'
uname -r
zgrep '^CONFIG_MMC_BLOCK=' /proc/config.gz
modinfo -F filename mmc_block
modinfo -k 7.2.9-1-cachyos -F filename mmc_block
modinfo -k 7.2.9-1-cachyos -F alias mmc_block
pacman -Q                      # inspected the linux-cachyos entry only
```

`lspci -Dnnk` reported a libkmod resource warning, but PCI ID, driver binding,
sysfs, and udev agreed independently. No upstream lookup was needed to identify
the immediate local gap.

## Recommended next step and uncertainties

Arrange a separately authorized, planned boot into a kernel with its matching
module tree, then repeat read-only checks of `uname -r`, `modinfo mmc_block`,
the card's MMC driver link, `lsblk`, and targeted kernel messages with an SD
card inserted. The already installed `7.2.9-1-cachyos` tree contains the
matching block module, but a successful block device after boot is **not yet
observed**. A boot plan should identify a known-good fallback and how to select
it if verification fails; this investigation did not change boot state.

If a matching boot still detects the card without `mmcblk`, inspect the
specific udev/module-load failure and kernel messages before proposing any
module, package, quirk, or firmware change. Card readability, partition layout,
and filesystem health remain unknown.
