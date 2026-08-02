#!/usr/bin/env python3
"""
Frost Runner - Princess Adventure (v2)
A gentle running & jumping game for young children (age ~6).
Original artwork drawn in code. No copyrighted assets.

Kids:    SPACE / UP / MOUSE CLICK = Jump | ESC = Pause | ENTER = Start
Parents: hold P for 3 seconds on the title screen to open Parent Settings
"""
import sys, os, json, random, math

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
pygame.display.set_caption("Frost Runner - Princess Adventure")
clock = pygame.time.Clock()

CFG_PATH = os.path.join(os.path.expanduser("~"), "frost_runner_settings.json")
DEFAULTS = {"dress": 0, "limit_min": 0, "muted": False, "best": 0}

def load_cfg():
    out = dict(DEFAULTS)
    try:
        with open(CFG_PATH) as f:
            d = json.load(f)
        for k in DEFAULTS:
            if k in d and isinstance(d[k], type(DEFAULTS[k])):
                out[k] = d[k]
    except Exception:
        pass
    return out

cfg = load_cfg()

def save_cfg():
    try:
        with open(CFG_PATH, "w") as f:
            json.dump(cfg, f)
    except Exception:
        pass

SKY_TOP = (150, 205, 255); SKY_BOT = (224, 244, 255)
SNOW = (245, 250, 255); ICE = (170, 220, 255); DARKICE = (120, 180, 235)
SKIN = (255, 224, 200)
GOLD = (255, 210, 70); WHITE = (255, 255, 255); TEXTCOL = (40, 70, 120)
PINK = (255, 120, 170)

PRINCESS = [
    {"name": "Aria",  "d1": (110, 180, 240), "d2": (150, 210, 255), "hair": (238, 232, 170)},
    {"name": "Rosa",  "d1": (245, 140, 180), "d2": (255, 185, 210), "hair": (120, 72, 48)},
    {"name": "Luna",  "d1": (170, 130, 235), "d2": (205, 175, 250), "hair": (45, 45, 70)},
    {"name": "Mira",  "d1": (110, 205, 175), "d2": (160, 235, 210), "hair": (225, 140, 70)},
]
LIMITS = [0, 10, 15, 20, 30]

def pick_font(size, bold=True):
    for name in ("comicsansms", "segoeui", "arial"):
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            continue
    return pygame.font.Font(None, size)

font_big = pick_font(56); font_mid = pick_font(32); font_sm = pick_font(22)

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
snd_click = make_tone(660, 90, 0.25)

def play(s):
    if s and not cfg["muted"]:
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

def draw_princess(x, y, skin_idx, leg=0.0, scale=1.0):
    p = PRINCESS[skin_idx]
    d1, d2, hair = p["d1"], p["d2"], p["hair"]
    def P(dx, dy):
        return (x + dx * scale, y + dy * scale)
    pygame.draw.polygon(screen, d1, [P(-22, 0), P(22, 0), P(12, -40), P(-12, -40)])
    pygame.draw.polygon(screen, d2, [P(-10, -2), P(10, -2), P(6, -38), P(-6, -38)])
    pygame.draw.line(screen, SKIN, P(-6, 0), P(-6 - leg, 0), max(3, int(6 * scale)))
    pygame.draw.rect(screen, d1, (x - 10 * scale, y - 58 * scale, 20 * scale, 20 * scale), border_radius=6)
    pygame.draw.line(screen, SKIN, P(-8, -52), P(-16, -40 + leg), max(3, int(5 * scale)))
    pygame.draw.line(screen, SKIN, P(8, -52), P(16, -40 - leg), max(3, int(5 * scale)))
    pygame.draw.circle(screen, SKIN, (int(x), int(y - 66 * scale)), int(13 * scale))
    pygame.draw.line(screen, hair, P(8, -70), P(22, -40), max(4, int(7 * scale)))
    pygame.draw.circle(screen, hair, (int(x), int(y - 74 * scale)), int(9 * scale))
    pygame.draw.polygon(screen, GOLD, [P(-9, -77), P(-4, -85), P(0, -78), P(4, -85), P(9, -77)])
    pygame.draw.circle(screen, TEXTCOL, (int(x - 4 * scale), int(y - 66 * scale)), max(1, int(2 * scale)))
    pygame.draw.circle(screen, TEXTCOL, (int(x + 4 * scale), int(y - 66 * scale)), max(1, int(2 * scale)))

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
        leg = math.sin(self.run * math.pi) * (6 if self.on_ground else 0)
        draw_princess(self.x, self.y, cfg["dress"], leg)

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

