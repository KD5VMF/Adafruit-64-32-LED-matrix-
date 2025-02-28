import time
import random
import board
import displayio
import framebufferio
import rgbmatrix

class Fireplace:
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
                board.MTX_R2, board.MTX_G2, board.MTX_B2,
            ],
            addr_pins=[
                board.MTX_ADDRA, board.MTX_ADDRB, board.MTX_ADDRC, board.MTX_ADDRD,
            ],
            clock_pin=board.MTX_CLK,
            latch_pin=board.MTX_LAT,
            output_enable_pin=board.MTX_OE,
            tile=1,
            serpentine=True,
            doublebuffer=True,
        )
        self.display = framebufferio.FramebufferDisplay(self.matrix, auto_refresh=False)
        
        # Create a bitmap and a palette.
        self.bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, self.BITMAP_COLORS)
        self.palette = displayio.Palette(self.BITMAP_COLORS)
        # We'll use a fire intensity range of 0 (off) to max_intensity (brightest)
        self.max_intensity = 36
        
        # Build a fire palette:
        # Map intensity values to colors ranging from black -> deep red -> red -> orange -> yellow -> white.
        for i in range(self.max_intensity + 1):
            f = i / self.max_intensity
            if f <= 0.33:
                # Ramp red from 0 to 255.
                r = int(255 * (f / 0.33))
                g = 0
                b = 0
            elif f <= 0.66:
                # Red is max; ramp green from 0 to 255.
                r = 255
                g = int(255 * ((f - 0.33) / 0.33))
                b = 0
            else:
                # Red and green max; ramp blue from 0 to 255.
                r = 255
                g = 255
                b = int(255 * ((f - 0.66) / 0.34))
            self.palette[i] = (r << 16) | (g << 8) | b

        # Ensure the background (intensity 0) is black.
        self.palette[0] = 0x000000

        # Create a TileGrid for the bitmap and add it to a group.
        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.display.root_group = self.group

        # Create the fire buffer (a 2D list) to hold intensity values.
        self.fire_buffer = [[0 for _ in range(self.HEIGHT)] for _ in range(self.WIDTH)]

    def update_fire(self):
        # Randomize the bottom row to act as the flame source.
        for x in range(self.WIDTH):
            # With some randomness, light up the bottom row at full intensity
            self.fire_buffer[x][self.HEIGHT - 1] = self.max_intensity if random.random() > 0.3 else int(self.max_intensity / 2)
        
        # Propagate the fire upward.
        for y in range(self.HEIGHT - 2, -1, -1):
            for x in range(self.WIDTH):
                # Use three pixels from the row below (with wrap-around for horizontal boundaries).
                left = self.fire_buffer[(x - 1) % self.WIDTH][y + 1]
                down = self.fire_buffer[x][y + 1]
                right = self.fire_buffer[(x + 1) % self.WIDTH][y + 1]
                avg = (left + down + right) // 3
                decay = random.randint(0, 2)  # Random decay factor.
                new_intensity = avg - decay
                if new_intensity < 0:
                    new_intensity = 0
                self.fire_buffer[x][y] = new_intensity

    def update_bitmap(self):
        # Update the display bitmap with the current fire buffer intensities.
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                self.bitmap[x, y] = self.fire_buffer[x][y]

    def run(self):
        while True:
            self.update_fire()
            self.update_bitmap()
            self.display.refresh(minimum_frames_per_second=60)
            time.sleep(0.05)  # About 20 FPS

if __name__ == "__main__":
    fire = Fireplace()
    fire.run()
