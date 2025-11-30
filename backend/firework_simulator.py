import pygame
import time
import random
import math
pygame.init()

class Type:
    NORMAL = 0
    FIRE_CHARGE = 1
    STAR = 2
    CREEPER = 3
    BURST = 4

class Effects:
    NORMAL = 0
    TRAIL = 1
    TWINKLE = 2
    TRAIL_TWINKLE = 3

class Star:
    def __init__(self, type:Type, effects:Effects, color):
        self.type = type
        self.effects = effects
        self.color = color

class Colours:
    colors = {
        "White": "#F9FFFE",
        "Light gray": "#9D9D97", 
        "Gray": "#474F52",
        "Black": "#1D1D21",
        "Brown": "#835432",
        "Red": "#B02E26",
        "Orange": "#F9801D",
        "Yellow": "#FED83D",
        "Lime": "#80C71F",
        "Green": "#5E7C16",
        "Cyan": "#169C9C",
        "Light blue": "#3AB3DA",
        "Blue": "#3C44AA",
        "Purple": "#8932B8",
        "Magenta": "#C74EBD",
        "Pink": "#F38BAA"
    }
    
    WHITE = "#F9FFFE"
    LIGHT_GRAY = "#9D9D97"
    GRAY = "#474F52"
    BLACK = "#1D1D21"
    BROWN = "#835432"
    RED = "#B02E26"
    ORANGE = "#F9801D"
    YELLOW = "#FED83D"
    LIME = "#80C71F"
    GREEN = "#5E7C16"
    CYAN = "#169C9C"
    LIGHT_BLUE = "#3AB3DA"
    BLUE = "#3C44AA"
    PURPLE = "#8932B8"
    MAGENTA = "#C74EBD"
    PINK = "#F38BAA"

rocket = pygame.image.load("assets/firework/rocket.png")
rocket = pygame.transform.scale(rocket, (10, 20))
particles = [pygame.transform.scale(pygame.image.load(f"assets/firework/{i}.png"), (10, 10)) for i in range(6)]
particles.reverse()

class TrailParticle:
    def __init__(self, position, lifespan, color, particles, size, parent_effects=Effects.NORMAL):
        self.position = [position[0], position[1]]  # Copy position
        self.lifespan = lifespan
        self.age = 0
        self.color = color
        self.particles = particles
        self.size = size
        self.parent_effects = parent_effects
    
    def update(self, delta_time):
        self.age += delta_time
        return self.age < self.lifespan
    
    def draw(self, screen):
        if self.age >= self.lifespan:
            return
        
        # Calculate fade factor (1.0 at birth, 0.0 at death)
        fade_factor = 1.0 - (self.age / self.lifespan)
        
        # Early exit if too faded to see
        if fade_factor < 0.01:
            return
        
        # Calculate which image to use based on effect and fade
        if self.parent_effects == Effects.TRAIL_TWINKLE:
            # For trail+twinkle: randomize image selection for sparkly trail
            image_index = random.randint(0, len(self.particles) - 1)
        else:
            # Normal trail: fade-based image selection
            image_index = int((1.0 - fade_factor) * (len(self.particles) - 1))
            image_index = max(0, min(image_index, len(self.particles) - 1))
        
        # Get the base image
        base_image = self.particles[image_index]
        
        # Only scale if necessary (avoid constant scaling)
        current_size = max(2, int(self.size * fade_factor))
        if current_size != self.size:
            # Cache scaled images to avoid repeated scaling
            if not hasattr(self, '_scaled_cache') or self._last_size != current_size:
                self._scaled_cache = pygame.transform.scale(base_image, (current_size, current_size))
                self._last_size = current_size
            scaled_image = self._scaled_cache
        else:
            scaled_image = base_image
        
        # Apply transparency using blend mode for better performance
        alpha = int(255 * fade_factor * fade_factor)  # Quadratic fade for more dramatic effect
        if alpha < 255:
            # Use a more efficient alpha blending method
            temp_surface = scaled_image.copy()
            temp_surface.set_alpha(alpha)
            scaled_image = temp_surface
        
        # Center the scaled image on the original position
        offset_x = current_size // 2
        offset_y = current_size // 2
        screen.blit(scaled_image, (int(self.position[0] - offset_x), int(self.position[1] - offset_y)))

