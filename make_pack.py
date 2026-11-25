"""Builds the Cosmic Craft resource pack -> cosmic-pack.zip (next to this script).

Art becomes glyphs in Minecraft's own font (minecraft:default), so any text can show it with a plain character:
rank tags (LuckPerms prefixes), chat, the tab list, name tags, titles.

  U+E000           the logo, 56 px tall, hanging ~6 lines below its own line (tab header)
  U+E001..U+E00C   the logo with a diagonal shine sweeping across it (12 frames)
  U+E010           the logo, small, for the welcome title
  U+E011..U+E014   the title logo popping in (4 sizes), U+E015..U+E020 the title logo's shine (12 frames)
  U+E100..U+E105   rank badges: owner, admin, mod, creator, vip, member (11 px pills from Claude Design)
  U+E110..U+E115   rank icons, same order (7x7)
  U+E120..U+E127   the owner badge with a moving glint (8 frames, for the tab list)
  U+E130           the Cosmic Coin, text-sized (8 px)
  U+E140..U+E143   playtime ranks after the name (Explorer compass, Veteran diamond, Legend nether star) and the tab's
                   playtime clock: Minecraft's own textures, by path (CosmicCraft plugin Playtime.java)
  U+E200..         item icons for the price book: Minecraft's own textures, referenced by path (nothing of Mojang's is copied)
  U+F801..U+F820   blank spaces of 1-32 px, U+F701..U+F720 the same backwards: exact layout in books

Item models (data component item_model, set by the CosmicCraft plugin):
  cosmic:cosmetic/<id>  the Cosmic Wardrobe's hats and pets (cosmetics.py)
  cosmic:coin      the Cosmic Coin you can hold: a 3D coin 2 px thick built from 7 slices that make a circle,
                   gold reeded edge, a glint sweeping across the face every few seconds. Textures come from
                   src/coin_face_16.png, coin_back_16.png, coin_edge_16.png (Claude Design, claude-design-coin.md);
                   until those arrive they are made from src/coin_16.png. In the inventory it spins (src/coin_spin, 12 frames).

The logo frames are also in the font minecraft:cosmic, which older tab styles use.

book_font.json (next to this script) is for the CosmicCraft plugin's price book: which character is which icon,
and the width of every character, measured from the 26.3 client's font sheets (MC_CLIENT_JAR, default: Fabric
Loom's cache), so the book can line prices up to the pixel.

python -I make_pack.py
"""
import json
import os
import shutil
import sys
import zipfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # python -I leaves the script's folder out
import cosmetics  # noqa: E402
SRC = HERE / "src"
OUT = HERE / "build"
RANKS = ["owner", "admin", "mod", "creator", "vip", "member"]
SHINE_FRAMES = 12
LOGO_HEIGHT = 56   # on-screen height in GUI pixels
LOGO_ASCENT = 7    # top of the logo sits at the top of its text line; it hangs ~6 lines down
BADGE_ASCENT = 8   # 11 px pills, centred on a text line: 1 px above the letters, 2 below
JAR = Path(os.environ.get("MC_CLIENT_JAR", Path.home() / ".gradle/caches/fabric-loom/26.3/minecraft-client.jar"))
COIN = 0xE130
SPACES = {n: 0xF800 + n for n in (1, 2, 4, 8, 16, 32)} | {-n: 0xF700 + n for n in (1, 2, 4, 8, 16, 32)}
# material -> vanilla texture (under assets/minecraft/textures); the bank's worth.yml items
PRICE_ICONS = {
    "netherite_ingot": "item/netherite_ingot", "ancient_debris": "block/ancient_debris_side", "diamond": "item/diamond",
    "emerald": "item/emerald", "gold_ingot": "item/gold_ingot", "iron_ingot": "item/iron_ingot", "copper_ingot": "item/copper_ingot",
    "coal": "item/coal", "redstone": "item/redstone", "lapis_lazuli": "item/lapis_lazuli", "quartz": "item/quartz",
    "amethyst_shard": "item/amethyst_shard", "ender_pearl": "item/ender_pearl", "blaze_rod": "item/blaze_rod",
    "gunpowder": "item/gunpowder", "slime_ball": "item/slime_ball", "bone": "item/bone", "string": "item/string",
    "leather": "item/leather", "wheat": "item/wheat", "carrot": "item/carrot", "potato": "item/potato",
    "sugar_cane": "item/sugar_cane", "pumpkin": "block/pumpkin_side", "melon_slice": "item/melon_slice",
    "oak_log": "block/oak_log", "spruce_log": "block/spruce_log", "birch_log": "block/birch_log", "jungle_log": "block/jungle_log",
    "acacia_log": "block/acacia_log", "dark_oak_log": "block/dark_oak_log", "cherry_log": "block/cherry_log",
    "mangrove_log": "block/mangrove_log",
    # pause-menu buttons (cosmic-paper/tools/menu.py)
    "ender_eye": "item/ender_eye", "book": "item/book", "nether_star": "item/nether_star", "oak_sapling": "block/oak_sapling",
    "gold_nugget": "item/gold_nugget", "writable_book": "item/writable_book", "golden_helmet": "item/golden_helmet",
}
# The pause screen's own buttons, while connected to Cosmic Craft (English for every client language)
LANG = {"menu.disconnect": "Leave Cosmic Craft", "menu.returnToGame": "Back to the Cosmos", "menu.server_links": "Cosmic Links"}

