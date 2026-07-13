#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V3


def main():
    print('stage: create EPD', flush=True)
    epd = epd2in13_V3.EPD()
    print('stage: init', flush=True)
    epd.init()
    print('stage: clear', flush=True)
    epd.Clear()

    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), 'Hello World', font=font, fill=0)
    draw.text((10, 40), 'Hello World', font=font, fill=0)
    draw.text((10, 70), 'Hello World', font=font, fill=0)

    print('stage: display', flush=True)
    epd.display(epd.getbuffer(image))
    print('stage: sleep', flush=True)
    epd.sleep()
    print('stage: done', flush=True)


if __name__ == '__main__':
    main()
