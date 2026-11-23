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

The logo frames are also in the font minecraft:cosmic, which older tab styles use.

python -I make_pack.py
"""
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
SRC = HERE / "src"
OUT = HERE / "build"
RANKS = ["owner", "admin", "mod", "creator", "vip", "member"]
SHINE_FRAMES = 12
LOGO_HEIGHT = 56   # on-screen height in GUI pixels
LOGO_ASCENT = 7    # top of the logo sits at the top of its text line; it hangs ~6 lines down
BADGE_ASCENT = 8   # 11 px pills, centred on a text line: 1 px above the letters, 2 below

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

# Font files from every pack are merged, so this only adds our characters to Minecraft's default font.
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
print(f"{zip_path.name}: {zip_path.stat().st_size // 1024} KB, {len(default)} glyphs in minecraft:default")
