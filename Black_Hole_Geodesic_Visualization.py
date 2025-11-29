import pygame
import sys
import math


pygame.init()

WIDTH = 800
HEIGHT = 600
TITLE = "2D Black Hole Geodesic Visualization"
FPS = 60

# Black Hole Center
BX = 4 * WIDTH // 6 
BY = HEIGHT // 2  

# Black Hole Parameters
G = 30
MASS = 20.9
c = 4
RS = (2 * G * MASS) / (c**2)  # Schwarzschild Radius

# Integration step size
DLAMBDA = 0.3 


# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (75, 75, 75)
RED = (155, 0, 0)
UNIVERSAL_TRAIL_COLOR = (255, 255, 255) # Unified trail color (was BLUE_TRAIL)


# Create the display surface
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
CLOCK = pygame.time.Clock()


# --- 3. Photon Class ---
class Photon:
    def __init__(self, x_init, y_init, color):
        self.initial_x = x_init
        self.initial_y = y_init
        self.color = color 
        self.trail = []
        self.active = True
        self.has_hit_horizon = False

        self.r = math.hypot(BX - x_init, BY - y_init)
        self.phi = math.atan2(y_init - BY, x_init - BX) 
        initial_angle_of_motion = 0 
        self.dr = c * math.cos(initial_angle_of_motion - self.phi)
        self.dphi = (c * math.sin(initial_angle_of_motion - self.phi)) / self.r
        self.x = x_init
        self.y = y_init

    def update(self):

        if not self.active:
            return

        # 1. Geodesic Integration (Euler's Method)
        if self.r > RS:
            
            # d^2 r / d(lambda)^2 (Radial Acceleration)
            # The simplified Schwarzschild Geodesic Equation for a photon
            d2r = self.r * self.dphi**2 * (1 - RS / self.r) - (RS * c**2) / (2 * self.r**2)
            
            # d^2 phi / d(lambda)^2 (Angular Acceleration)
            d2phi = -2 * self.dr * self.dphi / self.r
            
            # Update the FIRST derivatives
            self.dr += d2r * DLAMBDA
            self.dphi += d2phi * DLAMBDA
            
            # Update the position
            self.r += self.dr * DLAMBDA
            self.phi += self.dphi * DLAMBDA

            # Convert back to SCREEN coordinates
            x_rel = self.r * math.cos(self.phi)
            y_rel = self.r * math.sin(self.phi)
            
            # Absolute Screen Coordinates
            self.x = int(BX + x_rel)
            self.y = int(BY + y_rel)

            # Update Trail
            self.trail.append((self.x, self.y))

            if not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT):
                self.active = False
        
        else:
            # Ray crossed the Event Horizon (RS)
            self.has_hit_horizon = True
            self.active = False
            self.trail.append((self.x, self.y))

    def draw(self, surface):
        
        # 1. Draw Trail (as connecting lines)
        if len(self.trail) > 1:
            for i in range(len(self.trail) - 1):
                # Now using the single assigned color for all trail segments
                thickness = 1 
                pygame.draw.line(surface, self.color, self.trail[i], self.trail[i+1], thickness)

        # 2. Draw Photon Head
        if self.active:
            pygame.draw.circle(surface, WHITE, (self.x, self.y), 3)


# --- 4. Initialization of Photon Array ---

photons = []
num_rays = 30
start_x = 0
spacing = HEIGHT / (num_rays + 1) 

# Launch rays with slightly different vertical starting positions
for i in range(num_rays):
    y_start = (i + 1) * spacing
    
    color = UNIVERSAL_TRAIL_COLOR
    
    photons.append(Photon(start_x, y_start, color))


# --- 5. Game Loop ---
running = True
while running:

    CLOCK.tick(FPS)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    
    # Update all active photons
    for photon in photons:
        photon.update()

    # Fill the screen with a background color
    SCREEN.fill(BLACK) 

    # Draw all photon trails and heads
    for photon in photons:
        photon.draw(SCREEN)

    # Draw Black Hole (Event Horizon)
    pygame.draw.circle(SCREEN, GRAY, (BX, BY), int(RS))
    
    # Draw the Schwarzschild radius line for reference
    pygame.draw.circle(SCREEN, RED, (BX, BY), int(RS), 1)
    
    # Update the full display surface to the screen
    pygame.display.flip()
    
# --- 6. Game Exit ---
pygame.quit()
sys.exit()