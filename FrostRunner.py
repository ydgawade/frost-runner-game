#!/usr/bin/env python3
"""
Frost Runner Adventure (v3) - main game loop.

Kids:    LEFT / RIGHT = move    SPACE / UP / CLICK = jump    ESC = pause
Parents: hold P for 3 seconds on the title screen for Parent Settings
"""
import math, random
import pygame
from frost_core import (
    W, H, GROUND, screen, clock, cfg, save_cfg, clamp, play, overlay, text_center,
    WHITE, SNOW, ICE, SKIN, GOLD, TEXTCOL, PINK,
    PRINCESS, STAGES, LIMITS, font_big, font_mid, font_sm,
    draw_background, draw_princess, draw_particles, draw_chest,
    burst, sparkle_ring, float_text, hit,
    snd_star, snd_gem, snd_crown, snd_oops, snd_poof, snd_power, snd_win, snd_click,
)
from frost_entities import Player, Arrow, Monster, Pickup

MENU, PICK, PLAY, PAUSE, OVER, PARENT, TIMEUP, LEVELDONE, WINGAME = range(9)


def new_run(stage, score=0, hearts=3, crowns=0):
    return {"player": Player(), "stage": stage, "score": score, "hearts": hearts,
            "crowns": crowns, "dist": 0.0, "scroll": 0.0, "spawn": 30, "arrows": [],
            "mons": [], "picks": [], "combo": 0, "combo_t": 0, "mult": 1,
            "shield": False, "slow_t": 0, "magnet_t": 0, "checkpoint": False,
            "praise": "", "praise_t": 0, "banner": "", "banner_t": 0, "cheer": 0}


praises = ["Great jump!", "Amazing!", "Wow!", "Super!", "You did it!", "Yay!", "Nice one!"]


def stage_speed(st):
    return STAGES[st]["speed"] * (0.82 if cfg["easy"] else 1.0)


def draw_hearts(n):
    for i in range(5):
        if i >= max(3, n):
            break
        x = W - 40 - i * 32
        y = 30
        c = (255, 90, 120) if i < n else (205, 205, 215)
        pygame.draw.circle(screen, c, (x - 5, y), 7)
        pygame.draw.circle(screen, c, (x + 5, y), 7)
        pygame.draw.polygon(screen, c, [(x - 11, y + 2), (x + 11, y + 2), (x, y + 14)])


def draw_hud(g):
    screen.blit(font_mid.render("Score: %d" % g["score"], True, TEXTCOL), (20, 16))
    draw_hearts(g["hearts"])
    if g["mult"] > 1:
        screen.blit(font_sm.render("x%d combo!" % g["mult"], True, (235, 130, 60)), (22, 54))
    st = STAGES[g["stage"]]
    frac = clamp(g["dist"] / st["dist"], 0.0, 1.0)
    bx, bw = 200, W - 400
    pygame.draw.rect(screen, WHITE, (bx, H - 26, bw, 14), border_radius=7)
    pygame.draw.rect(screen, (120, 200, 140), (bx, H - 26, int(bw * frac), 14), border_radius=7)
    pygame.draw.rect(screen, (150, 175, 205), (bx, H - 26, bw, 14), 2, border_radius=7)
    screen.blit(font_sm.render("%d/5  %s" % (g["stage"] + 1, st["name"]), True, TEXTCOL), (bx - 175, H - 30))
    fx = bx + bw + 12
    pygame.draw.rect(screen, (170, 130, 90), (fx, H - 34, 8, 28))
    pygame.draw.polygon(screen, (240, 190, 90), [(fx + 8, H - 34), (fx + 30, H - 27), (fx + 8, H - 20)])
    ix = 20
    if g["shield"]:
        pygame.draw.polygon(screen, (140, 215, 255),
                            [(ix, 84), (ix + 20, 84), (ix + 17, 100), (ix + 10, 106), (ix + 3, 100)])
        ix += 30
    if g["slow_t"] > 0:
        for i in range(6):
            a = i * math.pi / 3
            pygame.draw.line(screen, (200, 235, 255), (ix + 10, 94),
                             (ix + 10 + math.cos(a) * 10, 94 + math.sin(a) * 10), 3)
        ix += 30
    if g["magnet_t"] > 0:
        pygame.draw.arc(screen, (235, 100, 110), (ix, 84, 22, 22), 0.6, 2.6, 5)


