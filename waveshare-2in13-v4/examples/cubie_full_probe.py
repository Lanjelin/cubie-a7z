#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4


def make_image(epd, label, inverted=False):
    image = Image.new('1', (epd.width, epd.height), 0 if inverted else 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    fill = 255 if inverted else 0
    draw.text((10, 10), label, font=font, fill=fill)
    draw.text((10, 50), label, font=font, fill=fill)
    draw.text((10, 90), label, font=font, fill=fill)
    return image


def show(epd, image, label):
    print(f'stage: display {label}', flush=True)
    t0 = time.monotonic()
    epd.display(epd.getbuffer(image))
    print(f'busy after {label}: {epd2in13_V4.epdconfig.digital_read(epd.busy_pin)} elapsed={time.monotonic() - t0:.2f}s', flush=True)
    print(f'wait: settle after {label}', flush=True)
    time.sleep(12)


def main():
    print('stage: create EPD', flush=True)
    epd = epd2in13_V4.EPD()

    for cycle in range(2):
        print(f'stage: init cycle {cycle + 1}', flush=True)
        t0 = time.monotonic()
        epd.init()
        print(f'busy after init {cycle + 1}: {epd2in13_V4.epdconfig.digital_read(epd.busy_pin)} elapsed={time.monotonic() - t0:.2f}s', flush=True)

        print(f'stage: clear cycle {cycle + 1}', flush=True)
        t0 = time.monotonic()
        epd.Clear(0xFF)
        print(f'busy after clear {cycle + 1}: {epd2in13_V4.epdconfig.digital_read(epd.busy_pin)} elapsed={time.monotonic() - t0:.2f}s', flush=True)
        time.sleep(8)

        show(epd, make_image(epd, f'BLACK {cycle + 1}', inverted=True), f'black {cycle + 1}')
        show(epd, make_image(epd, f'WHITE {cycle + 1}', inverted=False), f'white {cycle + 1}')
        show(epd, make_image(epd, f'OK {cycle + 1}', inverted=False), f'ok {cycle + 1}')

        print(f'stage: sleep cycle {cycle + 1}', flush=True)
        epd.sleep()
        time.sleep(3)

    print('stage: done', flush=True)


if __name__ == '__main__':
    main()
