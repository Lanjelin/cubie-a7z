# Screen Time for Waveshare 2.13inch e-Paper HAT+ V4 on Cubie A7Z

This directory is self-contained for the Waveshare version of `screen-time.py`.

It includes:

- `screen-time.py`: the status display script, updated from Inky to Waveshare V4
- `waveshare_epd/`: vendored Waveshare Python driver with the working Cubie pin mapping
- `requirements.txt`: minimal Python dependencies for the current Waveshare status display
- `cubie-header-io-power.dts`: source for the header I/O-bank power overlay; the deployed application does not need a source/DTBO copy in `/opt/screen-time` at runtime

## Working Cubie wiring for the Waveshare HAT

- `PIN_22` DC = `gpiochip1` offset `5` (`PL5`)
- `PIN_11` reset = `gpiochip0` offset `33` (`PB1`)
- `PIN_18` busy = `gpiochip0` offset `313` (`PJ25`)
- `PIN_24` CS = native SPI1 chip select (`PD10`), owned by the kernel; never request it with gpiod
- `/dev/spidev1.0`: SPI bus `1`, device `0`, mode `0`, `500000` Hz, `no_cs=False`

The Cubie backend uses `CS_PIN=None`, so Waveshare's GPIO chip-select writes are no-ops and the SPI controller drives CS. These are gpiochip-local offsets, not BCM numbers. Keep Wi-Fi enabled; no Wi-Fi disable overlay is needed.

## Boot-time header power overlay

The current kernel base DTB already enables SPI1 with native `PD10`–`PD13` pinctrl and one `spidev@0` device. Do not load the old manual-CS SPI overlay: it conflicts with this native-CS configuration. `/dev/spidev1.0` existing alone does not prove that the header I/O banks are powered.

`cubie-header-io-power.dts` adds only `regulator-boot-on` and `regulator-always-on` to `&reg_dc1sw1`. This switch supplies `VCC33-LCD`/`SWOUT1`, powering the PD (SPI1) and PJ (BUSY) banks; it does not change SPI pinctrl or disable Wi-Fi.

Compile and install it from this `screen-time/` directory on Armbian:

```bash
dtc -@ -I dts -O dtb -o cubie-header-io-power.dtbo cubie-header-io-power.dts
sudo install -d /boot/overlay-user
sudo install -m 0644 cubie-header-io-power.dtbo /boot/overlay-user/cubie-header-io-power.dtbo
sudo nano /boot/armbianEnv.txt
```

In the existing `user_overlays` line, remove the obsolete `sun60iw2p1-spi1-spidev-manual-cs` token and add `cubie-header-io-power`, preserving every unrelated overlay token. With no unrelated overlays, the line is:

```ini
user_overlays=cubie-header-io-power
```

Do not add a Wi-Fi disable overlay. Reboot for the boot-time power change to take effect, then check the SPI device and run the one-shot display test below:

```bash
sudo reboot
```

After reconnecting:

```bash
ls /dev/spidev1.0
```

### Apt-upgrade regression and recovery

After the upgrade, SPI1 was still present but `dc1sw1` was disabled while its parent `DCDC1` remained at 3.3 V. The upgraded base DTB omitted the original board DTS's `regulator-boot-on`; GPIO/pinctrl source was unchanged. Unpowered `VCC33-LCD` header banks, not different GPIO pins or a different display controller, caused the missing updates.

With this power overlay and native CS, the recovery diagnostic produced a BUSY rise and a full refresh in `2.283 s`; visible panel updates were confirmed. The deployed status application also completed full and partial refreshes, with a partial-refresh BUSY wait of about `0.60 s`. The installed recovery uses `user_overlays=cubie-header-io-power` and leaves Wi-Fi enabled.

References: [Radxa A7Z schematic v1.11, pages 4 and 7](https://dl.radxa.com/cubie/a7z/docs/hw/radxa_cubie_a7z_schematic_v1.11.pdf) and [original Radxa board DTS](https://github.com/radxa/allwinner-device/blob/device-a733-v1.4.8/configs/cubie_a7z/linux-6.6/board.dts).

## Running

The script adds its own directory to `sys.path` and defaults `EPD_PLATFORM=cubie`, so it can use the bundled driver directly.

Run the following commands from this `screen-time/` directory in your checkout.

Install the minimal Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

One-shot test:

```bash
python3 screen-time.py --once
```

Normal loop:

```bash
python3 screen-time.py
```

Custom refresh interval:

```bash
python3 screen-time.py --interval 15
```

## Install as a boot service

`screen-time.service` runs the display as root because the script needs direct SPI/GPIO access. The unit assumes the deployed files live in `/opt/screen-time`.

From this directory:

```bash
sudo install -d /opt/screen-time
sudo cp -a screen-time.py waveshare_epd README.md requirements.txt /opt/screen-time/
sudo install -m 0644 screen-time.service /etc/systemd/system/screen-time.service
```

Optional local overrides:

```bash
sudo install -m 0644 screen-time.env.example /etc/default/screen-time
sudo nano /etc/default/screen-time
```

Available overrides:

- `SCREEN_TIME_INTERVAL=10`: seconds between update checks.
- `SCREEN_TIME_TUNNEL_REMOTE=`: optional `host:port` endpoint for the ▲/▼ tunnel indicator. Leave blank to skip that check completely.
- `SCREEN_TIME_HIDDEN_PORTS=111,5355`: comma-separated listening ports hidden from the port list.

Enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now screen-time.service
systemctl status screen-time.service
```

Logs:

```bash
journalctl -u screen-time.service -f
```

Before enabling the service, verify the boot overlay and Python dependencies manually:

```bash
ls /dev/spidev1.0
python3 screen-time.py --once
```

If your Python dependencies live in a virtualenv instead of system Python, edit `/etc/systemd/system/screen-time.service` and change `/usr/bin/python3` in `ExecStart` to the venv interpreter path.

## Notes

- This version now uses a full refresh to establish the base image, then uses Waveshare partial refresh for subsequent updates.
- After a number of partial refreshes, it forces a full refresh again to limit ghosting.
- The current implementation still sends the full framebuffer; it does not yet do true rectangle-only hardware partial window updates.
- The script renders onto a landscape canvas and feeds it through the Waveshare V4 driver.
- The vendored driver already contains the working Cubie pin mapping, so no separate patch file is needed.
