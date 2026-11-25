"""Voxel pets for the Cosmic Wardrobe: each pet is sculpted here as coloured voxels (like MagicaVoxel), then turned
into a Minecraft item model: same-coloured voxels merged into boxes (greedy), only the faces you can see, every face
coloured from a palette texture. The palette is an animation strip, so colours can change over time: eyes blink,
glows pulse. Each pet also gets poses (walk1/walk2 for the steps, sit, sleep, or flap1/flap2 for wings), a shiny
gold palette and a dark "locked" one for the menu.

make_pack.py calls write(OUT); it also writes pet_meta.json (next to this file) for the CosmicCraft plugin:
  {pet: {"walk": bool, "scale": display scale, "feet": lowest y, "top": highest y, "neck": [x,y,z], "poses": [...]}}
1 voxel = 1 model unit (1/16 block at scale 1). The face looks north (-z): an item display turns models 180°, so
the plugin's yaw is the way the pet looks. Models are centred on 8,8,8.
"""
import json
import math
from pathlib import Path

from PIL import Image

CELL = 4          # each palette colour is a 4x4 block, so mipmaps never mix colours
GRID = 16         # 16x16 colours per palette
FRAMES = 60       # palette animation: 60 frames x 2 ticks = 6 s
BLINK = (52, 53, 54)


class Vox:
    def __init__(self):
        self.v = {}

    def put(self, x, y, z, c):
        self.v[(x, y, z)] = c

    def box(self, x0, x1, y0, y1, z0, z1, c):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    self.v[(x, y, z)] = c

    def ell(self, cx, cy, cz, rx, ry, rz, c):
        for x in range(math.floor(cx - rx), math.ceil(cx + rx) + 1):
            for y in range(math.floor(cy - ry), math.ceil(cy + ry) + 1):
                for z in range(math.floor(cz - rz), math.ceil(cz + rz) + 1):
                    if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2 <= 1.0:
                        self.v[(x, y, z)] = c

    def cut(self, x0, x1, y0, y1, z0, z1):
        for k in [k for k in self.v if x0 <= k[0] <= x1 and y0 <= k[1] <= y1 and z0 <= k[2] <= z1]:
            del self.v[k]

    def front(self, x, y, c, depth=1):
        """Paint the frontmost voxel(s) of column x,y (the face side, lowest z)."""
        zs = sorted(k[2] for k in self.v if k[0] == x and k[1] == y)
        for z in zs[:depth]:
            self.v[(x, y, z)] = c

    def side(self, y, z, c, right=False):
        """Paint the outermost voxel of row y,z on the left (low x) or right side."""
        xs = sorted(k[0] for k in self.v if k[1] == y and k[2] == z)
        if xs:
            self.v[(xs[-1] if right else xs[0], y, z)] = c

    def top(self, x, z, c):
        ys = sorted(k[1] for k in self.v if k[0] == x and k[2] == z)
        if ys:
            self.v[(x, ys[-1], z)] = c

    def mirror(self, axis_x):
        """Copy the left half (x < axis) to the right (x' = 2*axis - x), for symmetric pets."""
        for (x, y, z), c in list(self.v.items()):
            if x < axis_x:
                self.v[(round(2 * axis_x - x), y, z)] = c

    def moved(self, dx=0, dy=0, dz=0, where=lambda k: True):
        out = Vox()
        for k, c in self.v.items():
            out.v[(k[0] + dx, k[1] + dy, k[2] + dz) if where(k) else k] = c
        return out

    def recolour(self, mapping):
        out = Vox()
        out.v = {k: mapping.get(c, c) for k, c in self.v.items()}
        return out

    def copy(self):
        out = Vox()
        out.v = dict(self.v)
        return out


# ---------------- palette ----------------

def hexc(h):
    return tuple(int(h[i:i + 2], 16) for i in range(1, len(h), 2))


class Palette:
    """name -> base colour, plus how it changes over the 60 frames (blink: the eye turns into the lid colour)."""

    def __init__(self, colours, blink=None, pulse=None):
        self.names = list(colours)
        self.base = {k: hexc(v) if isinstance(v, str) else v for k, v in colours.items()}
        self.blink = blink or {}       # name -> lid colour name, during BLINK frames
        self.pulse = pulse or {}       # name -> (bright colour, speed): glows

    def index(self, name):
        return self.names.index(name)

    def frame(self, f, shade=None):
        out = {}
        for n, c in self.base.items():
            if n in self.blink and f in BLINK:
                c = self.base[self.blink[n]]
            if n in self.pulse:
                bright, speed = self.pulse[n]
                k = 0.5 + 0.5 * math.sin(2 * math.pi * f * speed / FRAMES)
                c = tuple(round(a + (b - a) * k) for a, b in zip(c[:3], hexc(bright)[:3])) + c[3:]
            out[n] = shade(n, c) if shade else c
        return out

    def image(self, shade=None):
        strip = Image.new("RGBA", (GRID * CELL, GRID * CELL * FRAMES), (0, 0, 0, 0))
        for f in range(FRAMES):
            cols = self.frame(f, shade)
            for i, n in enumerate(self.names):
                x, y = i % GRID * CELL, f * GRID * CELL + i // GRID * CELL
                strip.paste(tuple(cols[n][:4]) + (255,) * (4 - len(cols[n])), (x, y, x + CELL, y + CELL))
        return strip


def gold(name, c):
    """Shiny: every colour on a gold ramp by its brightness; eyes and their shine stay as they are."""
    if name in ("eye", "eyehl", "mouth"):
        return c
    lum = (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]) / 255
    lo, hi = (150, 90, 20), (255, 236, 140)
    return tuple(round(a + (b - a) * lum) for a, b in zip(lo, hi)) + tuple(c[3:])


def dark(name, c):
    lum = (0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]) / 255
    return tuple(round(v) for v in (28 + 26 * lum, 18 + 16 * lum, 48 + 30 * lum)) + tuple(c[3:])


# ---------------- voxels -> model ----------------

DIRS = {"north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0), "east": (1, 0, 0), "down": (0, -1, 0), "up": (0, 1, 0)}


def boxes(vox):
    """Greedy: grow each box along x, then z, then y, over voxels of one colour."""
    left = dict(vox.v)
    out = []
    for key in sorted(vox.v, key=lambda k: (k[1], k[2], k[0])):
        if key not in left:
            continue
        c = left[key]
        x0, y0, z0 = key
        x1 = x0
        while left.get((x1 + 1, y0, z0)) == c:
            x1 += 1
        z1 = z0
        while all(left.get((x, y0, z1 + 1)) == c for x in range(x0, x1 + 1)):
            z1 += 1
        y1 = y0
        while all(left.get((x, y1 + 1, z)) == c for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)):
            y1 += 1
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    del left[(x, y, z)]
        out.append(((x0, y0, z0), (x1, y1, z1), c))
    return out