shutil.rmtree(OUT, ignore_errors=True)
tex = OUT / "assets/cosmic/textures/font"
for sub in ("", "badges", "icons", "owner_anim"):
    (tex / sub).mkdir(parents=True, exist_ok=True)
(OUT / "assets/minecraft/font").mkdir(parents=True)

logo = Image.open(SRC / "cosmic_craft_256.png").convert("RGBA")
logo = logo.crop(logo.getchannel("A").getbbox())
pad = Image.new("RGBA", (logo.width + 4, logo.height + 4), (0, 0, 0, 0))
pad.paste(logo, (2, 2), logo)
logo = pad
w, h = logo.size


def shine(img, t):
    """A soft white band along x + y/2, centred at fraction t of the sweep; only where the logo is."""
    out = img.copy()
    px = out.load()
    centre = -0.3 * w + t * 1.6 * w
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            d = abs((x + y * 0.5) - centre)
            k = max(0.0, 1 - d / (w * 0.09)) * 0.8
            px[x, y] = (round(r + (255 - r) * k), round(g + (255 - g) * k), round(b + (255 - b) * k), a)
    return out


def glyph(file, char, height, ascent):
    return {"type": "bitmap", "file": f"cosmic:font/{file}", "ascent": ascent, "height": height, "chars": [char]}


logo_glyphs = []
for i in range(SHINE_FRAMES + 1):
    frame = logo if i == 0 else shine(logo, (i - 1) / (SHINE_FRAMES - 1))
    frame.save(tex / f"logo_{i:02d}.png")
    logo_glyphs.append(glyph(f"logo_{i:02d}.png", chr(0xE000 + i), LOGO_HEIGHT, LOGO_ASCENT))

default = list(logo_glyphs)
default.append(glyph("logo_00.png", "", 16, 12))
# Welcome intro: the title logo pops in (U+E011..E014: small, bigger, overshoot, settle), then a shine
# crosses it (U+E015..E020 reuse the 12 shine frames). Ascent keeps each size centred on the same point.
for i, size in enumerate((6, 11, 19, 16)):
    default.append(glyph("logo_00.png", chr(0xE011 + i), size, round(size * 0.75)))
for i in range(SHINE_FRAMES):
    default.append(glyph(f"logo_{i + 1:02d}.png", chr(0xE015 + i), 16, 12))
