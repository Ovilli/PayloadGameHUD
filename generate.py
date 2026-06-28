#!/usr/bin/env python3
"""Generates the PayloadGame custom HUD resource pack (functional placeholder art).

Glyphs (font payloadgame:hud):
  U+E010 bar fill      U+E011 bar empty     U+E002 finish flag
  U+E012 health full   U+E013 health empty
  U+E020..E025 hero portraits (enum order: Bulwark, Bullrush, Pyre, Volt, Bloom, Aegis)
  U+E0F1 space glyph, advance -1 (pulls tiles flush so bars are seamless)
"""
import json, os
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/ovilli/IdeaProjects/PayloadGame/resourcepack"
MC = os.path.join(ROOT, "assets", "minecraft")
PG = os.path.join(ROOT, "assets", "payloadgame")

def ensure(*parts):
    p = os.path.join(*parts)
    os.makedirs(p, exist_ok=True)
    return p

# ---- pack.mcmeta -------------------------------------------------------------
ensure(ROOT)
with open(os.path.join(ROOT, "pack.mcmeta"), "w") as f:
    json.dump({"pack": {
        "pack_format": 75,  # Minecraft 1.21.11
        "supported_formats": {"min_inclusive": 46, "max_inclusive": 99},
        "description": "PayloadGame HUD - invisible boss bar + payload HUD font"
    }}, f, indent=2)

# ---- pack.png icon -----------------------------------------------------------
icon = Image.new("RGBA", (64, 64), (20, 20, 28, 255))
d = ImageDraw.Draw(icon)
d.rectangle([6, 28, 40, 36], fill=(220, 170, 40, 255))   # gold payload fill
d.rectangle([40, 28, 57, 36], fill=(60, 60, 70, 255))    # empty
d.rectangle([6, 28, 57, 36], outline=(240, 240, 240, 255))
icon.save(os.path.join(ROOT, "pack.png"))

# ---- invisible boss bar sprites ---------------------------------------------
bb = ensure(MC, "textures", "gui", "sprites", "boss_bar")
names = []
for c in ["pink", "blue", "red", "green", "yellow", "purple", "white"]:
    names += [f"{c}_background", f"{c}_progress"]
for n in (6, 10, 12, 20):
    names += [f"notched_{n}_background", f"notched_{n}_progress"]
transparent = Image.new("RGBA", (182, 5), (0, 0, 0, 0))
for n in names:
    transparent.save(os.path.join(bb, f"{n}.png"))

# ---- HUD glyph bitmaps -------------------------------------------------------
fontdir = ensure(PG, "textures", "font")

def bar_tile(w, h, fill, border):
    """Full-width opaque tile with a 1px top/bottom border; seamless when kerned."""
    img = Image.new("RGBA", (w, h), fill)
    dd = ImageDraw.Draw(img)
    dd.line([(0, 0), (w - 1, 0)], fill=border)
    dd.line([(0, h - 1), (w - 1, h - 1)], fill=border)
    return img

bar_tile(8, 8, (225, 175, 45, 255), (120, 90, 20, 255)).save(os.path.join(fontdir, "seg_fill.png"))
bar_tile(8, 8, (55, 55, 65, 255), (30, 30, 36, 255)).save(os.path.join(fontdir, "seg_empty.png"))
bar_tile(6, 8, (215, 55, 55, 255), (110, 25, 25, 255)).save(os.path.join(fontdir, "hp_full.png"))
bar_tile(6, 8, (55, 40, 40, 255), (30, 24, 24, 255)).save(os.path.join(fontdir, "hp_empty.png"))

# finish flag (8x8): pole + small checkered flag
flag = Image.new("RGBA", (8, 8), (0, 0, 0, 0))
df = ImageDraw.Draw(flag)
df.line([(1, 0), (1, 7)], fill=(220, 220, 220, 255))  # pole
df.rectangle([2, 0, 5, 2], fill=(240, 240, 240, 255))
df.rectangle([3, 1, 3, 1], fill=(40, 40, 40, 255))
df.rectangle([5, 1, 5, 1], fill=(40, 40, 40, 255))
df.rectangle([2, 0, 2, 0], fill=(40, 40, 40, 255))
df.rectangle([4, 0, 4, 0], fill=(40, 40, 40, 255))
flag.save(os.path.join(fontdir, "flag.png"))

# ---- hero portraits ----------------------------------------------------------
try:
    PFONT = ImageFont.load_default()
except Exception:
    PFONT = None

ROLE_BG = {"TANK": (200, 160, 40), "DAMAGE": (200, 60, 60), "SUPPORT": (70, 170, 80)}
# (key, role, label) in enum order -> E020..E025
HEROES = [
    ("bulwark", "TANK", "BW"), ("bullrush", "TANK", "BR"),
    ("pyre", "DAMAGE", "PY"), ("volt", "DAMAGE", "VO"),
    ("bloom", "SUPPORT", "BL"), ("aegis", "SUPPORT", "AE"),
]
for key, role, label in HEROES:
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img)
    bg = ROLE_BG[role]
    dd.rectangle([0, 0, 15, 15], fill=(bg[0], bg[1], bg[2], 255), outline=(245, 245, 245, 255))
    if PFONT:
        dd.text((2, 4), label, fill=(255, 255, 255, 255), font=PFONT)
    img.save(os.path.join(fontdir, f"hero_{key}.png"))

# ---- font definition ---------------------------------------------------------
fjson = ensure(PG, "font")
bitmaps = [
    ("payloadgame:font/seg_fill.png",  0xE010, 7, 8),
    ("payloadgame:font/seg_empty.png", 0xE011, 7, 8),
    ("payloadgame:font/flag.png",      0xE002, 7, 8),
    ("payloadgame:font/hp_full.png",   0xE012, 7, 8),
    ("payloadgame:font/hp_empty.png",  0xE013, 7, 8),
]
for i, (key, role, label) in enumerate(HEROES):
    bitmaps.append((f"payloadgame:font/hero_{key}.png", 0xE020 + i, 12, 16))

providers = [{"type": "bitmap", "file": fp, "ascent": asc, "height": h, "chars": [chr(cp)]}
             for fp, cp, asc, h in bitmaps]
# negative-kern glyph: -1px advance, inserted between tiles to remove the gap
providers.append({"type": "space", "advances": {chr(0xE0F1): -1}})

with open(os.path.join(fjson, "hud.json"), "w") as f:
    json.dump({"providers": providers}, f, indent=2, ensure_ascii=True)

# remove obsolete v1 glyphs if present
for old in ("arrow_left.png", "arrow_right.png", "seg_red.png", "seg_blue.png"):
    p = os.path.join(fontdir, old)
    if os.path.exists(p):
        os.remove(p)

print("resource pack written to", ROOT)