def elements(vox, palette, offset):
    """Glass (a colour with alpha) keeps only its outer faces: the inside of a bubble would stack up and hide what is in it."""
    els = []
    clear = {c for c in set(vox.v.values()) if len(palette.base[c]) > 3}
    middle = {c: [sum(k[i] for k in vox.v if vox.v[k] == c) / sum(1 for k in vox.v if vox.v[k] == c) + 0.5 for i in range(3)] for c in clear}
    for (x0, y0, z0), (x1, y1, z1), c in boxes(vox):
        i = palette.index(c)
        u, v = i % GRID, i // GRID
        uv = [u + 0.25, v + 0.25, u + 0.75, v + 0.75]  # the middle of the colour's cell (UV units: 1 = one cell)
        faces = {}
        for name, (dx, dy, dz) in DIRS.items():
            if dx:
                layer = [(x1 + 1 if dx > 0 else x0 - 1, y, z) for y in range(y0, y1 + 1) for z in range(z0, z1 + 1)]
            elif dy:
                layer = [(x, y1 + 1 if dy > 0 else y0 - 1, z) for x in range(x0, x1 + 1) for z in range(z0, z1 + 1)]
            else:
                layer = [(x, y, z1 + 1 if dz > 0 else z0 - 1) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
            if c in clear:
                mid = ((x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2, (z0 + z1 + 1) / 2)
                if sum(d * (m - o) for d, m, o in zip((dx, dy, dz), mid, middle[c])) < 0:
                    continue
            if any(k not in vox.v for k in layer):
                faces[name] = {"uv": uv, "texture": "#p"}
        if faces:
            els.append({"from": [x0 + offset[0], y0 + offset[1], z0 + offset[2]],
                        "to": [x1 + 1 + offset[0], y1 + 1 + offset[1], z1 + 1 + offset[2]], "faces": faces})
    return els


def bounds(vox):
    xs, ys, zs = zip(*vox.v)
    return (min(xs), min(ys), min(zs)), (max(xs) + 1, max(ys) + 1, max(zs) + 1)


# ---------------- the pets ----------------

PETS = {}  # id -> function returning dict(pose -> Vox), palette, walk, size (blocks, longest side), neck (voxel x,y,z)


def pet(name, walk, size):
    def wrap(fn):
        PETS[name] = (fn, walk, size)
        return fn
    return wrap


def legs_walk(base, legs, step=1):
    """Two walk frames: diagonal leg pairs swing forward and back (legs: list of (x0,x1,z0,z1,y0,y1,colour) per leg,
    in order front-left, front-right, back-left, back-right)."""
    frames = []
    for phase in (1, -1):
        m = base.copy()
        for i, (x0, x1, z0, z1, y0, y1, c) in enumerate(legs):
            m.cut(x0, x1, y0, y1, z0, z1)
        for i, (x0, x1, z0, z1, y0, y1, c) in enumerate(legs):
            dz = -step * phase if i in (0, 3) else step * phase
            m.box(x0, x1, y0, y1, z0 + dz, z1 + dz, c)
        frames.append(m)
    return frames


@pet("axolotl", walk=True, size=0.78)
def axolotl():
    pal = Palette({"skin": "#F6A6C9", "belly": "#FCD5E5", "dark": "#E58BB0", "gill": "#E2457E", "gilltip": "#B21F5A",
                   "fin": "#FFC9DF", "eye": "#1B1024", "eyehl": "#FFFFFF", "mouth": "#B94A78", "blush": "#FF7FA3"},
                  blink={"eye": "skin", "eyehl": "skin"}, pulse={"gilltip": ("#FF5C9A", 1)})
    m = Vox()
    # the body: long and low, a lighter belly, a fin along the back
    m.box(2, 6, 1, 4, 6, 14, "skin")
    m.box(3, 5, 1, 1, 6, 14, "belly")
    m.box(4, 4, 5, 5, 8, 14, "fin")
    # the big head in front, corners rounded
    m.box(0, 8, 2, 7, 0, 6, "skin")
    for x in (0, 8):
        for y in (2, 7):
            m.cut(x, x, y, y, 0, 6)
        m.cut(x, x, 2, 7, 0, 0)
    m.box(1, 7, 2, 2, 0, 6, "belly")
    # face: big eyes with a shine, a wide smile, rosy cheeks
    for ex in (1, 6):
        m.box(ex, ex + 1, 5, 6, 0, 0, "eye")
        m.put(ex, 6, 0, "eyehl")
    for x, y in ((2, 4), (3, 3), (4, 3), (5, 3), (6, 4)):
        m.put(x, y, 0, "mouth")
    m.put(1, 4, 0, "blush")
    m.put(7, 4, 0, "blush")
    # gills: three feathery fronds each side, pink-red tips that glow
    for side, x0 in ((-1, 0), (1, 8)):
        x1, x2 = x0 + side, x0 + 2 * side
        for pts in (((x1, 7, 4), (x1, 8, 5), (x1, 9, 5)), ((x1, 5, 4), (x2, 6, 5), (x2, 7, 6)), ((x1, 3, 4), (x2, 3, 5), (x2, 2, 6))):
            for i, p in enumerate(pts):
                m.put(*p, "gilltip" if i == len(pts) - 1 else "gill")
    # stubby legs out to the sides, little darker toes
    legs = [(1, 1, 7, 8, 0, 1, "skin"), (7, 7, 7, 8, 0, 1, "skin"), (1, 1, 12, 13, 0, 1, "skin"), (7, 7, 12, 13, 0, 1, "skin")]
    for x0, x1, z0, z1, y0, y1, c in legs:
        m.box(x0, x1, y0, y1, z0, z1, c)
    # the tail: a flat fin that narrows, swishing
    tail = Vox()
    tail.box(3, 5, 1, 4, 15, 16, "skin")
    tail.box(4, 4, 1, 5, 17, 19, "fin")
    tail.box(4, 4, 2, 4, 20, 21, "fin")
    tail.box(4, 4, 3, 3, 22, 22, "dark")
    tail.box(4, 4, 5, 5, 15, 16, "fin")
    idle = m.copy()
    idle.v.update(tail.v)
    w1, w2 = legs_walk(m, legs)
    w1.v.update(tail.moved(dx=1, where=lambda k: k[2] >= 19).v)
    w2.v.update(tail.moved(dx=-1, where=lambda k: k[2] >= 19).v)
    sleep = idle.copy()
    for ex in (1, 6):  # eyes shut: a little curved line
        sleep.box(ex, ex + 1, 5, 6, 0, 0, "skin")
        sleep.box(ex, ex + 1, 5, 5, 0, 0, "mouth")
    sleep.cut(0, 8, 0, 0, 0, 22)
    sleep = sleep.moved(dy=-1)
    return {"idle": idle, "walk1": w1, "walk2": w2, "sleep": sleep}, pal, (4, 2, 5)


@pet("tiger_cub", walk=True, size=0.72)
def tiger_cub():
    pal = Palette({"fur": "#F28A2E", "light": "#F7A54D", "stripe": "#2A1B14", "white": "#FFF4E2", "nose": "#F27C9B",
                   "inner": "#F7A8B8", "eye": "#1E1410", "eyehl": "#FFFFFF", "mouth": "#5A3020", "paw": "#FFE9CC"},
                  blink={"eye": "fur", "eyehl": "fur"})
    head = Vox()
    head.ell(4.5, 10, 3.5, 5.1, 4.4, 3.9, "fur")
    # muzzle and nose stick out a little; cheeks fluffy white
    head.box(3, 6, 7, 8, -1, 0, "white")
    head.box(4, 5, 9, 9, -1, -1, "nose")
    head.put(4, 7, -1, "mouth")
    head.put(5, 7, -1, "mouth")
    for x in (0, 1, 8, 9):
        head.front(x, 8, "white")
        head.front(x, 7, "white")
    # eyes
    for ex in (2, 6):
        for y in (10, 11):
            head.front(ex, y, "eye")
            head.front(ex + 1, y, "eye")
        head.front(ex, 11, "eyehl")
    # forehead and side stripes
    for x, y in ((4, 13), (5, 13), (2, 12), (7, 12)):
        head.front(x, y, "stripe")
    for z in (2, 3, 4):
        head.side(10, z, "stripe")
        head.side(10, z, "stripe", right=True)
        head.side(12, z + 1, "stripe")
        head.side(12, z + 1, "stripe", right=True)
    # round ears, pink inside
    for x0 in (0, 7):
        head.box(x0, x0 + 2, 14, 15, 2, 3, "fur")
        head.box(x0 + 1, x0 + 1, 16, 16, 2, 3, "fur")
        head.put(x0 + 1, 15, 2, "inner")
        head.box(x0, x0 + 2, 14, 15, 3, 3, "stripe")
    body = Vox()
    body.box(2, 7, 3, 7, 6, 15, "fur")
    body.box(3, 6, 3, 3, 6, 15, "white")
    for z in (8, 11, 14):  # stripes over the back and down the sides
        body.box(2, 7, 7, 7, z, z, "stripe")
        body.box(2, 2, 5, 6, z, z, "stripe")
        body.box(7, 7, 5, 6, z, z, "stripe")
    legs = [(2, 3, 6, 7, 0, 2, "fur"), (6, 7, 6, 7, 0, 2, "fur"), (2, 3, 13, 14, 0, 2, "fur"), (6, 7, 13, 14, 0, 2, "fur")]
    for x0, x1, z0, z1, y0, y1, c in legs:
        body.box(x0, x1, y0, y1, z0, z1, c)
        body.box(x0, x1, 0, 0, z0, z0, "paw")
    tail = Vox()
    for i, (y, z) in enumerate(((7, 16), (8, 17), (9, 17), (10, 17), (11, 16))):
        tail.put(4, y, z, "white" if i == 4 else "stripe" if i % 2 else "fur")
    idle = body.copy()
    idle.v.update(head.v)
    idle.v.update(tail.v)
    w1, w2 = legs_walk(body, legs)
    for frame, dx in ((w1, 1), (w2, -1)):
        frame.v.update(head.v)
        frame.v.update(tail.moved(dx=dx, where=lambda k: k[1] >= 10).v)
    for frame in (w1, w2):
        for k, c in list(frame.v.items()):
            if k[1] == 0 and c == "fur":
                frame.v[k] = "paw"
    # sitting: the back end down on the ground, front legs straight, tail round the side
    sit = Vox()
    sit.box(2, 7, 3, 8, 6, 11, "fur")
    sit.box(3, 6, 3, 4, 6, 9, "white")
    sit.box(2, 7, 0, 4, 11, 14, "fur")
    sit.box(2, 7, 0, 0, 9, 10, "paw")
    for z in (12, 14):
        sit.box(2, 7, 4, 4, z, z, "stripe")
    sit.box(2, 7, 8, 8, 9, 9, "stripe")
    for x0 in (2, 6):
        sit.box(x0, x0 + 1, 0, 2, 6, 7, "fur")
        sit.box(x0, x0 + 1, 0, 0, 6, 6, "paw")
    for i, (x, z) in enumerate(((8, 14), (8, 13), (9, 12), (9, 11), (9, 10))):
        sit.put(x, 0, z, "white" if i == 4 else "stripe" if i % 2 else "fur")
    sit.v.update(head.moved(dy=1).v)
    # sleeping: lying flat, head down on its paws, eyes shut
    sleep = Vox()
    sleep.box(2, 7, 0, 4, 6, 15, "fur")
    for z in (8, 11, 14):
        sleep.box(2, 7, 4, 4, z, z, "stripe")
    shut = head.copy()
    for k, c in list(shut.v.items()):
        if c in ("eye", "eyehl"):
            shut.v[k] = "fur" if k[1] == 11 else "stripe"
    sleep.v.update(shut.moved(dy=-6, dz=-1).v)
    sleep.box(2, 3, 0, 1, 3, 5, "paw")
    sleep.box(6, 7, 0, 1, 3, 5, "paw")
    for i, (x, z) in enumerate(((8, 15), (9, 14), (9, 13), (9, 12), (9, 11))):
        sleep.put(x, 0, z, "white" if i == 4 else "stripe" if i % 2 else "fur")
    return {"idle": idle, "walk1": w1, "walk2": w2, "sit": sit, "sleep": sleep}, pal, (4, 6, 4)



def four_legs(body, legs, paw):
    for x0, x1, z0, z1, y0, y1, c in legs:
        body.box(x0, x1, y0, y1, z0, z1, c)
        body.box(x0, x1, 0, 0, z0, z1, paw)


def quad_poses(head, body, legs, tail, paw, sit, sleep_body, shut, tail_sway_from=10, head_sleep=(0, -6, -1)):
    """idle, the two steps (legs swing, the tail sways), sitting and sleeping, from the parts."""
    idle = body.copy()
    idle.v.update(head.v)
    idle.v.update(tail.v)
    w1, w2 = legs_walk(body, legs)
    for frame, dx in ((w1, 1), (w2, -1)):
        for x0, x1, z0, z1, y0, y1, c in legs:  # the paws again, on the moved legs
            for k in [k for k in frame.v if k[1] == 0 and x0 <= k[0] <= x1]:
                frame.v[k] = paw
        frame.v.update(head.v)
        frame.v.update(tail.moved(dx=dx, where=lambda k: k[1] >= tail_sway_from).v)
    sleep = sleep_body.copy()
    sleep.v.update(shut.moved(*head_sleep).v)
    return {"idle": idle, "walk1": w1, "walk2": w2, "sit": sit, "sleep": sleep}


def shut_eyes(head, open_colour, line):
    """Eyes closed: the lowest row of each eye becomes a dark line, the rest fur."""
    out = head.copy()
    eyes = [k for k, c in head.v.items() if c in ("eye", "eyehl")]
    if not eyes:
        return out
    low = min(k[1] for k in eyes)
    for k in eyes:
        out.v[k] = line if k[1] == low else open_colour
    return out


def eyes2(head, xs, ys):
    """Two 2x2 eyes on the face, a shine top-left."""
    for ex in xs:
        for y in ys:
            head.front(ex, y, "eye")
            head.front(ex + 1, y, "eye")
        head.front(ex, max(ys), "eyehl")


@pet("fox_kit", walk=True, size=0.7)
def fox_kit():
    pal = Palette({"fur": "#F08A3C", "white": "#FFF6EC", "sock": "#4A2E22", "tip": "#2A1A14", "inner": "#FFD7C4",
                   "nose": "#22161A", "eye": "#1E1410", "eyehl": "#FFFFFF", "mouth": "#7A4030", "blush": "#FF9C8A"},
                  blink={"eye": "fur", "eyehl": "fur"})
    head = Vox()
    head.ell(4.5, 10, 3.5, 4.7, 3.9, 3.6, "fur")
    for x in (0, 1, 2, 7, 8, 9):
        for y in (7, 8, 9):
            head.front(x, y, "white")
    head.box(3, 6, 7, 8, -2, 0, "white")
    head.box(4, 5, 8, 8, -2, -2, "nose")
    head.put(4, 7, -2, "mouth")
    head.put(5, 7, -2, "mouth")
    eyes2(head, (2, 6), (10, 11))
    head.front(1, 9, "blush")
    head.front(8, 9, "blush")
    for x0, d in ((0, 1), (9, -1)):  # tall pointed ears, dark tips, pale inside
        head.box(min(x0, x0 + 2 * d), max(x0, x0 + 2 * d), 13, 14, 2, 3, "fur")
        head.box(min(x0, x0 + d), max(x0, x0 + d), 15, 15, 2, 3, "fur")
        head.box(x0, x0, 16, 16, 2, 3, "tip")
        head.put(x0 + d, 14, 2, "inner")
    body = Vox()
    body.box(2, 7, 3, 6, 6, 14, "fur")
    body.box(3, 6, 3, 3, 6, 14, "white")
    body.box(3, 6, 4, 6, 6, 6, "white")
    legs = [(2, 3, 6, 7, 0, 2, "sock"), (6, 7, 6, 7, 0, 2, "sock"), (2, 3, 12, 13, 0, 2, "sock"), (6, 7, 12, 13, 0, 2, "sock")]
    four_legs(body, legs, "sock")
    tail = Vox()  # big and bushy, white at the end
    tail.ell(4.5, 7.5, 18, 1.9, 2.1, 3.2, "fur")
    tail.cut(0, 9, 0, 20, 0, 14)
    for k in [k for k in tail.v if k[2] >= 20]:
        tail.v[k] = "white"
    sit = Vox()
    sit.box(2, 7, 3, 8, 6, 11, "fur")
    sit.box(3, 6, 3, 7, 6, 6, "white")
    sit.box(2, 7, 0, 4, 11, 14, "fur")
    for x0 in (2, 6):
        sit.box(x0, x0 + 1, 0, 2, 6, 7, "sock")
    sit.ell(4.5, 1.5, 16, 3, 1.6, 2.4, "fur")
    sit.box(3, 6, 0, 1, 18, 18, "white")
    sit.v.update(head.moved(dy=1).v)
    sleep = Vox()  # curled up, the bushy tail round the front
    sleep.box(2, 7, 0, 4, 6, 14, "fur")
    sleep.ell(1, 1.5, 8, 2, 1.6, 6, "fur")
    sleep.box(-1, 0, 0, 1, 2, 3, "white")
    return quad_poses(head, body, legs, tail, "sock", sit, sleep, shut_eyes(head, "fur", "tip"), head_sleep=(1, -6, 0)), pal, (4, 6, 5)


@pet("red_panda", walk=True, size=0.7)
def red_panda():
    pal = Palette({"fur": "#C4532B", "dark": "#3B2219", "white": "#FFF4EA", "ring": "#E68A52", "nose": "#22161A",
                   "eye": "#1E1410", "eyehl": "#FFFFFF", "mouth": "#5A2A1E", "tear": "#8E3A20"},
                  blink={"eye": "fur", "eyehl": "fur"})
    head = Vox()
    head.ell(4.5, 10, 3.5, 5, 4.2, 3.8, "fur")
    head.box(3, 6, 7, 8, -1, 0, "white")
    head.box(4, 5, 8, 8, -1, -1, "nose")
    head.put(4, 7, -1, "mouth")
    head.put(5, 7, -1, "mouth")
    for x in (0, 1, 8, 9):
        for y in (8, 9):
            head.front(x, y, "white")
    eyes2(head, (2, 6), (10, 11))
    for ex in (2, 6):  # white brows, red tear marks: the red panda face
        head.front(ex, 13, "white")
        head.front(ex + 1, 13, "white")
        head.front(ex, 9, "tear")
        head.front(ex + 1, 9, "tear")
    for x0, rim in ((0, 0), (7, 9)):  # round ears, white rims
        head.box(x0, x0 + 2, 13, 15, 2, 3, "fur")
        head.box(x0, x0 + 2, 15, 15, 2, 2, "white")
        head.box(rim, rim, 13, 15, 2, 2, "white")
    body = Vox()
    body.box(2, 7, 3, 7, 6, 14, "fur")
    body.box(3, 6, 3, 3, 6, 14, "dark")
    legs = [(2, 3, 6, 7, 0, 2, "dark"), (6, 7, 6, 7, 0, 2, "dark"), (2, 3, 12, 13, 0, 2, "dark"), (6, 7, 12, 13, 0, 2, "dark")]
    four_legs(body, legs, "dark")
    tail = Vox()  # thick and ringed, going back and up
    for i, (y, z) in enumerate(((5, 15), (6, 16), (7, 17), (8, 18), (9, 18), (10, 18))):
        tail.box(3, 6, y, y + 1, z, z + 1, "ring" if i % 2 else "fur")
    tail.box(3, 6, 12, 12, 18, 19, "dark")
    sit = Vox()
    sit.box(2, 7, 3, 8, 6, 11, "fur")
    sit.box(3, 6, 3, 7, 6, 6, "dark")
    sit.box(2, 7, 0, 4, 11, 14, "fur")
    for x0 in (2, 6):
        sit.box(x0, x0 + 1, 0, 2, 6, 7, "dark")
    for i, z in enumerate(range(15, 21)):
        sit.box(3, 6, 0, 1, z, z, "ring" if i % 2 else "fur")
    sit.v.update(head.moved(dy=1).v)
    sleep = Vox()
    sleep.box(2, 7, 0, 4, 6, 14, "fur")
    for i, z in enumerate(range(8, 14)):
        sleep.box(8, 9, 0, 1, z, z, "ring" if i % 2 else "fur")
    return quad_poses(head, body, legs, tail, "dark", sit, sleep, shut_eyes(head, "fur", "dark")), pal, (4, 6, 5)


@pet("capybara", walk=True, size=0.72)
def capybara():
    pal = Palette({"fur": "#9C6B43", "dark": "#74502F", "snout": "#5E3F27", "black": "#1E140E", "orange": "#FF9A1F",
                   "leaf": "#4CBF4A", "eye": "#1E140E", "eyehl": "#FFFFFF", "blush": "#E58A7A"},
                  blink={"eye": "fur", "eyehl": "fur"})
    head = Vox()  # a calm square head with a big snout
    head.box(1, 8, 6, 12, -3, 4, "fur")
    for x in (1, 8):
        head.cut(x, x, 12, 12, -3, 4)
        head.cut(x, x, 6, 12, -3, -3)
    head.box(2, 7, 6, 8, -3, -3, "snout")
    head.put(3, 8, -3, "black")
    head.put(6, 8, -3, "black")
    head.box(3, 6, 6, 6, -3, -3, "black")
    for ex in (2, 6):
        head.box(ex, ex + 1, 10, 11, -3, -3, "eye")
        head.put(ex, 11, -3, "eyehl")
    head.put(1, 9, -2, "blush")
    head.put(8, 9, -2, "blush")
    head.box(1, 2, 13, 13, 3, 4, "dark")
    head.box(7, 8, 13, 13, 3, 4, "dark")
    head.ell(4.5, 14.2, 0.5, 1.8, 1.4, 1.8, "orange")  # the orange on its head, and a leaf
    head.put(4, 16, 0, "leaf")
    head.put(5, 16, 1, "leaf")
    body = Vox()
    body.ell(4.5, 6, 10, 4.6, 3.8, 6.5, "fur")
    body.cut(-5, 15, -5, 1, 0, 20)
    legs = [(2, 3, 5, 6, 0, 2, "dark"), (6, 7, 5, 6, 0, 2, "dark"), (2, 3, 13, 14, 0, 2, "dark"), (6, 7, 13, 14, 0, 2, "dark")]
    four_legs(body, legs, "dark")
    sit = Vox()
    sit.ell(4.5, 5, 10, 4.6, 4.2, 6, "fur")
    sit.cut(-5, 15, -5, -1, 0, 20)
    sit.v.update(head.moved(dy=-1).v)
    sleep = Vox()
    sleep.ell(4.5, 3.5, 10, 4.6, 3.2, 6.5, "fur")
    sleep.cut(-5, 15, -5, -1, 0, 20)
    return quad_poses(head, body, legs, Vox(), "dark", sit, sleep, shut_eyes(head, "fur", "black"), head_sleep=(0, -3, 0)), pal, (4, 6, 5)


@pet("penguin", walk=True, size=0.62)
def penguin():
    pal = Palette({"fluff": "#A9B2C3", "cap": "#2B2F3A", "face": "#FFFFFF", "beak": "#F5A623", "foot": "#F59A23",
                   "eye": "#151820", "eyehl": "#FFFFFF", "blush": "#FFA0B4"}, blink={"eye": "face", "eyehl": "face"})
    m = Vox()
    m.ell(4, 6.5, 4, 4.4, 5.8, 3.8, "fluff")
    for k in [k for k in m.v if k[1] >= 9]:
        m.v[k] = "cap"
    for x in range(1, 8):
        for y in range(5, 11):
            m.front(x, y, "face")
    eyes2(m, (2, 5), (8, 9))
    m.front(1, 7, "blush")
    m.front(7, 7, "blush")
    beak_z = min(k[2] for k in m.v if k[0] == 4 and k[1] == 7) - 1
    m.put(4, 7, beak_z, "beak")
    m.put(4, 6, beak_z + 1, "beak")
    flips = Vox()
    flips.box(-1, -1, 4, 7, 3, 5, "cap")
    flips.box(9, 9, 4, 7, 3, 5, "cap")
    feet = [(2, 3, 2, 3), (5, 6, 2, 3)]
    body = m.copy()
    body.cut(-2, 10, 0, 0, -5, 15)
    idle = body.copy()
    idle.v.update(flips.v)
    for x0, x1, z0, z1 in feet:
        idle.box(x0, x1, 0, 0, z0 - 1, z1, "foot")
    frames = []
    for phase in (1, -1):  # a waddle: one foot forward, the flippers up and down
        f = body.copy()
        f.v.update(flips.moved(dy=phase, where=lambda k: k[0] < 4).v)
        f.v.update(flips.moved(dy=-phase, where=lambda k: k[0] > 4).v)
        for i, (x0, x1, z0, z1) in enumerate(feet):
            dz = phase if i == 0 else -phase
            f.box(x0, x1, 0, 0, z0 - 1 + dz, z1 + dz, "foot")
        frames.append(f)
    sit = body.moved(dy=-1)
    sit.v.update(flips.moved(dy=-1).v)
    sleep = shut_eyes(body, "face", "cap").moved(dy=-1)
    sleep.v.update(flips.moved(dy=-2).v)
    return {"idle": idle, "walk1": frames[0], "walk2": frames[1], "sit": sit, "sleep": sleep}, pal, (4, 5, 1)


@pet("frog", walk=True, size=0.62)
def frog():
    pal = Palette({"green": "#7BC74D", "deep": "#5FA03A", "belly": "#D6F2A8", "white": "#FFFFFF", "eye": "#151820",
                   "eyehl": "#FFFFFF", "mouth": "#3E6B25", "blush": "#FF9FB0", "cap": "#E5383B", "dot": "#FFF4EA", "stem": "#F3E6D0"},
                  blink={"eye": "green", "eyehl": "green", "white": "green"})
    m = Vox()
    m.ell(5, 3.5, 5, 5.2, 3.4, 4.6, "green")
    m.cut(-5, 15, -5, -1, -5, 15)
    for k in [k for k in m.v if k[1] <= 1]:
        m.v[k] = "belly"
    for ex in (2.5, 7.5):  # big round eyes on top at the front
        m.ell(ex, 7, 2.5, 1.9, 1.9, 1.9, "green")
    for ex in (1, 6):
        for x in (ex, ex + 1, ex + 2):
            for y in (6, 7, 8):
                m.front(x, y, "white")
        for x, y in ((ex + 1, 7), (ex + 2, 7), (ex + 1, 6), (ex + 2, 6)):
            m.front(x, y, "eye")
        m.front(ex + 1, 7, "eyehl")
    for x in range(2, 9):
        m.front(x, 3, "mouth")
    m.front(1, 4, "blush")
    m.front(9, 4, "blush")
    m.ell(5, 9.5, 5.5, 3.4, 1.7, 3.4, "cap")  # the mushroom on its head
    for k in [k for k in m.v if m.v[k] == "cap" and k[1] < 9]:
        del m.v[k]
    m.box(4, 6, 8, 8, 5, 6, "stem")
    for x, z in ((3, 4), (6, 6), (5, 3), (7, 4), (4, 7)):
        m.top(x, z, "dot")
    front_legs = Vox()
    front_legs.box(2, 3, 0, 1, 1, 2, "green")
    front_legs.box(7, 8, 0, 1, 1, 2, "green")
    idle = m.copy()
    idle.v.update(front_legs.v)
    idle.box(-1, 1, 0, 2, 6, 9, "deep")
    idle.box(9, 11, 0, 2, 6, 9, "deep")
    leap = m.copy()  # mid-hop: back legs stretched out behind
    leap.v.update(front_legs.v)
    leap.box(-1, 0, 0, 1, 8, 12, "deep")
    leap.box(10, 11, 0, 1, 8, 12, "deep")
    sleep = shut_eyes(idle, "green", "mouth")
    for k, c in list(sleep.v.items()):
        if c == "white":
            sleep.v[k] = "green"
    return {"idle": idle, "walk1": idle, "walk2": leap, "sleep": sleep}, pal, (5, 7, 2)


@pet("baby_trex", walk=True, size=0.72)
def baby_trex():
    pal = Palette({"green": "#6CC24A", "belly": "#D8F5A2", "spot": "#4E9A35", "eye": "#151820", "eyehl": "#FFFFFF",
                   "mouth": "#7A2C2C", "tooth": "#FFFFFF", "claw": "#F3E6D0", "blush": "#FF9FB0"},
                  blink={"eye": "green", "eyehl": "green"})
    head = Vox()
    head.box(0, 7, 9, 15, -2, 5, "green")
    for x in (0, 7):
        for y in (9, 15):
            head.cut(x, x, y, y, -2, 5)
        head.cut(x, x, 9, 15, -2, -2)
    head.box(1, 6, 9, 10, -2, -2, "belly")
    head.box(1, 6, 11, 11, -2, -2, "mouth")
    head.put(2, 10, -2, "tooth")
    head.put(5, 10, -2, "tooth")
    for ex in (1, 5):
        head.box(ex, ex + 1, 13, 14, -2, -2, "eye")
        head.put(ex, 14, -2, "eyehl")
    head.put(0, 12, -1, "blush")
    head.put(7, 12, -1, "blush")
    for z in (0, 2, 4):
        head.put(3, 16, z, "spot")
        head.put(4, 16, z, "spot")
    body = Vox()
    body.ell(3.5, 7, 8, 3.3, 3.6, 3.6, "green")
    for x in range(1, 7):
        for y in range(4, 9):
            body.front(x, y, "belly")
    body.box(0, 0, 6, 7, 5, 5, "green")  # tiny arms
    body.box(7, 7, 6, 7, 5, 5, "green")
    body.put(0, 5, 4, "claw")
    body.put(7, 5, 4, "claw")
    for z in (7, 9, 11):
        body.top(3, z, "spot")
        body.top(4, z, "spot")
    tail = Vox()
    tail.box(2, 5, 5, 7, 11, 13, "green")
    tail.box(3, 4, 5, 6, 14, 16, "green")
    tail.box(3, 4, 6, 6, 17, 18, "green")
    tail.put(3, 7, 13, "spot")
    tail.put(4, 7, 13, "spot")
    legs = [(1, 2, 7, 9), (5, 6, 7, 9)]

    def stepping(dz):
        f = body.copy()
        f.v.update(head.v)
        f.v.update(tail.v)
        for i, (x0, x1, z0, z1) in enumerate(legs):
            d = dz if i == 0 else -dz
            f.box(x0, x1, 0, 4, z0 + d, z1 + d, "green")
            f.box(x0, x1, 0, 0, z0 - 1 + d, z0 - 1 + d, "claw")
        return f
    sit = body.moved(dy=-2)
    sit.v.update(head.moved(dy=-2).v)
    sit.v.update(tail.moved(dy=-3).v)
    sit.box(1, 2, 0, 2, 7, 10, "green")
    sit.box(5, 6, 0, 2, 7, 10, "green")
    sleep = body.moved(dy=-4)
    sleep.v.update(shut_eyes(head, "green", "mouth").moved(dy=-7, dz=-1).v)
    sleep.v.update(tail.moved(dy=-5).v)
    return {"idle": stepping(0), "walk1": stepping(1), "walk2": stepping(-1), "sit": sit, "sleep": sleep}, pal, (3, 9, 3)


@pet("astro_kitten", walk=False, size=0.62)
def astro_kitten():
    pal = Palette({"cat": "#F2A65A", "white": "#FFF6EC", "suit": "#EEF1F8", "stripe": "#A855F7", "pack": "#9AA3B5",
                   "lamp": "#22D3EE", "nose": "#F27C9B", "inner": "#F7A8B8", "eye": "#151820", "eyehl": "#FFFFFF",
                   "glass": "#BFEFFF38", "collar": "#7D8597"},
                  blink={"eye": "cat", "eyehl": "cat"}, pulse={"lamp": ("#B9F6FF", 3)})
    m = Vox()
    m.box(2, 6, 0, 5, 3, 7, "suit")  # the little space suit
    m.box(2, 6, 3, 3, 3, 7, "stripe")
    m.box(2, 6, 1, 4, 8, 9, "pack")
    m.put(4, 3, 10, "lamp")
    m.box(1, 1, 2, 4, 4, 6, "suit")
    m.box(7, 7, 2, 4, 4, 6, "suit")
    head = Vox()
    head.ell(4, 9.5, 5, 3.9, 3.4, 3.3, "cat")
    for x in (3, 4, 5):
        head.front(x, 8, "white")
        head.front(x, 7, "white")
    head.front(4, 9, "nose")
    eyes2(head, (2, 5), (9, 10))
    for x0, d in ((1, 1), (7, -1)):
        head.box(min(x0, x0 + d), max(x0, x0 + d), 12, 13, 4, 5, "cat")
        head.box(x0, x0, 14, 14, 4, 5, "cat")
        head.put(x0, 13, 4, "inner")
    m.v.update(head.v)
    for x in range(-2, 11):  # the glass bubble round the head, open at the collar
        for y in range(6, 16):
            for z in range(-1, 11):
                r = math.sqrt((x - 4) ** 2 + ((y - 9.5) * 1.05) ** 2 + (z - 5) ** 2)
                if 5.1 <= r <= 5.9 and z >= 2 and (x, y, z) not in m.v:  # open at the front, so the face shows
                    m.put(x, y, z, "glass")
    for x in range(0, 9):
        for z in range(1, 10):
            if 3.2 <= math.hypot(x - 4, z - 5) <= 4.6:
                m.put(x, 5, z, "collar")
    return {"idle": m, "sleep": shut_eyes(m, "cat", "pack")}, pal, (4, 5, 2)


@pet("space_whale", walk=False, size=1.05)
def space_whale():
    pal = Palette({"blue": "#4F7FD9", "deep": "#3A5FB0", "belly": "#C3DAFF", "spot": "#FFF3B0", "eye": "#151820",
                   "eyehl": "#FFFFFF", "mouth": "#22356B", "blush": "#FF9FC4", "spout": "#7FF0FF"},
                  blink={"eye": "blue", "eyehl": "blue"}, pulse={"spout": ("#FFFFFF", 3), "spot": ("#FFD54A", 2)})
    m = Vox()
    m.ell(5, 5, 9, 5.2, 4.3, 8.8, "blue")
    for k in [k for k in m.v if k[1] <= 2]:
        m.v[k] = "belly"
    for x in range(2, 9):
        for y in (2, 3):
            m.front(x, y, "belly")
    eyes2(m, (2, 7), (5, 6))
    for x in range(4, 7):
        m.front(x, 3, "mouth")
    m.front(3, 4, "mouth")
    m.front(7, 4, "mouth")
    m.front(1, 4, "blush")
    m.front(9, 4, "blush")
    for x, z in ((3, 8), (7, 11), (5, 14), (2, 12), (8, 6)):
        m.top(x, z, "spot")
    m.box(-1, 0, 2, 3, 6, 8, "deep")
    m.box(10, 11, 2, 3, 6, 8, "deep")
    m.box(5, 5, 10, 11, 5, 5, "spout")  # a little star-shaped spout
    m.box(4, 6, 12, 12, 5, 5, "spout")
    m.box(5, 5, 12, 12, 4, 6, "spout")
    m.box(5, 5, 13, 13, 5, 5, "spout")
    m.box(3, 7, 4, 6, 18, 19, "blue")

    def flukes(y):
        f = m.copy()
        f.box(1, 9, y, y, 20, 21, "deep")
        f.box(0, 0, y + 1, y + 1, 21, 21, "deep")
        f.box(10, 10, y + 1, y + 1, 21, 21, "deep")
        return f
    return {"idle": flukes(5), "flap1": flukes(7), "flap2": flukes(3), "sleep": shut_eyes(flukes(5), "blue", "mouth")}, pal, (5, 3, 2)


@pet("star_jelly", walk=False, size=0.66)
def star_jelly():
    pal = Palette({"bell": "#B48CFFD0", "core": "#FF9AD8", "rim": "#8E62E0", "tent": "#C9A8FF", "tip": "#FFD54A",
                   "eye": "#151820", "eyehl": "#FFFFFF", "mouth": "#5B3A9C", "blush": "#FF9FC4"},
                  blink={"eye": "bell", "eyehl": "bell"}, pulse={"bell": ("#E6D6FFD0", 1), "tip": ("#FFFFFF", 2), "core": ("#FFD0F0", 1)})
    m = Vox()
    m.ell(4.5, 8, 4.5, 4.7, 4.6, 4.7, "bell")
    m.cut(-5, 15, -5, 7, -5, 15)
    m.ell(4.5, 9.5, 4.5, 2.2, 2, 2.2, "core")
    for k in [k for k in m.v if k[1] == 8]:
        m.v[k] = "rim"
    eyes2(m, (2, 6), (10, 11))
    m.front(4, 9, "mouth")
    m.front(5, 9, "mouth")
    m.front(1, 9, "blush")
    m.front(8, 9, "blush")
    spots = ((1, 2), (4, 1), (7, 2), (2, 6), (6, 7), (4, 4))

    def tentacles(phase):
        f = m.copy()
        for i, (x, z) in enumerate(spots):
            for y in range(1, 8):
                dx = round(math.sin((y + i + phase) * 1.1) * 0.8)
                f.put(x + dx, y, z, "tip" if y == 1 else "tent")
        return f
    return {"idle": tentacles(0), "flap1": tentacles(1.5), "flap2": tentacles(3), "sleep": shut_eyes(tentacles(0), "bell", "mouth")}, pal, (4, 8, 1)


@pet("star_buddy", walk=False, size=0.56)
def star_buddy():
    pal = Palette({"gold": "#FFD54A", "edge": "#F5A623", "eye": "#3A2410", "eyehl": "#FFFFFF", "mouth": "#B8611A", "blush": "#FF9FB0"},
                  blink={"eye": "gold", "eyehl": "gold"}, pulse={"gold": ("#FFF0A0", 1)})
    m = Vox()
    cx, cy, R, r = 6, 6, 6.6, 2.9

    def inside(px, py):  # a five-point star, one point up
        a = math.atan2(px - cx, py - cy)
        d = math.hypot(px - cx, py - cy)
        k = (a / (2 * math.pi / 5)) % 1
        return d <= r + (R - r) * abs(1 - 2 * k) ** 1.6
    for x in range(-1, 14):
        for y in range(-1, 14):
            if inside(x, y):
                for z in range(0, 4 if math.hypot(x - cx, y - cy) < 3.6 else 3):
                    m.put(x, y, z, "gold")
    for (x, y, z) in list(m.v):
        if any((x + dx, y + dy, z) not in m.v for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            m.v[(x, y, z)] = "edge"
    for ex in (4, 7):
        m.box(ex, ex + 1, 6, 7, 0, 0, "eye")
        m.put(ex, 7, 0, "eyehl")
    for x in (5, 6, 7):
        m.put(x, 4, 0, "mouth")
    m.put(3, 5, 0, "blush")
    m.put(9, 5, 0, "blush")
    return {"idle": m, "sleep": shut_eyes(m, "gold", "mouth")}, pal, (6, 2, 0)


@pet("baby_dragon", walk=False, size=0.9)
def baby_dragon():
    pal = Palette({"scale": "#2B2238", "belly": "#5B4A75", "wing": "#7A3FB8", "bone": "#3E2F55", "horn": "#D8D2E8",
                   "eye": "#D27BFF", "eyehl": "#FFFFFF", "dark": "#120C1C"},
                  blink={"eye": "scale", "eyehl": "scale"}, pulse={"eye": ("#F3D2FF", 2)})
    body = Vox()
    body.ell(4.5, 6, 8.5, 3.2, 3, 4.6, "scale")
    for k in [k for k in body.v if k[1] <= 4]:
        body.v[k] = "belly"
    head = Vox()
    head.ell(4.5, 9.5, 2.5, 3.9, 3.3, 3.2, "scale")
    head.box(3, 6, 7, 9, -2, -1, "scale")
    head.put(3, 9, -2, "dark")
    head.put(6, 9, -2, "dark")
    eyes2(head, (2, 6), (10, 11))
    for x in (2, 7):
        head.box(x, x, 12, 14, 3, 3, "horn")
        head.put(x, 15, 4, "horn")
    tail = Vox()
    for i, z in enumerate(range(13, 20)):
        w = 1 if i < 3 else 0
        tail.box(4 - w, 4 + w, 5 + i // 3, 6 + i // 3, z, z, "scale")
        if i % 2 == 0:
            tail.put(4, 7 + i // 3, z, "horn")
    legs = Vox()
    legs.box(2, 3, 2, 3, 7, 8, "scale")
    legs.box(6, 7, 2, 3, 7, 8, "scale")

    def wings(up):
        f = body.copy()
        f.v.update(head.v)
        f.v.update(tail.v)
        f.v.update(legs.v)
        for side in (-1, 1):
            root = 1 if side < 0 else 8
            for i in range(1, 6):
                y0 = 8 + (i if up else -(i // 2))
                for z in range(7, 12 - i // 2):
                    f.put(root + side * i, y0, z, "bone" if z == 7 else "wing")
        return f
    return {"idle": wings(True), "flap1": wings(True), "flap2": wings(False), "sleep": shut_eyes(wings(False), "scale", "dark")}, pal, (4, 6, 5)


# ---------------- writing ----------------

def model_json(vox, palette_tex, offset, gui):
    els = elements(vox, PAL_CACHE[palette_tex], offset)
    return {"texture_size": [GRID * CELL, GRID * CELL], "textures": {"p": f"cosmic:item/cosmetic/{palette_tex}", "particle": f"cosmic:item/cosmetic/{palette_tex}"},
            "elements": els, "display": {"gui": gui, "fixed": {"rotation": [0, 180, 0], "scale": [0.8, 0.8, 0.8]},
                                          "ground": {"translation": [0, 2, 0], "scale": [0.4, 0.4, 0.4]}}}


PAL_CACHE = {}


def build():
    """id -> (poses dict(pose -> Vox), palette, meta)."""
    out = {}
    for name, (fn, walk, size) in PETS.items():
        poses, pal, neck = fn()
        out[name] = (poses, pal, walk, size, neck)
    return out


def write(out_dir, meta_path):
    import cosmetics  # gui_pose: fit the icon in the slot
    tex = out_dir / "assets/cosmic/textures/item/cosmetic"
    models = out_dir / "assets/cosmic/models/cosmetic"
    items = out_dir / "assets/cosmic/items/cosmetic"
    for d in (tex, models, items):
        d.mkdir(parents=True, exist_ok=True)
    meta = {}
    for name, (poses, pal, walk, size, neck) in build().items():
        (lo, hi) = bounds(poses["idle"])
        centre = [(a + b) / 2 for a, b in zip(lo, hi)]
        offset = [8 - centre[0], 8 - centre[1], 8 - centre[2]]
        longest = max(b - a for a, b in zip(lo, hi))
        for variant, shade in (("", None), ("_shiny", gold), ("_locked", dark)):
            pname = f"{name}_palette{variant}"
            pal.image(shade).save(tex / f"{pname}.png")
            (tex / f"{pname}.png.mcmeta").write_text(json.dumps({"animation": {"frametime": 2}}), encoding="utf-8")
            PAL_CACHE[pname] = pal
            for pose, vox in poses.items():
                if variant == "_locked" and pose != "idle":
                    continue
                mid = name + variant + ("" if pose == "idle" else "_" + pose)
                gui = cosmetics.gui_pose(elements(poses["idle"], pal, offset), (25, 145, 0))
                (models / f"{mid}.json").write_text(json.dumps(model_json(vox, pname, offset, gui)), encoding="utf-8")
                (items / f"{mid}.json").write_text(json.dumps({"model": {"type": "minecraft:model", "model": f"cosmic:cosmetic/{mid}"}}), encoding="utf-8")
        meta[name] = {"walk": walk, "scale": round(size * 16 / longest, 3), "feet": lo[1] + offset[1], "top": hi[1] + offset[1],
                      "neck": [neck[0] + 0.5 + offset[0], neck[1] + 0.5 + offset[1], neck[2] + offset[2]],
                      "poses": [p for p in poses if p != "idle"]}
    if meta_path is not None:
        old = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        old.update(meta)
        meta_path.write_text(json.dumps(old, indent=1), encoding="utf-8")
    return len(meta)


# ---------------- preview: an iso render of the voxels, every face in its colour ----------------

def render(vox, pal, scale=12, yaw=35, pitch=28, frame=0, size=(360, 300), bg=(46, 40, 70)):
    cols = pal.frame(frame)
    a, b = math.radians(yaw), math.radians(pitch)
    light = {"up": 1.0, "north": 0.86, "west": 0.74, "east": 0.6, "south": 0.66, "down": 0.45}
    (lo, hi) = bounds(vox)
    c = [(p + q) / 2 for p, q in zip(lo, hi)]
    polys = []
    corners = {"north": [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], "south": [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)],
               "west": [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)], "east": [(1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)],
               "down": [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)], "up": [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]}

    def project(x, y, z):
        x, y, z = x - c[0], y - c[1], z - c[2]
        xr, zr = x * math.cos(a) - z * math.sin(a), x * math.sin(a) + z * math.cos(a)
        yr, zr2 = y * math.cos(b) + zr * math.sin(b), -y * math.sin(b) + zr * math.cos(b)
        return xr, yr, zr2

    clear = {n for n in set(vox.v.values()) if len(pal.base[n]) > 3}
    middle = {n: [sum(k[i] for k in vox.v if vox.v[k] == n) / sum(1 for k in vox.v if vox.v[k] == n) for i in range(3)] for n in clear}
    for (x, y, z), name in vox.v.items():
        for f, (dx, dy, dz) in DIRS.items():
            if (x + dx, y + dy, z + dz) in vox.v:
                continue
            if name in clear and dx * (x - middle[name][0]) + dy * (y - middle[name][1]) + dz * (z - middle[name][2]) < 0:
                continue
            pts = [project(x + p[0], y + p[1], z + p[2]) for p in corners[f]]
            depth = sum(p[2] for p in pts) / 4
            col = tuple(int(v * light[f]) for v in cols[name][:3]) + (cols[name][3] if len(cols[name]) > 3 else 255,)
            polys.append((depth, [(size[0] / 2 + p[0] * scale, size[1] * 0.55 - p[1] * scale) for p in pts], col))
    from PIL import ImageDraw
    img = Image.new("RGBA", size, bg + (255,))
    d = ImageDraw.Draw(img, "RGBA")
    for _, pts, col in sorted(polys, key=lambda t: -t[0]):
        d.polygon(pts, fill=col)
    return img


if __name__ == "__main__":  # python -I voxels.py <out.png>: every pet in every pose
    import sys
    built = build()
    rows = []
    for name, (poses, pal, walk, size, neck) in built.items():
        tiles = [render(v, pal) for v in poses.values()] + [render(poses["idle"], pal, yaw=200)]
        row = Image.new("RGBA", (360 * len(tiles), 300))
        for i, t in enumerate(tiles):
            row.paste(t, (360 * i, 0))
        rows.append(row)
    sheet = Image.new("RGBA", (max(r.width for r in rows), 300 * len(rows)), (30, 26, 46, 255))
    for i, r in enumerate(rows):
        sheet.paste(r, (0, 300 * i))
    sheet.save(sys.argv[1])
    for name, (poses, pal, *_ ) in built.items():
        print(name, {p: len(boxes(v)) for p, v in poses.items()}, "boxes")
