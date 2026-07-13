#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from inky.phat import InkyPHAT_SSD1608

inky = InkyPHAT_SSD1608("black")
inky.cs_pin = "CUBIE_HW_CS"
inky.dc_pin = "PIN_15"
inky.reset_pin = "PIN_13"
inky.busy_pin = "PIN_11"

image = Image.new("P", (inky.width, inky.height), 1)
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

# The panel on this setup renders with inverted-looking palette values.
# This combination produces black background with white text on the screen.
draw.text((10, 10), "Hello World", font=font, fill=0)
draw.text((10, 50), "Hello World", font=font, fill=0)
draw.text((10, 90), "Hello World", font=font, fill=0)

inky.set_image(image)
inky.show()
