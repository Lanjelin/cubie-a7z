# Inky Cubie A7Z Fix

This folder captures the working setup for the Cubie A7Z with the 2.13" Inky pHAT (SSD1608).

## What this is for

- `inky.auto.auto()` does not work on this board because the EEPROM is not visible on any of the accessible I2C buses.
- The working display path is the manual SSD1608 pHAT driver.
- The Cubie wiring uses:
  - `PIN_11` busy = `gpiochip0` line `33`
  - `PIN_24` CS = `gpiochip0` line `106`
  - `PIN_13` reset = `gpiochip1` line `6`
  - `PIN_15` DC = `gpiochip1` line `7`
  - `spidev1.0`

## Files

- `inky-cubie-a7z.patch`: patch for the installed `inky` library
- Python dependencies are intentionally not frozen here; install the Pimoroni `inky` package version that matches your target environment before applying the patch.
- `spi1-spidev-manual-cs.dts`: source for the custom overlay
- `sun60iw2p1-spi1-spidev-manual-cs.dtbo`: compiled boot-time overlay required for `/dev/spidev1.0` and the Cubie GPIO mapping
- `examples/hello_world_3x.py`: minimal visible test

## Boot-time overlay

This setup assumes your custom device-tree overlay is loaded at boot. The source is `spi1-spidev-manual-cs.dts` and the compiled artifact is `sun60iw2p1-spi1-spidev-manual-cs.dtbo`.

On Armbian, install the compiled DTBO at:

- `/boot/overlay-user/sun60iw2p1-spi1-spidev-manual-cs.dtbo`

Then edit `/boot/armbianEnv.txt` and add:

```ini
user_overlays=sun60iw2p1-spi1-spidev-manual-cs
```

After applying the changes in `/boot`, reboot the board for the overlay to take effect. You can verify it loaded with:

```bash
ls /dev/spidev1.0
```

That overlay is responsible for exposing:

- `/dev/spidev1.0`
- `gpiochip0` line `33` for `PIN_11` busy
- `gpiochip0` line `106` for `PIN_24` CS
- `gpiochip1` line `6` for `PIN_13` reset
- `gpiochip1` line `7` for `PIN_15` DC

The patch and the example only work correctly when that overlay is already active at boot.

## How to include this in a project

Recommended flow:

1. Create or activate the project virtualenv.
2. Build and install the boot-time overlay: copy `sun60iw2p1-spi1-spidev-manual-cs.dtbo` to `/boot/overlay-user/` and add `user_overlays=sun60iw2p1-spi1-spidev-manual-cs` to `/boot/armbianEnv.txt`.
3. Install the Pimoroni `inky` package and its normal dependencies for your target environment.
4. Apply `inky-cubie-a7z.patch` to the installed `inky` package.
5. Import the SSD1608 pHAT driver directly in your code:

```python
from inky.phat import InkyPHAT_SSD1608
```

6. Instantiate it manually with the Cubie pin mapping:

```python
inky = InkyPHAT_SSD1608("black")
inky.cs_pin = "CUBIE_HW_CS"
inky.dc_pin = "PIN_15"
inky.reset_pin = "PIN_13"
inky.busy_pin = "PIN_11"
```

7. Build your image with PIL and call `set_image()` and `show()`.

## Notes

- Do not rely on `auto()` on this board unless the EEPROM becomes visible on a usable I2C bus.
- The working display path is the SSD1608 pHAT class, not the generic base driver.
- The panel on this setup renders with an inverted-looking palette relative to the PIL buffer values. The example uses the known-good polarity.

## Applying the patch

From the `site-packages` directory of the virtualenv:

```bash
cd ~/.venvs/inky/lib/python3.13/site-packages
patch -p1 < /home/las/inky-fix/inky-cubie-a7z.patch
```

If you vendor `inky` inside a project, apply the same patch relative to that vendored copy.
