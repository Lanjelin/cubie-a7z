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
    chip0 = gpiod.Chip('/dev/gpiochip0')
    chip1 = gpiod.Chip('/dev/gpiochip1')

    lines0 = chip0.request_lines(
        consumer='waveshare_busy_monitor',
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
        consumer='waveshare_busy_monitor',
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

    def dump_edges(label):
        if not lines0.wait_edge_events(0.05):
            print(label, 'edge_count=', 0, flush=True)
            return
        events = lines0.read_edge_events()
        print(label, 'edge_count=', len(events), flush=True)
        for event in events:
            event_type = getattr(event, 'type', None)
            if event_type is None:
                event_type = getattr(event, 'Type', None)
            seqno = getattr(event, 'line_seqno', None)
            if seqno is None:
                seqno = getattr(event, 'line_seqno', None)
            timestamp = getattr(event, 'timestamp_ns', None)
            print('  edge', event_type, seqno, timestamp, flush=True)

    def cmd(byte):
        lines1.set_value(DC_PIN, Value.INACTIVE)
        lines0.set_value(CS_PIN, Value.INACTIVE)
        write_spi(spi, [byte])
        lines0.set_value(CS_PIN, Value.ACTIVE)

    def data(byte):
        lines1.set_value(DC_PIN, Value.ACTIVE)
        lines0.set_value(CS_PIN, Value.INACTIVE)
        write_spi(spi, [byte])
        lines0.set_value(CS_PIN, Value.ACTIVE)

    print('initial busy:', busy(), flush=True)
    dump_edges('initial')

    print('reset pulse', flush=True)
    lines1.set_value(RST_PIN, Value.INACTIVE)
    time.sleep(0.02)
    lines1.set_value(RST_PIN, Value.ACTIVE)
    time.sleep(0.05)
    print('busy after reset:', busy(), flush=True)
    dump_edges('after reset')

    print('raw swreset', flush=True)
    cmd(0x12)
    for i in range(20):
        time.sleep(0.1)
        print(f'busy[{i}]: {busy()}', flush=True)
        dump_edges(f'poll {i}')

    print('raw init bytes', flush=True)
    cmd(0x01)
    data(0xF9)
    data(0x00)
    data(0x00)
    cmd(0x11)
    data(0x03)
    time.sleep(0.2)
    print('busy after init bytes:', busy(), flush=True)
    dump_edges('after init bytes')

    spi.close()
    lines0.release()
    lines1.release()


if __name__ == '__main__':
    main()
