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
    epd = epd2in13_V4.EPD()

    print('init 1', flush=True)
    epd.init()

    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), 'V4 literal', font=font, fill=0)
    draw.text((10, 50), 'V4 literal', font=font, fill=0)
    draw.text((10, 90), 'V4 literal', font=font, fill=0)

    print('clear', flush=True)
    epd.Clear(0xFF)
    time.sleep(4)

    print('init 2', flush=True)
    epd.init()
    time.sleep(2)

    print('base image', flush=True)
    base = Image.new('1', (epd.height, epd.width), 255)
    epd.displayPartBaseImage(epd.getbuffer(base))
    time.sleep(4)

    print('partial image', flush=True)
    epd.displayPartial(epd.getbuffer(image))
    time.sleep(6)

    print('sleep', flush=True)
    epd.sleep()


if __name__ == '__main__':
    main()
