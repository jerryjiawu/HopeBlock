import pygame
import time
import random
import math
pygame.init()

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

class Particle:
    def __init__(self, parent, position, vx, vy, size, lifespan, color=Colours.WHITE, gravity=0.1):
        self.position = position
        self.parent = parent
        self.screen = parent.screen
        self.velocity = [vx, vy]
        self.color = color
        self.size = size
        self.lifespan = lifespan
        self.age = 0
        self.gravity = gravity

        self.particles = []
        if self.color != Colours.WHITE:
            for particle in particles:
                particle_copy = particle.copy()
                particle_copy.fill(pygame.Color(self.color), special_flags=pygame.BLEND_MULT)
                self.particles.append(particle_copy)
    
    def update(self, delta_time):
        self.velocity[1] += self.gravity * delta_time
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time

        damping_factor = 0.95 ** (delta_time * 60)
        self.velocity[0] *= damping_factor
        self.velocity[1] *= damping_factor

        self.age += delta_time
        self.draw()

    def draw(self):
        if self.age >= self.lifespan:
            self.parent.particles.remove(self)
            return

        particle_images = self.particles if self.particles else particles
        self.screen.blit(particle_images[int(self.age / self.lifespan * (len(particle_images) - 1))], (int(self.position[0]), int(self.position[1])))

class Firework:
    def __init__(self, screen, x, y, color, size, duration=1):
        self.screen = screen
        self.position = [x, y]
        self.color = color
        self.size = size
        self.duration = duration
        self.particles = []
        self.age = 0
        self.has_exploded = False

    def update_particles(self, delta_time):
        for particle in self.particles:
            particle.update(delta_time)

    def update(self, delta_time):
        self.position[1] -= delta_time * 300
        if self.age < self.duration:
            self.screen.blit(rocket, (int(self.position[0]), int(self.position[1])))
            if random.randint(0, 100) == 0:
                self.particles.append(Particle(self, [self.position[0], self.position[1] + 16], random.uniform(-40, 40), random.uniform(-10, 0), self.size, 0.5, Colours.WHITE))
            self.age += delta_time
        else:
            if not self.has_exploded:
                self.has_exploded = True
                for i in range(100):
                    angle = random.uniform(0, 2 * 3.14159)
                    speed = random.uniform(100, 250)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    self.particles.append(Particle(self, [self.position[0], self.position[1]], vx, vy, self.size, random.uniform(0.5, 1.5), self.color, gravity=1))

        self.update_particles(delta_time)
            
        

if __name__ == "__main__":
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Firework Simulator")

    running = True
    t = time.time()
    firework = Firework(screen, 400, 500, Colours.RED, 5)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        firework.update(time.time() - t)
        t = time.time()

        pygame.display.flip()

    pygame.quit()