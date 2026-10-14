# CachyOS workstation reinstall state — 2026-10

This record captures workstation decisions and verified setup outcomes from the
September/October 2026 CachyOS reinstall. It is a reproducibility note, not an
authorization to mutate a machine. Secrets, refresh tokens, browser profiles,
and other private account state must not be committed.

## Application baseline

The following applications or workflows were selected for this workstation.

### Confirmed installed or working

- ChatGPT / Codex
- Spotify via `spotify-launcher`
- Brave
- Blender
- Krita
- Inkscape
- Visual Studio Code, using the Microsoft `visual-studio-code-bin` build
- Obsidian
- Godot with C# support via `godot-mono`
- GitHub CLI (`gh`)
- Thunderbird for mail
- AnyDesk
- JetBrains Toolbox
- CachyOS gaming stack, including Steam, Heroic, Lutris, Gamescope, MangoHud,
  and GOverlay
- ModernUO built locally
- Ultima Online Classic game assets installed through the official updater
- ClassicUO running natively against the UO asset directory
- Insync selected as the OneDrive integration

### Standard JetBrains IDE set

The normal IDE set for this workstation is:

- PyCharm
- Rider
- CLion
- WebStorm

JetBrains Toolbox manages these IDE installations and updates.

## Package-management decisions

CachyOS uses Shelly for repository/AUR workflows on this installation. The
working Shelly grammar observed on this machine is:

```text
shelly search aur <package>
shelly install aur <package>
```

Equivalent shorthand uses `-Sa` for AUR search. Do not assume `paru` is
installed.

For Visual Studio Code, prefer the Microsoft binary package
`visual-studio-code-bin` rather than the Arch `code` build unless the user
explicitly chooses otherwise.

For Godot, prefer `godot-mono` because C# is part of the user's normal
development stack.

## Ultima Online / ModernUO layout

ModernUO is kept under the normal repository root:

```text
~/Projects/ModernUO
```

ModernUO required a project-pinned .NET SDK newer than the CachyOS system SDK
at the time of setup. A user-local .NET installation under `~/.dotnet` was
used rather than editing ModernUO's `global.json`.

The official Ultima Online Classic updater was installed in a dedicated Wine
prefix:

```text
~/.local/share/wineprefixes/ultima-online
```

The UO asset directory used by ModernUO and ClassicUO is:

```text
~/.local/share/wineprefixes/ultima-online/drive_c/Program Files (x86)/Electronic Arts/Ultima Online Classic/
```

The official updater did not launch usefully under plain Wine, but did run
when added to Steam and forced through Proton Experimental.

ClassicUO runs natively on Linux and reads the same official UO asset
directory. Keep the native ClassicUO client separate from the official UO
asset installation.

## OneDrive

The abraunegg OneDrive client / OneDriveGUI approach was abandoned because a
normal sync would locally mirror a very large OneDrive library. A proposed
rclone-mount replacement was also superseded.

The selected solution is **Insync**. Treat Insync as the canonical OneDrive
integration for this workstation unless that decision is explicitly revisited.

## Windows virtualization

The host virtualization stack is installed and validated:

- QEMU/KVM
- libvirt
- virt-manager
- OVMF / UEFI firmware
- swtpm
- VirtIO Windows drivers

Observed host validation:

- Intel VMX available
- `/dev/kvm` present and accessible
- `kvm_intel` loaded
- IOMMU/DMAR available and enabled
- libvirt running
- virt-manager launches successfully

The intended Windows 11 guest configuration is:

- Q35 machine type
- UEFI/OVMF
- TPM 2.0, CRB model
- VirtIO storage
- VirtIO network
- default libvirt NAT network
- Windows install ISO plus a second `virtio-win.iso` CD-ROM

Windows 11 installation is **deferred** because the Secure Boot firmware/key
enrollment path was not yet working acceptably. Host virtualization itself is
not blocked.

## Gaming compatibility work still open

### Star Trek Fleet Command

Native Linux support is not available. The current preferred path is Lutris
with its STFC installer and a GE-Proton-compatible runner. Steam non-Steam
installer launch was attempted first and did not start the Scopely installer.

Status: in progress / not yet confirmed working.

### GOG Galaxy

GOG Galaxy itself remains unresolved. Heroic is already installed as part of
the CachyOS gaming stack and may replace the need for Galaxy. Decide whether a
Galaxy-specific workflow is actually required before adding another Windows
compatibility prefix.

## Hardware enablement

The HP Envy fingerprint reader and audio work are tracked separately under
this machine profile. Do not duplicate those investigations here.

The fingerprint reader is ELAN `04f3:0c4c`; stock `libfprint` does not
currently expose it. See the dedicated fingerprint investigation for the
experimental driver direction.

## Reproducibility inventory

A future workstation capture should gather normalized, reviewable state rather
than copying arbitrary home-directory configuration.

Useful inventory surfaces include:

- explicitly installed repository packages
- explicitly installed foreign/AUR packages
- Flatpak/AppImage applications
- enabled system and user services
- VS Code extensions
- available .NET SDKs
- Git/GitHub CLI configuration presence
- development toolchain versions
- Steam/Lutris/Wine compatibility locations and runner choices
- app-specific installation decisions documented above

Do not commit tokens, credentials, refresh tokens, private browser state, SSH
private keys, or an indiscriminate copy of `~/.config`.

The goal is a reinstall workflow where Linux Workbench can reconstruct known
software and configuration deterministically while leaving account
authentication and other secret-bearing steps manual.
