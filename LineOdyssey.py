import time
import math
import board
import displayio
import framebufferio
import rgbmatrix

class LineOdyssey:
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
        self.palette[0] = 0x000000  # Black background.
        self.palette[1] = 0xFFFFFF  # White for the lines.

        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        self.group = displayio.Group()
        self.group.append(self.tile_grid)
        self.display.root_group = self.group

        # Create a grid of 3D points.
        # We'll use an 8x8 grid.
        self.rows = 8
        self.cols = 8
        # Define the grid dimensions in 3D space.
        self.grid_width = 8   # x spans from -grid_width/2 to grid_width/2
        self.grid_height = 8  # y spans similarly
        self.x_spacing = self.grid_width / (self.cols - 1)
        self.y_spacing = self.grid_height / (self.rows - 1)
        # The grid initially lies on the z=0 plane.
        
        # Projection parameters.
        self.scale = 30       # Scaling factor for projection.
        self.distance = 10    # Translate z to avoid division by zero.

        # Initial rotation angles.
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0

    def clear_bitmap(self):
        """Clear the entire bitmap to the background color."""
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                self.bitmap[x, y] = 0

    def rotate_point(self, x, y, z, ax, ay, az):
        """Rotate a 3D point (x, y, z) around the x, y, and z axes."""
        # Rotate around X-axis.
        cosx = math.cos(ax)
        sinx = math.sin(ax)
        y, z = y * cosx - z * sinx, y * sinx + z * cosx

        # Rotate around Y-axis.
        cosy = math.cos(ay)
        siny = math.sin(ay)
        x, z = x * cosy + z * siny, -x * siny + z * cosy

        # Rotate around Z-axis.
        cosz = math.cos(az)
        sinz = math.sin(az)
        x, y = x * cosz - y * sinz, x * sinz + y * cosz

        return x, y, z

    def project(self, x, y, z):
        """Project a 3D point onto 2D using perspective projection."""
        z = z + self.distance  # Ensure z is always positive.
        if z == 0:
            z = 0.001  # Avoid division by zero.
        factor = self.scale / z
        x_proj = x * factor + self.WIDTH / 2
        y_proj = -y * factor + self.HEIGHT / 2
        return int(x_proj), int(y_proj)

    def draw_line(self, x0, y0, x1, y1, color=1):
        """Draw a line on the bitmap using Bresenham's algorithm."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            if 0 <= x0 < self.WIDTH and 0 <= y0 < self.HEIGHT:
                self.bitmap[x0, y0] = color
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def update(self):
        """Update the grid's rotation and redraw the wireframe grid."""
        self.clear_bitmap()
        
        # Create a 2D array to hold the projected points.
        points = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Compute each grid point's position.
        for i in range(self.rows):
            for j in range(self.cols):
                # Map grid coordinates: center the grid around (0,0).
                x = -self.grid_width / 2 + j * self.x_spacing
                y = -self.grid_height / 2 + i * self.y_spacing
                z = 0  # The grid lies on z=0.
                # Apply rotation.
                rx, ry, rz = self.rotate_point(x, y, z, self.angle_x, self.angle_y, self.angle_z)
                # Project the 3D point onto 2D.
                px, py = self.project(rx, ry, rz)
                points[i][j] = (px, py)
        
        # Draw horizontal lines.
        for i in range(self.rows):
            for j in range(self.cols - 1):
                x0, y0 = points[i][j]
                x1, y1 = points[i][j + 1]
                self.draw_line(x0, y0, x1, y1)
        
        # Draw vertical lines.
        for j in range(self.cols):
            for i in range(self.rows - 1):
                x0, y0 = points[i][j]
                x1, y1 = points[i + 1][j]
                self.draw_line(x0, y0, x1, y1)
        
        # Increment rotation angles for continuous animation.
        self.angle_x += 0.03
        self.angle_y += 0.02
        self.angle_z += 0.01

    def run(self):
        """Main loop: update the grid and refresh the display."""
        while True:
            self.update()
            self.display.refresh(minimum_frames_per_second=60)
            time.sleep(0.02)  # Roughly 50 FPS

if __name__ == "__main__":
    odyssey = LineOdyssey()
    odyssey.run()