MENU, PICK, PLAY, PAUSE, OVER, PARENT, TIMEUP = range(7)

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

def overlay(a=140):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((255, 255, 255, a))
    screen.blit(ov, (0, 0))

def draw_mute_icon():
    x, y = 24, H - 34
    c = (150, 170, 200) if cfg["muted"] else (70, 130, 200)
    pygame.draw.polygon(screen, c, [(x, y - 6), (x + 7, y - 6), (x + 14, y - 14), (x + 14, y + 10), (x + 7, y + 2), (x, y + 2)])
    if cfg["muted"]:
        pygame.draw.line(screen, (220, 80, 90), (x + 18, y - 10), (x + 32, y + 6), 3)
        pygame.draw.line(screen, (220, 80, 90), (x + 32, y - 10), (x + 18, y + 6), 3)
    else:
        pygame.draw.arc(screen, c, (x + 14, y - 12, 18, 20), -1.0, 1.0, 3)
    screen.blit(font_sm.render("M", True, c), (x + 40, y - 12))

state = MENU
g = new_game()
hold_t = 0.0
play_seconds = 0.0
running = True

while running:
    dt = clock.tick(60) / 1000.0
    keys = pygame.key.get_pressed()

    if state in (MENU, TIMEUP) and keys[pygame.K_p]:
        hold_t += dt
        if hold_t >= 3.0:
            hold_t = 0.0
            if state == TIMEUP:
                play_seconds = 0.0
                state = MENU
            else:
                state = PARENT
            play(snd_click)
    else:
        hold_t = 0.0

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_m:
                cfg["muted"] = not cfg["muted"]
                save_cfg()
                play(snd_click)
            elif e.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            elif state == PARENT:
                if e.key == pygame.K_LEFT:
                    cfg["limit_min"] = LIMITS[(LIMITS.index(cfg["limit_min"]) - 1) % len(LIMITS)] if cfg["limit_min"] in LIMITS else 0
                    save_cfg(); play(snd_click)
                elif e.key == pygame.K_RIGHT:
                    cfg["limit_min"] = LIMITS[(LIMITS.index(cfg["limit_min"]) + 1) % len(LIMITS)] if cfg["limit_min"] in LIMITS else 10
                    save_cfg(); play(snd_click)
                elif e.key == pygame.K_r:
                    play_seconds = 0.0; play(snd_click)
                elif e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    state = MENU; play(snd_click)
            elif state == MENU:
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    state = PICK; play(snd_click)
            elif state == PICK:
                if e.key == pygame.K_LEFT:
                    cfg["dress"] = (cfg["dress"] - 1) % len(PRINCESS); save_cfg(); play(snd_click)
                elif e.key == pygame.K_RIGHT:
                    cfg["dress"] = (cfg["dress"] + 1) % len(PRINCESS); save_cfg(); play(snd_click)
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    g = new_game(); state = PLAY; play(snd_click)
                elif e.key == pygame.K_ESCAPE:
                    state = MENU
            elif state == PLAY:
                if e.key == pygame.K_ESCAPE:
                    state = PAUSE
                elif e.key in (pygame.K_SPACE, pygame.K_UP):
                    g["player"].jump()
            elif state == PAUSE:
                if e.key == pygame.K_ESCAPE:
                    state = PLAY
            elif state == OVER:
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    g = new_game(); state = PLAY
                elif e.key == pygame.K_ESCAPE:
                    state = PICK
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if state == PLAY:
                g["player"].jump()
            elif state == PICK:
                g = new_game(); state = PLAY; play(snd_click)
            elif state in (MENU, OVER):
                state = PICK; play(snd_click)

    if state == PLAY:
        play_seconds += dt
        if cfg["limit_min"] > 0 and play_seconds >= cfg["limit_min"] * 60:
            state = TIMEUP
            play(snd_win)

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
                    state = OVER
                    if g["score"] > cfg["best"]:
                        cfg["best"] = g["score"]
                        save_cfg()
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
    if state in (PLAY, PAUSE, OVER, TIMEUP):
        g["player"].draw()
    draw_particles()

    if state in (PLAY, PAUSE, OVER):
        screen.blit(font_mid.render("Score: %d" % g["score"], True, TEXTCOL), (20, 18))
        draw_hearts(g["hearts"])
    if g["praise_t"] > 0 and state == PLAY:
        text_center(g["praise"], font_mid, H // 2 - 150, PINK)

    if state == MENU:
        overlay(120)
        text_center("Frost Runner", font_big, 90, (70, 120, 200))
        text_center("Princess Adventure", font_mid, 165, (140, 90, 180))
        text_center("Press ENTER or CLICK to Play", font_mid, 265)
        text_center("Best score: %d" % cfg["best"], font_sm, 320, (120, 150, 190))
        text_center("Parents: hold P for 3 seconds for settings", font_sm, 400, (140, 160, 190))
        if hold_t > 0:
            pygame.draw.rect(screen, (200, 215, 235), (W // 2 - 100, 430, 200, 10), border_radius=5)
            pygame.draw.rect(screen, (70, 130, 200), (W // 2 - 100, 430, int(200 * hold_t / 3.0), 10), border_radius=5)
        draw_mute_icon()

    elif state == PICK:
        overlay(140)
        text_center("Choose your princess", font_mid, 45, (140, 90, 180))
        for i, p in enumerate(PRINCESS):
            cx = 140 + i * 210
            sel = (i == cfg["dress"])
            if sel:
                pygame.draw.rect(screen, (255, 245, 200), (cx - 85, 95, 170, 260), border_radius=18)
                pygame.draw.rect(screen, GOLD, (cx - 85, 95, 170, 260), 4, border_radius=18)
            else:
                pygame.draw.rect(screen, (255, 255, 255, 200), (cx - 80, 100, 160, 250), border_radius=16)
            draw_princess(cx, 300, i, 0, 1.15)
            nm = font_mid.render(p["name"], True, TEXTCOL if sel else (140, 160, 190))
            screen.blit(nm, (cx - nm.get_width() // 2, 310))
        text_center("LEFT / RIGHT to choose    ENTER to play", font_sm, 400)
        text_center("ESC to go back", font_sm, 432, (140, 160, 190))
        draw_mute_icon()

    elif state == PAUSE:
        overlay(150)
        text_center("Paused", font_big, 140)
        text_center("Press ESC to keep playing", font_sm, 240)
        draw_mute_icon()

    elif state == OVER:
        overlay(150)
        text_center("Great Playing!", font_big, 100, PINK)
        text_center("You scored %d" % g["score"], font_mid, 190)
        text_center("Best ever: %d" % cfg["best"], font_sm, 240, (120, 150, 190))
        text_center("Press ENTER to play again", font_sm, 300)
        text_center("ESC to change princess", font_sm, 335, (140, 160, 190))
        draw_mute_icon()

    elif state == PARENT:
        overlay(200)
        text_center("Parent Settings", font_big, 60, (70, 120, 200))
        lim = "No limit" if cfg["limit_min"] == 0 else "%d minutes" % cfg["limit_min"]
        text_center("Play time limit:  < %s >" % lim, font_mid, 165)
        text_center("LEFT / RIGHT to change", font_sm, 210, (140, 160, 190))
        text_center("Sound:  %s   (press M)" % ("MUTED" if cfg["muted"] else "ON"), font_mid, 265)
        used = int(play_seconds // 60)
        text_center("Played this session: %d min   (press R to reset)" % used, font_sm, 320, (140, 160, 190))
        text_center("Press ESC to go back", font_sm, 400)
        text_center("Settings are saved automatically", font_sm, 435, (170, 185, 205))

    elif state == TIMEUP:
        overlay(200)
        text_center("Time for a break!", font_big, 110, PINK)
        text_center("Great playing today.", font_mid, 200)
        text_center("Ask a grown-up if you want more time.", font_sm, 255, (120, 150, 190))
        text_center("Parents: hold P for 3 seconds to allow more", font_sm, 340, (140, 160, 190))
        if hold_t > 0:
            pygame.draw.rect(screen, (200, 215, 235), (W // 2 - 100, 380, 200, 10), border_radius=5)
            pygame.draw.rect(screen, (70, 130, 200), (W // 2 - 100, 380, int(200 * hold_t / 3.0), 10), border_radius=5)

    pygame.display.flip()

save_cfg()
pygame.quit()
