"""Back displays, balloons, effect models and pet accessories for the Cosmic Wardrobe, plus the `locked` silhouette texture.
Prompts: claude-design-back-balloons.md, claude-design-effects.md.

Back items: the pack's north face is at z=8 (it touches the player's back), centred x=8, y=8 at the middle of the back.
Balloons: the balloon centred on 8,8,8 (about 10 units), a knot at the bottom. Accessories (bow, medal): small, centred
on 8,8,8, facing north. paw_print lies flat (y 0..0.2); cat_grave stands on y=0. gift_box + gift_lid share one space.
"""
import math

from cos_art import (BLINK, CYAN, GOLD, INK, PURPLE, WHITE, cheeks, disc, face, mouth, pair, pulse, put, rect, speckle,
                     star_shape, tex, tiger_stripes, twinkle, tx)
from cosmetics import blank, box, glint, model, part, shade


def textures():
    # the locked silhouette: purple-black, a faint shimmer drifting across now and then
    lk = tex((34, 24, 50), "lk", 0.05)
    part("locked", [lk] * 16 + [glint(lk, i / 7, 3, 0.18) for i in range(8)], 2)

    # JETPACK
    metal = tex((150, 154, 182), "jm", 0.05)
    rect(metal, 0, 0, 15, 0, (190, 194, 220))
    put(metal, [(2, 2), (13, 2), (2, 13), (13, 13)], (90, 92, 120))  # rivets
    part("jet_metal", metal)
    tank = tex(PURPLE, "jt", 0.04)
    rect(tank, 0, 6, 15, 8, CYAN)
    rect(tank, 2, 0, 3, 15, shade(PURPLE, 1.25))  # a shine down the tank
    part("jet_tank", [tank] * 10 + [glint(tank, i / 5) for i in range(6)], 2)
    part("jet_cone", tex(GOLD, "jc", 0.05))
    flames = []
    for i in range(8):
        f = blank()
        for y in range(16):
            for x in range(16):
                w = 7.5 * (1 - y / 18) + 0.8 * math.sin(y * 0.9 + i / 8 * 2 * math.pi)
                d = abs(x + 0.5 - 8)
                if d <= w:
                    k = d / max(w, 0.1)
                    c = (255, 255, 230) if k < 0.3 and y < 9 else (CYAN if k < 0.65 else PURPLE)
                    f.putpixel((x, y), c + (235 if y < 12 else 150,))
        flames.append(f)
    part("jet_flame", flames, 1)
    part("jet_light", [pulse(tex(CYAN, "jl", 0.03), 0.8 + 0.25 * math.sin(i / 8 * 2 * math.pi)) for i in range(8)],
         {"frametime": 3, "interpolate": True})

    # AXOLOTL BACKPACK (a plush): soft fabric with stitches, and a stitched face
    pink = (255, 178, 206)
    fab = tex(pink, "apf", 0.04)
    for i in range(0, 16, 2):
        put(fab, [(i, 0), (0, i), (i, 15), (15, i)], shade(pink, 0.8))  # stitched seams at the edges
    part("axo_pack", fab)
    pf = []
    for closed in (False, True):
        f = fab.copy()
        for x in (3, 10):
            if closed:
                put(f, [(x, 7), (x + 1, 8), (x + 2, 7)], INK)
            else:
                disc(f, x + 1.5, 7.5, 1.6, INK)
                put(f, [(x + 1, 6)], WHITE)
        cheeks(f, 10)
        mouth(f, 11, "w")
        pf.append(f)
    part("axo_pack_face", pf, BLINK)

    # BALLOONS: glossy rubber with a white shine, a face, a knot
    for name, c in (("axo_balloon", (255, 160, 196)), ("tiger_balloon", (246, 146, 46))):
        g = tex(c, name, 0.03)
        if name == "tiger_balloon":
            tiger_stripes(g)
        put(g, [(2, 2), (3, 2), (2, 3), (3, 3), (4, 2), (2, 4)], (255, 255, 255))
        part(name, g)
        iris = (120, 60, 120) if name == "axo_balloon" else (110, 200, 90)
        fc = face(c, name + "f", mouth_kind="smile" if name == "axo_balloon" else "w", iris=iris)
        for f in fc:
            put(f, [(2, 2), (3, 2), (2, 3)], (255, 255, 255))
        part(name + "_face", fc, BLINK)
    part("balloon_knot", tex((236, 120, 170), "bk", 0.05))

    # CUTE GHOST: soft white, a little see-through
    gh = tex((244, 244, 255), "gh", 0.03, alpha=215)
    part("ghost", gh)
    gf = face((244, 244, 255), "ghf", mouth_kind="o", iris=(150, 120, 255))
    for f in gf:
        px = f.load()
        for y in range(16):
            for x in range(16):
                r, g, b, a = px[x, y]
                if r > 200 and g > 200 and b > 230:
                    px[x, y] = (r, g, b, 215)
    part("ghost_face", gf, BLINK)

    # FALLING STAR: bright gold with a white glint
    fs = tex((255, 220, 90), "fs", 0.04)
    part("falling_star", [pulse(fs, 1 + 0.1 * math.sin(i / 6 * 2 * math.pi)) for i in range(6)] + [glint(fs, i / 5) for i in range(6)], 2)

    # PAW PRINT (flat, transparent): a pink-purple print that sparkles
    paw = blank()
    disc(paw, 8, 10.5, 3.6, (214, 130, 255))
    for cx, cy in ((3.5, 6), (6.5, 3.5), (9.5, 3.5), (12.5, 6)):
        disc(paw, cx, cy, 1.7, (214, 130, 255))
    part("paw_print", [paw] * 6 + [glint(paw, i / 5, 2.4, 0.6) for i in range(6)], 2)

    # COSMIC EGG: a dark speckled shell, two crack stages with light inside
    shell = twinkle((62, 40, 110), "egg", 10, 9, bright=(200, 240, 255))
    part("egg_shell", shell, 3)
    crack1 = [(4, 0), (5, 1), (5, 2), (6, 3), (5, 4), (6, 5), (7, 6)]
    crack2 = crack1 + [(8, 6), (9, 5), (10, 6), (11, 7), (12, 6), (13, 7), (14, 8), (2, 9), (3, 10), (3, 11), (4, 12), (5, 12), (6, 13)]
    for name, cr in (("egg_crack_1", crack1), ("egg_crack_2", crack2)):
        frames = []
        for i, f in enumerate(shell):
            f = f.copy()
            put(f, cr, shade(CYAN, 0.85 + 0.3 * math.sin(i / 10 * 2 * math.pi)))
            frames.append(f)
        part(name, frames, 3)
    part("egg_glow", [pulse(tex((190, 250, 255), "eg", 0.03), 0.85 + 0.15 * math.sin(i / 8 * 2 * math.pi)) for i in range(8)],
         {"frametime": 2, "interpolate": True})

    # GIFT: purple paper with gold stars, a gold ribbon with a glint
    paper = tex(PURPLE, "gp", 0.04)
    for x, y in ((2, 3), (11, 2), (6, 8), (13, 11), (3, 13), (9, 14)):
        put(paper, [(x, y), (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)], GOLD)
    part("gift_paper", paper)
    rib = tex(GOLD, "gr", 0.04)
    rect(rib, 0, 0, 0, 15, shade(GOLD, 0.75))
    rect(rib, 15, 0, 15, 15, shade(GOLD, 0.75))
    part("gift_ribbon", [rib] * 10 + [glint(rib, i / 5) for i in range(6)], 2)

    # CAT GRAVE: grey stone, the front with a carved cat face and a heart
    stone = tex((150, 150, 165), "gs", 0.08)
    speckle(stone, (110, 140, 100), 5, "moss", (0, 11, 15, 15))  # a little moss low down
    part("grave_stone", stone)
    front = stone.copy()
    carve = (96, 96, 112)
    put(front, [(4, 4), (5, 4), (10, 4), (11, 4), (7, 7), (8, 7), (6, 8), (9, 8)], carve)  # eyes and a tiny mouth
    for x, y in ((6, 11), (7, 11), (9, 11), (10, 11), (6, 12), (7, 12), (8, 12), (9, 12), (10, 12), (7, 13), (8, 13), (9, 13), (8, 14)):
        put(front, [(x - 0, y)], (220, 110, 150))  # a pink heart
    part("grave_front", front)

    # BOW and MEDAL (accessories at a pet's neck)
    bow = tex((255, 120, 190), "bw", 0.04)
    rect(bow, 0, 7, 15, 8, (255, 180, 220))
    part("bow_ribbon", bow)
    mr = tex(PURPLE, "mr", 0.04)
    rect(mr, 6, 0, 9, 15, CYAN)
    part("medal_ribbon", mr)
    md = tex(GOLD, "md", 0.04)
    for x, y, d in star_shape(16, 6, 2.6, 8, 8):
        md.putpixel((x, y), shade((255, 240, 160), 1.05 - 0.2 * d) + (255,))
    rect(md, 0, 0, 15, 0, shade(GOLD, 0.7))
    rect(md, 0, 15, 15, 15, shade(GOLD, 0.7))
    part("medal_gold", [md] * 10 + [glint(md, i / 5) for i in range(6)], 2)


