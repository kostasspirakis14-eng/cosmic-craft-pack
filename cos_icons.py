"""Flat 2D icons (16x16) for the Cosmic Wardrobe menu, and the three elytra-style wings.

Icons: item model cosmic:icon/<id> (parent item/generated, texture cosmic:item/icon/<id>); src/cosmetics/icon_<id>.png
from Claude Design (claude-design-icons.md) replaces the placeholder, with its .mcmeta if animated. Every cosmetic icon
also gets <id>_locked, a dark silhouette made from the final art.
Wings: the vanilla elytra "wings" equipment layer, textures/entity/equipment/wings/<wing>.png (64x32, elytra layout;
src/cosmetics/<wing>.png replaces the placeholder). Equipment assets: cosmic:<wing> (wings only, for an elytra) and
cosmic:<wing>__<material> (a vanilla chestplate's own layers + the wings) so the real armour still shows.
"""
import json
import math

from PIL import Image

from cos_art import CYAN, GOLD, INK, PURPLE, WHITE, disc, outline, put, rect, silhouette, star_shape
from cosmetics import blank, glint, shade

COSMETIC_ICONS = ["angel_wings", "bat_wings", "butterfly_wings", "bubble_trail", "paw_trail", "heart_trail", "sakura_trail",
                  "music_trail", "rainbow_trail", "cat_grave", "flower_grave", "planet_grave", "cute_ghost", "heart_burst",
                  "star_poof", "falling_star", "rainbow_arrival", "confetti_pop", "name_cosmic", "name_sunset", "name_mint",
                  "name_gold", "name_rainbow"]
UI_ICONS = ["tab_hats", "tab_pets", "tab_back", "tab_balloons", "tab_trails", "tab_effects", "tab_shop", "tab_sets",
            "tab_outfits", "btn_prev", "btn_next", "btn_filter", "btn_sort", "btn_coins", "btn_takeoff", "btn_gift", "btn_name",
            "btn_info", "btn_outfit"]
WINGS = ["angel_wings", "bat_wings", "butterfly_wings"]
# vanilla equipment assets with humanoid layers that a chestplate can use (26.3 jar; turtle_scute is helmet-only)
MATERIALS = ["leather", "chainmail", "iron", "gold", "diamond", "netherite", "copper"]

PAL = {"P": PURPLE, "p": (110, 50, 170), "L": (214, 176, 255), "C": CYAN, "c": (20, 140, 170), "l": (176, 240, 250),
       "G": GOLD, "g": (200, 148, 30), "Y": (255, 246, 184), "W": WHITE, "w": (206, 210, 226), "S": (156, 156, 172),
       "s": (104, 104, 120), "K": INK, "R": (236, 64, 100), "k": (255, 152, 200), "O": (255, 150, 40), "N": (96, 196, 84),
       "n": (52, 132, 62), "B": (80, 120, 236)}


# ---------------- drawing ----------------

