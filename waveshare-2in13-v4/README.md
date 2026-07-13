# Waveshare 2.13inch e-Paper HAT+ V4

This workspace is for the black/white Waveshare 2.13inch e-Paper HAT+ V4 with partial refresh support.

## What carries over from the Cubie setup

- The SPI1 overlay setup is still reusable.
- The same boot-time overlay mechanism on Armbian still applies.
- Verifying `/dev/spidev1.0` after reboot is still the first sanity check.

## What does not carry over

- The Inky driver patch is specific to the Pimoroni library and does not apply here.
- The exact display Python module still needs to be selected for the Waveshare board/library.

## Files

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

If you prefer environment setup instead of modifying the script, export:

```bash
export PYTHONPATH=/home/las/.cubie-setup/waveshare-2in13-v4
export EPD_PLATFORM=cubie
```

`EPD_PLATFORM=cubie` forces the patched Cubie backend in `epdconfig.py`.

- `spi1-spidev-manual-cs.dts`: overlay source reused from the Cubie setup
- `sun60iw2p1-spi1-spidev-manual-cs.dtbo`: compiled overlay reused from the Cubie setup
- Python dependencies are intentionally not frozen here; use `../screen-time/requirements.txt` for the current Waveshare status display setup
- `examples/`: place Waveshare test scripts here

## Boot-time overlay

On Armbian, install the compiled DTBO at:

- `/boot/overlay-user/sun60iw2p1-spi1-spidev-manual-cs.dtbo`

Then edit `/boot/armbianEnv.txt` and add:

```ini
user_overlays=sun60iw2p1-spi1-spidev-manual-cs
```

After changes under `/boot`, reboot the board.

Verify the overlay loaded with:

```bash
ls /dev/spidev1.0
```

## Next step

Install the Waveshare Python driver that matches the 2.13inch HAT+ V4 board, then add a minimal text test under `examples/`.

If the V4 driver produces no visible update on the panel, try the alternate black/white controller family:

- `examples/hello_world_v3.py`
- `examples/hello_world_v2.py`

Those scripts use `waveshare_epd/epd2in13_V3.py` and `waveshare_epd/epd2in13_V2.py` against the same Cubie SPI/GPIO wiring.

The official Waveshare e-Paper repository is here:

- https://github.com/waveshareteam/e-Paper

## Notes

- The display itself is different from the Inky pHAT, so the previous `inky`-specific code should not be reused directly.
- The SPI1 overlay and the boot-time deployment pattern are the reusable parts.
- The vendored `waveshare_epd/` directory is the local copy to modify for Cubie-specific fixes.
