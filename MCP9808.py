# Temperature Display with Degree Circle on MatrixPortal S3
# This program reads the temperature from the MCP9808 sensor and displays
# it in Fahrenheit on a 64x32 RGB matrix. A small degree circle (°) is
# drawn next to the last digit. The display is rotated 180 degrees, and
# the program updates the temperature every second.

import time
import displayio
import board
import busio
from adafruit_matrixportal.matrix import Matrix
from adafruit_display_text import label
import terminalio
import adafruit_mcp9808

# About:
# - The MatrixPortal S3 is used to display the temperature in Fahrenheit.
# - A degree symbol is manually drawn as a small circle next to the temperature.
# - The program updates the temperature from the MCP9808 sensor every second.

# Initialize the matrix and display
matrix = Matrix(width=64, height=32, bit_depth=4)
display = matrix.display

# Set rotation to 180 degrees for proper orientation
display.rotation = 180

# Create a bitmap for the screen (64x32 resolution, 2 color options)
bitmap = displayio.Bitmap(64, 32, 2)

# Create a palette with two colors: black (background) and white (text/circle)
palette = displayio.Palette(2)
palette[0] = 0x000000  # Black background
palette[1] = 0xFFFFFF  # White text and degree circle

# Create TileGrid to display the bitmap and add it to the display group
tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
group = displayio.Group()
group.append(tile_grid)
display.root_group = group  # Set the group as the root display group

# Initialize I2C and MCP9808 temperature sensor
i2c = busio.I2C(board.SCL, board.SDA)
mcp9808 = adafruit_mcp9808.MCP9808(i2c)

# Label to display the temperature in Fahrenheit
temp_label = label.Label(terminalio.FONT, text="00.0", color=0xFFFFFF, scale=2, x=0, y=16)

# Add the temperature label to the display group
group.append(temp_label)

def draw_degree_circle(x, y):
    """Draw a small degree circle (°) next to the temperature."""
    radius = 2  # Set the radius of the degree circle
    for x_offset in range(-radius, radius + 1):
        for y_offset in range(-radius, radius + 1):
            # Ensure the pixel falls within the circle radius
            if x_offset ** 2 + y_offset ** 2 <= radius ** 2:
                # Draw the circle only if the coordinates are within display bounds
                if 0 <= x + x_offset < 64 and 0 <= y + y_offset < 32:
                    bitmap[x + x_offset, y + y_offset] = 1  # Draw white circle

def update_temperature():
    """Read the temperature from the MCP9808 sensor and display it in Fahrenheit."""
    # Read temperature in Celsius and convert to Fahrenheit
    temp_celsius = mcp9808.temperature
    temp_fahrenheit = temp_celsius * 9 / 5 + 32
    # Format the temperature string without the degree symbol
    temp_text = f"{temp_fahrenheit:.1f}"
    # Update the label with the new temperature text
    temp_label.text = temp_text

    # Center the temperature text horizontally
    temp_label.x = (64 - len(temp_text) * 12) // 2

    # Draw the degree circle next to the last digit of the temperature
    circle_x = temp_label.x + len(temp_text) * 12 + 4  # Place the circle slightly to the right of the last digit
    circle_y = temp_label.y - 8  # Position the circle slightly above the temperature text
    draw_degree_circle(circle_x, circle_y)

# Main loop: Update the temperature and refresh the display every second
while True:
    update_temperature()  # Read and display the updated temperature
    display.refresh()     # Refresh the display to show the updated content
    time.sleep(1)         # Wait for 1 second before the next update
