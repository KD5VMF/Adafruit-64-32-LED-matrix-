import time
import random
import board
import displayio
import framebufferio
import rgbmatrix

class Particle:
    def __init__(self, x, y, dx, dy, palette_index):
        self.x = x        # X position (float for smooth movement)
        self.y = y        # Y position
        self.dx = dx      # X velocity
        self.dy = dy      # Y velocity
        self.palette_index = palette_index  # The color index in the palette

class CosmicWanderers:
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
        
        # Create a display group and attach a TileGrid.
        self.group = displayio.Group()
        self.display.root_group = self.group
        
        # Create the bitmap and a palette.
        self.bitmap = displayio.Bitmap(self.WIDTH, self.HEIGHT, self.BITMAP_COLORS)
        self.palette = displayio.Palette(self.BITMAP_COLORS)
        self.palette[0] = 0x000000  # Black background.
        
        # Define a set of bright colors.
        self.BRIGHT_COLORS = [
            0xFF0000,  # Red
            0xFFFF00,  # Yellow
            0x00FF00,  # Green
            0x00FFFF,  # Cyan
            0xFF00FF,  # Magenta
            0xFFA500,  # Orange
            0xFFFFFF,  # White
        ]
        
        # Create a swarm of particles.
        self.NUM_PARTICLES = 15
        self.particles = []
        for i in range(self.NUM_PARTICLES):
            x = random.uniform(0, self.WIDTH)
            y = random.uniform(0, self.HEIGHT)
            dx = random.uniform(-1.5, 1.5)
            dy = random.uniform(-1.5, 1.5)
            palette_index = i + 1  # Reserve index 0 for the background.
            # Assign each particle a random bright color.
            self.palette[palette_index] = random.choice(self.BRIGHT_COLORS)
            self.particles.append(Particle(x, y, dx, dy, palette_index))
        
        # Attach the bitmap to the display group.
        self.tile_grid = displayio.TileGrid(self.bitmap, pixel_shader=self.palette)
        self.group.append(self.tile_grid)
    
    def clear_screen(self):
        """Fill the entire bitmap with the background color (black)."""
        for x in range(self.WIDTH):
            for y in range(self.HEIGHT):
                self.bitmap[x, y] = 0

    def update_particles(self):
        """Update each particle's position and velocity, adding a slight random drift and bouncing off the edges."""
        for p in self.particles:
            # Add a small random acceleration to create a drifting effect.
            p.dx += random.uniform(-0.05, 0.05)
            p.dy += random.uniform(-0.05, 0.05)
            # Clamp the speed to a maximum value.
            max_speed = 2.0
            p.dx = max(-max_speed, min(p.dx, max_speed))
            p.dy = max(-max_speed, min(p.dy, max_speed))
            
            # Update position.
            p.x += p.dx
            p.y += p.dy
            
            # Bounce off the left/right edges.
            if p.x < 0:
                p.x = 0
                p.dx = abs(p.dx)
            elif p.x >= self.WIDTH:
                p.x = self.WIDTH - 1
                p.dx = -abs(p.dx)
            # Bounce off the top/bottom edges.
            if p.y < 0:
                p.y = 0
                p.dy = abs(p.dy)
            elif p.y >= self.HEIGHT:
                p.y = self.HEIGHT - 1
                p.dy = -abs(p.dy)

    def draw_particles(self):
        """Draw each particle onto the bitmap."""
        for p in self.particles:
            self.bitmap[int(p.x), int(p.y)] = p.palette_index

    def update_display(self):
        """Refresh the display to show the current frame."""
        self.display.refresh(minimum_frames_per_second=60)

    def run(self):
        """Main animation loop."""
        while True:
            self.clear_screen()
            self.update_particles()
            self.draw_particles()
            self.update_display()
            time.sleep(0.02)  # About 50 FPS

if __name__ == "__main__":
    animation = CosmicWanderers()
    animation.run()
