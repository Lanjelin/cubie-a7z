#!/usr/bin/env python3
import sys
import time

import gpiod
import spidev
from gpiod.line import Bias, Direction, Edge, Value


BUSY_PIN = 33
CS_PIN = 106
RST_PIN = 6
DC_PIN = 7


def write_spi(spi, values):
    for offset in range(0, len(values), 4096):
        spi.xfer(list(values[offset:offset + 4096]))


def run_case(mode, speed_hz):
    chip0 = gpiod.Chip('/dev/gpiochip0')
    chip1 = gpiod.Chip('/dev/gpiochip1')
    lines0 = chip0.request_lines(
        consumer='waveshare_spi_sweep',
        config={
            BUSY_PIN: gpiod.LineSettings(
                direction=Direction.INPUT,
                edge_detection=Edge.FALLING,
                active_low=True,
                bias=Bias.DISABLED,
            ),
            CS_PIN: gpiod.LineSettings(
                direction=Direction.OUTPUT,
                output_value=Value.ACTIVE,
                bias=Bias.DISABLED,
            ),
        },
    )
    lines1 = chip1.request_lines(
        consumer='waveshare_spi_sweep',
        config={
            RST_PIN: gpiod.LineSettings(
                direction=Direction.OUTPUT,
                output_value=Value.ACTIVE,
                bias=Bias.DISABLED,
            ),
            DC_PIN: gpiod.LineSettings(
                direction=Direction.OUTPUT,
                output_value=Value.INACTIVE,
                bias=Bias.DISABLED,
            ),
        },
    )

    spi = spidev.SpiDev()
    spi.open(1, 0)
    spi.mode = mode
    spi.max_speed_hz = speed_hz

    def busy():
        return lines0.get_value(BUSY_PIN).value

    def cmd(byte):
        lines1.set_value(DC_PIN, Value.INACTIVE)
        lines0.set_value(CS_PIN, Value.INACTIVE)
        write_spi(spi, [byte])
        lines0.set_value(CS_PIN, Value.ACTIVE)

    print(f'case mode={mode} speed={speed_hz}', flush=True)
    lines1.set_value(RST_PIN, Value.ACTIVE)
    time.sleep(0.02)
    lines1.set_value(RST_PIN, Value.INACTIVE)
    time.sleep(0.005)
    lines1.set_value(RST_PIN, Value.ACTIVE)
    time.sleep(0.02)
    print(f'busy after reset: {busy()}', flush=True)
    try:
        cmd(0x12)
        for i in range(10):
            print(f'busy[{i}]: {busy()}', flush=True)
            time.sleep(0.1)
    except OSError as exc:
        print(f'error: {exc}', flush=True)

    spi.close()
    lines0.release()
    lines1.release()


def main():
    cases = []
    if len(sys.argv) > 1:
        mode = int(sys.argv[1])
        speed = int(sys.argv[2]) if len(sys.argv) > 2 else 4000000
        cases.append((mode, speed))
    else:
        speeds = [100000, 250000, 500000, 1000000, 2000000, 4000000]
        for mode in range(4):
            for speed in speeds:
                cases.append((mode, speed))
    for mode, speed in cases:
        try:
            run_case(mode, speed)
        except OSError as exc:
            print(f'case mode={mode} speed={speed} failed: {exc}', flush=True)


if __name__ == '__main__':
    main()
