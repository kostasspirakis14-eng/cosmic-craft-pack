"""Cosmetics for the Cosmic Wardrobe: 3D item models for hats and pets, and their (animated) textures.

make_pack.py calls write(OUT). Every cosmetic is an item model cosmic:cosmetic/<id> (items/cosmetic/<id>.json):
  hats   astronaut_helmet, alien_antennae, saturn_hat, crown: shaped for the head slot (the CosmicCraft plugin shows
         them over the helmet), their gui pose fitted to the inventory slot
  pets   satellite, ufo, mini_saturn: centred on 8,8,8, shown by item displays that orbit or follow the player
  more   cos_hats.py (12 hats), cos_things.py (jetpack, axolotl backpack, balloons, effect models, egg, gift, cat grave,
         bow, medal, the locked texture), cos_icons.py (flat menu icons and the elytra-style wings); helpers in cos_art.py
  <id>_locked for every model (a dark silhouette), <id>_shiny for SHINY (gold copies of the final textures)
Textures: src/cosmetics/<part>.png from Claude Design (claude-design-cosmetics.md, -hats-2, -back-balloons, -effects,
-icons) when present, otherwise the pixel-art placeholders. A texture taller than wide is an animation strip (square
frames, or the frame size its .mcmeta gives).

Head space (where a hat sits): Minecraft draws a head-slot item 0.625 block big, centred on the head, so in model units
the head fills 1.6..14.4 on every axis (its outer skin layer 1.2..14.8); the face is on the north side (low z).
"""
import json
import math

from PIL import Image

PARTS = {}  # name -> (frames list of RGBA images, frametime)


# ---------------- placeholder pixel art ----------------

def blank(n=16):
    return Image.new("RGBA", (n, n), (0, 0, 0, 0))


def fill(img, colour):
    img.paste(colour + (255,) if len(colour) == 3 else colour, (0, 0, img.width, img.height))
    return img


def shade(c, k):
    return tuple(max(0, min(255, round(v * k))) for v in c[:3])


def glint(img, t, width=2.4, strength=0.8):
    """A diagonal shine at position t (0..1 across the texture), on opaque pixels only."""
    out = img.copy()
    px = out.load()
    n = out.width
    centre = -3 + t * (2 * n + 6)
    for y in range(n):
        for x in range(n):
            r, g, b, a = px[x, y]
            k = max(0.0, 1 - abs(x + y - centre) / width) * strength
            if a and k:
                px[x, y] = (round(r + (255 - r) * k), round(g + (255 - g) * k), round(b + (255 - b) * k), a)
    return out


def part(name, frames, frametime=2):
    PARTS[name] = (frames if isinstance(frames, list) else [frames], frametime)