class Particle:
    def __init__(self, parent, position, vx, vy, size, lifespan, color=Colours.WHITE, gravity=0.1, effects=Effects.NORMAL):
        self.position = position
        self.parent = parent
        self.screen = parent.screen
        self.velocity = [vx, vy]
        self.color = color
        self.size = size
        self.lifespan = lifespan
        self.age = 0
        self.gravity = gravity
        self.effects = effects
        
        # Effect-specific properties
        self.trail_particles = []  # For trail effect - stores independent trail particles
        self.trail_spawn_timer = 0

        self.particles = []
        if self.color != Colours.WHITE:
            for particle in particles:
                particle_copy = particle.copy()
                particle_copy.fill(pygame.Color(self.color), special_flags=pygame.BLEND_MULT)
                self.particles.append(particle_copy)
    
    def update(self, delta_time):
        # Physics update with proper delta time scaling
        self.velocity[1] += self.gravity * delta_time * 60  # Scale gravity for consistent behavior
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time

        # Frame-rate independent damping
        damping_factor = 0.98 ** (delta_time * 60)
        self.velocity[0] *= damping_factor
        self.velocity[1] *= damping_factor

        # Handle trail effect - spawn independent trail particles
        if self.effects == Effects.TRAIL or self.effects == Effects.TRAIL_TWINKLE:
            self.trail_spawn_timer += delta_time
            # Adaptive trail spawn rate based on velocity for better performance
            velocity_magnitude = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
            spawn_interval = max(0.008, min(0.02, 0.01 + velocity_magnitude * 0.00001))
            
            if self.trail_spawn_timer >= spawn_interval:
                trail_lifespan = 0.12  # Slightly shorter for performance
                trail_particle = TrailParticle(self.position.copy(), trail_lifespan, self.color, self.particles if self.particles else particles, self.size, self.effects)
                self.trail_particles.append(trail_particle)
                self.trail_spawn_timer = 0
            
            # Efficiently update and remove expired trail particles
            alive_trails = []
            for tp in self.trail_particles:
                if tp.update(delta_time):
                    alive_trails.append(tp)
            self.trail_particles = alive_trails

        self.age += delta_time

    def is_expired(self):
        return self.age >= self.lifespan
    
    def draw(self):
        particle_images = self.particles if self.particles else particles
        
        # Handle trail effect - draw all independent trail particles first (background)
        if self.effects == Effects.TRAIL or self.effects == Effects.TRAIL_TWINKLE:
            for trail_particle in self.trail_particles:
                trail_particle.draw(self.screen)
        
        # Draw main particle (foreground)
        if self.effects == Effects.TWINKLE or self.effects == Effects.TRAIL_TWINKLE:
            # Twinkle: randomize the displayed image
            image_index = random.randint(0, len(particle_images) - 1)
        else:
            # Normal: age-based image selection with bounds checking
            age_ratio = min(1.0, self.age / self.lifespan)
            image_index = int(age_ratio * (len(particle_images) - 1))
        
        self.screen.blit(particle_images[image_index], (int(self.position[0]), int(self.position[1])))


