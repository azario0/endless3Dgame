import pygame
import math
import numba
import numpy as np

# --- Constants ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Player settings
PLAYER_SPEED = 0.05
PLAYER_ROT_SPEED = 0.03

# Raycasting settings
FOV = math.pi / 3  # 60 degrees
NUM_RAYS = SCREEN_WIDTH // 3  # Reduced for better performance
MAX_DEPTH = 25.0
RAY_ANGLE_STEP = FOV / NUM_RAYS

# Maze settings
MAZE_SEED = 42
CELL_SIZE = 1.0

# Colors
COLOR_CEILING = (20, 20, 40)
COLOR_FLOOR = (40, 25, 15)
COLOR_WALL_DARK = (80, 40, 20)
COLOR_WALL_LIGHT = (120, 60, 30)
COLOR_MINIMAP_WALL = (200, 200, 200)
COLOR_MINIMAP_PLAYER = (255, 100, 100)
COLOR_MINIMAP_BG = (0, 0, 0)

# Performance optimization with Numba JIT compilation
@numba.jit(nopython=True, cache=True)
def fast_hash(x, y, seed):
    """Fast hash function for maze generation"""
    x, y = int(x), int(y)
    h = seed + x * 374761393 + y * 668265263
    h = (h ^ (h >> 13)) * 1274126177
    h = h ^ (h >> 16)
    return h & 0x7fffffff

