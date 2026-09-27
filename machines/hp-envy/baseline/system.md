# System baseline

Collected 2026-09-27 using unprivileged read-only commands.

## Operating system and kernel

- Distribution: CachyOS Linux (rolling; Arch-compatible base).
- Kernel: `7.2.8-1-cachyos`.
- Architecture: x86_64.

## Processor and memory

- CPU: 11th Gen Intel Core i7-1165G7, 4 cores / 8 threads.
- Installed memory: approximately 15 GiB reported by the running environment.
- Swap: approximately 15 GiB, presented as zram.

## System and firmware

- System vendor/model: HP ENVY Laptop 17-ch0xxx.
- Board vendor/model: HP / 88B5.
- BIOS vendor/version/date: Insyde / F.12 / 2022-02-24.

## Storage and filesystems

- Internal storage: Samsung 1 TB NVMe device (about 954 GiB reported).
- EFI system partition: 4 GiB VFAT mounted at `/boot`.
- Main filesystem: Btrfs, with subvolume mounts for root, home, srv, cache, log, tmp, and root's home.
- zram device: about 15.4 GiB, used for swap.

## EFI boot information

- EFI variables were readable without privilege.
- Current boot entry was `Limine`; firmware output also listed the internal disk boot option.
- Entry paths, boot identifiers, UUIDs, and removable-media labels were omitted.