# ---------------- models ----------------

def jetpack():
    el = [box((3.5, 3.0, 8), (12.5, 13, 9.2), "metal")]
    el += pair((3.0, 2.5, 9.2), (7.4, 12.5, 13.6), "tank")
    el += pair((3.6, 12.5, 9.8), (6.8, 14.2, 13.0), "cone") + pair((4.4, 14.2, 10.6), (6.0, 15.2, 12.2), "cone")
    el += pair((3.8, 1.2, 10), (6.6, 2.5, 12.8), "metal")
    el += pair((4.2, -3.2, 10.4), (6.2, 1.2, 12.4), "flame", ("north", "south", "east", "west", "down"), light=15)
    el += [box((7.4, 5, 9.2), (8.6, 11, 10.4), "light", light=12)]
    return model(el, {"metal": "jet_metal", "tank": "jet_tank", "cone": "jet_cone", "flame": "jet_flame", "light": "jet_light"})


def axolotl_backpack():
    el = [box((3.5, 3.0, 8), (12.5, 12.0, 13.2), tx("fab", south="face"))]
    for y, a in ((11, 22.5), (9, 0), (7, -22.5)):
        el += pair((12.5, y - 0.5, 10.2), (15.6, y + 0.5, 11.2), "gills", rot={"origin": [12.5, y, 10.7], "axis": "z", "angle": a} if a else None)
    el += pair((2.4, 4.0, 10.0), (3.5, 5.6, 11.6), "fab") + pair((4.6, 2.0, 11.2), (6.4, 3.0, 13.0), "fab")
    return model(el, {"fab": "axo_pack", "face": "axo_pack_face", "gills": "axo_frills"})


