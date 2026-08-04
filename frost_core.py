"""Frost Runner Adventure - shared setup, config, colors, drawing helpers."""
import sys, os, json, math, random

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

W, H = 960, 540
GROUND = H - 95
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Frost Runner Adventure")
clock = pygame.time.Clock()

CFG_PATH = os.path.join(os.path.expanduser("~"), "frost_runner_settings.json")
DEFAULTS = {"dress": 0, "limit_min": 0, "muted": False, "best": 0, "easy": True, "unlocked": 1}


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


WHITE = (255, 255, 255)
SNOW = (245, 250, 255)
ICE = (170, 220, 255)
DARKICE = (120, 180, 235)
SKIN = (255, 224, 200)
GOLD = (255, 210, 70)
TEXTCOL = (40, 70, 120)
PINK = (255, 120, 170)
WOOD = (140, 100, 62)
STEEL = (95, 115, 145)

PRINCESS = [
    {"name": "Aria", "d1": (110, 180, 240), "d2": (150, 210, 255), "hair": (238, 232, 170)},
    {"name": "Rosa", "d1": (245, 140, 180), "d2": (255, 185, 210), "hair": (120, 72, 48)},
    {"name": "Luna", "d1": (170, 130, 235), "d2": (205, 175, 250), "hair": (45, 45, 70)},
    {"name": "Mira", "d1": (110, 205, 175), "d2": (160, 235, 210), "hair": (225, 140, 70)},
]

