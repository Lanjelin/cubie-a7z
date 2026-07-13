#!/usr/bin/env python3
import time

import gpiod
from gpiod.line import Bias, Direction, Edge, Value


BUSY_PIN = 33
CS_PIN = 106
RST_PIN = 6
DC_PIN = 7


def main():
    chip0 = gpiod.Chip('/dev/gpiochip0')
    chip1 = gpiod.Chip('/dev/gpiochip1')

    lines0 = chip0.request_lines(
        consumer='waveshare_gpio_sanity',
        config={
            BUSY_PIN: gpiod.LineSettings(
                direction=Direction.INPUT,
                edge_detection=Edge.BOTH,
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
        consumer='waveshare_gpio_sanity',
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

    def read_all():
        return {
            'busy': lines0.get_value(BUSY_PIN).value,
            'cs': lines0.get_value(CS_PIN).value,
            'rst': lines1.get_value(RST_PIN).value,
            'dc': lines1.get_value(DC_PIN).value,
        }

    print('initial', read_all(), flush=True)

    print('toggle cs', flush=True)
    lines0.set_value(CS_PIN, Value.INACTIVE)
    time.sleep(0.1)
    print('after cs low', read_all(), flush=True)
    lines0.set_value(CS_PIN, Value.ACTIVE)
    time.sleep(0.1)
    print('after cs high', read_all(), flush=True)

    print('toggle dc', flush=True)
    lines1.set_value(DC_PIN, Value.ACTIVE)
    time.sleep(0.1)
    print('after dc high', read_all(), flush=True)
    lines1.set_value(DC_PIN, Value.INACTIVE)
    time.sleep(0.1)
    print('after dc low', read_all(), flush=True)

    print('toggle reset', flush=True)
    lines1.set_value(RST_PIN, Value.INACTIVE)
    time.sleep(0.1)
    print('after rst low', read_all(), flush=True)
    lines1.set_value(RST_PIN, Value.ACTIVE)
    time.sleep(0.1)
    print('after rst high', read_all(), flush=True)

    lines0.release()
    lines1.release()


if __name__ == '__main__':
    main()
