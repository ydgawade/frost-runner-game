#!/usr/bin/env python3
"""
Frost Runner - Princess Aria
A gentle running & jumping game for young children (age ~6).
Original artwork drawn in code. No copyrighted assets.
Controls: SPACE / UP / MOUSE CLICK = Jump | ESC = Pause | ENTER = Start/Retry
"""
import sys, random, math

try:
    import pygame
except ImportError:
    print("Pygame is not installed. Run:  python -m pip install pygame")
    sys.exit(1)

pygame.init()
try:
    pygame.mixer.pre_init(22050, -16, 2, 512)
    pygame.mixer.init()
    HAS_SOUND = True
except Exception:
    HAS_SOUND = False

W, H = 900, 500
GROUND = H - 90
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Frost Runner - Princess Aria")
clock = pygame.time.Clock()

SKY_TOP = (150, 205, 255); SKY_BOT = (224, 244, 255)
SNOW = (245, 250, 255); ICE = (170, 220, 255); DARKICE = (120, 180, 235)
DRESS = (110, 180, 240); DRESS2 = (150, 210, 255)
SKIN = (255, 224, 200); HAIR = (238, 232, 170)
GOLD = (255, 210, 70); WHITE = (255, 255, 255); TEXTCOL = (40, 70, 120)

def pick_font(size, bold=True):
    for name in ("comicsansms", "segoeui", "arial"):
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            continue
    return pygame.font.Font(None, size)

font_big = pick_font(58); font_mid = pick_font(34); font_sm = pick_font(24)

def make_tone(freq, ms, vol=0.3):
    if not HAS_SOUND:
        return None
    import array
    rate = 22050
    n = int(rate * ms / 1000)
    buf = array.array("h")
    amp = int(32767 * vol)
    for i in range(n):
        env = 1 - i / n
        s = int(amp * env * math.sin(2 * math.pi * freq * i / rate))
        buf.append(s); buf.append(s)
    try:
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except Exception:
        return None

snd_jump = make_tone(520, 160, 0.25)
snd_star = make_tone(880, 180, 0.30)
snd_gold = make_tone(1200, 300, 0.35)
snd_oops = make_tone(200, 300, 0.30)
snd_win = make_tone(1000, 450, 0.35)

def play(s):
    if s:
        try:
            s.play()
        except Exception:
            pass

def draw_sky():
    for y in range(0, H, 2):
        t = y / H
        c = [int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * t) for i in range(3)]
        pygame.draw.rect(screen, c, (0, y, W, 2))

hills = [(random.randint(0, W), random.randint(60, 120)) for _ in range(4)]
clouds = [[random.randint(0, W), random.randint(40, 180), random.uniform(0.4, 0.9)] for _ in range(5)]
flakes = [[random.randint(0, W), random.randint(0, H), random.uniform(1, 3)] for _ in range(70)]

def draw_cloud(x, y, s):
    for dx, dy, r in [(0, 0, 22), (24, 4, 26), (48, 0, 20), (20, -12, 20)]:
        pygame.draw.circle(screen, WHITE, (int(x + dx * s), int(y + dy * s)), int(r * s))

def draw_background(scroll):
    draw_sky()
    for hx, hh in hills:
        x = (hx - scroll * 0.2) % (W + 400) - 200
        pygame.draw.ellipse(screen, (200, 230, 255), (x - 150, GROUND + 20 - hh, 300, hh * 2))
    for c in clouds:
        c[0] -= 0.3
        if c[0] < -140:
            c[0] = W + 90
            c[1] = random.randint(40, 180)
        draw_cloud(c[0], c[1], c[2])
    pygame.draw.rect(screen, SNOW, (0, GROUND, W, H - GROUND))
    pygame.draw.rect(screen, ICE, (0, GROUND, W, 8))
    for f in flakes:
        f[1] += f[2]; f[0] -= 0.4
        if f[1] > H:
            f[1] = 0
            f[0] = random.randint(0, W)
        pygame.draw.circle(screen, WHITE, (int(f[0]), int(f[1])), int(f[2]))

