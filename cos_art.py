"""Pixel-art and model helpers shared by the cosmetic files (cos_hats.py, cos_things.py, cos_icons.py)."""
import math
import random

from PIL import Image

from cosmetics import FACES, blank, box, shade

INK = (30, 22, 42)          # eyes and outlines
WHITE = (255, 255, 255)
BLUSH = (255, 128, 160)
PURPLE, CYAN, GOLD = (168, 85, 247), (34, 211, 238), (255, 213, 74)
BLINK = {"frames": [{"index": 0, "time": 76}, {"index": 1, "time": 4}]}  # open ~4 s, then a quick blink


# ---------------- pixels ----------------

def put(img, pts, c):
    c = tuple(c) if len(c) == 4 else tuple(c) + (255,)
    for x, y in pts:
        if 0 <= x < img.width and 0 <= y < img.height:
            img.putpixel((x, y), c)
    return img


def rect(img, x0, y0, x1, y1, c):  # corners inclusive
    return put(img, [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)], c)


def tex(base, seed, var=0.07, w=16, h=None, alpha=255):
    """A flat colour with soft pixel noise, a little lighter towards the top-left (Minecraft's light)."""
    r = random.Random(seed)
    h = h or w
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            k = 1 + r.uniform(-var, var) + 0.08 * (1 - (x / w + y / h))
            img.putpixel((x, y), shade(base, k) + (alpha,))
    return img


def speckle(img, c, n, seed, region=None):
    r = random.Random(seed)
    x0, y0, x1, y1 = region or (0, 0, img.width - 1, img.height - 1)
    return put(img, [(r.randint(x0, x1), r.randint(y0, y1)) for _ in range(n)], c)


def disc(img, cx, cy, rad, c):
    return put(img, [(x, y) for y in range(img.height) for x in range(img.width) if math.hypot(x + 0.5 - cx, y + 0.5 - cy) <= rad], c)


def eyes(img, y=6, xs=(3, 10), closed=False, iris=None, h=4, w=3):
    """Two big chibi eyes (w x h) with a white highlight; closed = happy curved lines."""
    for x in xs:
        if closed:
            put(img, [(x, y + h - 2), (x + w - 1, y + h - 2)] + [(x + i, y + h - 1) for i in range(1, w - 1)], INK)
        else:
            rect(img, x, y, x + w - 1, y + h - 1, INK)
            put(img, [(x, y), (x + 1, y)] if w > 2 else [(x, y)], WHITE)
            put(img, [(x + w - 1, y + h - 1)], iris or (90, 80, 130))
    return img


def cheeks(img, y=10, xs=(1, 13), c=BLUSH):
    return put(img, [(x, y) for x in xs] + [(x + 1, y) for x in xs], c)


def mouth(img, y=11, kind="w", c=(80, 30, 50)):
    pts = {"w": [(5, y), (6, y + 1), (7, y), (8, y), (9, y + 1), (10, y)],
           "smile": [(6, y), (7, y + 1), (8, y + 1), (9, y)],
           "o": [(7, y), (8, y), (7, y + 1), (8, y + 1)],
           "wide": [(4, y), (5, y + 1), (6, y + 1), (7, y + 1), (8, y + 1), (9, y + 1), (10, y + 1), (11, y)]}[kind]
    return put(img, pts, c)


def face(base, seed, under=None, over=None, eye_y=6, xs=(3, 10), mouth_kind="w", mouth_y=None, iris=None, blush=True, eh=4, ew=3):
    """A pet face: [open, blink] frames (use with BLINK). under(img) paints markings first, over(img) after."""
    out = []
    for closed in (False, True):
        f = tex(base, seed)
        if under:
            under(f)
        eyes(f, eye_y, xs, closed, iris, eh, ew)
        if blush:
            cheeks(f, eye_y + eh)
        if mouth_kind:
            mouth(f, mouth_y if mouth_y is not None else eye_y + eh + 1, mouth_kind)
        if over:
            over(f)
        out.append(f)
    return out


