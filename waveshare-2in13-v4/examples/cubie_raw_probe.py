#!/usr/bin/env python3
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


def main():
    use_manual_cs = True
    if len(__import__('sys').argv) > 1 and __import__('sys').argv[1].lower() == 'hardware':
        use_manual_cs = False

    chip0 = gpiod.Chip('/dev/gpiochip0')
    chip1 = gpiod.Chip('/dev/gpiochip1')

    config0 = {
        BUSY_PIN: gpiod.LineSettings(
            direction=Direction.INPUT,
            edge_detection=Edge.FALLING,
            active_low=True,
            bias=Bias.DISABLED,
        ),
    }
    if use_manual_cs:
        config0[CS_PIN] = gpiod.LineSettings(
            direction=Direction.OUTPUT,
            output_value=Value.ACTIVE,
            bias=Bias.DISABLED,
        )
    lines0 = chip0.request_lines(
        consumer='waveshare_raw_probe',
        config=config0,
    )
    lines1 = chip1.request_lines(
        consumer='waveshare_raw_probe',
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
    spi.mode = 0b00
    spi.max_speed_hz = 4000000

    def busy():
        return lines0.get_value(BUSY_PIN).value

    def cmd(byte):
        lines1.set_value(DC_PIN, Value.INACTIVE)
        if use_manual_cs:
            lines0.set_value(CS_PIN, Value.INACTIVE)
        write_spi(spi, [byte])
        if use_manual_cs:
            lines0.set_value(CS_PIN, Value.ACTIVE)

    def data(byte):
        lines1.set_value(DC_PIN, Value.ACTIVE)
        if use_manual_cs:
            lines0.set_value(CS_PIN, Value.INACTIVE)
        write_spi(spi, [byte])
        if use_manual_cs:
            lines0.set_value(CS_PIN, Value.ACTIVE)

    print(f'mode: {"manual_cs" if use_manual_cs else "hardware_cs"}', flush=True)
    print(f'busy initial: {busy()}', flush=True)
    print('pulse reset', flush=True)
    lines1.set_value(RST_PIN, Value.ACTIVE)
    time.sleep(0.02)
    lines1.set_value(RST_PIN, Value.INACTIVE)
    time.sleep(0.005)
    lines1.set_value(RST_PIN, Value.ACTIVE)
    time.sleep(0.02)
    print(f'busy after reset: {busy()}', flush=True)

    print('send SWRESET', flush=True)
    cmd(0x12)
    for i in range(20):
        print(f'busy[{i}]: {busy()}', flush=True)
        time.sleep(0.1)

    print('send minimal init bytes', flush=True)
    cmd(0x01)
    data(0xF9)
    data(0x00)
    data(0x00)
    cmd(0x11)
    data(0x03)
    print(f'busy after init bytes: {busy()}', flush=True)

    spi.close()
    if use_manual_cs:
        lines0.release()
    lines1.release()


if __name__ == '__main__':
    main()