class Player:
    def __init__(self):
        self.x = 140; self.y = GROUND; self.vy = 0; self.on_ground = True; self.run = 0

    def jump(self):
        if self.on_ground:
            self.vy = -15.5
            self.on_ground = False
            play(snd_jump)

    def update(self):
        self.vy += 0.75
        self.y += self.vy
        if self.y >= GROUND:
            self.y = GROUND; self.vy = 0; self.on_ground = True
        self.run = (self.run + 0.25) % 4

    def rect(self):
        return pygame.Rect(self.x - 18, self.y - 70, 38, 70)

    def draw(self):
        x, y = self.x, self.y
        leg = math.sin(self.run * math.pi) * (6 if self.on_ground else 0)
        pygame.draw.polygon(screen, DRESS, [(x - 22, y), (x + 22, y), (x + 12, y - 40), (x - 12, y - 40)])
        pygame.draw.polygon(screen, DRESS2, [(x - 10, y - 2), (x + 10, y - 2), (x + 6, y - 38), (x - 6, y - 38)])
        pygame.draw.line(screen, SKIN, (x - 6, y), (x - 6 - leg, y), 6)
        pygame.draw.rect(screen, DRESS, (x - 10, y - 58, 20, 20), border_radius=6)
        pygame.draw.line(screen, SKIN, (x - 8, y - 52), (x - 16, y - 40 + leg), 5)
        pygame.draw.line(screen, SKIN, (x + 8, y - 52), (x + 16, y - 40 - leg), 5)
        pygame.draw.circle(screen, SKIN, (x, y - 66), 13)
        pygame.draw.line(screen, HAIR, (x + 8, y - 70), (x + 22, y - 40), 7)
        pygame.draw.circle(screen, HAIR, (x, y - 74), 9)
        pygame.draw.polygon(screen, GOLD, [(x - 9, y - 77), (x - 4, y - 85), (x, y - 78), (x + 4, y - 85), (x + 9, y - 77)])
        pygame.draw.circle(screen, TEXTCOL, (x - 4, y - 66), 2)
        pygame.draw.circle(screen, TEXTCOL, (x + 4, y - 66), 2)

class Star:
    def __init__(self, x, gold=False):
        self.x = x; self.gold = gold
        self.y = GROUND - random.choice([40, 90, 140])
        self.t = random.random() * 6

    def update(self, sp):
        self.x -= sp; self.t += 0.1

    def draw(self):
        yy = self.y + math.sin(self.t) * 4
        c = GOLD if self.gold else (255, 255, 180)
        pts = []
        for i in range(10):
            r = (14 if self.gold else 11) if i % 2 == 0 else 5
            a = math.pi / 2 + i * math.pi / 5
            pts.append((self.x + math.cos(a) * r, yy - math.sin(a) * r))
        pygame.draw.polygon(screen, c, pts)
        pygame.draw.circle(screen, TEXTCOL, (int(self.x - 3), int(yy - 1)), 1)
        pygame.draw.circle(screen, TEXTCOL, (int(self.x + 3), int(yy - 1)), 1)

    def rect(self):
        return pygame.Rect(self.x - 12, self.y - 12, 24, 24)

class Obstacle:
    def __init__(self, x):
        self.x = x
        self.kind = random.choice(["log", "block", "snowman"])
        self.h = random.choice([34, 44])

    def update(self, sp):
        self.x -= sp

    def draw(self):
        x = self.x; b = GROUND
        if self.kind == "log":
            pygame.draw.rect(screen, (150, 110, 70), (x - 18, b - self.h, 36, self.h), border_radius=8)
        elif self.kind == "block":
            pygame.draw.rect(screen, DARKICE, (x - 16, b - self.h, 32, self.h), border_radius=6)
            pygame.draw.rect(screen, ICE, (x - 16, b - self.h, 32, 10), border_radius=6)
        else:
            pygame.draw.circle(screen, WHITE, (int(x), b - 12), 12)
            pygame.draw.circle(screen, WHITE, (int(x), b - 30), 9)
            pygame.draw.circle(screen, TEXTCOL, (int(x - 3), b - 32), 1)
            pygame.draw.circle(screen, TEXTCOL, (int(x + 3), b - 32), 1)

    def rect(self):
        return pygame.Rect(self.x - 15, GROUND - self.h, 30, self.h)

particles = []

def burst(x, y, c):
    for _ in range(12):
        particles.append([x, y, random.uniform(-3, 3), random.uniform(-4, 0), c, 20])

def draw_particles():
    for p in particles[:]:
        p[0] += p[2]; p[1] += p[3]; p[3] += 0.2; p[5] -= 1
        pygame.draw.circle(screen, p[4], (int(p[0]), int(p[1])), 3)
        if p[5] <= 0:
            particles.remove(p)

STATE_MENU, STATE_PLAY, STATE_OVER, STATE_PAUSE = 0, 1, 2, 3

def new_game():
    return {"player": Player(), "stars": [], "obs": [], "score": 0, "hearts": 3,
            "speed": 5.0, "scroll": 0.0, "spawn": 0, "praise": "", "praise_t": 0, "milestone": 0}

praises = ["Great jump!", "Amazing!", "Wow!", "Super!", "You did it!", "Yay!"]

