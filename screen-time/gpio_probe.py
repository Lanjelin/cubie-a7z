#!/usr/bin/env python3
import argparse
import os
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('EPD_PLATFORM', 'cubie')

from waveshare_epd import epdconfig



parser = argparse.ArgumentParser(description='Cubie A7Z GPIO probe')
parser.add_argument('--repeat', type=int, default=3, help='Number of pulse cycles')
parser.add_argument('--delay', type=float, default=0.5, help='Delay between pulses in seconds')
args = parser.parse_args()

print(f'using bundled Cubie backend: DC={epdconfig.DC_PIN} '
      f'RST={epdconfig.RST_PIN} BUSY={epdconfig.BUSY_PIN}; native SPI1 CS')

try:
    if epdconfig.module_init() != 0:
        raise SystemExit('GPIO initialization failed')

    print('initial: BUSY=', epdconfig.digital_read(epdconfig.BUSY_PIN), sep='')

    for i in range(args.repeat):
        print(f'cycle {i + 1}: pulse RST low/high')
        epdconfig.digital_write(epdconfig.RST_PIN, 0)
        time.sleep(0.1)
        epdconfig.digital_write(epdconfig.RST_PIN, 1)
        time.sleep(args.delay)
        print('after RST pulse: BUSY=', epdconfig.digital_read(epdconfig.BUSY_PIN), sep='')

        print(f'cycle {i + 1}: toggle DC low/high')
        epdconfig.digital_write(epdconfig.DC_PIN, 0)
        time.sleep(0.1)
        epdconfig.digital_write(epdconfig.DC_PIN, 1)
        time.sleep(args.delay)
        print('after DC pulse: BUSY=', epdconfig.digital_read(epdconfig.BUSY_PIN), sep='')
finally:
    epdconfig.module_exit()