def make_placeholders():
    # Astronaut helmet: white shell with panel seams, a gold visor with stars and a sweeping glint, blinking side lamps
    shell = blank()
    for y in range(16):
        for x in range(16):
            c = (236, 238, 245) if (x + y) % 7 else (214, 218, 230)
            if x in (0, 15) or y in (0, 15):
                c = (190, 196, 210)
            shell.putpixel((x, y), c + (255,))
    for x in range(3, 13):
        shell.putpixel((x, 13), (168, 85, 247, 255))  # a purple Cosmic stripe
    part("helmet_shell", shell)
    visor = blank()
    for y in range(16):
        for x in range(16):
            k = 0.55 + 0.45 * (y / 15)
            visor.putpixel((x, y), shade((255, 196, 60), k) + (255,))
    for x, y in ((3, 4), (10, 3), (6, 9), (12, 10), (4, 13)):
        visor.putpixel((x, y), (255, 255, 230, 255))
    part("helmet_visor", [visor] * 6 + [glint(visor, i / 5) for i in range(6)], 3)
    lamp_on, lamp_off = fill(blank(), (120, 255, 240)), fill(blank(), (30, 90, 90))
    part("helmet_lamp", [lamp_on] * 3 + [lamp_off] * 2, 5)

    # Alien antennae: green stalks with glowing pulsing tips
    stalk = blank()
    for y in range(16):
        for x in range(16):
            stalk.putpixel((x, y), shade((96, 200, 70), 0.75 + 0.25 * (x % 4 == 1)) + (255,))
    part("antenna_stalk", stalk)
    tips = []
    for i in range(8):
        k = 0.7 + 0.3 * math.sin(i / 8 * 2 * math.pi)
        t = blank()
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - 7.5, y - 7.5) / 10
                t.putpixel((x, y), shade((190, 255, 90), k * (1.15 - d)) + (255,))
        tips.append(t)
    part("antenna_tip", tips, 2)

    # Saturn: a banded planet and a round ring (transparent middle) with sparkles running round it
    planet = []
    for i in range(8):
        p = blank()
        for y in range(16):
            band = (y + i // 4) % 6
            base = [(230, 190, 120), (205, 150, 90), (245, 215, 160), (190, 130, 80), (235, 200, 140), (215, 165, 100)][band]
            for x in range(16):
                p.putpixel((x, y), shade(base, 0.92 + 0.08 * ((x + i) % 5 == 0)) + (255,))
        planet.append(p)
    part("planet", planet, 4)
    ring_frames = []
    for i in range(12):
        r = blank(32)
        for y in range(32):
            for x in range(32):
                d = math.hypot(x - 15.5, y - 15.5)
                if 9.5 <= d <= 15.5:
                    band = int(d) % 3
                    c = [(240, 220, 170), (200, 170, 120), (250, 235, 200)][band]
                    ang = (math.atan2(y - 15.5, x - 15.5) / (2 * math.pi) * 12 - i) % 12
                    if ang < 0.7:  # the sparkle travelling round
                        c = (255, 255, 255)
                    r.putpixel((x, y), c + (235,))
        ring_frames.append(r)
    part("ring", ring_frames, 2)

    # Crown: gold with a travelling glint, purple and cyan gems
    gold = blank()
    for y in range(16):
        for x in range(16):
            gold.putpixel((x, y), shade((255, 205, 60), 0.85 + 0.2 * (y < 4) - 0.15 * (y > 12)) + (255,))
    part("crown_gold", [gold] * 8 + [glint(gold, i / 5) for i in range(6)], 2)
    gem = []
    for i in range(6):
        g = blank()
        for y in range(16):
            for x in range(16):
                k = 1.25 if (x + y + i * 3) % 12 < 2 else 1.0
                g.putpixel((x, y), shade((168, 85, 247), k * (0.8 + 0.2 * (y < 8))) + (255,))
        gem.append(g)
    part("crown_gem", gem, 3)

    # Satellite: gold foil body, blue solar cells, a white dish
    foil = blank()
    for y in range(16):
        for x in range(16):
            foil.putpixel((x, y), shade((232, 180, 60), 0.8 + 0.3 * (((x * 7 + y * 13) % 11) / 10)) + (255,))
    part("satellite_body", foil)
    cells = blank()
    for y in range(16):
        for x in range(16):
            line = x % 4 == 0 or y % 4 == 0
            cells.putpixel((x, y), ((180, 190, 210) if line else shade((40, 90, 200), 0.9 + 0.2 * (y < 8))) + (255,))
    part("satellite_panel", [cells] * 6 + [glint(cells, i / 4, 3, 0.5) for i in range(5)], 3)
    part("satellite_dish", fill(blank(), (235, 238, 245)))

    # UFO: a metal saucer with running rim lights, a glass dome, a little green alien
    hull = []
    for i in range(8):
        h = blank()
        for y in range(16):
            for x in range(16):
                c = shade((150, 150, 175), 0.85 + 0.25 * (y < 6))
                if y in (7, 8) and x % 4 == 0:
                    c = (255, 80, 220) if (x // 4 + i) % 4 == 0 else (120, 255, 240)
                h.putpixel((x, y), c + (255,))
        hull.append(h)
    part("ufo_hull", hull, 2)
    dome = blank()
    for y in range(16):
        for x in range(16):
            dome.putpixel((x, y), (150, 230, 255, 120 if (x + y) % 9 else 190))
    part("ufo_dome", dome)
    alien = fill(blank(), (110, 220, 80))
    for x, y in ((4, 6), (5, 6), (10, 6), (11, 6), (4, 7), (11, 7)):
        alien.putpixel((x, y), (15, 15, 25, 255))
    part("ufo_alien", alien)


# ---------------- models ----------------

FACES = ("north", "south", "east", "west", "up", "down")


def box(a, b, tex, faces=FACES, rot=None, light=0, tile=()):
    """An element; tex is one texture key or a dict face -> key; light (1-15) makes it glow in the dark.
    Faces show the whole texture, except texture keys in tile: those show the face's own size at 1 texel per unit
    (cropped from the top-left), so a pattern keeps its proportions on long thin faces."""
    assert all(-16 <= v <= 32 for v in (*a, *b)), (a, b)
    size = [abs(b[i] - a[i]) for i in range(3)]
    dims = {"north": (0, 1), "south": (0, 1), "east": (2, 1), "west": (2, 1), "up": (0, 2), "down": (0, 2)}
    e = {"from": [round(v, 3) for v in a], "to": [round(v, 3) for v in b], "faces": {}}
    for f in faces:
        key = tex[f] if isinstance(tex, dict) else tex
        u, v = (min(16, round(size[i], 2)) for i in dims[f])
        e["faces"][f] = {"uv": [0, 0, u, v] if key in tile else [0, 0, 16, 16], "texture": "#" + key}
    if rot:
        assert rot["angle"] in (-45, -22.5, 0, 22.5, 45), rot
        e["rotation"] = {**rot, "origin": list(rot["origin"])}  # a copy: several elements may share one rotation
    if light:
        e["light_emission"] = light
    return e


def gui_pose(elements, base_rotation=(30, 225, 0)):
    """A gui display transform that centres and fits the model in the slot (vanilla block icons are 0.625)."""
    lo = [min(min(e["from"][i], e["to"][i]) for e in elements) for i in range(3)]
    hi = [max(max(e["from"][i], e["to"][i]) for e in elements) for i in range(3)]
    size = max(h - l for l, h in zip(lo, hi))
    scale = round(0.625 * 16 / max(size, 12) * 1.15, 3)
    rx, ry, _ = (math.radians(v) for v in base_rotation)
    c = [(l + h) / 2 - 8 for l, h in zip(lo, hi)]
    # where the model's middle lands after the y then x rotation, so the translation can bring it back to the centre
    x1, z1 = c[0] * math.cos(ry) + c[2] * math.sin(ry), -c[0] * math.sin(ry) + c[2] * math.cos(ry)
    y2 = c[1] * math.cos(rx) - z1 * math.sin(rx)
    return {"rotation": list(base_rotation), "translation": [round(-x1 * scale, 2), round(-y2 * scale, 2), 0], "scale": [scale] * 3}


def model(elements, textures):
    return {"textures": {**{k: f"cosmic:item/cosmetic/{v}" for k, v in textures.items()}, "particle": f"cosmic:item/cosmetic/{next(iter(textures.values()))}"},
            "elements": elements,
            "display": {"head": {"rotation": [0, 0, 0], "translation": [0, 0, 0], "scale": [1, 1, 1]},
                        "gui": gui_pose(elements),
                        "fixed": {"rotation": [0, 180, 0], "scale": [0.8, 0.8, 0.8]},
                        "ground": {"translation": [0, 2, 0], "scale": [0.4, 0.4, 0.4]}}}


def astronaut_helmet():
    # a shell round the whole head (just outside the skin's outer layer), a gold visor, a lamp each side, an antenna
    el = [box((0.4, 0.4, 0.4), (15.6, 15.8, 15.6), "shell", ("south", "east", "west", "up")),
          box((0.4, 0.4, 0.4), (15.6, 4, 0.4), "shell", ("north",)),                       # chin under the visor
          box((0.4, 13, 0.4), (15.6, 15.8, 0.4), "shell", ("north",)),                     # brow over it
          box((0.4, 4, 0.4), (2.2, 13, 0.4), "shell", ("north",)), box((13.8, 4, 0.4), (15.6, 13, 0.4), "shell", ("north",)),
          box((2.2, 4, -0.4), (13.8, 13, 0.4), "visor"),                                    # the visor bulges out a little
          box((-0.6, 6.5, 6), (0.4, 9.5, 10), "lamp"), box((15.6, 6.5, 6), (16.6, 9.5, 10), "lamp"),
          box((12, 15.8, 10), (13, 21, 11), "shell"), box((11.5, 21, 9.5), (13.5, 23, 11.5), "lamp")]
    return model(el, {"shell": "helmet_shell", "visor": "helmet_visor", "lamp": "helmet_lamp"})


def alien_antennae():
    el = []
    for side, x in ((-1, 4.5), (1, 10.5)):  # two stalks leaning out, round glowing tips
        el.append(box((x, 14.4, 7.25), (x + 1.5, 23, 8.75), "stalk", rot={"origin": [x + 0.75, 14.4, 8], "axis": "z", "angle": -22.5 * side}))
        tx = x + 0.75 + side * 3.6
        el.append(box((tx - 1.6, 22.2, 6.4), (tx + 1.6, 25.4, 9.6), "tip"))
    el.append(box((3.5, 14.4, 6.5), (12.5, 15.2, 9.5), "stalk", ("up", "north", "south", "east", "west")))  # the band they stand on
    return model(el, {"stalk": "antenna_stalk", "tip": "antenna_tip"})


def planet_and_ring(cx, cy, cz, r, tilt=-22.5):
    """A roundish planet (three crossed boxes) with a flat round ring, tilted."""
    el = [box((cx - r, cy - r * 0.7, cz - r * 0.7), (cx + r, cy + r * 0.7, cz + r * 0.7), "planet"),
          box((cx - r * 0.7, cy - r, cz - r * 0.7), (cx + r * 0.7, cy + r, cz + r * 0.7), "planet"),
          box((cx - r * 0.7, cy - r * 0.7, cz - r), (cx + r * 0.7, cy + r * 0.7, cz + r), "planet")]
    R = r * 2.1
    el.append(box((cx - R, cy, cz - R), (cx + R, cy, cz + R), "ring", ("up", "down"), rot={"origin": [cx, cy, cz], "axis": "x", "angle": tilt}))
    return el


def saturn_hat():
    el = planet_and_ring(8, 19.5, 8, 3.2) + [box((7.4, 14.4, 7.4), (8.6, 16.6, 8.6), "ring", ("north", "south", "east", "west"))]  # a stand
    return model(el, {"planet": "planet", "ring": "ring"})


def crown():
    el = [box((1.8, 14.0, 1.8), (14.2, 17.2, 2.8), "gold"), box((1.8, 14.0, 13.2), (14.2, 17.2, 14.2), "gold"),
          box((1.8, 14.0, 2.8), (2.8, 17.2, 13.2), "gold"), box((13.2, 14.0, 2.8), (14.2, 17.2, 13.2), "gold")]
    for i in range(8):  # eight points round the band, gems on the four in the middle of each side
        a = i * math.pi / 4
        x, z = 8 + 5.7 * math.cos(a) * (1.25 if i % 2 else 1), 8 + 5.7 * math.sin(a) * (1.25 if i % 2 else 1)
        x, z = min(13.2, max(2.8, x)), min(13.2, max(2.8, z))
        h = 21 if i % 2 == 0 else 19.5
        el.append(box((x - 0.9, 17.2, z - 0.9), (x + 0.9, h, z + 0.9), "gold"))
        if i % 2 == 0:
            el.append(box((x - 0.8, h, z - 0.8), (x + 0.8, h + 1.6, z + 0.8), "gem"))
    el.append(box((6.8, 15.0, 1.2), (9.2, 17.0, 1.8), "gem"))  # the big gem at the front
    return model(el, {"gold": "crown_gold", "gem": "crown_gem"})


def satellite():
    el = [box((6, 6, 6), (10, 10, 10), "body"),
          box((-1, 7.6, 7.4), (6, 8.4, 8.6), "dish", ("north", "south", "up", "down")),    # arms
          box((10, 7.6, 7.4), (17, 8.4, 8.6), "dish", ("north", "south", "up", "down")),
          box((-7, 4.5, 7.6), (-1, 11.5, 8.4), "panel"), box((17, 4.5, 7.6), (23, 11.5, 8.4), "panel"),
          box((7, 10, 7), (9, 11, 9), "dish"), box((6, 11, 6), (10, 11.6, 10), "dish")]   # the dish on top
    return model(el, {"body": "satellite_body", "panel": "satellite_panel", "dish": "satellite_dish"})


def ufo():
    el = [box((1, 6, 1), (15, 8, 15), "hull"), box((3, 4.5, 3), (13, 6, 13), "hull"), box((-1, 6.5, 3), (17, 7.5, 13), "hull"),
          box((3, 6.5, -1), (13, 7.5, 17), "hull"),
          box((6.2, 8, 6.2), (9.8, 11, 9.8), "alien"),                                     # the pilot, under the dome
          box((5, 8, 5), (11, 12.5, 11), "dome")]
    return model(el, {"hull": "ufo_hull", "dome": "ufo_dome", "alien": "ufo_alien"})


def mini_saturn():
    return model(planet_and_ring(8, 8, 8, 4.2), {"planet": "planet", "ring": "ring"})


SHINY = ["satellite", "ufo", "mini_saturn"]  # also get <id>_shiny: the same shape with gold copies of the final textures
MODELS = {"astronaut_helmet": astronaut_helmet, "alien_antennae": alien_antennae, "saturn_hat": saturn_hat, "crown": crown,
          "satellite": satellite, "ufo": ufo, "mini_saturn": mini_saturn}


def locked(m, cutouts):
    """The same shape as a dark silhouette for cosmetics the player does not own yet: every face uses the texture
    locked, except faces whose texture has see-through holes (a ring, blades, leaves): those use <texture>_locked,
    a dark copy keeping the holes, so a halo does not turn into a black square."""
    names = {k: v.split("/")[-1] for k, v in m["textures"].items() if k != "particle"}
    textures = {"locked": "cosmic:item/cosmetic/locked", "particle": "cosmic:item/cosmetic/locked"}
    textures.update({k: f"cosmic:item/cosmetic/{t}_locked" for k, t in names.items() if t in cutouts})
    el = [{**{k: v for k, v in e.items() if k != "light_emission"},
           "faces": {f: {**face, "texture": face["texture"] if names[face["texture"][1:]] in cutouts else "#locked"}
                     for f, face in e["faces"].items()}} for e in m["elements"]]
    return {**m, "textures": textures, "elements": el}


def shiny(m):
    return {**m, "textures": {k: v + "_gold" for k, v in m["textures"].items()}}


def write(out, src):
    """Textures, models and item definitions into the pack being built at out/."""
    import cos_art, cos_hats, cos_icons, cos_things  # they import this module's helpers
    make_placeholders()
    for mod in (cos_hats, cos_things):
        mod.textures()
    tex = out / "assets/cosmic/textures/item/cosmetic"  # inside item/: only atlas-listed folders load, cosmetic/ alone showed nothing
    tex.mkdir(parents=True, exist_ok=True)
    for name, (frames, frametime) in PARTS.items():
        art = src / "cosmetics" / f"{name}.png"
        if art.exists():  # Claude Design art wins; its own .mcmeta (if any) comes along
            Image.open(art).convert("RGBA").save(tex / f"{name}.png")
            meta = art.with_suffix(".png.mcmeta")
            if meta.exists():
                (tex / f"{name}.png.mcmeta").write_text(meta.read_text(encoding="utf-8"), encoding="utf-8")
            continue
        w, h = frames[0].size
        strip = Image.new("RGBA", (w, h * len(frames)))
        for i, f in enumerate(frames):
            strip.paste(f, (0, h * i))
        strip.save(tex / f"{name}.png")
        if len(frames) > 1:
            anim = dict(frametime) if isinstance(frametime, dict) else {"frametime": frametime}
            if h != w:
                anim.update(width=w, height=h)
            (tex / f"{name}.png.mcmeta").write_text(json.dumps({"animation": anim}), encoding="utf-8")
    makers = {**MODELS, **cos_hats.MODELS, **cos_things.MODELS}
    models = {name: make() for name, make in makers.items()}
    used = {v.split("/")[-1] for m in models.values() for k, v in m["textures"].items() if k != "particle"}
    cutouts = {t for t in used if Image.open(tex / f"{t}.png").convert("RGBA").getextrema()[3][0] == 0}
    for t in cutouts:  # dark copies keeping the holes and the animation, for the locked models
        cos_art.silhouette(Image.open(tex / f"{t}.png")).save(tex / f"{t}_locked.png")
        if (tex / f"{t}.png.mcmeta").exists():
            (tex / f"{t}_locked.png.mcmeta").write_text((tex / f"{t}.png.mcmeta").read_text(encoding="utf-8"), encoding="utf-8")
    for name in list(models):
        models[name + "_locked"] = locked(models[name], cutouts)
    for name in SHINY:
        models[name + "_shiny"] = shiny(models[name])
        for t in models[name]["textures"].values():  # gold copies of the final art (Claude Design or placeholder)
            t = t.split("/")[-1]
            cos_art.to_gold(Image.open(tex / f"{t}.png")).save(tex / f"{t}_gold.png")
            meta = tex / f"{t}.png.mcmeta"
            if meta.exists():
                (tex / f"{t}_gold.png.mcmeta").write_text(meta.read_text(encoding="utf-8"), encoding="utf-8")
    (out / "assets/cosmic/models/cosmetic").mkdir(parents=True, exist_ok=True)
    (out / "assets/cosmic/items/cosmetic").mkdir(parents=True, exist_ok=True)
    for name, m in models.items():
        (out / f"assets/cosmic/models/cosmetic/{name}.json").write_text(json.dumps(m, indent=1), encoding="utf-8")
        (out / f"assets/cosmic/items/cosmetic/{name}.json").write_text(json.dumps(
            {"model": {"type": "minecraft:model", "model": f"cosmic:cosmetic/{name}"}}), encoding="utf-8")
    n_icons = cos_icons.write(out, src)  # flat 2D icons (+ locked ones) and the three elytra-style wings
    return len(models) + n_icons