for i, rank in enumerate(RANKS):
    shutil.copy(SRC / "badges" / f"{rank}.png", tex / "badges" / f"{rank}.png")
    shutil.copy(SRC / "icons" / f"{rank}.png", tex / "icons" / f"{rank}.png")
    default.append(glyph(f"badges/{rank}.png", chr(0xE100 + i), 11, BADGE_ASCENT))
    default.append(glyph(f"icons/{rank}.png", chr(0xE110 + i), 7, 7))
for i, frame in enumerate(sorted((SRC / "owner_anim").glob("owner_*.png"))):
    shutil.copy(frame, tex / "owner_anim" / frame.name)
    default.append(glyph(f"owner_anim/{frame.name}", chr(0xE120 + i), 11, BADGE_ASCENT))

shutil.copy(SRC / "coin_16.png", tex / "coin_16.png")
default.append(glyph("coin_16.png", chr(COIN), 8, 7))
for i, (material, texture) in enumerate(PRICE_ICONS.items()):
    default.append({"type": "bitmap", "file": f"minecraft:{texture}.png", "ascent": 7, "height": 8, "chars": [chr(0xE200 + i)]})
for cp, texture in {0xE140: "item/compass_00", 0xE141: "item/diamond", 0xE142: "item/nether_star", 0xE143: "item/clock_00"}.items():
    default.append({"type": "bitmap", "file": f"minecraft:{texture}.png", "ascent": 7, "height": 8, "chars": [chr(cp)]})
default.append({"type": "space", "advances": {chr(cp): n for n, cp in SPACES.items()}})


COIN_SLICES = [(5, 11, 0, 1), (3, 13, 1, 2), (2, 14, 2, 3), (1, 15, 3, 5), (0, 16, 5, 11), (1, 15, 11, 13), (2, 14, 13, 14), (3, 13, 14, 15),
               (5, 11, 15, 16)]  # x1, x2, y1, y2: the silhouette of src/coin_face_16.png (Claude Design), row by row


def coin_textures():
    """Face (with glint animation strip), back and edge. Claude Design art if present, else made from the 16 px coin."""
    def load(name, fallback):
        p = SRC / name
        return Image.open(p).convert("RGBA") if p.exists() else fallback()

    def placeholder_face():
        face = Image.open(SRC / "coin_16.png").convert("RGBA")
        mask = Image.new("L", (16, 16), 0)
        for x1, x2, y1, y2 in COIN_SLICES:  # keep exactly the model's silhouette (texture y runs down)
            mask.paste(255, (x1, 16 - y2, x2, 16 - y1))
        out = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
        out.paste(face, (0, 0), mask)
        return out

    def placeholder_edge():
        edge = Image.new("RGBA", (16, 16))
        for x in range(16):
            for y in range(16):
                light = (255, 213, 74) if x % 2 == 0 else (184, 134, 11)
                k = 1.08 - y / 30  # lighter on top so it reads as round
                edge.putpixel((x, y), tuple(min(255, int(c * k)) for c in light) + (255,))
        return edge

    face = load("coin_face_16.png", placeholder_face)
    back = load("coin_back_16.png", lambda: face.transpose(Image.FLIP_LEFT_RIGHT))
    edge = load("coin_edge_16.png", placeholder_edge)
    frames = [face]
    for i in range(6):  # a glint sweeping across, only where the coin is
        f = face.copy()
        px = f.load()
        centre = -2 + i * 3.6
        for y in range(16):
            for x in range(16):
                r, g, b, a = px[x, y]
                k = max(0.0, 1 - abs((x + y) / 2 - centre) / 2.2) * 0.75
                if a and k:
                    px[x, y] = (round(r + (255 - r) * k), round(g + (255 - g) * k), round(b + (255 - b) * k), a)
        frames.append(f)
    strip = Image.new("RGBA", (16, 16 * len(frames)))
    for i, f in enumerate(frames):
        strip.paste(f, (0, 16 * i))
    return strip, back, edge


