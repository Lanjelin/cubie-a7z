# Examples

## Waveshare 2.13-inch BW V4 on Cubie A7Z

`hello_world_v4_fast.py` imports the bundled `waveshare_epd` driver and Cubie
backend. It performs fast initialization, clears to white, draws a text image,
uses fast refresh, and puts the panel to sleep.

```sh
EPD_PLATFORM=cubie python3 examples/hello_world_v4_fast.py
```

Run from the parent `waveshare-2in13-v4` directory with its dependencies
installed and no other process using the display.

The backend uses RST on header 11 (`gpiochip0` offset 33), DC on header 22
(`gpiochip1` offset 5), and active-high BUSY on header 18 (`gpiochip0` offset
313). SPI is `/dev/spidev1.0`, mode 0, 500 kHz; header 24 / PD10 is native SPI
chip select, not a userspace GPIO.

The confirmed setup requires the `cubie-header-io-power` overlay to keep DC1SW1
enabled for the PD/PJ banks. Do not load the old manual-CS overlay. See the
parent README for setup details.

The obsolete GPIO/manual-CS and SPI-mode sweep experiments have been removed.
Printed completion is not proof of a visible panel update; inspect the display.
