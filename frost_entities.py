"""Frost Runner Adventure - player, arrows, monsters and pickups."""
import math, random
import pygame
from frost_core import (
    W, H, GROUND, screen, cfg, clamp, play,
    WHITE, SNOW, ICE, DARKICE, SKIN, GOLD, TEXTCOL, PINK, WOOD, STEEL,
    draw_princess, snd_jump,
)


class Player:
    def __init__(self):
        self.x = 200.0
        self.y = float(GROUND)
        self.vy = 0.0
        self.on_ground = True
        self.run = 0.0
        self.squash = 0.0
        self.blink_t = random.randint(60, 160)
        self.blink = False
        self.inv = 0

    def jump(self):
        if self.on_ground:
            self.vy = -15.8
            self.on_ground = False
            play(snd_jump)

    def update(self, move):
        self.x = clamp(self.x + move * 5.4, 70, W - 90)
        self.vy += 0.76
        self.y += self.vy
        if self.y >= GROUND:
            if not self.on_ground and self.vy > 6:
                self.squash = 0.30
            self.y = float(GROUND)
            self.vy = 0.0
            self.on_ground = True
        self.run = (self.run + 0.26) % 4
        if self.squash > 0:
            self.squash = max(0.0, self.squash - 0.04)
        self.blink_t -= 1
        if self.blink_t <= 0:
            self.blink = True
            if self.blink_t < -7:
                self.blink = False
                self.blink_t = random.randint(70, 190)
        if self.inv > 0:
            self.inv -= 1

    def rect(self):
        return pygame.Rect(self.x - 17, self.y - 70, 36, 70)

    def draw(self, shield):
        leg = math.sin(self.run * math.pi) * (6 if self.on_ground else 0)
        if self.inv > 0 and (self.inv // 4) % 2 == 0:
            return
        draw_princess(self.x, self.y, cfg["dress"], leg, 1.0, self.squash, self.blink, False, shield)


ARROW_LEN = 92


class Arrow:
    """Falls straight down from above, aimed at the player. Tip points at her."""

    def __init__(self, px, speed):
        self.x = clamp(px + random.randint(-70, 70), 60, W - 60)
        self.y = -ARROW_LEN
        self.speed = speed
        self.drift = random.choice([-0.55, 0.0, 0.0, 0.55])
        self.state = "warn"
        self.warn = 42
        self.stuck = 40

    def update(self, slow):
        f = 0.45 if slow else 1.0
        if self.state == "warn":
            self.warn -= 1
            if self.warn <= 0:
                self.state = "fall"
        elif self.state == "fall":
            self.y += self.speed * f
            self.x += self.drift * f
            if self.y >= GROUND:
                self.y = float(GROUND)
                self.state = "stuck"
        else:
            self.stuck -= 1

    def dead(self):
        return self.state == "stuck" and self.stuck <= 0

    def rect(self):
        return pygame.Rect(self.x - 8, self.y - 26, 16, 30)

    def draw(self):
        gx = int(self.x)
        if self.state == "warn":
            if (self.warn // 5) % 2 == 0:
                pygame.draw.polygon(screen, (255, 95, 95), [(gx, 30), (gx - 12, 6), (gx + 12, 6)])
                pygame.draw.rect(screen, WHITE, (gx - 2, 11, 4, 10))
                pygame.draw.circle(screen, WHITE, (gx, 25), 2)
            pygame.draw.ellipse(screen, (196, 210, 232), (gx - 17, GROUND - 6, 34, 11))
            return
        top = self.y - ARROW_LEN
        pygame.draw.line(screen, WOOD, (gx, int(top + 10)), (gx, int(self.y - 20)), 5)
        pygame.draw.polygon(screen, (242, 244, 252),
                            [(gx, int(top)), (gx - 10, int(top + 16)), (gx, int(top + 12))])
        pygame.draw.polygon(screen, (242, 244, 252),
                            [(gx, int(top)), (gx + 10, int(top + 16)), (gx, int(top + 12))])
        pygame.draw.polygon(screen, STEEL,
                            [(gx, int(self.y)), (gx - 11, int(self.y - 22)), (gx + 11, int(self.y - 22))])
        pygame.draw.polygon(screen, (185, 205, 230),
                            [(gx, int(self.y - 4)), (gx - 5, int(self.y - 18)), (gx + 5, int(self.y - 18))])
        if self.state == "fall":
            d = clamp((GROUND - self.y) / 320.0, 0.0, 1.0)
            r = int(9 + 9 * (1 - d))
            pygame.draw.ellipse(screen, (198, 212, 232), (gx - r, GROUND - 5, r * 2, 10))


class Monster:
    def __init__(self, x, kind):
        self.x = float(x)
        self.kind = kind
        self.t = random.random() * 6

    def y_now(self):
        if self.kind == "slime":
            return GROUND - abs(math.sin(self.t)) * 48
        if self.kind == "bat":
            return GROUND - 150 + math.sin(self.t) * 30
        return float(GROUND)

    def update(self, sp, slow):
        f = 0.5 if slow else 1.0
        extra = 1.25 if self.kind == "goblin" else (1.45 if self.kind == "bat" else 1.0)
        self.x -= sp * f * extra
        self.t += 0.13 * f

    def rect(self):
        y = self.y_now()
        if self.kind == "slime":
            return pygame.Rect(self.x - 17, y - 27, 34, 27)
        if self.kind == "bat":
            return pygame.Rect(self.x - 17, y - 13, 34, 26)
        return pygame.Rect(self.x - 15, y - 36, 30, 36)

    def stomp_rect(self):
        y = self.y_now()
        if self.kind == "slime":
            return pygame.Rect(self.x - 17, y - 30, 34, 14)
        if self.kind == "bat":
            return pygame.Rect(self.x - 17, y - 16, 34, 12)
        return pygame.Rect(self.x - 15, y - 40, 30, 16)

    def draw(self):
        x = int(self.x)
        y = int(self.y_now())
        if self.kind == "goblin":
            wob = int(math.sin(self.t * 2) * 3)
            pygame.draw.ellipse(screen, (120, 175, 145), (x - 15, y - 34, 30, 34))
            pygame.draw.circle(screen, (140, 195, 165), (x, y - 32), 12)
            pygame.draw.polygon(screen, (150, 205, 175), [(x - 12, y - 38), (x - 18, y - 50), (x - 5, y - 42)])
            pygame.draw.polygon(screen, (150, 205, 175), [(x + 12, y - 38), (x + 18, y - 50), (x + 5, y - 42)])
            pygame.draw.circle(screen, WHITE, (x - 5, y - 33), 4)
            pygame.draw.circle(screen, WHITE, (x + 5, y - 33), 4)
            pygame.draw.circle(screen, TEXTCOL, (x - 5, y - 33), 2)
            pygame.draw.circle(screen, TEXTCOL, (x + 5, y - 33), 2)
            pygame.draw.line(screen, (95, 150, 120), (x - 6, y), (x - 6 + wob, y - 6), 5)
            pygame.draw.line(screen, (95, 150, 120), (x + 6, y), (x + 6 - wob, y - 6), 5)
        elif self.kind == "slime":
            sq = abs(math.sin(self.t)) * 6
            pygame.draw.ellipse(screen, (150, 205, 255), (x - 18 - sq / 2, y - 26 + sq, 36 + sq, 26 - sq))
            pygame.draw.ellipse(screen, (200, 235, 255), (x - 10, y - 22, 14, 8))
            pygame.draw.circle(screen, WHITE, (x - 6, y - 15), 4)
            pygame.draw.circle(screen, WHITE, (x + 6, y - 15), 4)
            pygame.draw.circle(screen, TEXTCOL, (x - 6, y - 15), 2)
            pygame.draw.circle(screen, TEXTCOL, (x + 6, y - 15), 2)
        else:
            flap = math.sin(self.t * 3) * 12
            pygame.draw.polygon(screen, (150, 160, 210), [(x - 6, y), (x - 30, y - 8 - flap), (x - 8, y + 8)])
            pygame.draw.polygon(screen, (150, 160, 210), [(x + 6, y), (x + 30, y - 8 - flap), (x + 8, y + 8)])
            pygame.draw.circle(screen, (120, 130, 190), (x, y), 12)
            pygame.draw.polygon(screen, (120, 130, 190), [(x - 9, y - 9), (x - 12, y - 19), (x - 3, y - 12)])
            pygame.draw.polygon(screen, (120, 130, 190), [(x + 9, y - 9), (x + 12, y - 19), (x + 3, y - 12)])
            pygame.draw.circle(screen, WHITE, (x - 4, y - 2), 3)
            pygame.draw.circle(screen, WHITE, (x + 4, y - 2), 3)
            pygame.draw.circle(screen, TEXTCOL, (x - 4, y - 2), 1)
            pygame.draw.circle(screen, TEXTCOL, (x + 4, y - 2), 1)


PICKUPS = ("star", "crystal", "crown", "heart", "shield", "snow", "magnet")


class Pickup:
    def __init__(self, x, kind, y=None):
        self.x = float(x)
        self.kind = kind
        self.y = float(y if y is not None else GROUND - random.choice([45, 95, 145]))
        self.t = random.random() * 6

    def update(self, sp, slow, player, magnet):
        self.x -= sp * (0.5 if slow else 1.0)
        self.t += 0.1
        if magnet and self.kind in ("star", "crystal"):
            dx = player.x - self.x
            dy = (player.y - 40) - self.y
            d = math.hypot(dx, dy)
            if 1 < d < 190:
                self.x += dx / d * 5.5
                self.y += dy / d * 5.5

    def rect(self):
        return pygame.Rect(self.x - 14, self.y - 14, 28, 28)

    def draw(self):
        x = int(self.x)
        y = int(self.y + math.sin(self.t) * 4)
        k = self.kind
        if k in ("star", "crown"):
            c = GOLD if k == "crown" else (255, 255, 185)
            rr = 15 if k == "crown" else 11
            pts = []
            for i in range(10):
                r = rr if i % 2 == 0 else rr * 0.45
                a = math.pi / 2 + i * math.pi / 5
                pts.append((x + math.cos(a) * r, y - math.sin(a) * r))
            pygame.draw.polygon(screen, c, pts)
            if k == "crown":
                pygame.draw.polygon(screen, (255, 240, 190),
                                    [(x - 8, y + 4), (x - 4, y - 5), (x, y + 2), (x + 4, y - 5), (x + 8, y + 4)])
            else:
                pygame.draw.circle(screen, TEXTCOL, (x - 3, y - 1), 1)
                pygame.draw.circle(screen, TEXTCOL, (x + 3, y - 1), 1)
        elif k == "crystal":
            pygame.draw.polygon(screen, (130, 225, 255), [(x, y - 15), (x + 10, y), (x, y + 15), (x - 10, y)])
            pygame.draw.polygon(screen, (215, 245, 255), [(x, y - 15), (x + 4, y), (x, y + 15)])
        elif k == "heart":
            pygame.draw.circle(screen, (255, 95, 125), (x - 6, y - 3), 7)
            pygame.draw.circle(screen, (255, 95, 125), (x + 6, y - 3), 7)
            pygame.draw.polygon(screen, (255, 95, 125), [(x - 12, y), (x + 12, y), (x, y + 14)])
        elif k == "shield":
            pygame.draw.polygon(screen, (140, 215, 255),
                                [(x - 12, y - 12), (x + 12, y - 12), (x + 9, y + 8), (x, y + 15), (x - 9, y + 8)])
            pygame.draw.polygon(screen, WHITE, [(x - 5, y - 6), (x + 5, y - 6), (x, y + 6)])
        elif k == "snow":
            for i in range(6):
                a = i * math.pi / 3
                pygame.draw.line(screen, (225, 245, 255), (x, y),
                                 (x + math.cos(a) * 14, y + math.sin(a) * 14), 3)
            pygame.draw.circle(screen, WHITE, (x, y), 4)
        else:
            pygame.draw.arc(screen, (235, 100, 110), (x - 13, y - 13, 26, 26), 0.6, 2.6, 6)
            pygame.draw.rect(screen, (225, 225, 235), (x - 13, y + 1, 6, 11))
            pygame.draw.rect(screen, (225, 225, 235), (x + 7, y + 1, 6, 11))
