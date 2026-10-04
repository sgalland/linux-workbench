# HP Envy fingerprint-reader investigation

Collected 2026-10-03. This is a read-only inventory of the HP ENVY Laptop
17-ch0xxx in the Codex execution environment. No fingerprint enrollment or
host configuration change was performed. Device serials, biometric data, and
unrelated device identifiers are omitted.

## Hardware identification

- USB vendor/product ID: **`04f3:0c4c`**. Sysfs and udev identify the device as
  `ELAN:ARM-M4` from ELAN. The ID, rather than the product string alone,
  distinguishes this reader from other ELAN ARM-M4 models.
- The device appears at `/sys/bus/usb/devices/3-5` in this collection. Its one
  interface (`3-5:1.0`) has class/subclass/protocol `ff/00/00` (vendor
  specific). `lsusb -t` likewise shows a vendor-specific interface at 12 Mb/s
  with `Driver=[none]`. The USB path is transient, not a stable machine ID.
- A targeted current-boot kernel journal query records `idVendor=04f3`,
  `idProduct=0c4c`, `bcdDevice=3.05`, and full-speed enumeration by `xhci_hcd`.
  It reports product/manufacturer strings matching sysfs. No serial value was
  collected.
- No fingerprint-named PCI function was found. This is a USB reader; the
  absence of a kernel interface driver alone does not establish whether a
  userspace `libfprint` driver can use it.

## Local software and recognition state

- Installed CachyOS packages: `libfprint 1.94.100-1.1` and `fprintd
  1.94.5-2.1` (`pacman -Q`).
- The installed `/usr/lib/udev/hwdb.d/60-autosuspend-libfprint-2.hwdb` has
  other ELAN `04f3` entries but no `04F3p0C4C` entry. The installed
  `70-libfprint-2.rules` also has no match for `0c4c`. These are indicators,
  not a direct runtime test of every driver compiled into the library.
- A read-only `fprintd` D-Bus `GetDevices` call failed before reaching the
  service: `Error connecting: Could not connect: Operation not permitted`.
  Thus recognition by the installed daemon was **not directly observed** in
  this execution environment. The older baseline documents similar host
  access limits here; this error is not evidence that `fprintd` fails in the
  normal desktop session.
- `lsusb -d 04f3:0c4c` reported `unable to initialize libusb: -99` here.
  Sysfs, udev, and `lsusb -t` supplied the identification and topology instead.

## Support assessment

The [upstream libfprint development-device list](https://fprint.freedesktop.org/supported-devices.html),
checked 2026-10-03, does **not** list `04f3:0c4c`; it lists nearby ELAN IDs,
which must not be assumed compatible. This and the installed hardware-database
absence make stock support unlikely. The available evidence fits **support
through an out-of-tree userspace libfprint driver**, rather than a missing
kernel module or a demonstrated firmware requirement. It does not prove that
the installed daemon rejects the device, because the local D-Bus check was
blocked.

An [experimental `elanmoc2` branch](https://gitlab.freedesktop.org/Depau/libfprint/-/tree/elanmoc2)
and [upstream merge request !330](https://gitlab.freedesktop.org/libfprint/libfprint/-/merge_requests/330)
target this exact ID. A [third-party port tested on Ubuntu 24.04](https://github.com/fschneid9/libfprint-elanmoc2-04f3-0c4c-ubuntu)
reports detection, enrollment, and verification for `04f3:0c4c` with a patched
`libfprint`. Those are external reports, not results on this CachyOS machine.
The upstream merge-request page could not be opened from this environment, so
its current merge status remains unverified; the upstream supported-device
list still omits this ID. No newer stock package with confirmed support was
identified.

## Evidence and commands

Only relevant fields were retained from these unprivileged, read-only checks:

```text
cat /sys/bus/usb/devices/3-5/{idVendor,idProduct,manufacturer,product}
cat /sys/bus/usb/devices/3-5:1.0/{bInterfaceClass,bInterfaceSubClass,bInterfaceProtocol}
readlink /sys/bus/usb/devices/3-5:1.0/driver
udevadm info --query=property --path=/sys/bus/usb/devices/3-5
lsusb -d 04f3:0c4c
lsusb -t
journalctl -k -b --no-pager -g '04f3|0c4c|3-5' -n 30
lspci -nn  # checked only for a fingerprint-related controller
pacman -Q libfprint fprintd
rg -i '0c4c|04f3' /usr/lib/udev/rules.d/70-libfprint-2.rules /usr/lib/udev/hwdb.d/60-autosuspend-libfprint-2.hwdb
gdbus call --system --dest net.reactivated.Fprint --object-path /net/reactivated/Fprint/Manager --method net.reactivated.Fprint.Manager.GetDevices
```

## Initial recommended next step and uncertainties (2026-10-03)

The initial recommendation was to repeat the read-only `GetDevices` query in
the ordinary CachyOS desktop session to confirm whether `fprintd` exposes the
reader. Do not infer support from a nearby USB ID. If it returns no device,
review the exact-ID `elanmoc2` source and merge-request status, then prepare a
separate, reversible CachyOS package/integration proposal for human review.
That proposal would need to account for replacing the packaged `libfprint`,
package upgrades, daemon compatibility, device-side template behavior, and a
rollback to the stock package before any install or enrollment is authorized.
No firmware need has been established. If further device diagnostics require
privilege, propose the specific command for separate approval.

## Desktop `fprintd` follow-up (2026-10-04)

Sysfs again identified the present reader as ELAN `04f3:0c4c` (`ELAN:ARM-M4`)
before the daemon result was interpreted. The exact read-only query was:

```text
gdbus call --system --dest net.reactivated.Fprint --object-path /net/reactivated/Fprint/Manager --method net.reactivated.Fprint.Manager.GetDevices
```

The sandboxed call was blocked with `Error connecting: Could not connect:
Operation not permitted`. Running the same query from the normal host
environment returned `(@ao [],)`: the installed `fprintd` service was reachable
but exposed no devices. Thus local stock runtime recognition of this reader is
**absent**. No fingerprint operation or host configuration change was performed.

Next, evaluate the exact-ID experimental `elanmoc2`/patched-`libfprint` path in
a separate human-reviewed proposal before any installation or enrollment.
