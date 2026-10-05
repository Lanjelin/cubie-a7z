#!/usr/bin/env python3
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4


def main():
    print('stage: create EPD', flush=True)
    epd = epd2in13_V4.EPD()
    print('stage: init_fast', flush=True)
    epd.init_fast()
    print('stage: clear-white', flush=True)
    epd.Clear(0xFF)

    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, epd.height - 1, epd.width - 1), outline=0, fill=255)
    draw.text((10, 10), 'FAST INIT', font=font, fill=0)
    draw.text((10, 40), 'FAST INIT', font=font, fill=0)
    draw.text((10, 70), 'FAST INIT', font=font, fill=0)

    print('stage: display_fast', flush=True)
    epd.display_fast(epd.getbuffer(image))
    print('stage: sleep', flush=True)
    epd.sleep()
    print('stage: done', flush=True)


if __name__ == '__main__':
    main()
