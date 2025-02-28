import time
import math
import board
import displayio
import framebufferio
import rgbmatrix

class RotatingCube:
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

        # Create a display group and attach a TileGrid.
        self.group = displayio.Group()
        self.display.root_group = self.group

        # Create the bitmap and palette.
        self.bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, self.BITMAP_COLORS)
        self.palette = displayio.Palette(self.BITMAP_COLORS)
        self.palette[0] = 0x000000  # Black background.
        self.palette[1] = 0xFFFFFF  # White for cube lines.

        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        self.group.append(self.tile_grid)

        # Define the cube vertices (cube centered at origin, side length 2).
        self.cube_vertices = [
            (-1, -1, -1),
            (-1, -1,  1),
            (-1,  1, -1),
            (-1,  1,  1),
            ( 1, -1, -1),
            ( 1, -1,  1),
            ( 1,  1, -1),
            ( 1,  1,  1)
        ]

        # Define edges by pairs of vertex indices.
        self.cube_edges = [
            (0, 1), (0, 2), (0, 4),
            (1, 3), (1, 5),
            (2, 3), (2, 6),
            (3, 7),
            (4, 5), (4, 6),
            (5, 7),
            (6, 7)
        ]

        # Rotation angles (in radians) for the x, y, and z axes.
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0

        # Projection parameters.
        self.scale = 20    # Scaling factor for projection.
        self.distance = 4  # Distance to shift the cube along z-axis.

    def rotate_point(self, x, y, z, ax, ay, az):
        """Rotate a 3D point around the x, y, and z axes."""
        # Rotate around the X-axis.
        cos_x = math.cos(ax)
        sin_x = math.sin(ax)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

        # Rotate around the Y-axis.
        cos_y = math.cos(ay)
        sin_y = math.sin(ay)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

        # Rotate around the Z-axis.
        cos_z = math.cos(az)
        sin_z = math.sin(az)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z

        return x, y, z

    def project(self, x, y, z):
        """Project a 3D point onto 2D using a simple perspective projection."""
        z += self.distance  # Shift z to ensure it remains positive.
        if z == 0:
            z = 0.001  # Prevent division by zero.
        factor = self.scale / z
        x_proj = x * factor + self.WIDTH / 2
        y_proj = -y * factor + self.HEIGHT / 2
        return int(x_proj), int(y_proj)

    def draw_line(self, x0, y0, x1, y1, color):
        """Draw a line using Bresenham's algorithm."""
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
        """Clear the screen, update cube rotation, and draw the cube."""
        # Clear the screen.
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                self.bitmap[x, y] = 0

        # Rotate and project each cube vertex.
        projected = []
        for vertex in self.cube_vertices:
            x, y, z = vertex
            rx, ry, rz = self.rotate_point(x, y, z, self.angle_x, self.angle_y, self.angle_z)
            proj = self.project(rx, ry, rz)
            projected.append(proj)

        # Draw the cube edges.
        for start, end in self.cube_edges:
            x0, y0 = projected[start]
            x1, y1 = projected[end]
            self.draw_line(x0, y0, x1, y1, 1)

        # Update rotation angles for continuous rotation.
        self.angle_x += 0.03
        self.angle_y += 0.04
        self.angle_z += 0.02

    def run(self):
        """Main loop to run the animation."""
        while True:
            self.update()
            self.display.refresh(minimum_frames_per_second=60)
            time.sleep(0.02)  # Roughly 50 FPS

if __name__ == "__main__":
    cube = RotatingCube()
    cube.run()