def balloon_body(skin, face_tex):
    """A roundish balloon (a box with a bump on each side), the face on the front bump, a knot underneath."""
    return [box((3, 3.5, 3.5), (13, 12.5, 12.5), skin),
            box((4, 12.5, 4.5), (12, 13.3, 11.5), skin), box((4, 2.7, 4.5), (12, 3.5, 11.5), skin),
            box((4, 4.5, 2.7), (12, 11.5, 3.5), tx(skin, north=face_tex)), box((4, 4.5, 12.5), (12, 11.5, 13.3), skin),
            box((2.2, 4.5, 4.5), (3, 11.5, 11.5), skin), box((13, 4.5, 4.5), (13.8, 11.5, 11.5), skin),
            box((7.3, 1.7, 7.3), (8.7, 2.7, 8.7), "knot")]


def axolotl_balloon():
    el = balloon_body("skin", "face")
    for y, a in ((11, 22.5), (9.2, 0), (7.4, -22.5)):
        el += pair((13.4, y - 0.5, 6.8), (15.8, y + 0.5, 7.8), "gills", rot={"origin": [13.4, y, 7.3], "axis": "z", "angle": a} if a else None)
    return model(el, {"skin": "axo_balloon", "face": "axo_balloon_face", "knot": "balloon_knot", "gills": "axo_frills"})


def tiger_balloon():
    el = balloon_body("skin", "face") + pair((3.6, 12.4, 6.6), (6.6, 15.0, 8.0), "ear")
    return model(el, {"skin": "tiger_balloon", "face": "tiger_balloon_face", "knot": "balloon_knot", "ear": "tiger_round_ear"})


def cute_ghost():
    el = [box((4, 5, 4.5), (12, 13, 11.5), tx("ghost", north="face")), box((5, 13, 5.5), (11, 14, 10.5), "ghost")]
    for i, x in enumerate((4, 6, 8, 10)):  # a wavy hem
        el.append(box((x, 2.6 if i % 2 == 0 else 3.6, 4.5), (x + 2, 5, 11.5), "ghost", ("north", "south", "east", "west", "down")))
    el += pair((2.8, 7, 7), (4, 9, 9), "ghost")
    return model(el, {"ghost": "ghost", "face": "ghost_face"})


def star_body(face_tex, skin, light):
    """A chunky five-point star (centre block, a point up, two arms, two legs)."""
    el = [box((4.5, 4, 6), (11.5, 11, 10), tx(skin, north=face_tex), light=light),
          box((6.2, 11, 6.5), (9.8, 13.4, 9.5), skin, light=light), box((7, 13.4, 7), (9, 15, 9), skin, light=light)]
    arm = {"origin": [11.5, 8.7, 8], "axis": "z", "angle": 22.5}
    el += pair((11.5, 7.2, 6.5), (14, 10.2, 9.5), skin, rot=arm, light=light)
    el += pair((14, 7.8, 7), (15.6, 9.6, 9), skin, rot=arm, light=light)
    leg = {"origin": [10.1, 4, 8], "axis": "z", "angle": 22.5}
    el += pair((8.6, 1.6, 6.5), (11.6, 4, 9.5), skin, rot=leg, light=light)
    el += pair((9.2, 0, 7), (11, 1.6, 9), skin, rot=leg, light=light)
    return el


