"""The Cosmic Wardrobe's painted screen: a font (cosmic:wardrobe) whose glyphs are drawn by the menu's title.

The CosmicCraft plugin writes the title as: shift, the background glyph, then for each slot a frame glyph moved to that
slot, then the tab's name. Items are drawn over title glyphs (26.3's GUI puts a later overlapping element on a higher
layer), so the background can be fully opaque.

Glyphs (keep in step with WardrobeMenu.java):
  U+E000            the background, 176x222 (the 6-row chest screen incl. your inventory), ascent 13 = its top at the
                    screen's top edge (the title is drawn at y 6, a glyph's top at y + 7 - ascent)
  U+E001            the same look for a 3-row chest (176x168: the title, three shelf rows, your inventory), for the
                    world menu (WorldMenu.java); cut from the big one so they always match
  U+E100 + 8*k + r  an 18x18 frame round a chest slot of row r (0..5), style k: 0 common, 1 rare, 2 epic,
                    3 legendary, 4 mythic, 5 worn (the one you wear), 6 tab (the open tab)
  U+F801..U+F809    spaces of -1, -2, -4 ... -256 px; U+F811..U+F819 spaces of +1 ... +256 px
Art: src/wardrobe/bg.png (176x222) and src/wardrobe/frame_<style>.png (18x18, transparent middle) from Claude Design
(claude-design-wardrobe-ui.md), otherwise the placeholders below. Font textures cannot animate (Minecraft ignores
.mcmeta for fonts); the moving parts are the item icons on top.
"""
import json
import random

from PIL import Image, ImageDraw

STYLES = ["common", "rare", "epic", "legendary", "mythic", "worn", "tab"]
COLOURS = {"common": (170, 170, 190), "rare": (34, 211, 238), "epic": (168, 85, 247), "legendary": (255, 213, 74),
           "mythic": (255, 85, 110), "worn": (120, 255, 200), "tab": (255, 255, 255)}


def placeholder_bg():
    img = Image.new("RGBA", (176, 222), (22, 16, 44, 255))
    d = ImageDraw.Draw(img)
    rnd = random.Random(7)
    for _ in range(90):  # stars
        x, y = rnd.randrange(176), rnd.randrange(222)
        img.putpixel((x, y), (200, 190, 255, 255) if rnd.random() < 0.8 else (255, 213, 74, 255))
    d.rectangle((0, 0, 175, 221), outline=(168, 85, 247, 255), width=2)
    d.rectangle((3, 3, 172, 218), outline=(80, 50, 140, 255))
    d.rectangle((4, 4, 171, 15), fill=(40, 26, 80, 255))  # the title strip
    d.line((6, 133, 169, 133), fill=(34, 211, 238, 255))  # between the Wardrobe and your inventory

    def cell(x, y, fill):
        d.rectangle((x - 1, y - 1, x + 16, y + 16), fill=fill)
        d.line((x - 1, y - 1, x + 16, y - 1), fill=(10, 6, 22, 255))
        d.line((x - 1, y - 1, x - 1, y + 16), fill=(10, 6, 22, 255))
        d.line((x - 1, y + 16, x + 16, y + 16), fill=(90, 70, 150, 255))
        d.line((x + 16, y - 1, x + 16, y + 16), fill=(90, 70, 150, 255))
    for r in range(6):
        for c in range(9):
            cell(8 + c * 18, 18 + r * 18, (52, 36, 96, 255) if r in (0, 5) else (34, 24, 66, 255))
    for r in range(3):  # your inventory: items at y 139 + 18r, the hotbar at 197 (vanilla ChestMenu)
        for c in range(9):
            cell(8 + c * 18, 139 + r * 18, (34, 24, 66, 255))
    for c in range(9):
        cell(8 + c * 18, 197, (34, 24, 66, 255))
    return img


def placeholder_frame(style):
    img = Image.new("RGBA", (18, 18), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    col = COLOURS[style] + (255,)
    d.rectangle((0, 0, 17, 17), outline=col)
    if style in ("legendary", "mythic", "worn", "tab"):  # a second, softer ring and corner sparks
        d.rectangle((1, 1, 16, 16), outline=COLOURS[style] + (120,))
        for x, y in ((0, 0), (17, 0), (0, 17), (17, 17)):
            img.putpixel((x, y), (255, 255, 255, 255))
    return img


def load(path, fallback, size):
    if path.exists():
        img = Image.open(path).convert("RGBA")
        if img.size == size:
            return img
        print(f"{path.name}: {img.size}, expected {size}: using the placeholder")
    return fallback


# shortcut: the first Claude Design bg (2026-11-25) drew your inventory 1 px too low (the prompt said so); set False for art from the corrected prompt
ART_INVENTORY_LOW = True


def small(bg):
    """The 3-row version: the title strip, three shelf rows, the bottom (the "Inventory" strip and your inventory)."""
    out = Image.new("RGBA", (176, 168))
    out.paste(bg.crop((0, 0, 176, 17)), (0, 0))
    out.paste(bg.crop((0, 35, 176, 89)), (0, 17))
    out.paste(bg.crop((0, 125, 176, 222)), (0, 71))
    return out


def write(out, src):
    tex = out / "assets/cosmic/textures/font/gui"
    tex.mkdir(parents=True, exist_ok=True)
    art = src / "wardrobe"
    bg = load(art / "bg.png", None, (176, 222))
    if bg is not None and ART_INVENTORY_LOW:
        lifted = bg.copy()
        lifted.paste(bg.crop((0, 138, 176, 222)), (0, 137))
        bg = lifted
    bg = bg or placeholder_bg()
    bg.save(tex / "wardrobe_bg.png")
    small(bg).save(tex / "world_bg.png")
    providers = [{"type": "bitmap", "file": "cosmic:font/gui/wardrobe_bg.png", "ascent": 13, "height": 222, "chars": [""]},
                 {"type": "bitmap", "file": "cosmic:font/gui/world_bg.png", "ascent": 13, "height": 168, "chars": [""]}]
    for k, style in enumerate(STYLES):
        load(art / f"frame_{style}.png", placeholder_frame(style), (18, 18)).save(tex / f"frame_{style}.png")
        for r in range(6):
            # the frame's top at the slot row's top edge (y 17 + 18r): 6 + 7 - ascent = 17 + 18r
            providers.append({"type": "bitmap", "file": f"cosmic:font/gui/frame_{style}.png", "ascent": -4 - 18 * r,
                              "height": 18, "chars": [chr(0xE100 + 8 * k + r)]})
    advances = {chr(0xF801 + i): -(1 << i) for i in range(9)}
    advances.update({chr(0xF811 + i): 1 << i for i in range(9)})
    providers.append({"type": "space", "advances": advances})
    (out / "assets/cosmic/font").mkdir(parents=True, exist_ok=True)
    (out / "assets/cosmic/font/wardrobe.json").write_text(json.dumps({"providers": providers}, indent=1), encoding="utf-8")
    return len(providers)


if __name__ == "__main__":  # self-check: the glyph table is the one WardrobeMenu.java expects
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as t:
        n = write(Path(t), Path(t) / "src")
        font = json.loads((Path(t) / "assets/cosmic/font/wardrobe.json").read_text(encoding="utf-8"))
        chars = [c for p in font["providers"] if p["type"] == "bitmap" for c in p["chars"]]
        assert len(chars) == 2 + 7 * 6 and len(set(chars)) == len(chars), chars
        assert font["providers"][-1]["advances"][""] == -256 and font["providers"][-1]["advances"][""] == 1
        print(f"gui.py ok: {n} providers")