def coin_model():
    elements = []
    for x1, x2, y1, y2 in COIN_SLICES:
        v1, v2 = 16 - y2, 16 - y1
        elements.append({"from": [x1, y1, 7], "to": [x2, y2, 9], "faces": {
            "south": {"uv": [x1, v1, x2, v2], "texture": "#face"},
            "north": {"uv": [x2, v1, x1, v2], "texture": "#back"},   # flipped: it is read from behind
            "up": {"uv": [x1, 0, x2, 2], "texture": "#edge"}, "down": {"uv": [x1, 14, x2, 16], "texture": "#edge"},
            "east": {"uv": [7, v1, 9, v2], "texture": "#edge"}, "west": {"uv": [7, v1, 9, v2], "texture": "#edge"}}})
    return {"textures": {"face": "cosmic:item/coin_face", "back": "cosmic:item/coin_back", "edge": "cosmic:item/coin_edge",
                         "particle": "cosmic:item/coin_edge"},
            "gui_light": "front",
            "elements": elements,
            "display": {  # vanilla item/generated poses; the inventory icon turned a little so it reads as 3D
                "gui": {"rotation": [15, -30, 0], "scale": [0.9, 0.9, 0.9]},
                "ground": {"translation": [0, 2, 0], "scale": [0.5, 0.5, 0.5]},
                "head": {"rotation": [0, 180, 0], "translation": [0, 13, 7]},
                "thirdperson_righthand": {"translation": [0, 3, 1], "scale": [0.55, 0.55, 0.55]},
                "firstperson_righthand": {"rotation": [0, -90, 25], "translation": [1.13, 3.2, 1.13], "scale": [0.68, 0.68, 0.68]},
                "fixed": {"rotation": [0, 180, 0]}}}


