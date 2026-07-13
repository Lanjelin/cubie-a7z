#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4


def main():
    epd = epd2in13_V4.EPD()
    epd.init()
    epd.Clear(0xFF)

    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), 'Hello World', font=font, fill=0)
    draw.text((10, 40), 'Hello World', font=font, fill=0)
    draw.text((10, 70), 'Hello World', font=font, fill=0)

    epd.display(epd.getbuffer(image))
    epd.sleep()


if __name__ == '__main__':
    main()
