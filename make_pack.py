"""Builds the Cosmic Craft resource pack -> cosmic-pack.zip (next to this script).

The Season 1 logo becomes glyphs of the font minecraft:cosmic (<font:cosmic> in tab styles), so text (tab list, chat, team tags) can show it:
  U+E000           the logo
  U+E001..U+E00C   the logo with a diagonal shine sweeping across it (12 frames)
Rank icons will be U+E100.. once their art arrives from Claude Design.

python -I make_pack.py
"""
import json
import shutil
import zipfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE / "build"
LOGO = HERE / "src" / "cosmic_craft_256.png"
SHINE_FRAMES = 12
LOGO_HEIGHT = 56   # on-screen height in GUI pixels
LOGO_ASCENT = 7    # top of the logo sits at the top of its text line; it hangs ~6 lines down

shutil.rmtree(OUT, ignore_errors=True)
tex = OUT / "assets/cosmic/textures/font"
tex.mkdir(parents=True)
(OUT / "assets/minecraft/font").mkdir(parents=True)

logo = Image.open(LOGO).convert("RGBA")
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


providers = []
for i in range(SHINE_FRAMES + 1):
    frame = logo if i == 0 else shine(logo, (i - 1) / (SHINE_FRAMES - 1))
    name = f"logo_{i:02d}.png"
    frame.save(tex / name)
    providers.append({"type": "bitmap", "file": f"cosmic:font/{name}", "ascent": LOGO_ASCENT, "height": LOGO_HEIGHT,
                      "chars": [chr(0xE000 + i)]})

(OUT / "assets/minecraft/font/cosmic.json").write_text(json.dumps({"providers": providers}, indent=1), encoding="utf-8")
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
print(f"{zip_path.name}: {zip_path.stat().st_size // 1024} KB, logo {w}x{h} px shown {LOGO_HEIGHT} px tall, {SHINE_FRAMES} shine frames")
