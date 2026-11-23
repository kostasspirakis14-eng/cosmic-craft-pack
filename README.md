# Cosmic Craft resource pack

The resource pack of the Cosmic Craft SMP (Minecraft 26.3). The server sends it to every player automatically.

What it adds:
- The Cosmic Craft logo as a font glyph (font `minecraft:cosmic`), with a 12-frame shine animation, shown at the top of the tab list.
- Rank badges (Owner, Admin, Mod, Creator, VIP, Member) and icons, an animated Owner badge, and a small logo for titles, all as characters of Minecraft's default font. The character map is at the top of make_pack.py.

Build: `python make_pack.py` (needs Pillow) → `cosmic-pack.zip`. Every new version is published as a release, and the server downloads it from
`releases/latest/download/cosmic-pack.zip`.
