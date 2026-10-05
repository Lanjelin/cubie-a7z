# Waveshare 2.13inch e-Paper HAT+ V4

This workspace is for the black/white Waveshare 2.13inch e-Paper HAT+ V4 with partial refresh support.

## Confirmed Cubie A7Z setup

The current kernel base DTB already enables SPI1, with native `PD10`–`PD13` pinctrl and one `spidev@0` device. No SPI-enabling/manual-CS overlay is needed. The required overlay is `cubie-header-io-power`, which keeps the header I/O-bank supply enabled. Wi-Fi stays enabled.

| HAT signal | Header pin | GPIO/controller |
| --- | --- | --- |
| Reset | 11 | `PB1`, `gpiochip0` offset `33` |
| BUSY | 18 | `PJ25`, `gpiochip0` offset `313` |
| DC | 22 | `PL5`, `gpiochip1` offset `5` |
| CS | 24 | `PD10`, native SPI1 chip select owned by the kernel |

These are gpiochip-local offsets, not BCM numbers. The Cubie backend uses `/dev/spidev1.0` (bus `1`, device `0`), SPI mode `0`, `500000` Hz and `no_cs=False`. It sets `CS_PIN=None`; Waveshare's GPIO CS toggles are no-ops. Never request `PD10` with gpiod.

The older Inky driver patch and its manual-CS SPI overlay are not the current Waveshare setup.

## Vendored driver

A minimal copy of the Waveshare Python driver lives in:

- `waveshare_epd/`

That directory contains only the files needed for the 2.13inch V4 board:

- `__init__.py`
- `epd2in13_V4.py`
- `epdconfig.py`

Use this copy when you want to patch the driver for Cubie instead of editing the downloaded repo.

## How to include `waveshare_epd`

Keep `waveshare_epd/` inside your project and add the project root to `sys.path` before the first import:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from waveshare_epd import epd2in13_V4
```

If you prefer environment setup instead of modifying the script, export these variables from this `waveshare-2in13-v4/` directory:

```bash
export PYTHONPATH="$PWD"
export EPD_PLATFORM=cubie
```

`EPD_PLATFORM=cubie` forces the patched Cubie backend in `epdconfig.py`.

- `cubie-header-io-power.dts`: proven two-property header power overlay source
- Python dependencies are intentionally not frozen here; use `../screen-time/requirements.txt` for the current Waveshare status display setup
- `examples/hello_world_v4_fast.py`: V4 fast-refresh example using the bundled Cubie backend

## Boot-time header power overlay

`VCC33-LCD`/`SWOUT1`, switched by `dc1sw1`, powers the PD (SPI1) and PJ (BUSY) header banks. The supplied overlay adds only `regulator-boot-on` and `regulator-always-on` to `&reg_dc1sw1`; it does not alter pinctrl or Wi-Fi.

From this directory, compile with symbol support and install on Armbian:

```bash
dtc -@ -I dts -O dtb -o cubie-header-io-power.dtbo cubie-header-io-power.dts
sudo install -d /boot/overlay-user
sudo install -m 0644 cubie-header-io-power.dtbo /boot/overlay-user/cubie-header-io-power.dtbo
sudo nano /boot/armbianEnv.txt
```

Edit the existing `user_overlays` line: remove the obsolete `sun60iw2p1-spi1-spidev-manual-cs` token, add `cubie-header-io-power`, and preserve all unrelated tokens. With no unrelated overlays:

```ini
user_overlays=cubie-header-io-power
```

Do not load the old manual-CS overlay or add a Wi-Fi disable overlay. Reboot to apply the power overlay:

```bash
sudo reboot
```

After reconnecting, check the device and run the V4 example from this directory:

```bash
ls /dev/spidev1.0
python3 examples/hello_world_v4_fast.py
```

The presence of `/dev/spidev1.0` alone is not proof that the header banks are powered or the panel updates. For the status display's full-refresh/partial-refresh workflow, see `../screen-time/README.md` and run `screen-time.py --once` before enabling its service.

### Apt-upgrade regression and recovery

The upgraded base DTB omitted the original Radxa board DTS's `regulator-boot-on` for `dc1sw1`. At runtime, this switch was disabled although its parent `DCDC1` supplied 3.3 V. SPI1 remained enabled and GPIO/pinctrl source was unchanged; the missing `VCC33-LCD` bank power caused the failure, not a changed display controller or GPIO mapping.

With `cubie-header-io-power` loaded and native CS, the recovery diagnostic showed BUSY rising and a full refresh lasting `2.283 s`; actual visible updates were confirmed. The deployed status application also completed full and partial refreshes, with a partial-refresh BUSY wait of about `0.60 s`. The installed boot configuration uses `user_overlays=cubie-header-io-power`, with Wi-Fi enabled.

References: [Radxa A7Z schematic v1.11, pages 4 and 7](https://dl.radxa.com/cubie/a7z/docs/hw/radxa_cubie_a7z_schematic_v1.11.pdf) and [original Radxa board DTS](https://github.com/radxa/allwinner-device/blob/device-a733-v1.4.8/configs/cubie_a7z/linux-6.6/board.dts).

The official Waveshare e-Paper repository is here:

- https://github.com/waveshareteam/e-Paper

## Notes

- The display itself is different from the Inky pHAT, so the previous `inky`-specific code should not be reused directly.
- The Armbian boot-time deployment mechanism is reusable, but the current Waveshare overlay fixes header power rather than enabling SPI1.
- The vendored `waveshare_epd/` directory is the local copy to modify for Cubie-specific fixes.
