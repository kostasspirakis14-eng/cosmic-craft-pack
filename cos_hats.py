"""Hats for the Cosmic Wardrobe (second set): placeholder textures and box models (prompt: claude-design-hats-2.md).

Head space as in cosmetics.py: the head fills 1.6..14.4 on every axis (skin overlay 1.2..14.8), the face is north.
A hood wraps the head just outside it (0.4..15.6) and leaves the face open.
"""
import math

from PIL import Image

from cos_art import BLINK, CYAN, GOLD, INK, PURPLE, cheeks, disc, eyes, pair, pulse, put, rect, tex, tiger_stripes, tx
from cosmetics import blank, box, glint, model, part, shade


def ring(n, r_in, r_out, c, alpha=255, glow=None):
    img = blank(n)
    for y in range(n):
        for x in range(n):
            d = math.hypot(x + 0.5 - n / 2, y + 0.5 - n / 2)
            if r_in <= d <= r_out:
                img.putpixel((x, y), shade(c, 1.1 - 0.25 * abs(d - (r_in + r_out) / 2) / ((r_out - r_in) / 2)) + (alpha,))
    return img


def textures():
    # hoods: the fabric, and the brow over the face (32x8: a wide strip) with a pair of sewn-on eyes
    for name, c, iris in (("axo_hood", (255, 172, 200), (120, 60, 120)), ("tiger_hood", (242, 142, 42), (110, 200, 90))):
        cloth, strip = tex(c, name, 0.05), tex(c, name + "b", 0.05, w=32, h=8)
        for img in (cloth, strip):
            for y in range(0, img.height, 4):
                for x in range((y // 4) % 2 * 2, img.width, 4):
                    put(img, [(x, y)], shade(c, 0.9))  # stitch dots
            if name == "tiger_hood":
                tiger_stripes(img)
        part(name, cloth)
        brow = []
        for closed in (False, True):
            b = strip.copy()
            eyes(b, 1, (9, 20), closed, iris)
            cheeks(b, 5, (6, 24))
            rect(b, 0, 7, 31, 7, shade(c, 0.8))  # the hem over the face
            brow.append(b)
        part(name + "_brow", brow, BLINK)
    frills = []
    for i in range(8):  # the axolotl's feathery gill fronds (hood, backpack, balloon), glowing softly in and out
        g = tex((232, 62, 132), "axg", 0.05)
        for y in range(16):
            for x in range(16):
                if (x + 2 * (y % 2)) % 4 == 0:
                    g.putpixel((x, y), (255, 120, 180, 255))
        frills.append(pulse(g, 1 + 0.12 * math.sin(i / 8 * 2 * math.pi)))
    part("axo_frills", frills, {"frametime": 3, "interpolate": True})
    ear = tex((242, 142, 42), "tge")
    rect(ear, 4, 4, 11, 13, (255, 170, 180))
    rect(ear, 0, 0, 15, 1, (44, 28, 22))
    part("tiger_round_ear", ear)  # tiger hood and tiger balloon

    # cat ears with a bell
    part("cat_band", tex((60, 40, 90), "cb", 0.05))
    part("cat_fur", tex((196, 168, 236), "cf"))
    inner = tex((196, 168, 236), "ci")
    for y in range(3, 16):
        rect(inner, 8 - (y - 1) // 3, y, 7 + (y - 1) // 3, y, (255, 170, 200))
    part("cat_ear_inner", inner)
    bell = tex(GOLD, "cbell", 0.05)
    rect(bell, 0, 10, 15, 11, shade(GOLD, 0.7))
    put(bell, [(7, 12), (8, 12), (7, 13), (8, 13)], INK)
    part("cat_bell", [bell] * 10 + [glint(bell, i / 5) for i in range(6)], 2)

    # headphones: a pastel band, glowing cups with an equaliser, glowing cat ears
    part("phones_band", tex((236, 200, 255), "pb", 0.04))
    cups = []
    for i in range(12):
        c = tex((150, 90, 220), "pc", 0.04)
        for x in range(4, 12, 2):  # equaliser bars bouncing
            h = 2 + round(3 * (0.5 + 0.5 * math.sin(i / 12 * 2 * math.pi * (1 + x % 3) + x)))
            rect(c, x, 11 - h, x, 11, CYAN)
        rect(c, 0, 0, 15, 0, shade((150, 90, 220), 1.3))
        cups.append(c)
    part("phones_cup", cups, 2)
    pe = [pulse(tex((255, 150, 220), "pe", 0.04), 0.85 + 0.2 * math.sin(i / 8 * 2 * math.pi)) for i in range(8)]
    part("phones_ear", pe, {"frametime": 3, "interpolate": True})

    # bunny ears
    part("bunny_fur", tex((248, 246, 252), "bf", 0.03))
    binn = tex((248, 246, 252), "bi", 0.03)
    rect(binn, 4, 2, 11, 15, (255, 176, 200))
    part("bunny_inner", binn)
    part("bunny_band", tex((255, 150, 200), "bb", 0.04))

    # strawberry
    berry = tex((228, 40, 64), "sb", 0.05)
    for y in range(1, 16, 4):
        for x in range((y // 4) % 2 * 2 + 1, 16, 4):
            put(berry, [(x, y)], (255, 226, 110))
            put(berry, [(x, y + 1)], (190, 30, 50))
    part("strawberry", berry)
    leaf = blank()
    for y in range(16):
        for x in range(16):
            a = math.atan2(y + 0.5 - 8, x + 0.5 - 8)
            if math.hypot(x + 0.5 - 8, y + 0.5 - 8) < 4.2 + 3.8 * abs(math.cos(a * 2.5)):
                leaf.putpixel((x, y), shade((70, 176, 60), 0.9 + 0.2 * ((x + y) % 3 == 0)) + (255,))
    part("strawberry_leaf", leaf)
    part("strawberry_stem", tex((90, 150, 60), "ss"))

    # mushroom cap: red with white spots, cream gills underneath
    cap = tex((222, 52, 52), "shc")
    for cx, cy, rr in ((4, 4, 2), (11, 6, 2.4), (6, 11, 1.6), (13, 13, 1.4), (1, 12, 1.2)):
        disc(cap, cx, cy, rr, (252, 246, 236))
    part("shroom_cap", cap)
    gl = tex((240, 226, 200), "shg", 0.03)
    for i in range(16):
        put(gl, [(i, i), (15 - i, i), (7, i), (i, 7)], (205, 185, 160))
    part("shroom_gills", gl)

    # flower crown
    vine = tex((80, 160, 70), "vn")
    for x in range(0, 16, 3):
        put(vine, [(x, 4), (x + 1, 3), (x, 11), (x + 1, 12)], (120, 210, 90))
    part("vine", vine)
    for name, petal in (("flower_pink", (255, 150, 200)), ("flower_yellow", (255, 222, 90)), ("flower_cyan", (110, 225, 245))):
        fl = tex(petal, name, 0.04)
        disc(fl, 8, 8, 3, (255, 236, 130) if name != "flower_yellow" else (255, 160, 60))
        for cx, cy in ((0, 0), (15, 0), (0, 15), (15, 15), (8, 0), (0, 8), (15, 8), (8, 15)):
            put(fl, [(cx, cy)], shade(petal, 0.8))
        part(name, [fl] * 12 + [glint(fl, i / 5, 2, 0.5) for i in range(6)], 2)

    # halo: a glowing gold ring (transparent middle), its glow breathing
    part("halo", [pulse(ring(32, 10, 15.5, (255, 232, 120)), 0.85 + 0.2 * math.sin(i / 12 * 2 * math.pi)) for i in range(12)],
         {"frametime": 3, "interpolate": True})

    # devil horns
    horn = tex((206, 30, 44), "dh", 0.04)
    rect(horn, 3, 0, 4, 15, (240, 90, 100))  # a glossy highlight
    part("devil_horn", [horn] * 10 + [glint(horn, i / 5) for i in range(6)], 2)

    # propeller beanie
    bea = blank()
    for y in range(16):
        for x in range(16):
            c = GOLD if x in (7, 8) else (PURPLE if x < 7 else CYAN)
            bea.putpixel((x, y), shade(c, 0.92 + 0.08 * ((x + y) % 3 == 0)) + (255,))
    part("beanie", bea)
    part("beanie_band", tex((60, 40, 90), "bnb", 0.05))
    part("beanie_stick", tex((200, 200, 215), "bns", 0.04))
    blades = []
    for i in range(8):  # two blades, one full turn of the pair every 8 frames (a half-turn repeats)
        p = blank(32)
        for y in range(32):
            for x in range(32):
                dx, dy = x + 0.5 - 16, y + 0.5 - 16
                d = math.hypot(dx, dy)
                ang = (math.atan2(dy, dx) - i / 8 * math.pi) % math.pi
                width = 0.45 * (1 - d / 17) + 0.12
                if 2.5 < d <= 15.5 and (ang < width or ang > math.pi - width):
                    c = [(255, 90, 120), (255, 213, 74)][int(ang > 1)]
                    p.putpixel((x, y), shade(c, 1.1 - d / 40) + (255,))
                elif d <= 2.5:
                    p.putpixel((x, y), (60, 40, 90, 255))
        blades.append(p)
    part("propeller", blades, 1)

    # rain cloud
    cl = tex((238, 242, 252), "cl", 0.04)
    rect(cl, 0, 13, 15, 15, (206, 214, 232))
    part("cloud", cl)
    cf = []  # the cloud's front face is 10x3.8 units: 32x12 frames keep the face round
    base = tex((238, 242, 252), "clf", 0.04, w=32, h=12)
    rect(base, 0, 10, 31, 11, (206, 214, 232))
    for closed in (False, True):
        f = base.copy()
        put(f, [(10, 5), (11, 6), (12, 5), (19, 5), (20, 6), (21, 5)] if closed else [(11, 4), (11, 5), (20, 4), (20, 5)], INK)
        cheeks(f, 7, (8, 22))
        put(f, [(15, 7), (16, 7), (15, 8), (16, 8)], (90, 70, 110))
        cf.append(f)
    part("cloud_face", cf, {"frames": [{"index": 0, "time": 60}, {"index": 1, "time": 30}]})  # sleepy: long blinks
    rain = []
    drops = [(1, 0), (5, 3), (9, 1), (13, 5), (3, 6), (11, 2), (7, 5), (15, 7)]
    for i in range(8):
        r = Image.new("RGBA", (16, 8), (0, 0, 0, 0))  # rain frames are 16x8 (the rain planes are 2:1)
        for x, y in drops:
            for k in range(2):
                put(r, [(x, (y + i + k) % 8)], (120, 200, 255, 220 if k else 150))
        rain.append(r)
    part("rain", rain, 2)


# ---------------- models ----------------

SIDES = ("north", "south", "east", "west", "up")


def hood(cloth, brow):
    """A hood round the head with the face open; the brow over the face carries the hood's own eyes."""
    return [box((0.4, 0.4, 0.4), (15.6, 15.8, 15.6), cloth, ("south", "east", "west", "up")),
            box((0.4, 11.6, -0.6), (15.6, 15.8, 0.4), tx(cloth, north=brow), ("north", "east", "west", "down")),
            box((0.4, 0.4, -0.2), (1.8, 11.6, 0.4), cloth, ("north", "east")),
            box((14.2, 0.4, -0.2), (15.6, 11.6, 0.4), cloth, ("north", "west"))]


def headband(tex_key, z=6.6, depth=1.6):
    """A band over the top of the head and down the sides."""
    return [box((1.0, 14.8, z), (15.0, 15.6, z + depth), tex_key)] + pair((0.4, 8.5, z), (1.0, 15.6, z + depth), tex_key)


def axolotl_hood():
    el = hood("hood", "brow")
    for y, a in ((12.5, 22.5), (10, 0), (7.5, -22.5)):
        el += pair((15.6, y - 0.6, 8.4), (19.4, y + 0.6, 9.6), "gills", rot={"origin": [15.6, y, 9], "axis": "z", "angle": a} if a else None)
    return model(el, {"hood": "axo_hood", "brow": "axo_hood_brow", "gills": "axo_frills"})


def tiger_hood():
    el = hood("hood", "brow") + pair((2.4, 15.8, 5.6), (6, 19, 7.2), tx("hood", north="ear"))
    return model(el, {"hood": "tiger_hood", "brow": "tiger_hood_brow", "ear": "tiger_round_ear"})


def ears(base_tex, inner):
    """Two pointy ears (three stacked boxes each), the inner side to the front."""
    el = []
    for a, b in (((2.4, 15.6, 6.2), (6.8, 17.4, 8.6)), ((3.0, 17.4, 6.5), (6.2, 19.0, 8.3)), ((3.8, 19.0, 6.9), (5.4, 20.2, 7.9))):
        el += pair(a, b, tx(base_tex, north=inner))
    return el


def cat_ears():
    el = headband("band") + ears("fur", "inner") + [box((7.0, 15.6, 4.6), (9.0, 17.4, 6.6), "bell")]
    return model(el, {"band": "cat_band", "fur": "cat_fur", "inner": "cat_ear_inner", "bell": "cat_bell"})


def cat_headphones():
    el = [box((2.2, 15.0, 7.0), (13.8, 16.2, 9.0), "band")]
    el += pair((0.8, 13.4, 7.0), (2.2, 15.6, 9.0), "band")
    el += pair((0.0, 10.6, 7.2), (1.2, 13.4, 8.8), "band")
    el += pair((-1.0, 5.4, 5.0), (1.2, 10.6, 11.0), tx("band", west="cup"))
    el += pair((3.4, 16.2, 7.2), (6.0, 18.0, 8.8), "ear", light=4) + pair((4.0, 18.0, 7.5), (5.4, 19.2, 8.5), "ear", light=4)
    return model(el, {"band": "phones_band", "cup": "phones_cup", "ear": "phones_ear"})


def bunny_ears():
    el = headband("band")
    el += [box((4.0, 15.6, 7.0), (6.6, 24.0, 8.2), tx("fur", north="inner"), rot={"origin": [5.3, 15.6, 7.6], "axis": "z", "angle": 22.5}),
           box((9.4, 15.6, 7.0), (12.0, 20.0, 8.2), tx("fur", north="inner")),
           box((9.4, 19.6, 7.0), (12.0, 24.0, 8.2), tx("fur", north="inner"), rot={"origin": [10.7, 19.8, 7.6], "axis": "z", "angle": -22.5})]
    return model(el, {"band": "bunny_band", "fur": "bunny_fur", "inner": "bunny_inner"})


def strawberry_hat():
    t = ("berry",)
    el = [box((1.0, 12.0, 1.0), (15.0, 17.0, 15.0), "berry", SIDES, tile=t), box((2.6, 17.0, 2.6), (13.4, 19.0, 13.4), "berry", SIDES, tile=t),
          box((4.6, 19.0, 4.6), (11.4, 19.8, 11.4), "berry", SIDES, tile=t),
          box((2.8, 19.9, 2.8), (13.2, 19.9, 13.2), "leaf", ("up", "down")),
          box((7.3, 19.8, 7.3), (8.7, 22.0, 8.7), "stem")]
    return model(el, {"berry": "strawberry", "leaf": "strawberry_leaf", "stem": "strawberry_stem"})


def mushroom_cap():
    t = ("cap",)
    el = [box((-0.4, 13.6, -0.4), (16.4, 16.0, 16.4), tx("cap", down="gills"), tile=t),
          box((1.0, 16.0, 1.0), (15.0, 18.0, 15.0), "cap", SIDES, tile=t), box((3.4, 18.0, 3.4), (12.6, 19.2, 12.6), "cap", SIDES, tile=t)]
    return model(el, {"cap": "shroom_cap", "gills": "shroom_gills"})


def flower_crown():
    el = [box((0.8, 14.0, 0.8), (15.2, 15.0, 1.4), "vine"), box((0.8, 14.0, 14.6), (15.2, 15.0, 15.2), "vine"),
          box((0.8, 14.0, 1.4), (1.4, 15.0, 14.6), "vine"), box((14.6, 14.0, 1.4), (15.2, 15.0, 14.6), "vine")]
    spots = [(3, 1.1), (8, 1.1), (13, 1.1), (1.1, 5.5), (14.9, 5.5), (1.1, 10.5), (14.9, 10.5), (5.5, 14.9), (10.5, 14.9)]
    for i, (x, z) in enumerate(spots):
        el.append(box((x - 1.3, 14.4, z - 1.3), (x + 1.3, 15.8, z + 1.3), ["pink", "yellow", "cyan"][i % 3]))
    return model(el, {"vine": "vine", "pink": "flower_pink", "yellow": "flower_yellow", "cyan": "flower_cyan"})


def halo():
    el = [box((2.8, 19.0, 2.8), (13.2, 19.0, 13.2), "halo", ("up", "down"), light=15)]
    return model(el, {"halo": "halo"})


def devil_horns():
    el = []
    for a, b in (((3.2, 14.6, 4.8), (5.6, 16.4, 7.0)), ((2.6, 16.4, 5.1), (4.8, 18.0, 6.7)),
                 ((2.4, 18.0, 5.4), (3.8, 19.4, 6.4)), ((2.6, 19.4, 5.6), (3.4, 20.4, 6.2))):
        el += pair(a, b, "horn")
    return model(el, {"horn": "devil_horn"})


def propeller_beanie():
    t = ("beanie",)
    el = [box((1.0, 11.4, 1.0), (15.0, 16.2, 15.0), "beanie", SIDES, tile=t), box((0.6, 11.0, 0.6), (15.4, 12.6, 15.4), "band"),
          box((3.0, 16.2, 3.0), (13.0, 17.0, 13.0), "beanie", SIDES, tile=t), box((7.0, 17.0, 7.0), (9.0, 17.8, 9.0), "band"),
          box((7.5, 17.8, 7.5), (8.5, 19.8, 8.5), "stick"), box((7.2, 19.8, 7.2), (8.8, 20.6, 8.8), "band"),
          box((1.6, 20.2, 1.6), (14.4, 20.2, 14.4), "propeller", ("up", "down"))]
    return model(el, {"beanie": "beanie", "band": "beanie_band", "stick": "beanie_stick", "propeller": "propeller"})


def rain_cloud():
    t = ("cloud",)
    el = [box((3, 18.2, 4), (13, 22, 12), tx("cloud", north="face"), tile=t),
          box((4.2, 22, 5), (8.6, 23.2, 10), "cloud", tile=t), box((8.2, 22, 6), (11.8, 22.8, 11), "cloud", tile=t),
          box((1.8, 18.8, 5.5), (3, 21.4, 10.5), "cloud", tile=t), box((13, 19, 5), (14.2, 21.4, 10), "cloud", tile=t),
          box((4, 17.8, 5), (12, 18.2, 11), "cloud", tile=t),
          box((5, 15, 8), (11, 18, 8), "rain", ("north", "south")), box((8, 15, 5), (8, 18, 11), "rain", ("east", "west"))]
    return model(el, {"cloud": "cloud", "face": "cloud_face", "rain": "rain"})


MODELS = {"axolotl_hood": axolotl_hood, "tiger_hood": tiger_hood, "cat_ears": cat_ears, "cat_headphones": cat_headphones,
          "bunny_ears": bunny_ears, "strawberry_hat": strawberry_hat, "mushroom_cap": mushroom_cap, "flower_crown": flower_crown,
          "halo": halo, "devil_horns": devil_horns, "propeller_beanie": propeller_beanie, "rain_cloud": rain_cloud}