def draw_mute_icon():
    x, y = 24, H - 62
    c = (150, 170, 200) if cfg["muted"] else (70, 130, 200)
    pygame.draw.polygon(screen, c, [(x, y - 6), (x + 7, y - 6), (x + 14, y - 14),
                                    (x + 14, y + 10), (x + 7, y + 2), (x, y + 2)])
    if cfg["muted"]:
        pygame.draw.line(screen, (220, 80, 90), (x + 18, y - 10), (x + 32, y + 6), 3)
        pygame.draw.line(screen, (220, 80, 90), (x + 32, y - 10), (x + 18, y + 6), 3)
    else:
        pygame.draw.arc(screen, c, (x + 14, y - 12, 18, 20), -1.0, 1.0, 3)
    screen.blit(font_sm.render("M", True, c), (x + 40, y - 12))


state = MENU
g = new_run(0)
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
                    i = LIMITS.index(cfg["limit_min"]) if cfg["limit_min"] in LIMITS else 0
                    cfg["limit_min"] = LIMITS[(i - 1) % len(LIMITS)]
                    save_cfg()
                    play(snd_click)
                elif e.key == pygame.K_RIGHT:
                    i = LIMITS.index(cfg["limit_min"]) if cfg["limit_min"] in LIMITS else 0
                    cfg["limit_min"] = LIMITS[(i + 1) % len(LIMITS)]
                    save_cfg()
                    play(snd_click)
                elif e.key == pygame.K_d:
                    cfg["easy"] = not cfg["easy"]
                    save_cfg()
                    play(snd_click)
                elif e.key == pygame.K_r:
                    play_seconds = 0.0
                    play(snd_click)
                elif e.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    state = MENU
                    play(snd_click)
            elif state == MENU:
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    state = PICK
                    play(snd_click)
            elif state == PICK:
                if e.key == pygame.K_LEFT:
                    cfg["dress"] = (cfg["dress"] - 1) % len(PRINCESS)
                    save_cfg()
                    play(snd_click)
                elif e.key == pygame.K_RIGHT:
                    cfg["dress"] = (cfg["dress"] + 1) % len(PRINCESS)
                    save_cfg()
                    play(snd_click)
                elif e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    g = new_run(0)
                    state = PLAY
                    play(snd_click)
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
            elif state == LEVELDONE:
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    nxt = g["stage"] + 1
                    if nxt >= len(STAGES):
                        state = WINGAME
                    else:
                        cfg["unlocked"] = max(cfg["unlocked"], nxt + 1)
                        save_cfg()
                        g = new_run(nxt, g["score"], min(5, g["hearts"] + 1), g["crowns"])
                        state = PLAY
            elif state in (OVER, WINGAME):
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                    g = new_run(0)
                    state = PLAY
                elif e.key == pygame.K_ESCAPE:
                    state = PICK
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if state == PLAY:
                g["player"].jump()
            elif state == PICK:
                g = new_run(0)
                state = PLAY
                play(snd_click)
            elif state == LEVELDONE:
                nxt = g["stage"] + 1
                if nxt >= len(STAGES):
                    state = WINGAME
                else:
                    g = new_run(nxt, g["score"], min(5, g["hearts"] + 1), g["crowns"])
                    state = PLAY
            elif state in (MENU, OVER, WINGAME):
                state = PICK
                play(snd_click)

    if state == PLAY:
        play_seconds += dt
        if cfg["limit_min"] > 0 and play_seconds >= cfg["limit_min"] * 60:
            state = TIMEUP
            play(snd_win)

        st = STAGES[g["stage"]]
        sp = stage_speed(g["stage"])
        slow = g["slow_t"] > 0
        eff = sp * (0.5 if slow else 1.0)
        g["scroll"] += eff
        g["dist"] += eff
        p = g["player"]

        move = 0
        if keys[pygame.K_LEFT]:
            move -= 1
        if keys[pygame.K_RIGHT]:
            move += 1
        p.update(move)

        if g["slow_t"] > 0:
            g["slow_t"] -= 1
        if g["magnet_t"] > 0:
            g["magnet_t"] -= 1
        if g["combo_t"] > 0:
            g["combo_t"] -= 1
            if g["combo_t"] == 0:
                g["combo"] = 0
                g["mult"] = 1

        if not g["checkpoint"] and g["dist"] >= st["dist"] * 0.5:
            g["checkpoint"] = True
            g["hearts"] = min(5, g["hearts"] + 1)
            g["banner"] = "Checkpoint!  +1 heart"
            g["banner_t"] = 90
            sparkle_ring(p.x, p.y - 40, (150, 235, 170))
            play(snd_power)

        g["spawn"] -= 1
        if g["spawn"] <= 0:
            g["spawn"] = random.randint(42, 74)
            ar = st["arrow"] * (0.55 if cfg["easy"] else 1.0)
            if random.random() < ar * 12:
                g["arrows"].append(Arrow(p.x, 6.2 + g["stage"] * 0.5))
            mr = st["mon"] * (0.6 if cfg["easy"] else 1.0)
            if random.random() < mr:
                kinds = ["goblin", "slime"] if g["stage"] < 2 else ["goblin", "slime", "bat"]
                g["mons"].append(Monster(W + 50, random.choice(kinds)))
            roll = random.random()
            if roll < 0.10:
                g["picks"].append(Pickup(W + 60, "crown"))
            elif roll < 0.16 and g["hearts"] < 5:
                g["picks"].append(Pickup(W + 60, "heart"))
            elif roll < 0.21:
                g["picks"].append(Pickup(W + 60, "shield"))
            elif roll < 0.25:
                g["picks"].append(Pickup(W + 60, "snow"))
            elif roll < 0.29:
                g["picks"].append(Pickup(W + 60, "magnet"))
            elif roll < 0.55:
                for k in range(random.randint(2, 3)):
                    g["picks"].append(Pickup(W + 60 + k * 40, "crystal"))
            else:
                for k in range(random.randint(2, 4)):
                    g["picks"].append(Pickup(W + 60 + k * 38, "star"))

        for a in g["arrows"][:]:
            a.update(slow)
            if a.dead():
                g["arrows"].remove(a)
                continue
            if a.state == "fall" and p.inv <= 0 and hit(a.rect(), p.rect()):
                a.state = "stuck"
                a.stuck = 20
                burst(a.x, a.y, (225, 235, 250), 14)
                if g["shield"]:
                    g["shield"] = False
                    float_text(p.x, p.y - 92, "Shield saved you!", (90, 170, 220))
                    play(snd_poof)
                else:
                    g["hearts"] -= 1
                    p.inv = 70
                    play(snd_oops)
                    if g["hearts"] <= 0:
                        state = OVER

        for m in g["mons"][:]:
            m.update(eff, slow)
            if m.x < -70:
                g["mons"].remove(m)
                continue
            pr = p.rect()
            if p.vy > 0 and hit(m.stomp_rect(), pr):
                g["mons"].remove(m)
                p.vy = -11.5
                gain = 25 * g["mult"]
                g["score"] += gain
                burst(m.x, m.y_now() - 12, (225, 245, 255), 16)
                float_text(m.x, m.y_now() - 46, "+%d" % gain, (90, 160, 210))
                play(snd_poof)
                continue
            if p.inv <= 0 and hit(m.rect(), pr):
                if g["shield"]:
                    g["shield"] = False
                    g["mons"].remove(m)
                    burst(m.x, m.y_now() - 12, (225, 245, 255), 16)
                    float_text(p.x, p.y - 92, "Shield saved you!", (90, 170, 220))
                    play(snd_poof)
                else:
                    g["mons"].remove(m)
                    g["hearts"] -= 1
                    p.inv = 70
                    burst(p.x, p.y - 40, (255, 155, 155), 14)
                    play(snd_oops)
                    if g["hearts"] <= 0:
                        state = OVER

        for pk in g["picks"][:]:
            pk.update(eff, slow, p, g["magnet_t"] > 0)
            if pk.x < -50:
                g["picks"].remove(pk)
                continue
            if hit(pk.rect(), p.rect()):
                g["picks"].remove(pk)
                k = pk.kind
                if k == "star":
                    gain = 10 * g["mult"]
                    g["score"] += gain
                    burst(pk.x, pk.y, (255, 255, 190), 10)
                    float_text(pk.x, pk.y - 18, "+%d" % gain, (215, 165, 40))
                    play(snd_star)
                elif k == "crystal":
                    g["combo"] += 1
                    g["combo_t"] = 170
                    g["mult"] = 1 + min(2, g["combo"] // 3)
                    gain = 20 * g["mult"]
                    g["score"] += gain
                    burst(pk.x, pk.y, (150, 230, 255), 12)
                    float_text(pk.x, pk.y - 18, "+%d" % gain, (60, 170, 215))
                    play(snd_gem)
                elif k == "crown":
                    g["crowns"] += 1
                    gain = 100 * g["mult"]
                    g["score"] += gain
                    sparkle_ring(pk.x, pk.y, GOLD)
                    float_text(pk.x, pk.y - 20, "Crown! +%d" % gain, (215, 150, 40))
                    play(snd_crown)
                elif k == "heart":
                    g["hearts"] = min(5, g["hearts"] + 1)
                    sparkle_ring(pk.x, pk.y, (255, 130, 160))
                    float_text(pk.x, pk.y - 20, "Extra heart!", (230, 90, 130))
                    play(snd_power)
                elif k == "shield":
                    g["shield"] = True
                    sparkle_ring(pk.x, pk.y, (150, 225, 255))
                    float_text(pk.x, pk.y - 20, "Sparkle shield!", (70, 165, 220))
                    play(snd_power)
                elif k == "snow":
                    g["slow_t"] = 360
                    sparkle_ring(pk.x, pk.y, (215, 245, 255))
                    float_text(pk.x, pk.y - 20, "Slow snow!", (90, 175, 225))
                    play(snd_power)
                else:
                    g["magnet_t"] = 360
                    sparkle_ring(pk.x, pk.y, (240, 130, 140))
                    float_text(pk.x, pk.y - 20, "Star magnet!", (225, 95, 110))
                    play(snd_power)
                if random.random() < 0.30:
                    g["praise"] = random.choice(praises)
                    g["praise_t"] = 46

        if g["praise_t"] > 0:
            g["praise_t"] -= 1
        if g["banner_t"] > 0:
            g["banner_t"] -= 1

        if g["dist"] >= st["dist"]:
            g["score"] += 200
            g["cheer"] = 0
            state = LEVELDONE
            play(snd_win)
            if g["score"] > cfg["best"]:
                cfg["best"] = g["score"]
            save_cfg()

        if state == OVER and g["score"] > cfg["best"]:
            cfg["best"] = g["score"]
            save_cfg()

    draw_background(g["scroll"], g["stage"])

    if state in (PLAY, PAUSE, OVER, LEVELDONE, WINGAME, TIMEUP):
        for pk in g["picks"]:
            pk.draw()
        for m in g["mons"]:
            m.draw()
        for a in g["arrows"]:
            a.draw()
        if state in (LEVELDONE, WINGAME):
            g["cheer"] += 1
            draw_princess(g["player"].x, g["player"].y, cfg["dress"], 0, 1.0, 0.0, False, True, False)
        else:
            g["player"].draw(g["shield"])
        draw_particles()
        if state in (PLAY, PAUSE):
            draw_hud(g)
        if g["praise_t"] > 0 and state == PLAY:
            text_center(g["praise"], font_mid, 120, PINK)
        if g["banner_t"] > 0 and state == PLAY:
            text_center(g["banner"], font_mid, 160, (70, 165, 110))

    if state == MENU:
        overlay(120)
        text_center("Frost Runner", font_big, 74, (70, 120, 200))
        text_center("Adventure", font_mid, 138, (140, 90, 180))
        text_center("Press ENTER or CLICK to Play", font_mid, 236)
        text_center("Best score: %d" % cfg["best"], font_sm, 286, (120, 150, 190))
        text_center("Move: LEFT / RIGHT     Jump: SPACE", font_sm, 322, (110, 145, 185))
        text_center("Mode: %s   (change in Parent Settings)" % ("Easy" if cfg["easy"] else "Adventure"),
                    font_sm, 356, (140, 160, 190))
        text_center("Parents: hold P for 3 seconds for settings", font_sm, 424, (140, 160, 190))
        if hold_t > 0:
            pygame.draw.rect(screen, (200, 215, 235), (W // 2 - 100, 456, 200, 10), border_radius=5)
            pygame.draw.rect(screen, (70, 130, 200), (W // 2 - 100, 456, int(200 * hold_t / 3.0), 10),
                             border_radius=5)
        draw_mute_icon()

    elif state == PICK:
        overlay(140)
        text_center("Choose your princess", font_mid, 40, (140, 90, 180))
        for i, pp in enumerate(PRINCESS):
            cx = 150 + i * 220
            sel = (i == cfg["dress"])
            if sel:
                pygame.draw.rect(screen, (255, 245, 200), (cx - 88, 96, 176, 268), border_radius=18)
                pygame.draw.rect(screen, GOLD, (cx - 88, 96, 176, 268), 4, border_radius=18)
            else:
                pygame.draw.rect(screen, (250, 252, 255), (cx - 82, 102, 164, 256), border_radius=16)
            draw_princess(cx, 312, i, 0, 1.15)
            nm = font_mid.render(pp["name"], True, TEXTCOL if sel else (150, 168, 195))
            screen.blit(nm, (cx - nm.get_width() // 2, 322))
        text_center("LEFT / RIGHT to choose      ENTER to play", font_sm, 404)
        text_center("5 stages, monsters, crowns and power-ups await!", font_sm, 438, (140, 160, 190))
        draw_mute_icon()

    elif state == PAUSE:
        overlay(150)
        text_center("Paused", font_big, 150)
        text_center("Press ESC to keep playing", font_sm, 250)
        draw_mute_icon()

    elif state == OVER:
        overlay(155)
        text_center("Great Playing!", font_big, 96, PINK)
        text_center("You scored %d" % g["score"], font_mid, 180)
        text_center("Crowns collected: %d" % g["crowns"], font_sm, 226, (200, 150, 40))
        text_center("Best ever: %d" % cfg["best"], font_sm, 258, (120, 150, 190))
        text_center("Press ENTER to try again", font_sm, 318)
        text_center("ESC to change princess", font_sm, 350, (140, 160, 190))
        draw_mute_icon()

    elif state == LEVELDONE:
        overlay(165)
        draw_chest(W // 2, 250, g["cheer"])
        text_center("Stage Complete!", font_big, 72, (70, 165, 120))
        text_center(STAGES[g["stage"]]["name"] + "  cleared", font_mid, 140, (140, 90, 180))
        text_center("Score: %d      Crowns: %d" % (g["score"], g["crowns"]), font_sm, 306)
        if g["stage"] + 1 < len(STAGES):
            text_center("Next: " + STAGES[g["stage"] + 1]["name"], font_mid, 348, (60, 130, 200))
        text_center("Press ENTER to continue", font_sm, 402)
        if g["cheer"] % 22 == 0:
            burst(random.randint(200, W - 200), 150, random.choice([GOLD, PINK, (150, 225, 255)]), 14, 4.0)

    elif state == WINGAME:
        overlay(180)
        g["cheer"] += 1
        draw_chest(W // 2, 268, 60)
        text_center("You saved the Ice Castle!", font_big, 66, (215, 150, 40))
        text_center("Final score: %d" % g["score"], font_mid, 138)
        text_center("Crowns: %d" % g["crowns"], font_mid, 180, (200, 150, 40))
        text_center("Press ENTER to play again", font_sm, 400)
        if g["cheer"] % 14 == 0:
            burst(random.randint(120, W - 120), random.randint(90, 240),
                  random.choice([GOLD, PINK, (150, 225, 255), (150, 235, 170)]), 16, 4.4)

    elif state == PARENT:
        overlay(205)
        text_center("Parent Settings", font_big, 48, (70, 120, 200))
        lim = "No limit" if cfg["limit_min"] == 0 else "%d minutes" % cfg["limit_min"]
        text_center("Play time limit:   < %s >" % lim, font_mid, 140)
        text_center("LEFT / RIGHT to change", font_sm, 182, (140, 160, 190))
        text_center("Difficulty:  %s   (press D)" % ("Easy" if cfg["easy"] else "Adventure"), font_mid, 226)
        text_center("Sound:  %s   (press M)" % ("MUTED" if cfg["muted"] else "ON"), font_mid, 274)
        text_center("Played this session: %d min   (press R to reset)" % int(play_seconds // 60),
                    font_sm, 320, (140, 160, 190))
        text_center("Press ESC to go back", font_sm, 396)
        text_center("Settings are saved automatically", font_sm, 428, (170, 185, 205))

    elif state == TIMEUP:
        overlay(205)
        text_center("Time for a break!", font_big, 100, PINK)
        text_center("Great playing today.", font_mid, 188)
        text_center("Ask a grown-up if you want more time.", font_sm, 240, (120, 150, 190))
        text_center("Parents: hold P for 3 seconds to allow more", font_sm, 330, (140, 160, 190))
        if hold_t > 0:
            pygame.draw.rect(screen, (200, 215, 235), (W // 2 - 100, 368, 200, 10), border_radius=5)
            pygame.draw.rect(screen, (70, 130, 200), (W // 2 - 100, 368, int(200 * hold_t / 3.0), 10),
                             border_radius=5)

    pygame.display.flip()

save_cfg()
pygame.quit()
