import time
import math
import board
import displayio
import framebufferio
import rgbmatrix

class SolarSystemSimulator:
    def __init__(self):
        # Release any resources currently in use.
        displayio.release_displays()
        
        # Display configuration.
        self.WIDTH = 64
        self.HEIGHT = 32
        self.BITMAP_COLORS = 256
        
        # Initialize the RGB matrix display.
        self.matrix = rgbmatrix.RGBMatrix(
            width=self.WIDTH,
            height=self.HEIGHT,
            bit_depth=6,
            rgb_pins=[
                board.MTX_R1, board.MTX_G1, board.MTX_B1,
                board.MTX_R2, board.MTX_G2, board.MTX_B2
            ],
            addr_pins=[
                board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD
            ],
            clock_pin=board.MTX_CLK,
            latch_pin=board.MTX_LAT,
            output_enable_pin=board.MTX_OE,
            tile=1,
            serpentine=True,
            doublebuffer=True,
        )
        self.display = framebufferio.FramebufferDisplay(self.matrix, auto_refresh=False)
        
        # Create a bitmap and palette.
        self.bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, self.BITMAP_COLORS)
        self.palette = displayio.Palette(self.BITMAP_COLORS)
        self.palette[0] = 0x000000  # Background: Black
        self.palette[1] = 0xFFFF00  # Sun: Yellow
        self.palette[2] = 0xFF0000  # Planet 1: Red
        self.palette[3] = 0x00FF00  # Planet 2: Green
        self.palette[4] = 0x0000FF  # Planet 3: Blue
        self.palette[5] = 0xFF00FF  # Planet 4: Magenta

        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.display.root_group = self.group
        
        # Define the sun at the center.
        self.sun_x = self.WIDTH // 2
        self.sun_y = self.HEIGHT // 2
        
        # Define a list of planets.
        # Each planet is a dictionary with:
        #  - orbit_radius: distance from sun (in pixels)
        #  - angle: current angular position (radians)
        #  - speed: angular speed per frame (radians)
        #  - color: palette index for this planet.
        self.planets = [
            {"orbit_radius": 6,  "angle": 0.0, "speed": 0.08, "color": 2},
            {"orbit_radius": 10, "angle": 1.0, "speed": 0.05, "color": 3},
            {"orbit_radius": 14, "angle": 2.0, "speed": 0.03, "color": 4},
            {"orbit_radius": 18, "angle": 3.0, "speed": 0.02, "color": 5},
        ]
        
    def clear_bitmap(self):
        """Clear the entire bitmap to the background color."""
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                self.bitmap[x, y] = 0

    def update(self):
        """Update planet positions and redraw the solar system."""
        self.clear_bitmap()
        
        # Draw the sun.
        if 0 <= self.sun_x < self.WIDTH and 0 <= self.sun_y < self.HEIGHT:
            self.bitmap[self.sun_x, self.sun_y] = 1
        
        # Update and draw each planet.
        for planet in self.planets:
            # Update the angle.
            planet["angle"] += planet["speed"]
            
            # Calculate the planet's x, y position.
            x = self.sun_x + planet["orbit_radius"] * math.cos(planet["angle"])
            y = self.sun_y + planet["orbit_radius"] * math.sin(planet["angle"])
            ix, iy = int(x), int(y)
            
            # Draw the planet (as a single pixel).
            if 0 <= ix < self.WIDTH and 0 <= iy < self.HEIGHT:
                self.bitmap[ix, iy] = planet["color"]
    
    def run(self):
        """Main loop: update the solar system and refresh the display."""
        while True:
            self.update()
            self.display.refresh(minimum_frames_per_second=60)
            time.sleep(0.02)  # Roughly 50 FPS

if __name__ == "__main__":
    sim = SolarSystemSimulator()
    sim.run()
