import time
import math
import board
import displayio
import framebufferio
import rgbmatrix

def hsv_to_rgb(h, s, v):
    """Convert HSV (h in [0,1], s in [0,1], v in [0,1]) to RGB tuple (0-255)."""
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i = i % 6
    if i == 0:
        r, g, b = v, t, p
    elif i == 1:
        r, g, b = q, v, p
    elif i == 2:
        r, g, b = p, v, t
    elif i == 3:
        r, g, b = p, q, v
    elif i == 4:
        r, g, b = t, p, v
    elif i == 5:
        r, g, b = v, p, q
    return int(r * 255), int(g * 255), int(b * 255)

class AbstractFractalExplorer:
    def __init__(self):
        # Release any resources currently in use.
        displayio.release_displays()

        # Display configuration.
        self.WIDTH = 64
        self.HEIGHT = 32
        # Use a 16-color palette.
        self.BITMAP_COLORS = 16

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

        # Create a bitmap and palette.
        self.bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, self.BITMAP_COLORS)
        self.palette = displayio.Palette(self.BITMAP_COLORS)
        # Reserve index 0 as black.
        self.palette[0] = 0x000000

        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.display.root_group = self.group

        # Fractal parameters.
        self.max_iter = 10  # Lower iteration count for performance

    def update_palette(self, t):
        """
        Update the dynamic palette so that colors fade and shift over time.
        We'll update palette indices 1 to BITMAP_COLORS-1.
        """
        base_hue = (t * 0.1) % 1.0  # Slowly shifting base hue.
        fade_range = 0.5           # The range of hues to span.
        for i in range(1, self.BITMAP_COLORS):
            # Compute a hue for this palette index.
            # The hue will shift over time.
            hue = (base_hue + ((i - 1) / (self.BITMAP_COLORS - 2)) * fade_range) % 1.0
            # Use full saturation and brightness.
            r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
            self.palette[i] = (r << 16) | (g << 8) | b

    def compute_fractal(self, c, zoom, offset_x, offset_y):
        """
        Compute an abstract fractal pattern.
        Each pixel is mapped to a complex coordinate and iterated with: z = z^2 + c.
        The iteration count (modulo palette size) is used to color the pixel.
        """
        for py in range(self.HEIGHT):
            for px in range(self.WIDTH):
                # Map pixel coordinate to the complex plane.
                # Adjust these values for different views.
                x = (px / self.WIDTH - 0.5) * 3.0 * zoom + offset_x
                y = (py / self.HEIGHT - 0.5) * 2.0 * zoom + offset_y
                z = complex(x, y)
                iter_count = 0
                while iter_count < self.max_iter and abs(z) <= 2.0:
                    z = z * z + c
                    iter_count += 1
                color_index = iter_count % self.BITMAP_COLORS
                self.bitmap[px, py] = color_index

    def run(self):
        start_time = time.monotonic()
        while True:
            t = time.monotonic() - start_time
            # Update the dynamic palette.
            self.update_palette(t)
            # Evolve the parameter c over time.
            c = complex(0.285 + 0.1 * math.sin(t), 0.01 + 0.1 * math.cos(t))
            # Oscillate zoom to create a pulsing effect.
            zoom = 1 + 0.5 * math.sin(t * 0.5)
            # Slowly pan the fractal.
            offset_x = 0.3 * math.sin(t * 0.3)
            offset_y = 0.3 * math.cos(t * 0.3)
            self.compute_fractal(c, zoom, offset_x, offset_y)
            self.display.refresh(minimum_frames_per_second=30)
            time.sleep(0.1)

if __name__ == "__main__":
    explorer = AbstractFractalExplorer()
    explorer.run()