def tiger_stripes(img, c=(44, 28, 22)):
    """Tapered black stripes coming down from the top edge."""
    for x0 in range(1, img.width, 5):
        for y in range(min(img.height, 6)):
            put(img, [(x0 + y // 3, y)] + ([(x0 + 1 + y // 3, y)] if y < 3 else []), c)
    return img


def shift(img, dx, dy):
    """Scrolls the image with wrap-around (for seamless looping strips)."""
    out = blank(img.width) if img.width == img.height else Image.new("RGBA", img.size, (0, 0, 0, 0))
    for y in range(img.height):
        for x in range(img.width):
            out.putpixel(((x + dx) % img.width, (y + dy) % img.height), img.getpixel((x, y)))
    return out


def pulse(img, k):
    """Brightness k (1 = unchanged) on opaque pixels."""
    out = img.copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = shade((r, g, b), k) + (a,)
    return out


def outline(img, c=INK):
    """A 1-pixel outline round the opaque shapes (on the transparent pixels next to them)."""
    out = img.copy()
    src = img.load()
    for y in range(img.height):
        for x in range(img.width):
            if src[x, y][3] == 0 and any(0 <= x + dx < img.width and 0 <= y + dy < img.height and src[x + dx, y + dy][3] > 0
                                         for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                out.putpixel((x, y), tuple(c) + (255,))
    return out


def star_shape(n=16, r_out=7.6, r_in=3.4, cx=7.5, cy=8.0):
    pts = []
    for y in range(n):
        for x in range(n):
            a = math.atan2(-(y + 0.5 - cy), x + 0.5 - cx)
            d = math.hypot(x + 0.5 - cx, y + 0.5 - cy)
            k = ((a - math.pi / 2) % (2 * math.pi / 5)) / (2 * math.pi / 5)  # 0..1 between two points
            lim = r_in + (r_out - r_in) * abs(1 - 2 * k) ** 1.6
            if d <= lim:
                pts.append((x, y, d / lim))
    return pts


def twinkle(base, seed, n=8, dots=6, bright=(255, 255, 240), var=0.07, alpha=255):
    """Stars in a texture blinking one after another (seamless loop)."""
    r = random.Random(seed)
    spots = [(r.randrange(16), r.randrange(16), r.random()) for _ in range(dots)]
    out = []
    for i in range(n):
        f = tex(base, seed, var, alpha=alpha)
        for x, y, ph in spots:
            k = 0.5 + 0.5 * math.cos(2 * math.pi * (i / n - ph))
            c = tuple(round(shade(base, 1.3)[j] + (bright[j] - shade(base, 1.3)[j]) * k) for j in range(3))
            put(f, [(x, y)], c)
            if k > 0.8:
                put(f, [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)], shade(c, 0.8))
        out.append(f)
    return out


def silhouette(img):
    """A dark purple-black version keeping the shape (for icons the player has not unlocked)."""
    out = img.convert("RGBA").copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = ((22, 14, 32) if 0.3 * r + 0.59 * g + 0.11 * b < 60 else (58, 42, 84)) + (a,)
    return out


GOLD_RAMP = [(0.0, (46, 24, 6)), (0.3, (140, 80, 14)), (0.55, (222, 160, 34)), (0.78, (255, 214, 84)), (1.0, (255, 250, 214))]


def to_gold(img):
    """Maps each pixel's brightness onto a gold ramp, keeping alpha (for the shiny pets)."""
    out = img.convert("RGBA").copy()
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            r, g, b, a = px[x, y]
            t = min(1.0, max(0.0, ((0.3 * r + 0.59 * g + 0.11 * b) / 255 - 0.06) / 0.88))
            for (t0, c0), (t1, c1) in zip(GOLD_RAMP, GOLD_RAMP[1:]):
                if t <= t1:
                    k = (t - t0) / (t1 - t0)
                    px[x, y] = tuple(round(c0[i] + (c1[i] - c0[i]) * k) for i in range(3)) + (a,)
                    break
    return out


# ---------------- models ----------------

def tx(default, **faces):
    """Per-face texture keys: tx("skin", north="face")."""
    return {f: faces.get(f, default) for f in FACES}


def mirrored(e):
    """The same element mirrored across x = 8 (east and west swap, y/z rotations flip)."""
    m = {"from": [16 - e["to"][0], e["from"][1], e["from"][2]], "to": [16 - e["from"][0], e["to"][1], e["to"][2]],
         "faces": {{"east": "west", "west": "east"}.get(f, f): v for f, v in e["faces"].items()}}
    for k in ("light_emission", "shade"):
        if k in e:
            m[k] = e[k]
    if "rotation" in e:
        r = e["rotation"]
        m["rotation"] = {"origin": [16 - r["origin"][0], *r["origin"][1:]], "axis": r["axis"],
                         "angle": r["angle"] if r["axis"] == "x" else -r["angle"]}
    return m


def pair(*a, **k):
    e = box(*a, **k)
    return [e, mirrored(e)]


def corners(e):
    (x1, y1, z1), (x2, y2, z2) = e["from"], e["to"]
    pts = [(x, y, z) for x in (x1, x2) for y in (y1, y2) for z in (z1, z2)]
    r = e.get("rotation")
    if not r:
        return pts
    o, a = r["origin"], math.radians(r["angle"])
    out = []
    for p in pts:
        x, y, z = (p[i] - o[i] for i in range(3))
        if r["axis"] == "x":
            y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
        elif r["axis"] == "y":
            x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
        else:
            x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        out.append((x + o[0], y + o[1], z + o[2]))
    return out


def bounds(elements):
    pts = [p for e in elements for p in corners(e)]
    return [min(p[i] for p in pts) for i in range(3)], [max(p[i] for p in pts) for i in range(3)]


def moved(elements, d):
    """Shifts elements (and their rotation origins) by d."""
    for e in elements:
        e["from"] = [round(v + d[i], 3) for i, v in enumerate(e["from"])]
        e["to"] = [round(v + d[i], 3) for i, v in enumerate(e["to"])]
        if "rotation" in e:
            e["rotation"]["origin"] = [round(v + d[i], 3) for i, v in enumerate(e["rotation"]["origin"])]
    return elements


def centre(elements, *points):
    """Moves the model so its bounding box is centred on 8,8,8; returns the shift applied to the given points too."""
    lo, hi = bounds(elements)
    d = [round(8 - (l + h) / 2, 2) for l, h in zip(lo, hi)]
    moved(elements, d)
    return [[round(p[i] + d[i], 2) for i in range(3)] for p in points]
