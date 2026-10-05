#!/usr/bin/env python3
import argparse
import os
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from waveshare_epd import epd2in13_V4, epdconfig


class DisplayTest(epd2in13_V4.EPD):
    def ReadBusy(self):
        start = time.monotonic()
        while epdconfig.digital_read(self.busy_pin) == 1:
            if time.monotonic() - start >= 10:
                raise TimeoutError('BUSY remained high for 10 seconds')
            epdconfig.delay_ms(10)


def make_image(epd, label):
    img = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, img.width - 1, img.height - 1), outline=0)
    draw.text((8, 8), 'EPD TEST', font=font, fill=0)
    draw.text((8, 24), 'SPI1 V4', font=font, fill=0)
    draw.text((8, 40), label, font=font, fill=0)
    return img


parser = argparse.ArgumentParser(description='Cubie A7Z Waveshare 2.13 V4 display test')
parser.add_argument('--black-white', action='store_true', help='Run a black flash and then a white flash before the image')
args = parser.parse_args()

print(f'using bundled Cubie backend: DC={epdconfig.DC_PIN} '
      f'RST={epdconfig.RST_PIN} BUSY={epdconfig.BUSY_PIN}; native SPI1 CS')

epd = DisplayTest()
try:
    if epd.init() != 0:
        raise SystemExit('EPD init failed')

    if args.black_white:
        epd.Clear(0x00)
        epd.Clear(0xFF)

    img = make_image(epd, 'CUBIE NATIVE CS')
    epd.display(epd.getbuffer(img))
    epd.sleep()
except BaseException:
    epdconfig.module_exit()
    raise
print('display sequence completed; confirm the image on the panel')