def falling_star():
    el = star_body("star", "star", 15)
    return model(el, {"star": "falling_star"})


def paw_print():
    return model([box((5, 0, 5), (11, 0.2, 11), "paw", ("up",))], {"paw": "paw_print"})


def egg(stage):
    shell = ["shell", "crack1", "crack2"][stage]
    lift = 0.6 if stage == 2 else 0  # the very cracked egg: its top has come loose and light shines out of the seam
    el = [box((5, 3, 5), (11, 4, 11), shell), box((4, 4, 4), (12, 9.5, 12), shell),
          box((4.6, 9.5 + lift, 4.6), (11.4, 11.8 + lift, 11.4), shell), box((5.8, 11.8 + lift, 5.8), (10.2, 13 + lift, 10.2), shell)]
    if stage == 2:
        el.append(box((4.8, 9.4, 4.8), (11.2, 10.2, 11.2), "glow", light=15))
    tex_map = {"shell": "egg_shell", "crack1": "egg_crack_1", "crack2": "egg_crack_2", "glow": "egg_glow"}
    return model(el, {k: v for k, v in tex_map.items() if any(f["texture"] == "#" + k for e in el for f in e["faces"].values())})


def gift_box():
    el = [box((4, 2.4, 4), (12, 9.4, 12), "paper"),
          box((7, 2.4, 3.9), (9, 9.4, 12.1), "ribbon", ("north", "south")), box((3.9, 2.4, 7), (12.1, 9.4, 9), "ribbon", ("east", "west"))]
    return model(el, {"paper": "gift_paper", "ribbon": "gift_ribbon"})


def gift_lid():
    el = [box((3.5, 9.4, 3.5), (12.5, 11.6, 12.5), "paper"),
          box((7, 9.4, 3.4), (9, 11.7, 12.6), "ribbon", ("north", "south", "up")),
          box((3.4, 9.4, 7), (12.6, 11.66, 9), "ribbon", ("east", "west", "up")),
          box((7.2, 11.7, 7.2), (8.8, 12.8, 8.8), "ribbon")]
    el += pair((4.8, 11.7, 7.2), (7.6, 13.9, 8.8), "ribbon", rot={"origin": [7.6, 11.7, 8], "axis": "z", "angle": -22.5})
    return model(el, {"paper": "gift_paper", "ribbon": "gift_ribbon"})


def cat_grave():
    el = [box((3, 0, 5), (13, 1.4, 11), "stone"),
          box((4.6, 1.4, 6.6), (11.4, 8.2, 9.2), tx("stone", north="front")), box((5.4, 8.2, 6.6), (10.6, 8.8, 9.2), "stone")]
    el += pair((4.6, 8.2, 7.2), (6.6, 10.2, 8.6), "stone")
    el += [box((3.9, 1.4, 5.5), (4.5, 2.8, 6.1), "vine"), box((3.4, 2.8, 5.0), (5.0, 3.8, 6.6), "flower")]
    return model(el, {"stone": "grave_stone", "front": "grave_front", "vine": "vine", "flower": "flower_pink"})


def bow():
    el = [box((7.3, 7.3, 7.4), (8.7, 8.7, 8.6), "ribbon")]
    el += pair((5.4, 7.0, 7.6), (7.3, 9.2, 8.4), "ribbon", rot={"origin": [7.3, 8, 8], "axis": "z", "angle": -22.5})
    el += pair((6.6, 5.6, 7.8), (7.4, 7.4, 8.2), "ribbon", rot={"origin": [7.4, 7.4, 8], "axis": "z", "angle": -22.5})
    return model(el, {"ribbon": "bow_ribbon"})


def medal():
    el = [box((7.0, 8.6, 7.8), (9.0, 10.6, 8.2), "ribbon"),
          box((6.5, 6.0, 7.6), (9.5, 8.2, 8.4), "gold"), box((6.9, 5.6, 7.7), (9.1, 8.6, 8.3), "gold")]  # no shared faces: no z-fighting
    return model(el, {"ribbon": "medal_ribbon", "gold": "medal_gold"})


MODELS = {"jetpack": jetpack, "axolotl_backpack": axolotl_backpack, "axolotl_balloon": axolotl_balloon,
          "tiger_balloon": tiger_balloon, "cute_ghost": cute_ghost, "falling_star": falling_star, "paw_print": paw_print,
          "cosmic_egg_0": lambda: egg(0), "cosmic_egg_1": lambda: egg(1), "cosmic_egg_2": lambda: egg(2),
          "gift_box": gift_box, "gift_lid": gift_lid, "cat_grave": cat_grave, "bow": bow, "medal": medal}
