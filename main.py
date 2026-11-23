import math
import random
import pygame

# NOVA — Interactive Universe
# Controls: move mouse to attract stars, click to create a burst, SPACE to pause, ESC to quit.

pygame.init()
WIDTH, HEIGHT = 1100, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NOVA — Interactive Universe")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("consolas", 16)
BIG = pygame.font.SysFont("consolas", 38, bold=True)
SMALL = pygame.font.SysFont("consolas", 12)

BG = (5, 8, 19)
WHITE = (230, 238, 255)
CYAN = (70, 225, 255)
VIOLET = (150, 100, 255)
PINK = (255, 90, 190)

def lerp(a, b, t):
    return a + (b-a)*t

class Star:
    def __init__(self):
        self.x = random.randrange(WIDTH)
        self.y = random.randrange(HEIGHT)
        self.base_x, self.base_y = self.x, self.y
        self.radius = random.choice([1, 1, 1, 2, 2, 3])
        self.speed = random.uniform(.15, .9)
        self.phase = random.random()*math.tau
        self.color = random.choice([(140,180,255), (180,150,255), (110,230,255), (255,220,245)])
        self.vx, self.vy = 0, 0

    def update(self, t, mouse):
        self.phase += .025
        mx, my = mouse
        dx, dy = mx-self.x, my-self.y
        dist = math.hypot(dx, dy)
        if dist < 150 and dist > 0:
            force = (1-dist/150)*.045
            self.vx += dx*force*.018
            self.vy += dy*force*.018
        self.vx += (self.base_x-self.x)*.002
        self.vy += (self.base_y-self.y)*.002
        self.vx *= .985
        self.vy *= .985
        self.x += self.vx
        self.y += self.vy + math.sin(self.phase)*self.speed*.15

    def draw(self, surf):
        twinkle = .65 + .35*math.sin(self.phase*2)
        c = tuple(max(0, min(255, int(v*twinkle))) for v in self.color)
        pygame.draw.circle(surf, c, (int(self.x), int(self.y)), self.radius)
        if self.radius >= 3:
            pygame.draw.line(surf, c, (self.x-4,self.y), (self.x+4,self.y), 1)
            pygame.draw.line(surf, c, (self.x,self.y-4), (self.x,self.y+4), 1)

class Particle:
    def __init__(self, x, y, color=None):
        angle = random.random()*math.tau
        speed = random.uniform(1, 5.5)
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(angle)*speed, math.sin(angle)*speed
        self.life = random.randint(35, 85)
        self.maxlife = self.life
        self.color = color or random.choice([CYAN, VIOLET, PINK, WHITE])
        self.r = random.randint(1, 3)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= .985
        self.vy *= .985
        self.life -= 1

    def draw(self, surf):
        alpha = max(0, self.life/self.maxlife)
        col = tuple(int(c*alpha) for c in self.color)
        pygame.draw.circle(surf, col, (int(self.x), int(self.y)), max(1, int(self.r*alpha)))

stars = [Star() for _ in range(320)]
particles = []
paused = False
t = 0
mouse = (WIDTH//2, HEIGHT//2)

# Soft, layered nebulae painted once
nebula = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for _ in range(26):
    x, y = random.randrange(WIDTH), random.randrange(HEIGHT)
    radius = random.randint(60, 220)
    color = random.choice([(60,25,130,12), (10,80,130,12), (120,25,90,10)])
    pygame.draw.circle(nebula, color, (x,y), radius)
nebula = pygame.transform.smoothscale(nebula, (WIDTH, HEIGHT))

def burst(x, y, count=90):
    for _ in range(count):
        particles.append(Particle(x, y))

def draw_glow(surf, pos, radius, color):
    glow = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
    for r in range(radius, 0, -5):
        alpha = int(3 + 18*(r/radius))
        pygame.draw.circle(glow, (*color, alpha), (radius, radius), r)
    surf.blit(glow, (pos[0]-radius, pos[1]-radius), special_flags=pygame.BLEND_RGBA_ADD)

running = True
while running:
    clock.tick(60)
    t += 1
    mouse = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            burst(*event.pos, count=100)

    screen.fill(BG)
    screen.blit(nebula, (0,0))

    # Subtle drifting haze glow
    draw_glow(screen, (WIDTH*.28 + math.sin(t*.006)*70, HEIGHT*.42), 170, VIOLET)
    draw_glow(screen, (WIDTH*.72 + math.cos(t*.005)*60, HEIGHT*.60), 140, CYAN)

    if not paused:
        for star in stars:
            star.update(t, mouse)
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

    # Constellation-like links around cursor
    nearby = [s for s in stars if math.hypot(s.x-mouse[0], s.y-mouse[1]) < 105]
    for i, s in enumerate(nearby):
        for other in nearby[i+1:i+4]:
            if math.hypot(s.x-other.x, s.y-other.y) < 75:
                pygame.draw.line(screen, (40, 90, 150), (s.x,s.y), (other.x,other.y), 1)

    for star in stars:
        star.draw(screen)
    for p in particles:
        p.draw(screen)

    # Cursor halo
    draw_glow(screen, mouse, 28, CYAN)
    pygame.draw.circle(screen, (140,235,255), mouse, 4, 1)

    # HUD
    pygame.draw.line(screen, (35,55,90), (28,28), (WIDTH-28,28), 1)
    screen.blit(BIG, (42, 42),)
    title_surface = BIG.render("NOVA", True, WHITE)
    screen.blit(title_surface, (42,42))
    screen.blit(FONT.render("INTERACTIVE UNIVERSE", True, CYAN), (47,91))
    screen.blit(SMALL.render("MOVE  /  GRAVITY", True, (125,155,190)), (42,130))
    screen.blit(SMALL.render("CLICK  /  STARBURST", True, (125,155,190)), (42,150))
    screen.blit(SMALL.render("SPACE  /  PAUSE", True, (125,155,190)), (42,170))
    screen.blit(SMALL.render("ESC  /  EXIT", True, (125,155,190)), (42,190))

    # Bottom status panel
    pygame.draw.line(screen, (35,55,90), (28,HEIGHT-40), (WIDTH-28,HEIGHT-40), 1)
    status = "SYSTEM ONLINE" if not paused else "SYSTEM PAUSED"
    screen.blit(FONT.render(status, True, CYAN if not paused else PINK), (42, HEIGHT-29))
    screen.blit(SMALL.render(f"STARS: {len(stars):03}   PARTICLES: {len(particles):04}   FPS: {int(clock.get_fps()):02}", True, (125,155,190)), (WIDTH-390, HEIGHT-27))

    pygame.display.flip()

pygame.quit()