STAGES = [
    {"name": "Snow Valley", "dist": 2600, "sky": ((150, 205, 255), (226, 244, 255)),
     "speed": 4.4, "arrow": 0.000, "mon": 0.35, "hill": (200, 230, 255)},
    {"name": "Crystal Cave", "dist": 3000, "sky": ((110, 150, 220), (200, 220, 250)),
     "speed": 4.8, "arrow": 0.030, "mon": 0.45, "hill": (170, 195, 240)},
    {"name": "Frozen Forest", "dist": 3400, "sky": ((150, 200, 225), (225, 245, 240)),
     "speed": 5.2, "arrow": 0.045, "mon": 0.55, "hill": (185, 220, 210)},
    {"name": "Mountain Bridge", "dist": 3800, "sky": ((120, 170, 235), (215, 235, 255)),
     "speed": 5.6, "arrow": 0.060, "mon": 0.60, "hill": (175, 205, 245)},
    {"name": "Ice Castle", "dist": 4200, "sky": ((90, 130, 210), (195, 215, 250)),
     "speed": 6.0, "arrow": 0.075, "mon": 0.70, "hill": (160, 185, 235)},
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


font_big = pick_font(54)
font_mid = pick_font(30)
font_sm = pick_font(21)


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
        buf.append(s)
        buf.append(s)
    try:
        return pygame.mixer.Sound(buffer=buf.tobytes())
    except Exception:
        return None


snd_jump = make_tone(520, 150, 0.22)
snd_star = make_tone(880, 170, 0.26)
snd_gem = make_tone(1050, 200, 0.28)
snd_crown = make_tone(1300, 320, 0.32)
snd_oops = make_tone(190, 300, 0.28)
snd_poof = make_tone(700, 130, 0.22)
snd_power = make_tone(1500, 260, 0.30)
snd_win = make_tone(1000, 480, 0.32)
snd_click = make_tone(660, 90, 0.22)


def play(s):
    if s and not cfg["muted"]:
        try:
            s.play()
        except Exception:
            pass


def clamp(v, lo, hi):
    return lo if v < lo else (hi if v > hi else v)


def text_center(txt, fnt, y, col=TEXTCOL):
    s = fnt.render(txt, True, col)
    screen.blit(s, (W // 2 - s.get_width() // 2, y))


def overlay(a=140):
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((255, 255, 255, a))
    screen.blit(ov, (0, 0))


hills = [(random.randint(0, W), random.randint(70, 140)) for _ in range(5)]
clouds = [[random.randint(0, W), random.randint(35, 175), random.uniform(0.45, 0.95)] for _ in range(6)]
flakes = [[random.randint(0, W), random.randint(0, H), random.uniform(1, 3)] for _ in range(80)]


def draw_background(scroll, stage):
    top, bot = STAGES[stage]["sky"]
    for y in range(0, H, 3):
        t = y / H
        c = [int(top[i] + (bot[i] - top[i]) * t) for i in range(3)]
        pygame.draw.rect(screen, c, (0, y, W, 3))
    hc = STAGES[stage]["hill"]
    for hx, hh in hills:
        x = (hx - scroll * 0.18) % (W + 420) - 210
        pygame.draw.ellipse(screen, hc, (x - 160, GROUND + 22 - hh, 320, hh * 2))
    for c in clouds:
        c[0] -= 0.28
        if c[0] < -150:
            c[0] = W + 100
            c[1] = random.randint(35, 175)
        s = c[2]
        for dx, dy, r in [(0, 0, 22), (24, 4, 26), (48, 0, 20), (20, -12, 20)]:
            pygame.draw.circle(screen, WHITE, (int(c[0] + dx * s), int(c[1] + dy * s)), int(r * s))
    pygame.draw.rect(screen, SNOW, (0, GROUND, W, H - GROUND))
    pygame.draw.rect(screen, ICE, (0, GROUND, W, 8))
    for f in flakes:
        f[1] += f[2]
        f[0] -= 0.35
        if f[1] > H:
            f[1] = 0
            f[0] = random.randint(0, W)
        pygame.draw.circle(screen, WHITE, (int(f[0]), int(f[1])), int(f[2]))


def draw_princess(x, y, idx, leg=0.0, scale=1.0, squash=0.0, blink=False, cheer=False, shield=False):
    p = PRINCESS[idx]
    d1, d2, hair = p["d1"], p["d2"], p["hair"]
    sy = 1.0 - squash
    sx = 1.0 + squash * 0.5

    def P(dx, dy):
        return (x + dx * scale * sx, y + dy * scale * sy)

    if shield:
        pygame.draw.circle(screen, (150, 225, 255), (int(x), int(y - 42 * scale)), int(46 * scale), 4)
        pygame.draw.circle(screen, (215, 245, 255), (int(x), int(y - 42 * scale)), int(40 * scale), 2)
    pygame.draw.polygon(screen, d1, [P(-23, 0), P(23, 0), P(12, -41), P(-12, -41)])
    pygame.draw.polygon(screen, d2, [P(-10, -2), P(10, -2), P(6, -39), P(-6, -39)])
    pygame.draw.line(screen, SKIN, P(-6, 0), P(-6 - leg, 0), max(3, int(6 * scale)))
    pygame.draw.line(screen, SKIN, P(6, 0), P(6 + leg * 0.5, 0), max(3, int(6 * scale)))
    pygame.draw.rect(screen, d1, (x - 10 * scale, y - (59 * scale * sy), 20 * scale, 20 * scale), border_radius=6)
    if cheer:
        pygame.draw.line(screen, SKIN, P(-8, -53), P(-22, -74), max(3, int(5 * scale)))
        pygame.draw.line(screen, SKIN, P(8, -53), P(22, -74), max(3, int(5 * scale)))
    else:
        pygame.draw.line(screen, SKIN, P(-8, -53), P(-17, -40 + leg), max(3, int(5 * scale)))
        pygame.draw.line(screen, SKIN, P(8, -53), P(17, -40 - leg), max(3, int(5 * scale)))
    hx, hy = int(x), int(y - 67 * scale * sy)
    pygame.draw.circle(screen, SKIN, (hx, hy), int(13 * scale))
    pygame.draw.line(screen, hair, P(8, -71), P(24, -38), max(4, int(7 * scale)))
    pygame.draw.circle(screen, hair, (hx, int(y - 75 * scale * sy)), int(9 * scale))
    pygame.draw.polygon(screen, GOLD, [P(-9, -78), P(-4, -87), P(0, -79), P(4, -87), P(9, -78)])
    if blink:
        pygame.draw.line(screen, TEXTCOL, (hx - 6, hy), (hx - 1, hy), 2)
        pygame.draw.line(screen, TEXTCOL, (hx + 1, hy), (hx + 6, hy), 2)
    else:
        pygame.draw.circle(screen, TEXTCOL, (hx - 4, hy), max(1, int(2 * scale)))
        pygame.draw.circle(screen, TEXTCOL, (hx + 4, hy), max(1, int(2 * scale)))
    if cheer:
        pygame.draw.arc(screen, TEXTCOL, (hx - 6, hy + 2, 12, 9), 3.4, 6.0, 2)


particles = []
floaters = []


def burst(x, y, c, n=12, spd=3.2):
    for _ in range(n):
        particles.append([x, y, random.uniform(-spd, spd), random.uniform(-spd - 1, 0.4), c,
                          random.randint(16, 26)])


def sparkle_ring(x, y, c):
    for i in range(12):
        a = i * math.pi / 6
        particles.append([x, y, math.cos(a) * 3.0, math.sin(a) * 3.0, c, 22])


def float_text(x, y, txt, col):
    floaters.append([x, y, txt, col, 44])


def draw_particles():
    for p in particles[:]:
        p[0] += p[2]
        p[1] += p[3]
        p[3] += 0.17
        p[5] -= 1
        pygame.draw.circle(screen, p[4], (int(p[0]), int(p[1])), 3)
        if p[5] <= 0:
            particles.remove(p)
    for f in floaters[:]:
        f[1] -= 1.1
        f[4] -= 1
        s = font_sm.render(f[2], True, f[3])
        screen.blit(s, (int(f[0] - s.get_width() // 2), int(f[1])))
        if f[4] <= 0:
            floaters.remove(f)


def draw_chest(cx, cy, t):
    pygame.draw.rect(screen, (150, 105, 60), (cx - 46, cy - 30, 92, 52), border_radius=6)
    pygame.draw.rect(screen, (185, 135, 80), (cx - 46, cy - 12, 92, 12))
    lift = int(min(26, t * 0.6))
    pygame.draw.rect(screen, (170, 120, 70), (cx - 46, cy - 40 - lift, 92, 20), border_radius=8)
    pygame.draw.circle(screen, GOLD, (cx, cy - 6), 7)
    if t > 20:
        for i in range(7):
            a = -math.pi / 2 + (i - 3) * 0.28
            r = 34 + (t % 26)
            pygame.draw.circle(screen, GOLD, (int(cx + math.cos(a) * r), int(cy - 24 + math.sin(a) * r)), 4)


def hit(a, b):
    return a.colliderect(b)