class Firework:
    def __init__(self, screen, x, y, size, firework_type:Type=Type.NORMAL, effects:Effects=Effects.NORMAL, duration=1, charges=[]):
        self.screen = screen
        self.charges = charges
        self.position = [x, y]
        self.size = size
        self.duration = duration
        self.particles = []
        self.effects = effects
        self.firework_type = firework_type
        self.age = 0
        self.has_exploded = False

    def update_particles(self, delta_time):
        # More efficient particle update and cleanup
        alive_particles = []
        for particle in self.particles:
            particle.update(delta_time)
            if not particle.is_expired():
                alive_particles.append(particle)
        self.particles = alive_particles
    
    def draw_particles(self):
        # Separate draw call for better performance
        for particle in self.particles:
            particle.draw()

    def update(self, delta_time):
        # Frame-rate independent rocket movement
        self.position[1] -= delta_time * 300
        
        if self.age < self.duration:
            self.screen.blit(rocket, (int(self.position[0]), int(self.position[1])))
            # Frame-rate independent particle spawning for rocket trail
            if random.random() < delta_time * 30:  # Adaptive spawn rate based on delta time
                self.particles.append(Particle(self, [self.position[0], self.position[1] + 16], random.uniform(-40, 40), random.uniform(-10, 0), self.size, 0.5, Colours.WHITE))
            self.age += delta_time
        else:
            if not self.has_exploded:
                self.has_exploded = True
                amount = 0
                duration = 1
                for charge in self.charges:
                    if charge.type == Type.NORMAL or charge.type == Type.FIRE_CHARGE or charge.type == Type.BURST:
                        speed_multiplier = 1.0
                        if charge.type == Type.NORMAL:
                            amount = 100
                            duration = 1
                        elif charge.type == Type.FIRE_CHARGE:
                            amount = 200
                            duration = 1.5
                            speed_multiplier = 1.5
                        for i in range(amount):
                            angle = random.uniform(0, 2 * 3.14159)
                            speed = random.uniform(50, 250) * speed_multiplier
                            vx = speed * math.cos(angle)
                            vy = speed * math.sin(angle)
                            self.particles.append(Particle(self, [self.position[0], self.position[1]], vx, vy, self.size, random.uniform(duration - 0.5, duration + 0.5), charge.color, gravity=1, effects=charge.effects))
                    elif charge.type == Type.STAR:
                        # Create a 5-pointed star outline
                        duration = 1
                        star_size = 80  # Size of the star
                        
                        # Generate star outline points
                        star_points = []
                        for i in range(10):  # 5 outer points + 5 inner points = 10 total
                            angle = (i * math.pi / 5) - math.pi / 2  # Start from top
                            if i % 2 == 0:  # Outer points
                                radius = star_size
                            else:  # Inner points
                                radius = star_size * 0.4  # Inner points are closer to center
                            
                            x = radius * math.cos(angle)
                            y = radius * math.sin(angle)
                            star_points.append((x, y))
                        
                        # Create particles along the star outline edges
                        for i in range(len(star_points)):
                            # Get current point and next point (wrap around)
                            current_point = star_points[i]
                            next_point = star_points[(i + 1) % len(star_points)]
                            
                            # Create particles along the line between these two points
                            particles_per_edge = 15
                            for j in range(particles_per_edge):
                                # Interpolate along the line
                                t = j / (particles_per_edge - 1)  # 0 to 1
                                target_x = current_point[0] + t * (next_point[0] - current_point[0])
                                target_y = current_point[1] + t * (next_point[1] - current_point[1])
                                
                                # Add some randomness
                                target_x += random.uniform(-3, 3)
                                target_y += random.uniform(-3, 3)
                                
                                # Calculate velocity to reach target position
                                distance = math.sqrt(target_x**2 + target_y**2)
                                if distance > 0:
                                    speed = distance * 4  # Speed proportional to distance
                                    vx = (target_x / distance) * speed
                                    vy = (target_y / distance) * speed
                                else:
                                    vx = random.uniform(-10, 10)
                                    vy = random.uniform(-10, 10)
                                
                                self.particles.append(Particle(self, [self.position[0], self.position[1]], 
                                                             vx, vy, self.size, 
                                                             random.uniform(duration - 0.15, duration), 
                                                             charge.color, gravity=1, effects=charge.effects))

                    elif charge.type == Type.CREEPER:
                        creeper_outline = [
                            [1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1],
                            [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
                            [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
                            [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],
                            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                            [0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0],
                            [0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0],
                            [0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0],
                            [0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0],
                            [0,0,1,0,0,1,1,1,1,1,1,0,0,1,0,0],
                            [0,0,1,0,0,1,0,0,0,0,1,0,0,1,0,0],
                            [0,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0],
     
                        ]
                        
                        duration = 1
                        creeper_color = charge.color
                        scale_factor = 12

                        
                        # Creeper face pattern - shoot particles toward their final positions
                        for row in range(len(creeper_outline)):
                            for col in range(len(creeper_outline[row])):
                                if creeper_outline[row][col] == 1:
                                    # Calculate where this pixel should end up (relative to center)
                                    target_x = (col - 8) * scale_factor  # Center the pattern
                                    target_y = (row - 8) * scale_factor * 1.1
                                    
                                    # Multiple particles per pixel for visibility
                                    for p in range(3):
                                        # Add small random offset to target position
                                        final_x = target_x + random.uniform(-4, 4)
                                        final_y = target_y + random.uniform(-4, 4)
                                        
                                        # Calculate velocity to reach target position
                                        # Distance from center to target
                                        distance = math.sqrt(final_x**2 + final_y**2)
                                        if distance > 0:
                                            # Normalize direction and set speed
                                            speed = distance * 4  # Speed proportional to distance
                                            vx = (final_x / distance) * speed
                                            vy = (final_y / distance) * speed
                                        else:
                                            vx = random.uniform(-10, 10)
                                            vy = random.uniform(-10, 10)
                                        
                                        self.particles.append(Particle(self, [self.position[0], self.position[1]], 
                                                                     vx, vy, self.size, 
                                                                     random.uniform(duration - 0.15, duration), creeper_color, gravity=1, effects=charge.effects))


                    

        self.update_particles(delta_time)
            
        

if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 800))
    pygame.display.set_caption("Firework Simulator")
    clock = pygame.time.Clock()

    running = True
    firework = Firework(screen, 400, 700, 5, charges=[Star(Type.FIRE_CHARGE, Effects.NORMAL, Colours.WHITE), Star(Type.STAR, Effects.TWINKLE, Colours.RED), CREEPER:=Star(Type.CREEPER, Effects.TRAIL, Colours.GREEN)])
    
    while running:
        # Cap delta time to prevent large jumps during lag
        delta_time = min(clock.tick(60) / 1000.0, 1/30)  # Max 30 FPS minimum, target 60 FPS
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        # Update and draw separately for better performance
        firework.update(delta_time)
        firework.draw_particles()

        pygame.display.flip()

    pygame.quit()