@numba.jit(nopython=True, cache=True)
def is_wall(x, y, seed):
    """Optimized wall detection using deterministic hash"""
    x, y = int(x), int(y)
    
    # Create a more interesting maze pattern
    # Rooms are at odd coordinates, walls can be at even coordinates
    if (x % 2 != 0) and (y % 2 != 0):
        return False  # Always open room centers
    
    if (x % 2 == 0) and (y % 2 == 0):
        # Pillars - sometimes open for more variety
        return fast_hash(x//2, y//2, seed) % 100 < 80
    
    # Potential walls between rooms
    room_x = x // 2
    room_y = y // 2
    hash_val = fast_hash(room_x, room_y, seed) % 100
    
    # Create passages based on hash
    if x % 2 == 0:  # Vertical wall
        return hash_val < 40
    else:  # Horizontal wall
        return hash_val < 35

@numba.jit(nopython=True, cache=True)
def cast_ray(start_x, start_y, angle, seed, max_depth):
    """Optimized raycasting with DDA-like algorithm"""
    dx = math.cos(angle)
    dy = math.sin(angle)
    
    # Step size for ray marching
    step = 0.02
    distance = 0.0
    
    x = start_x
    y = start_y
    
    while distance < max_depth:
        x += dx * step
        y += dy * step
        distance += step
        
        if is_wall(x, y, seed):
            return distance, x, y
    
    return max_depth, x, y

class OptimizedRenderer:
    def __init__(self, screen):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.wall_buffer = np.zeros((NUM_RAYS, 4), dtype=np.float32)  # x, top, height, distance
        
    def render_3d(self, player_x, player_y, player_angle):
        # Clear screen with ceiling
        self.screen.fill(COLOR_CEILING)
        
        # Draw floor
        floor_rect = pygame.Rect(0, self.height // 2, self.width, self.height // 2)
        pygame.draw.rect(self.screen, COLOR_FLOOR, floor_rect)
        
        # Cast all rays
        start_angle = player_angle - FOV / 2
        slice_width = self.width / NUM_RAYS
        
        for ray_idx in range(NUM_RAYS):
            current_angle = start_angle + ray_idx * RAY_ANGLE_STEP
            
            # Cast ray
            distance, hit_x, hit_y = cast_ray(player_x, player_y, current_angle, MAZE_SEED, MAX_DEPTH)
            
            if distance < MAX_DEPTH:
                # Correct fisheye effect
                distance *= math.cos(player_angle - current_angle)
                
                # Calculate wall height
                wall_height = min(self.height, self.height / (distance + 0.001))
                wall_top = (self.height - wall_height) / 2
                
                # Distance-based shading
                shading = max(0.1, 1.0 - (distance / MAX_DEPTH))
                
                # Determine wall orientation for different shading
                grid_x = int(hit_x)
                grid_y = int(hit_y)
                
                # Check which face we hit
                dx_to_grid = abs(hit_x - grid_x - 0.5)
                dy_to_grid = abs(hit_y - grid_y - 0.5)
                
                if dx_to_grid > dy_to_grid:
                    # Hit vertical face (east/west)
                    base_color = COLOR_WALL_LIGHT
                else:
                    # Hit horizontal face (north/south)  
                    base_color = COLOR_WALL_DARK
                
                # Apply shading
                wall_color = tuple(int(c * shading) for c in base_color)
                
                # Draw wall slice
                x_pos = ray_idx * slice_width
                wall_rect = pygame.Rect(x_pos, wall_top, slice_width + 1, wall_height)
                pygame.draw.rect(self.screen, wall_color, wall_rect)
                
                # Add depth cue with darker edges
                if distance > MAX_DEPTH * 0.7:
                    fog_alpha = int((distance - MAX_DEPTH * 0.7) / (MAX_DEPTH * 0.3) * 100)
                    fog_surface = pygame.Surface((slice_width + 1, wall_height))
                    fog_surface.set_alpha(fog_alpha)
                    fog_surface.fill((0, 0, 0))
                    self.screen.blit(fog_surface, (x_pos, wall_top))

class MiniMap:
    def __init__(self, size=120, scale=6):
        self.size = size
        self.scale = scale
        self.surface = pygame.Surface((size, size))
        self.surface.set_alpha(200)
        
    def render(self, screen, player_x, player_y, player_angle):
        self.surface.fill(COLOR_MINIMAP_BG)
        
        # Draw maze around player
        map_range = self.size // self.scale // 2
        center = self.size // 2
        
        for mx in range(-map_range, map_range):
            for my in range(-map_range, map_range):
                world_x = int(player_x) + mx
                world_y = int(player_y) + my
                
                if is_wall(world_x, world_y, MAZE_SEED):
                    screen_x = center + mx * self.scale
                    screen_y = center + my * self.scale
                    pygame.draw.rect(self.surface, COLOR_MINIMAP_WALL, 
                                   (screen_x, screen_y, self.scale, self.scale))
        
        # Draw player
        pygame.draw.circle(self.surface, COLOR_MINIMAP_PLAYER, (center, center), 4)
        
        # Draw player direction
        end_x = center + math.cos(player_angle) * 8
        end_y = center + math.sin(player_angle) * 8
        pygame.draw.line(self.surface, COLOR_MINIMAP_PLAYER, 
                        (center, center), (end_x, end_y), 2)
        
        screen.blit(self.surface, (10, 10))

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Optimized Endless 3D Maze")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
        # Game objects
        self.renderer = OptimizedRenderer(self.screen)
        self.minimap = MiniMap()
        
        # Player state - start in guaranteed open space
        self.player_x = 1.5
        self.player_y = 1.5  
        self.player_angle = math.pi / 4
        
        # Find a valid starting position
        while is_wall(self.player_x, self.player_y, MAZE_SEED):
            self.player_x += 2.0
            if self.player_x > 20:
                self.player_x = 1.5
                self.player_y += 2.0
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Rotation
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_angle -= PLAYER_ROT_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_angle += PLAYER_ROT_SPEED
        
        # Movement with collision detection
        dx = dy = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dx += math.cos(self.player_angle) * PLAYER_SPEED
            dy += math.sin(self.player_angle) * PLAYER_SPEED
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dx -= math.cos(self.player_angle) * PLAYER_SPEED
            dy -= math.sin(self.player_angle) * PLAYER_SPEED
        
        # Strafe movement
        if keys[pygame.K_q]:
            dx += math.cos(self.player_angle - math.pi/2) * PLAYER_SPEED * 0.7
            dy += math.sin(self.player_angle - math.pi/2) * PLAYER_SPEED * 0.7
        if keys[pygame.K_e]:
            dx += math.cos(self.player_angle + math.pi/2) * PLAYER_SPEED * 0.7
            dy += math.sin(self.player_angle + math.pi/2) * PLAYER_SPEED * 0.7
        
        # Apply movement with collision detection
        if not is_wall(self.player_x + dx, self.player_y, MAZE_SEED):
            self.player_x += dx
        if not is_wall(self.player_x, self.player_y + dy, MAZE_SEED):
            self.player_y += dy
    
    def render_ui(self):
        # FPS counter - calculate actual FPS
        current_time = pygame.time.get_ticks()
        if not hasattr(self, 'last_fps_time'):
            self.last_fps_time = current_time
            self.frame_count = 0
            self.current_fps = 0
        
        self.frame_count += 1
        if current_time - self.last_fps_time >= 1000:  # Update every second
            self.current_fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
        
        fps_text = self.font.render(f'FPS: {self.current_fps}', True, (255, 255, 255))
        self.screen.blit(fps_text, (SCREEN_WIDTH - 80, 10))
        
        # Position
        pos_text = self.font.render(f'X: {self.player_x:.1f} Y: {self.player_y:.1f}', 
                                   True, (255, 255, 255))
        self.screen.blit(pos_text, (SCREEN_WIDTH - 150, 35))
        
        # Controls
        controls = [
            "WASD/Arrows: Move",
            "Q/E: Strafe",
            "ESC: Exit"
        ]
        
        for i, control in enumerate(controls):
            text = self.font.render(control, True, (200, 200, 200))
            self.screen.blit(text, (10, SCREEN_HEIGHT - 80 + i * 20))
    
    def run(self):
        running = True
        target_fps = 60
        frame_time = 1.0 / target_fps
        last_time = pygame.time.get_ticks() / 1000.0
        
        while running:
            current_time = pygame.time.get_ticks() / 1000.0
            delta_time = current_time - last_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Only update if enough time has passed
            if delta_time >= frame_time:
                # Update
                self.handle_input()
                
                # Render
                self.renderer.render_3d(self.player_x, self.player_y, self.player_angle)
                self.minimap.render(self.screen, self.player_x, self.player_y, self.player_angle)
                self.render_ui()
                
                pygame.display.flip()
                last_time = current_time
            
            # Small sleep to prevent CPU spinning
            pygame.time.wait(1)
        
        pygame.quit()

if __name__ == "__main__":
    try:
        import numba
        game = Game()
        game.run()
    except ImportError:
        print("This optimized version requires numba for best performance.")
        print("Install with: pip install numba")
        print("Running without numba optimization...")
        
        # Fallback version without numba
        exec(open(__file__).read().replace("@numba.jit", "# @numba.jit"))