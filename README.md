# Cubie A7Z setup notes

This repository is a working notebook for a Radxa Cubie A7Z running Armbian. It collects the bits that made the board useful: first-boot configuration, Wi-Fi fallback setup, fan control, e-paper display experiments, a status display script, and printable enclosure files.

It is intentionally practical rather than polished. Some directories are hardware bring-up notes, some are deployable scripts, and some are snapshots of a known-good local environment.

<p align="center">
  <img src="print-files/photos/top.jpeg" alt="Cubie A7Z enclosure top view" width="100%">
</p>

<p align="center">
  <img src="print-files/photos/sc_slot.jpeg" alt="Cubie A7Z enclosure SD card slot detail" width="49%">
  <img src="print-files/photos/antenna_slot.jpeg" alt="Cubie A7Z enclosure antenna slot detail" width="49%">
</p>

## Quick start order

This is the intended path through the repo when bringing up a fresh Cubie A7Z:

1. Flash an Armbian image for the Cubie A7Z.
2. Optionally prepare first boot with `armbian/.not_logged_in_yet.example`.
3. Install the SPI1 overlay and verify `/dev/spidev1.0`.
4. Configure Wi-Fi and the fallback AP from `wifi/`.
5. Install `fan/` if using the vendor stock cooling/fan.
6. Test the e-paper status display with `screen-time/screen-time.py --once`.
7. Install `screen-time/screen-time.service` for boot startup.
8. Print or modify the enclosure from `print-files/`.

## Printable enclosure

The Cubie A7Z enclosure files live in [`print-files/`](print-files/). That folder includes editable CAD, STEP export, print-ready 3MF files, CAD screenshots, and photos of the printed result. The enclosure covers the stock vendor cooling/fan setup and includes ventilation holes plus cutouts for the camera, antenna, SD card, HDMI, and USB.

## Repository map

| Path | What it contains |
| --- | --- |
| `armbian/` | Armbian-specific setup notes. `armbian/.not_logged_in_yet.example` is a first-boot autoconfig template copied from the Armbian documentation. |
| `fan/` | A simple PWM fan daemon for the Cubie A7Z plus a systemd unit. The daemon reads thermal zones, ignores `skin_zone`, and writes `/sys/class/hwmon/hwmon1/pwm1` using a small temperature curve. |
| `wifi/` | NetworkManager/netplan notes for normal Wi-Fi plus a fallback access point. The timer/service waits after boot and starts the `cubie-ap` connection if `wlan0` never gets an IPv4 address or active Wi-Fi client connection. |
| `inky-fix/` | The older Pimoroni Inky pHAT bring-up path. Includes the Cubie A7Z patch, SPI1 overlay source/compiled DTBO, and minimal examples for the SSD1608 pHAT driver. |
| `waveshare-2in13-v4/` | Waveshare 2.13 inch e-Paper HAT+ V4 experiments. Includes a trimmed vendored `waveshare_epd/` driver copy, test scripts, and the same SPI1 overlay assets. |
| `screen-time/` | The current Waveshare-based status display project. It bundles the patched Waveshare driver, SPI1 overlay assets, minimal Python requirements, and `screen-time.py`, which renders a landscape status screen and uses partial refreshes with periodic full refreshes. |
| `print-files/` | Printable Cubie A7Z enclosure files: editable CAD, STEP export, print-ready 3MF files, screenshots, photos, and feature notes in `print-files/README.md`. |

## Armbian notes

The board is running Armbian.

- General Armbian documentation: <https://docs.armbian.com/>
- First-boot autoconfig docs: <https://docs.armbian.com/User-Guide_Autoconfig/>
- Local template: [`armbian/.not_logged_in_yet.example`](armbian/.not_logged_in_yet.example)
- Radxa Cubie A7Z Armbian images: <https://github.com/NickAlilovic/build/releases>
- Armbian forum thread for Radxa Cubie A7 / A7Z / Allwinner A733: <https://forum.armbian.com/topic/56130-radxa-cubie-a7aa7z-allwinner-a733/>

Typical flow for first boot:

1. Flash an Armbian image.
2. Mount the flashed image or boot media.
3. Copy `armbian/.not_logged_in_yet.example` to `/root/.not_logged_in_yet` on that mounted filesystem.
4. Replace every placeholder value before booting. Armbian stores these values in plaintext, including Wi-Fi and user/root passwords.
5. Boot the Cubie A7Z and let Armbian consume the file during first boot.

## SPI1 and e-paper overlay

The e-paper work depends on a custom SPI1 overlay that exposes `/dev/spidev1.0` and the Cubie-specific GPIO mapping used by the display drivers.

The repeated overlay files are:

- `spi1-spidev-manual-cs.dts` — source overlay
- `sun60iw2p1-spi1-spidev-manual-cs.dtbo` — compiled overlay

Install the compiled overlay on Armbian at:

```text
/boot/overlay-user/sun60iw2p1-spi1-spidev-manual-cs.dtbo
```

Then add this to `/boot/armbianEnv.txt`:

```ini
user_overlays=sun60iw2p1-spi1-spidev-manual-cs
```

Reboot and verify:

```bash
ls /dev/spidev1.0
```

## Display work

There are three display-related folders because the setup moved from Inky experiments to the current Waveshare status display.

### `inky-fix/`

Captures the Pimoroni Inky pHAT path. `inky.auto.auto()` did not work on this board because the EEPROM was not visible on the accessible I2C buses, so the working path used the manual SSD1608 pHAT class with Cubie-specific pins.

### `waveshare-2in13-v4/`

Captures the Waveshare 2.13 inch e-Paper HAT+ V4 bring-up. It keeps a local `waveshare_epd/` copy so Cubie pin and SPI fixes can be made without patching a global install. The full upstream Waveshare repository is <https://github.com/waveshareteam/e-Paper>.

### `screen-time/`

The status display application built on the Waveshare V4 setup. It defaults `EPD_PLATFORM=cubie`, imports its bundled `waveshare_epd` driver, renders through Pillow, and supports:

- one-shot test mode with `python3 screen-time.py --once`
- normal loop mode with `python3 screen-time.py`
- custom refresh interval with `python3 screen-time.py --interval 15`

## Wi-Fi fallback access point

`wifi/` contains notes and unit files for making the board recoverable when normal Wi-Fi does not connect.

- `etc_netplan_30-wifis-dhcp.yaml.example` is a netplan Wi-Fi config snapshot.
- `nmcli_network_priority_ap` records NetworkManager commands for connection priorities and the fallback AP.
- `wifi-fallback-ap.sh` waits for normal Wi-Fi, then brings up `cubie-ap` if no IPv4 address or active Wi-Fi client connection exists.
- `wifi-fallback-ap.service` and `wifi-fallback-ap.timer` run that check after boot.

## Fan daemon

`fan/cubie-fand` is a small Python daemon intended to be installed as `/usr/local/sbin/cubie-fand` and run with `fan/cubie-fand.service`.

It sets manual PWM mode, starts at a minimum PWM, samples thermal zones every five seconds, and raises/lowers the fan using hysteresis to avoid rapid speed changes.