def sprite(rows, img=None, at=None, flip=False, dy=0):
    """Paints string art (one char per pixel, PAL colours) centred on a 16x16 icon (or at a given top-left)."""
    img = img or blank()
    h, w = len(rows), max(len(r) for r in rows)
    x0, y0 = at if at else ((16 - w) // 2, (16 - h) // 2)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row[::-1] if flip else row):
            if ch in PAL:
                put(img, [(x0 + x + (w - len(row) if flip else 0), y0 + y + dy)], PAL[ch])
    return img


def pair_wings(rows, dy=0):
    img = blank()
    w = len(rows[0])
    sprite(rows, img, (8 - w, (16 - len(rows)) // 2 + dy))
    sprite(rows, img, (8, (16 - len(rows)) // 2 + dy), flip=True)
    return img


def heart(img, x, y, c, small=False):
    rows = [".#.#.", "#####", "#####", ".###.", "..#.."] if small else [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."]
    for j, r in enumerate(rows):
        put(img, [(x + i, y + j) for i, ch in enumerate(r) if ch == "#"], c)
    put(img, [(x + 1, y + 1)], (255, 220, 235))
    return img


def sparkle(img, x, y, c, big=True):
    put(img, [(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], c)
    if big:
        put(img, [(x - 2, y), (x + 2, y), (x, y - 2), (x, y + 2)], shade(c, 0.85))
    put(img, [(x, y)], WHITE)
    return img


def gradient(rows, colours, t):
    """String art whose '#' pixels take a diagonal colour gradient, scrolled by t (0..1) for a seamless shimmer."""
    img = blank()
    h, w = len(rows), len(rows[0])
    x0, y0 = (16 - w) // 2, (16 - h) // 2
    n = len(colours)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "#":
                u = ((x + y) / (w + h) + t) % 1 * n
                a, b = colours[int(u) % n], colours[(int(u) + 1) % n]
                k = u - int(u)
                put(img, [(x0 + x, y0 + y)], tuple(round(a[i] + (b[i] - a[i]) * k) for i in range(3)))
    return img


def tombstone(img, carve):
    sprite(["...SSSSSS...", "..SSSSSSSS..", ".SSSSSSSSSS.", ".SSSSSSSSSS.", ".SSSSSSSSSS.", ".SSSSSSSSSS.", ".SSSSSSSSSS.",
            ".SSSSSSSSSS.", ".SSSSSSSSSS.", "NNNNNNNNNNNN", "nNNNNNNNNNNn"], img, (2, 3))
    carve(img)
    return img


A_ROWS = ["...####...", "..######..", ".###..###.", ".##....##.", "###....###", "##########", "##########", "###....###",
          "###....###", "###....###"]
NAMES = {"name_cosmic": [PURPLE, (120, 140, 255), CYAN, (120, 140, 255)],
         "name_sunset": [(255, 213, 74), (255, 140, 60), (255, 90, 150), (168, 85, 247), (255, 90, 150), (255, 140, 60)],
         "name_mint": [(180, 255, 220), (60, 220, 170), (30, 170, 160), (60, 220, 170)],
         "name_gold": [(255, 246, 184), GOLD, (200, 140, 30), GOLD],
         "name_rainbow": [(236, 64, 100), (255, 150, 40), (255, 222, 70), (96, 196, 84), CYAN, (80, 120, 236), PURPLE]}
RAINBOW = [(236, 64, 100), (255, 150, 40), (255, 222, 70), (96, 196, 84), CYAN, PURPLE]


def bob(t, phase=0.0):
    return round(math.sin(2 * math.pi * (t + phase)))


def draw(name, t):
    """One frame (t = 0..1 through the loop) of an icon, before its outline."""
    img = blank()
    if name == "angel_wings":
        return pair_wings(["WW.....", "WWWW...", "wWWWWW.", ".wWWWWW", "..wWWWW", "..wwWWW", "...wwWW", ".....wG"], -1 if t >= 0.5 else 0)
    if name == "bat_wings":
        return pair_wings(["p......", "pP.....", "pPP...p", "pPPPPPP", "PPPPPPP", "P.PP.PP", "..P...P"], -1 if t >= 0.5 else 0)
    if name == "butterfly_wings":
        img = pair_wings(["CCCC...", "CCCCCC.", "CPPCCCC", "CPPCCCC", "CCCCCC.", ".CCCC..", "..kkkk.", ".kkWkkk", ".kkkkk.", "..kkk.."],
                         bob(t))
        return rect(img, 7, 3 + bob(t), 8, 12 + bob(t), INK)
    if name == "bubble_trail":
        for (cx, cy, r), ph in (((5, 11, 3.2), 0), ((10.5, 6.5, 2.4), 0.33), ((13, 2.5, 1.5), 0.66)):
            cy += bob(t, ph)
            disc(img, cx, cy, r, (170, 240, 250, 110))
            for y in range(16):
                for x in range(16):
                    if r - 1 < math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= r:
                        put(img, [(x, y)], CYAN)
            put(img, [(round(cx - r / 2), round(cy - r / 2))], WHITE)
        return img
    if name == "paw_trail":
        PAL["x"] = shade(PURPLE, 0.75 + 0.45 * (t < 0.5))   # the two prints light up in turn
        PAL["y"] = shade(PURPLE, 1.2 - 0.45 * (t < 0.5))
        sprite([".x.x.", "x...x", ".xxx.", "xxxxx", ".xxx."], img, (2, 9))
        return sprite([".y.y.", "y...y", ".yyy.", "yyyyy", ".yyy."], img, (9, 2))
    if name == "heart_trail":
        heart(img, 1, 9 + bob(t), (236, 64, 100))
        heart(img, 9, 5 + bob(t, 0.33), (255, 120, 170), True)
        return heart(img, 11, 0 + max(0, bob(t, 0.66)), (255, 170, 210), True)
    if name == "sakura_trail":
        for a in range(5):
            ang = a / 5 * 2 * math.pi - math.pi / 2
            disc(img, 6 + 2.6 * math.cos(ang), 9.5 + bob(t) + 2.6 * math.sin(ang), 1.9, (255, 176, 206))
        disc(img, 6, 9.5 + bob(t), 1.1, (255, 230, 120))
        disc(img, 12.5, 4 + bob(t, 0.4), 1.4, (255, 150, 196))
        return disc(img, 10, 1.8 + bob(t, 0.7), 1.0, (255, 196, 220))
    if name == "music_trail":
        sprite(["..PP", "..PP", "..P.", "..P.", "PPP.", "PPP."], img, (2, 7 + bob(t)))
        return sprite(["..CCCCC", "..CCCCC", "..C...C", "..C...C", "CCC.CCC", "CCC.CCC"], img, (7, 2 + bob(t, 0.5)))
    if name == "rainbow_trail":
        for i in range(6):
            c = RAINBOW[(i + int(t * 6)) % 6]
            put(img, [(x, 14 - x + i - 3) for x in range(1, 12) if 0 <= 14 - x + i - 3 < 16], c)
        return sparkle(img, 12, 3, GOLD)
    if name == "cat_grave":
        sprite([".SS......SS.", ".SSS....SSS.", ".SSSSSSSSSS.", ".SSSSSSSSSS.", ".SSsSSSSsSS.", ".SSsSSSSsSS.",
                ".SSSSkkSSSS.", ".SSSSSSSSSS.", ".SSSSSSSSSS.", ".SSSSSSSSSS.", "NNNNNNNNNNNN", "nNNNNNNNNNNn"], img, (2, 2))
        return img
    if name == "flower_grave":
        tombstone(img, lambda i: heart(i, 5, 6, (200, 110, 150), True))
        for x, c in ((3, (255, 150, 200)), (12, (255, 222, 90))):
            put(img, [(x, 11), (x - 1, 12), (x + 1, 12), (x, 13)], c)
            put(img, [(x, 12)], (255, 246, 184))
        return img
    if name == "planet_grave":
        def planet(i):
            disc(i, 8, 8.5, 2.2, PURPLE)
            put(i, [(4, 9), (5, 9), (11, 9), (12, 9), (6, 8), (10, 8)], GOLD)
        return tombstone(img, planet)
    if name == "cute_ghost":
        return sprite(["...WWWWW...", "..WWWWWWW..", ".WWWWWWWWW.", ".WWKWWWKWW.", ".WWKWWWKWW.", "WWkWWWWWkWW", "WWWWWKWWWWW",
                       "WWWWWWWWWWW", "WWWWWWWWWWW", "WWW.WWW.WWW", ".W...W...W."], img, (2, 2 + bob(t)))
    if name == "heart_burst":
        big = t < 0.5
        heart(img, 4, 5, (236, 64, 100) if big else (255, 110, 150))
        for x, y in ((2, 3), (13, 3), (1, 10), (14, 10), (7, 1)):
            put(img, [(x, y)] + ([(x, y - 1)] if big else []), GOLD)
        return img
    if name == "star_poof":
        for cx, cy, r in ((5, 11, 3), (9, 10, 3.4), (12, 12, 2.4)):
            disc(img, cx, cy, r, (236, 236, 250))
        for (x, y), ph in (((3, 4), 0), ((8, 2), 0.33), ((13, 5), 0.66)):
            if math.cos(2 * math.pi * (t - ph)) > -0.3:
                sparkle(img, x, y, GOLD, math.cos(2 * math.pi * (t - ph)) > 0.5)
        return img
    if name == "falling_star":
        for i in range(6):
            put(img, [(1 + i, 14 - i), (2 + i, 14 - i)], [PURPLE, PURPLE, CYAN, CYAN, (200, 240, 255), WHITE][i])
        k = 1 + 0.15 * math.sin(2 * math.pi * t)
        for x, y, d in star_shape(16, 5, 2.2, 10.5, 5.5):
            put(img, [(x, y)], shade((255, 222, 90), k * (1.2 - 0.4 * d)))
        return img
    if name == "rainbow_arrival":
        for y in range(16):
            for x in range(16):
                d = math.hypot(x + 0.5 - 8, y + 0.5 - 12)
                if 2 <= d < 8 and y < 12:
                    put(img, [(x, y)], RAINBOW[(int(8 - d) + int(t * 6)) % 6])
        for cx in (2.5, 13.5):
            disc(img, cx, 12, 2, WHITE)
        return img
    if name == "confetti_pop":
        sprite(["......G", ".....GP", "....GPG", "...GPGG", "..GPGG.", ".GPGG..", "GPGG...", "GGG...."], img, (1, 7))
        for i, (x, y) in enumerate(((9, 5), (12, 2), (14, 6), (11, 8), (7, 2), (13, 10), (10, 1))):
            dy = int(t * 4 + i) % 4 - 1
            put(img, [(x, y + dy)], [CYAN, (255, 120, 170), GOLD, (96, 196, 84)][i % 4])
        return img
    if name in NAMES:
        return gradient(A_ROWS, NAMES[name], t)
    if name == "tab_hats":
        return sprite(["..pPPPPPPp..", "..pPPLPPPp..", "..pPPLPPPp..", "..pPPPPPPp..", "..CCCCCCCC..", "..CCCCCCCC..",
                       "..pPPPPPPp..", "pppppppppppp", "pPPPPPPPPPPp"])
    if name == "tab_pets":
        return sprite(["...PP...PP...", "..PPPP.PPPP..", "..PPPP.PPPP..", "...PP...PP...", "PP.........PP", "PPP.PPPPP.PPP",
                       "PP.PPPPPPP.PP", "..PPPPPPPPP..", ".PPPPPPPPPPP.", ".PPPPPPPPPPP.", "..PPPP.PPPP.."])
    if name == "tab_back":
        sprite([".GG....GG.", "PPPP..PPPP", "PLPP..PLPP", "PLPPssPLPP", "PLPPCCPLPP", "CCCCCCCCCC", "PPPPCCPPPP", "PPPPssPPPP",
                "PPPP..PPPP", ".ss....ss."], img, (3, 1))
        put(img, [(4, 11), (5, 11), (11, 11), (12, 11)], (255, 150, 40))
        if t >= 0.5:
            put(img, [(4, 12), (5, 12), (11, 12), (12, 12)], (255, 222, 90))
            put(img, [(4, 13), (12, 13)], (255, 150, 40))
        else:
            put(img, [(5, 12), (11, 12)], (255, 222, 90))
        return img
    if name == "tab_balloons":
        dy = bob(t)
        for y in range(16):
            for x in range(16):
                if ((x + 0.5 - 8) / 4.6) ** 2 + ((y + 0.5 - 6 - dy) / 5.4) ** 2 <= 1:
                    put(img, [(x, y)], (255, 120, 180))
        put(img, [(6, 3 + dy), (6, 4 + dy), (5, 5 + dy)], (255, 214, 236))
        put(img, [(7, 11 + dy), (8, 11 + dy), (8, 12 + dy), (7, 13 + dy), (8, 14 + dy), (7, 15 + dy)], (220, 90, 150))
        return img
    if name == "tab_trails":
        for i in range(7):
            put(img, [(2 + i, 13 - i // 2 - (i * i) // 8)], shade(CYAN, 0.6 + i * 0.07))
        sparkle(img, 11, 5, GOLD)
        return sparkle(img, 4, 4, (214, 176, 255), False)
    if name == "tab_effects":
        n = 3 if t < 0.5 else 5
        for i in range(8):
            a = i / 8 * 2 * math.pi
            put(img, [(round(7.5 + r * math.cos(a)), round(7.5 + r * math.sin(a))) for r in range(2, n + 1)],
                [PURPLE, CYAN, GOLD, (255, 120, 170)][i % 4])
        return sparkle(img, 8, 8, WHITE, False)
    if name == "tab_shop":
        img = sprite(["....pppp....", "...p....p...", "...p....p...", ".PPPPPPPPPP.", ".PPPPPPPPPP.", ".PPPPGPPPPP.", ".PPPGGGPPPP.",
                      ".PPGGGGGPPP.", ".PPPGGGPPPP.", ".PPPPGPPPPP.", ".PPPPPPPPPP.", ".pppppppppp."])
        return glint(img, t * 2 - 0.5) if 0.25 <= t < 0.75 else img
    if name == "tab_sets":
        for i, (c, d) in enumerate(((PURPLE, (110, 50, 170)), (CYAN, (20, 140, 170)), (GOLD, (200, 148, 30)))):
            x0, y0 = 1 + 3 * i, 1 + 3 * i
            rect(img, x0, y0, x0 + 7, y0 + 7, d)
            rect(img, x0 + 1, y0 + 1, x0 + 6, y0 + 6, c)
        return img
    if name == "tab_outfits":
        return sprite(["......ww......", ".....w..w.....", "........w.....", ".......w......", "......ww......", "....ww..ww....",
                       "..ww......ww..", "ww..........ww", "wwwwwwwwwwwwww"])
    if name in ("btn_prev", "btn_next"):
        return sprite(["....C....", "...CC....", "..CCC....", ".CCCCCCCC", "CCCCCCCCC", ".CCCCCCCC", "..CCC....", "...CC....", "....C...."],
                      flip=name == "btn_next")
    if name == "btn_filter":
        return sprite(["CCCCCCCCCCCC", "lCCCCCCCCCCc", ".CCCCCCCCCC.", "..CCCCCCCC..", "...CCCCCC...", "....CCCC....", "....CCCC....",
                       "....CCCC....", "....CCCc...."])
    if name == "btn_sort":
        return sprite(["..C.........", ".CCC.....P..", "CCCCC....P..", "..C......P..", "..C......P..", "..C......P..", "..C......P..",
                       "..C....PPPPP", "..C.....PPP.", ".........P.."])
    if name == "btn_coins":
        disc(img, 8, 8, 6.2, (200, 148, 30))
        disc(img, 8, 8, 5, GOLD)
        for x, y, d in star_shape(16, 3.2, 1.4, 8, 8.2):
            put(img, [(x, y)], (255, 246, 184))
        return glint(img, t * 2 - 0.5) if 0.25 <= t < 0.75 else img
    if name == "btn_takeoff":
        disc(img, 8, 8, 6.5, (236, 64, 100))
        for i in range(-3, 3):
            put(img, [(8 + i, 8 + i), (7 + i, 8 + i), (8 + i, 7 - i), (7 + i, 7 - i)], WHITE)
        return img
    if name == "btn_gift":
        return sprite(["..GG....GG..", ".G..G..G..G.", "..GGGGGGGG..", "PPPPPGGPPPPP", "PPPPPGGPPPPP", "GGGGGGGGGGGG", ".PPPPGGPPPP.",
                       ".PPPPGGPPPP.", ".PPPPGGPPPP.", ".PPPPGGPPPP.", ".pppppppppp."])
    if name == "btn_name":
        return sprite(["...CCCCCCCCCC", "..CCCCCCCCCCC", ".CC.CCCCCCCCC", "CC...CWWWWWCC", ".CC.CCCCCCCCC", "..CCCCWWWCCCC", "...CCCCCCCCCC"])
    if name == "btn_info":
        disc(img, 8, 8, 6.5, CYAN)
        return put(img, [(7, 4), (8, 4)] + [(x, y) for y in range(6, 12) for x in (7, 8)] + [(6, 6), (6, 11), (9, 11)], WHITE)
    if name == "btn_outfit":
        return sprite(["..PPPP..PPPP..", ".PPPPPPPPPPPP.", "PPPPPPPPPPPPPP", "PPP.PPPPPP.PPP", "....PPPPPP....", "....PPGGPP....",
                       "....PGGGGP....", "....PPGGPP....", "....PPPPPP....", "....PPPPPP...."])
    raise KeyError(name)


FRAMES = {"angel_wings": (4, 5), "bat_wings": (4, 4), "butterfly_wings": (8, 3), "bubble_trail": (12, 3), "paw_trail": (8, 3),
          "heart_trail": (12, 3), "sakura_trail": (12, 3), "music_trail": (8, 4), "rainbow_trail": (6, 3), "cute_ghost": (8, 4),
          "heart_burst": (4, 5), "star_poof": (12, 2), "falling_star": (8, 2), "rainbow_arrival": (6, 4), "confetti_pop": (8, 2),
          "tab_back": (4, 2), "tab_balloons": (8, 4), "tab_effects": (4, 5), "tab_shop": (16, 2), "btn_coins": (16, 2),
          **{n: (12, 2) for n in NAMES}}  # frames, frametime


def icon_frames(name):
    n, _ = FRAMES.get(name, (1, 1))
    return [outline(draw(name, i / n)) for i in range(n)]


# ---------------- wings (elytra layout) ----------------

def wing_back(kind):
    """The wing's outer face, 10x20: x=0 is the edge by the spine, y=0 the shoulder."""
    img = Image.new("RGBA", (10, 20), (0, 0, 0, 0))
    for y in range(20):
        for x in range(10):
            top = max(0, (x - 5) * 1.2)
            if kind == "angel_wings":
                bottom = 13 + x * 0.65 - (x % 2) * 1.5
                if top <= y <= bottom:
                    feather = (y + (x // 2) * 2) % 5 == 0
                    c = (232, 236, 248) if feather else (252, 252, 255)
                    if y > bottom - 2:
                        c = (214, 222, 240)
                    if x == 0:
                        c = (255, 226, 130)
                    img.putpixel((x, y), c + (255,))
            elif kind == "bat_wings":
                bottom = 11 + 8 * x / 9 - 3 * abs(math.sin(x * math.pi / 3.2))
                if top <= y <= bottom:
                    bone = y <= top + 0.8 or abs(y - x * 1.9) < 0.6 or abs(y - x * 0.9) < 0.5
                    img.putpixel((x, y), ((48, 26, 66, 255) if bone else (110, 52, 150, 235)))
            else:  # butterfly: a big upper lobe, a smaller lower one
                upper = y <= 11 and not (y < 2 and x > 6) and not (y > 9 and x > 7)
                lower = 11 <= y <= 19 and x <= 8 - abs(y - 15) * 0.6
                if upper or lower:
                    c = CYAN if upper else (255, 150, 200)
                    d = min(x, 9 - x, y, 19 - y)
                    if (upper and (x >= 8 or y <= 0)) or (lower and x >= 7 - abs(y - 15) * 0.6):
                        c = PURPLE
                    if (x, y) in ((4, 4), (5, 5), (6, 3), (3, 14), (4, 16)):
                        c = WHITE
                    img.putpixel((x, y), shade(c, 1.0 if d else 0.9) + (255,))
    return img


def wing_texture(kind):
    back = wing_back(kind)
    tex = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    tex.paste(back, (36, 2))                                     # outer face (seen from behind)
    tex.paste(back.transpose(Image.FLIP_LEFT_RIGHT), (24, 2))    # inner face (towards the player's back)
    for y in range(20):
        inner, outer = back.getpixel((0, y)), back.getpixel((9, y))
        for x in (34, 35):
            tex.putpixel((x, 2 + y), inner)                      # the edge by the spine
        for x in (22, 23):
            tex.putpixel((x, 2 + y), outer)                      # the outer edge
    for x in range(10):
        for y in (0, 1):
            tex.putpixel((24 + x, y), back.getpixel((9 - x, 0)))  # top
            tex.putpixel((34 + x, y), back.getpixel((x, 19)))     # bottom
    return tex


def humanoid(material):
    if material == "leather":
        return [{"dyeable": {"color_when_undyed": -6265536}, "texture": "minecraft:leather"}, {"texture": "minecraft:leather_overlay"}]
    return [{"texture": f"minecraft:{material}"}]


def write(out, src):
    tex = out / "assets/cosmic/textures/item/icon"
    models, items = out / "assets/cosmic/models/icon", out / "assets/cosmic/items/icon"
    for d in (tex, models, items):
        d.mkdir(parents=True, exist_ok=True)

    def save(name, frames, frametime):
        w = frames[0].width
        strip = Image.new("RGBA", (w, w * len(frames)))
        for i, f in enumerate(frames):
            strip.paste(f, (0, w * i))
        strip.save(tex / f"{name}.png")
        if len(frames) > 1:
            (tex / f"{name}.png.mcmeta").write_text(json.dumps({"animation": {"frametime": frametime}}), encoding="utf-8")

    names = []
    for name in COSMETIC_ICONS + UI_ICONS:
        art = src / "cosmetics" / f"icon_{name}.png"
        if art.exists():  # Claude Design art wins, with its .mcmeta
            Image.open(art).convert("RGBA").save(tex / f"{name}.png")
            meta = art.with_suffix(".png.mcmeta")
            if meta.exists():
                (tex / f"{name}.png.mcmeta").write_text(meta.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            save(name, icon_frames(name), FRAMES.get(name, (1, 1))[1])
        names.append(name)
        if name in COSMETIC_ICONS:
            silhouette(Image.open(tex / f"{name}.png")).save(tex / f"{name}_locked.png")
            if (tex / f"{name}.png.mcmeta").exists():
                (tex / f"{name}_locked.png.mcmeta").write_text((tex / f"{name}.png.mcmeta").read_text(encoding="utf-8"), encoding="utf-8")
            names.append(name + "_locked")
    for name in names:
        (models / f"{name}.json").write_text(json.dumps({"parent": "minecraft:item/generated",
                                                          "textures": {"layer0": f"cosmic:item/icon/{name}"}}), encoding="utf-8")
        (items / f"{name}.json").write_text(json.dumps({"model": {"type": "minecraft:model", "model": f"cosmic:icon/{name}"}}),
                                            encoding="utf-8")

    wings_tex = out / "assets/cosmic/textures/entity/equipment/wings"
    equip = out / "assets/cosmic/equipment"
    wings_tex.mkdir(parents=True, exist_ok=True)
    equip.mkdir(parents=True, exist_ok=True)
    for wing in WINGS:
        art = src / "cosmetics" / f"{wing}.png"
        (Image.open(art).convert("RGBA") if art.exists() else wing_texture(wing)).save(wings_tex / f"{wing}.png")
        layer = [{"texture": f"cosmic:{wing}"}]
        (equip / f"{wing}.json").write_text(json.dumps({"layers": {"wings": layer}}, indent=1), encoding="utf-8")
        for m in MATERIALS:
            asset = {"layers": {"humanoid": humanoid(m), "wings": layer}}
            if m not in ("leather", "chainmail"):  # the vanilla darker trim palette on its own metal
                asset["trim_overrides"] = [{"palette": f"minecraft:trim/{m}_darker", "when": {"material": f"minecraft:{m}"}}]
            (equip / f"{wing}__{m}.json").write_text(json.dumps(asset, indent=1), encoding="utf-8")
    return len(names)
