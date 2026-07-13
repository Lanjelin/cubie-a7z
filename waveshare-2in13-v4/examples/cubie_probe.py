#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4


def main():
    print('stage: create EPD', flush=True)
    epd = epd2in13_V4.EPD()

    print('stage: init_fast', flush=True)
    t0 = time.monotonic()
    epd.init_fast()
    print(f'busy after init_fast: {epd2in13_V4.epdconfig.digital_read(epd.busy_pin)} elapsed={time.monotonic() - t0:.2f}s', flush=True)

    print('stage: clear', flush=True)
    t0 = time.monotonic()
    epd.Clear(0xFF)
    print(f'busy after clear: {epd2in13_V4.epdconfig.digital_read(epd.busy_pin)} elapsed={time.monotonic() - t0:.2f}s', flush=True)
    print('wait: settle after clear', flush=True)
    time.sleep(6)

    black = Image.new('1', (epd.width, epd.height), 0)
    white = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(white)
    font = ImageFont.load_default()
    draw.text((10, 10), 'OK', font=font, fill=0)
    draw.text((10, 50), 'OK', font=font, fill=0)
    draw.text((10, 90), 'OK', font=font, fill=0)

    print('stage: display black fast', flush=True)
    t0 = time.monotonic()
    epd.display_fast(epd.getbuffer(black))
    print(f'busy after black: {epd2in13_V4.epdconfig.digital_read(epd.busy_pin)} elapsed={time.monotonic() - t0:.2f}s', flush=True)
    print('wait: settle after black', flush=True)
    time.sleep(6)

    print('stage: display text fast', flush=True)
    t0 = time.monotonic()
    epd.display_fast(epd.getbuffer(white))
    print(f'busy after text: {epd2in13_V4.epdconfig.digital_read(epd.busy_pin)} elapsed={time.monotonic() - t0:.2f}s', flush=True)
    print('wait: settle after text', flush=True)
    time.sleep(6)

    print('stage: sleep', flush=True)
    epd.sleep()
    print('stage: done', flush=True)


if __name__ == '__main__':
    main()
