# Armbian notes for Radxa Cubie A7Z

This directory contains Armbian-specific first-boot setup notes for the Cubie A7Z.

Useful upstream/community links:

- Armbian documentation: <https://docs.armbian.com/>
- Armbian first-boot autoconfig: <https://docs.armbian.com/User-Guide_Autoconfig/>
- Cubie A7Z Armbian images: <https://github.com/NickAlilovic/build/releases>
- Armbian forum thread for Radxa Cubie A7A/A7Z / Allwinner A733: <https://forum.armbian.com/topic/56130-radxa-cubie-a7aa7z-allwinner-a733/>

## First-boot autoconfig

`./.not_logged_in_yet.example` is a public template for Armbian's `/root/.not_logged_in_yet` first-boot config.

Typical flow:

1. Flash the Armbian image.
2. Mount the flashed image or boot media.
3. Copy `.not_logged_in_yet.example` to `/root/.not_logged_in_yet` on the mounted filesystem.
4. Replace all placeholder values.
5. Boot the Cubie A7Z and let Armbian consume the file during first boot.

Example:

```bash
cp .not_logged_in_yet.example /path/to/mounted/root/.not_logged_in_yet
```

The values in `/root/.not_logged_in_yet` are plaintext. Do not commit a filled-out copy.

## Provisioning hook

Armbian also supports `/root/provisioning.sh`, which runs once as root after the first successful login. Use that for final local setup such as package installs, hostname changes, or service enablement.

See the upstream first-boot documentation for the current directive list and provisioning behavior: <https://docs.armbian.com/User-Guide_Autoconfig/>
