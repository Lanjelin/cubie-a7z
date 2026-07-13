# Examples

Add board-specific Waveshare test scripts here once the Python driver is installed.

The first useful test should be a minimal black/white text render that exercises:

- SPI1 transport
- reset line
- busy line
- partial refresh if supported by the chosen driver

## Example

- `hello_world.py`: minimal text render using the standard Waveshare Python driver style (`from waveshare_epd import epd2in13_V4`).
