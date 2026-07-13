# Screen Time for Waveshare 2.13inch e-Paper HAT+ V4 on Cubie A7Z

This directory is self-contained for the Waveshare version of `screen-time.py`.

It includes:

- `screen-time.py`: the status display script, updated from Inky to Waveshare V4
- `waveshare_epd/`: vendored Waveshare Python driver with the working Cubie pin mapping
- `requirements.txt`: minimal Python dependencies for the current Waveshare status display
- `spi1-spidev-manual-cs.dts`: source for the SPI1 overlay
- `sun60iw2p1-spi1-spidev-manual-cs.dtbo`: compiled SPI1 overlay

## Working Cubie wiring for the Waveshare HAT

- `PIN_11` reset = `gpiochip0` line `33`
- `PIN_18` busy = `gpiochip0` line `313`
- `PIN_22` DC = `gpiochip1` line `5`
- `PIN_24` CS = `gpiochip0` line `106`
- `spidev1.0`

## Boot-time overlay

This setup assumes your custom device-tree overlay is loaded at boot. The source is `spi1-spidev-manual-cs.dts` and the compiled artifact is `sun60iw2p1-spi1-spidev-manual-cs.dtbo`.

On Armbian, install the compiled DTBO at:

- `/boot/overlay-user/sun60iw2p1-spi1-spidev-manual-cs.dtbo`

Then edit `/boot/armbianEnv.txt` and add:

```ini
user_overlays=sun60iw2p1-spi1-spidev-manual-cs
```

After applying the changes in `/boot`, reboot the board for the overlay to take effect. Verify it loaded with:

```bash
ls /dev/spidev1.0
```

## Running

The script adds its own directory to `sys.path` and defaults `EPD_PLATFORM=cubie`, so it can use the bundled driver directly.

Install the minimal Python dependencies:

```bash
python3 -m pip install -r requirements.txt
```

One-shot test:

```bash
cd /home/las/screen-time
python3 screen-time.py --once
```

Normal loop:

```bash
cd /home/las/screen-time
python3 screen-time.py
```

Custom refresh interval:

```bash
python3 screen-time.py --interval 15
```

## Install as a boot service

The included `screen-time.service` runs the display as root because the script needs direct SPI/GPIO access. The unit assumes the deployed files live in `/opt/screen-time`.

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