def draw_hearts(n):
    for i in range(3):
        x = W - 40 - i * 34; y = 30
        c = (255, 90, 120) if i < n else (205, 205, 215)
        pygame.draw.circle(screen, c, (x - 5, y), 7)
        pygame.draw.circle(screen, c, (x + 5, y), 7)
        pygame.draw.polygon(screen, c, [(x - 11, y + 2), (x + 11, y + 2), (x, y + 14)])

def text_center(txt, fnt, y, col=TEXTCOL):
    s = fnt.render(txt, True, col)
    screen.blit(s, (W // 2 - s.get_width() // 2, y))

best = 0
state = STATE_MENU
g = new_game()
running = True

while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                if state == STATE_PLAY:
                    state = STATE_PAUSE
                elif state == STATE_PAUSE:
                    state = STATE_PLAY
            elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if state in (STATE_MENU, STATE_OVER):
                    g = new_game(); state = STATE_PLAY
            elif e.key in (pygame.K_SPACE, pygame.K_UP):
                if state == STATE_PLAY:
                    g["player"].jump()
                elif state in (STATE_MENU, STATE_OVER):
                    g = new_game(); state = STATE_PLAY
            elif e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if state == STATE_PLAY:
                g["player"].jump()
            elif state in (STATE_MENU, STATE_OVER):
                g = new_game(); state = STATE_PLAY

    if state == STATE_PLAY:
        g["scroll"] += g["speed"]
        g["speed"] = min(9.0, g["speed"] + 0.0008)
        g["player"].update()
        g["spawn"] -= 1
        if g["spawn"] <= 0:
            g["spawn"] = random.randint(55, 90)
            if random.random() < 0.55:
                g["obs"].append(Obstacle(W + 40))
            gold = random.random() < 0.15
            for k in range(random.randint(1, 3)):
                g["stars"].append(Star(W + 140 + k * 34, gold and k == 0))
        for o in g["obs"][:]:
            o.update(g["speed"])
            if o.x < -40:
                g["obs"].remove(o)
            elif o.rect().colliderect(g["player"].rect()):
                g["obs"].remove(o)
                g["hearts"] -= 1
                play(snd_oops)
                burst(g["player"].x, g["player"].y - 40, (255, 150, 150))
                if g["hearts"] <= 0:
                    state = STATE_OVER
                    best = max(best, g["score"])
        for s in g["stars"][:]:
            s.update(g["speed"])
            if s.x < -30:
                g["stars"].remove(s)
            elif s.rect().colliderect(g["player"].rect()):
                g["stars"].remove(s)
                if s.gold:
                    g["score"] += 50; play(snd_gold); burst(s.x, s.y, GOLD)
                else:
                    g["score"] += 10; play(snd_star); burst(s.x, s.y, (255, 255, 180))
                g["praise"] = random.choice(praises)
                g["praise_t"] = 45
        if g["praise_t"] > 0:
            g["praise_t"] -= 1
        if g["score"] >= g["milestone"] + 500:
            g["milestone"] += 500
            play(snd_win)
            burst(W // 2, 120, GOLD)

    draw_background(g["scroll"])
    for s in g["stars"]:
        s.draw()
    for o in g["obs"]:
        o.draw()
    g["player"].draw()
    draw_particles()
    screen.blit(font_mid.render("Score: %d" % g["score"], True, TEXTCOL), (20, 18))
    draw_hearts(g["hearts"])
    if g["praise_t"] > 0:
        text_center(g["praise"], font_mid, H // 2 - 150, (255, 120, 170))

    if state == STATE_MENU:
        ov = pygame.Surface((W, H), pygame.SRCALPHA); ov.fill((255, 255, 255, 120)); screen.blit(ov, (0, 0))
        text_center("Frost Runner", font_big, 110, (70, 120, 200))
        text_center("Princess Aria", font_mid, 190, (140, 90, 180))
        text_center("Press ENTER or CLICK to Play", font_mid, 290)
        text_center("SPACE / UP / CLICK = Jump    ESC = Pause", font_sm, 350)
    elif state == STATE_PAUSE:
        ov = pygame.Surface((W, H), pygame.SRCALPHA); ov.fill((255, 255, 255, 150)); screen.blit(ov, (0, 0))
        text_center("Paused", font_big, 150)
        text_center("Press ESC to keep playing", font_sm, 250)
    elif state == STATE_OVER:
        ov = pygame.Surface((W, H), pygame.SRCALPHA); ov.fill((255, 255, 255, 150)); screen.blit(ov, (0, 0))
        text_center("Great Playing!", font_big, 110, (255, 120, 170))
        text_center("You scored %d" % g["score"], font_mid, 205)
        text_center("Best today: %d" % best, font_sm, 255, (120, 150, 190))
        text_center("Press ENTER to play again", font_sm, 310)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