items_tex = OUT / "assets/cosmic/textures/item"
items_tex.mkdir(parents=True)
face_strip, coin_back, coin_edge = coin_textures()
face_strip.save(items_tex / "coin_face.png")
(items_tex / "coin_face.png.mcmeta").write_text(json.dumps({"animation": {"frames": [{"index": 0, "time": 70}] + [
    {"index": i, "time": 2} for i in range(1, face_strip.height // 16)]}}), encoding="utf-8")
coin_back.save(items_tex / "coin_back.png")
coin_edge.save(items_tex / "coin_edge.png")
(OUT / "assets/cosmic/models/item").mkdir(parents=True)
(OUT / "assets/cosmic/models/item/coin.json").write_text(json.dumps(coin_model(), indent=1), encoding="utf-8")
# In the inventory the coin spins (Claude Design's 12 frames); held, dropped or displayed it is the 3D coin.
spin = sorted((SRC / "coin_spin").glob("coin_spin_*.png"))
strip = Image.new("RGBA", (16, 16 * len(spin)))
for i, frame in enumerate(spin):
    strip.paste(Image.open(frame).convert("RGBA"), (0, 16 * i))
strip.save(items_tex / "coin_spin.png")
(items_tex / "coin_spin.png.mcmeta").write_text(json.dumps({"animation": {"frametime": 3}}), encoding="utf-8")
(OUT / "assets/cosmic/models/item/coin_icon.json").write_text(json.dumps({"parent": "minecraft:item/generated",
                                                                          "textures": {"layer0": "cosmic:item/coin_spin"}}), encoding="utf-8")
(OUT / "assets/cosmic/items").mkdir(parents=True)
(OUT / "assets/cosmic/items/coin.json").write_text(json.dumps({"model": {
    "type": "minecraft:select", "property": "minecraft:display_context",
    "cases": [{"when": "gui", "model": {"type": "minecraft:model", "model": "cosmic:item/coin_icon"}}],
    "fallback": {"type": "minecraft:model", "model": "cosmic:item/coin"}}}, indent=1), encoding="utf-8")


def advance(img, height, cell_w, cell_h, col=0, row=0):
    """Minecraft's bitmap rule: rightmost non-transparent column + 1, scaled to the glyph height, rounded, + 1."""
    a = img.getchannel("A").load()
    width = 0
    for x in range(cell_w - 1, -1, -1):
        if any(a[col * cell_w + x, row * cell_h + y] for y in range(cell_h)):
            width = x + 1
            break
    return int(0.5 + width * height / cell_h) + 1


def measure():
    """Widths of text characters (vanilla providers, first match wins), the coin, the icons and the spaces."""
    widths = {" ": 4}
    with zipfile.ZipFile(JAR) as jar:
        def tex(path):
            return Image.open(jar.open(f"assets/minecraft/textures/{path}")).convert("RGBA")
        for p in json.loads(jar.read("assets/minecraft/font/include/default.json"))["providers"]:
            img = tex(p["file"].split(":")[1])
            rows = p["chars"]
            cw, ch = img.width // len(rows[0]), img.height // len(rows)
            for r, line in enumerate(rows):
                for c, char in enumerate(line):
                    keep = 0x20 < ord(char) < 0x180 or 0x370 <= ord(char) < 0x400 or 0x2010 <= ord(char) < 0x2030  # Latin, Greek, dashes
                    if keep and char not in widths:
                        widths[char] = advance(img, p.get("height", 8), cw, ch, c, r)
        icons = {}
        for i, (material, texture) in enumerate(PRICE_ICONS.items()):
            img = tex(texture + ".png")
            assert img.size == (16, 16), f"{texture} is {img.size}, not one 16x16 frame"
            icons[material] = chr(0xE200 + i)
            widths[icons[material]] = advance(img, 8, 16, 16)
    coin = Image.open(SRC / "coin_16.png").convert("RGBA")
    widths[chr(COIN)] = advance(coin, 8, coin.width, coin.height)
    for n, cp in SPACES.items():
        widths[chr(cp)] = n
    return {"coin": chr(COIN), "icons": icons, "spaces": {str(n): chr(cp) for n, cp in SPACES.items()}, "widths": widths}


if JAR.exists():
    book = measure()
    (HERE / "book_font.json").write_text(json.dumps(book, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"book_font.json: {len(book['widths'])} widths, {len(book['icons'])} icons")
else:
    print(f"no client jar at {JAR}: book_font.json left as it was")

(OUT / "assets/minecraft/lang").mkdir(parents=True)
for lang in ("en_us", "en_gb", "el_gr"):
    (OUT / f"assets/minecraft/lang/{lang}.json").write_text(json.dumps(LANG, indent=1), encoding="utf-8")

# Font files from every pack are merged, so this only adds our characters to Minecraft's default font.
n_cosmetics = cosmetics.write(OUT, SRC)  # the Cosmic Wardrobe's hats and pets (cosmetics.py)

(OUT / "assets/minecraft/font/default.json").write_text(json.dumps({"providers": default}, indent=1), encoding="utf-8")
(OUT / "assets/minecraft/font/cosmic.json").write_text(json.dumps({"providers": logo_glyphs}, indent=1), encoding="utf-8")
(OUT / "pack.mcmeta").write_text(json.dumps({"pack": {
    "description": "§5✦ §dCosmic Craft §5✦ §7Season 2",
    "min_format": [97, 0],
    "max_format": [97, 1]}}, ensure_ascii=False, indent=2), encoding="utf-8")
icon = Image.new("RGBA", (max(w, h),) * 2, (0, 0, 0, 0))
icon.paste(logo, ((icon.width - w) // 2, (icon.height - h) // 2), logo)
icon.resize((128, 128), Image.LANCZOS).save(OUT / "pack.png")

zip_path = HERE / "cosmic-pack.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(OUT.rglob("*")):
        if f.is_file():
            z.write(f, f.relative_to(OUT).as_posix())
print(f"{zip_path.name}: {zip_path.stat().st_size // 1024} KB, {len(default)} glyphs in minecraft:default, {n_cosmetics} cosmetics")
