#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from PIL import Image, ImageDraw, ImageFont
from waveshare_epd import epd2in13_V4, epd2in13_V3, epd2in13_V2


def make_image(epd, text):
    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), text, font=font, fill=0)
    draw.text((10, 50), text, font=font, fill=0)
    draw.text((10, 90), text, font=font, fill=0)
    return image


def run_v4():
    epd = epd2in13_V4.EPD()
    epd.init_fast()
    epd.Clear(0xFF)
    epd.display_fast(epd.getbuffer(make_image(epd, 'V4')))
    epd.sleep()


def run_v3():
    epd = epd2in13_V3.EPD()
    epd.init()
    epd.Clear(0xFF)
    epd.display(epd.getbuffer(make_image(epd, 'V3')))
    epd.sleep()


def run_v2():
    epd = epd2in13_V2.EPD()
    epd.init(epd.FULL_UPDATE)
    epd.Clear(0xFF)
    epd.display(epd.getbuffer(make_image(epd, 'V2')))
    epd.sleep()


def main():
    family = sys.argv[1].lower() if len(sys.argv) > 1 else 'v4'
    print(f'family: {family}', flush=True)
    t0 = time.monotonic()
    if family == 'v4':
        run_v4()
    elif family == 'v3':
        run_v3()
    elif family == 'v2':
        run_v2()
    else:
        raise SystemExit('usage: cubie_family_probe.py [v4|v3|v2]')
    print(f'done elapsed={time.monotonic() - t0:.2f}s', flush=True)


if __name__ == '__main__':
    main()
