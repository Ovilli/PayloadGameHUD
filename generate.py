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

# ---- hide vanilla HUD elements ----------------------------------------------
# Our custom font HUD replaces the survival overlay, so make the vanilla hearts,
# armor, hunger, air and XP bar fully transparent. (1.20.5+ moved these to sprites
# under gui/sprites/hud/.) Overriding sprites that don't exist is harmless.
hud = ensure(MC, "textures", "gui", "sprites", "hud")
blank9 = Image.new("RGBA", (9, 9), (0, 0, 0, 0))      # heart / armor / food / air icons
blankxp = Image.new("RGBA", (182, 5), (0, 0, 0, 0))   # experience bar strip

# hearts live in a sub-folder; cover every state variant
heart_dir = ensure(hud, "heart")
heart_prefixes = ["", "hardcore_", "poisoned_", "poisoned_hardcore_", "withered_",
                  "withered_hardcore_", "absorbing_", "absorbing_hardcore_",
                  "frozen_", "frozen_hardcore_"]
heart_names = []
for pre in heart_prefixes:
    for kind in ("full", "full_blinking", "half", "half_blinking"):
        heart_names.append(pre + kind)
heart_names += ["container", "container_blinking",
                "hardcore_container", "hardcore_container_blinking",
                "vehicle_container", "vehicle_full", "vehicle_half"]
for n in heart_names:
    blank9.save(os.path.join(heart_dir, f"{n}.png"))

# armor, hunger/food and air bubbles sit directly under hud/
hud_icons = [
    "armor_empty", "armor_half", "armor_full",
    "food_empty", "food_half", "food_full",
    "food_empty_hunger", "food_half_hunger", "food_full_hunger",
    "air", "air_bursting",
]
for n in hud_icons:
    blank9.save(os.path.join(hud, f"{n}.png"))

# experience bar (background + green progress fill)
for n in ("experience_bar_background", "experience_bar_progress"):
    blankxp.save(os.path.join(hud, f"{n}.png"))

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
# health tiles are tall + chunky so the bar reads like an Overwatch health strip
bar_tile(8, 14, (215, 55, 55, 255), (110, 25, 25, 255)).save(os.path.join(fontdir, "hp_full.png"))
bar_tile(8, 14, (55, 40, 40, 255), (30, 24, 24, 255)).save(os.path.join(fontdir, "hp_empty.png"))

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

# nameplate box drawn BEHIND the portrait + health strip (via negative-space layering).
# Width must cover: inset(3) + portrait(27) + gap(3) + health bar(80) + inset(3) = 116.
FRAME_W, FRAME_H = 116, 30
frame = Image.new("RGBA", (FRAME_W, FRAME_H), (12, 12, 18, 200))  # dark translucent fill
dfr = ImageDraw.Draw(frame)
dfr.rectangle([0, 0, FRAME_W - 1, FRAME_H - 1], outline=(210, 210, 220, 255), width=2)
frame.save(os.path.join(fontdir, "frame.png"))

# ---- hero portraits ----------------------------------------------------------
PSIZE = 32  # portrait source resolution (rendered larger via the font height)
PFONT = None
for _path in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
    try:
        PFONT = ImageFont.truetype(_path, 14)
        break
    except Exception:
        pass
if PFONT is None:
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
    img = Image.new("RGBA", (PSIZE, PSIZE), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img)
    bg = ROLE_BG[role]
    dd.rectangle([0, 0, PSIZE - 1, PSIZE - 1], fill=(bg[0], bg[1], bg[2], 255),
                 outline=(245, 245, 245, 255), width=2)
    if PFONT:
        try:
            l, t, r, b = dd.textbbox((0, 0), label, font=PFONT)
            dd.text(((PSIZE - (r - l)) / 2 - l, (PSIZE - (b - t)) / 2 - t),
                    label, fill=(255, 255, 255, 255), font=PFONT)
        except Exception:
            dd.text((6, 9), label, fill=(255, 255, 255, 255), font=PFONT)
    img.save(os.path.join(fontdir, f"hero_{key}.png"))

# ---- ability icons -----------------------------------------------------------
# One emblem per ability (placeholder vector symbols; a designer can replace the PNGs).
# Order MUST match Hero enum order, two per hero (slot 0 then slot 1) -> U+E030..E03B.
ASIZE = 32
WHITE = (255, 255, 255, 255)

def _shield(d):  d.polygon([(16, 6), (25, 10), (25, 18), (16, 27), (7, 18), (7, 10)], outline=WHITE, width=2)
def _wave(d):    [d.ellipse([16 - r, 16 - r, 16 + r, 16 + r], outline=WHITE, width=2) for r in (5, 9, 13)]
def _arrow(d):   d.polygon([(9, 8), (24, 16), (9, 24)], fill=WHITE)
def _bang(d):    (d.rectangle([14, 7, 18, 20], fill=WHITE), d.rectangle([14, 23, 18, 27], fill=WHITE))
def _flame(d):   d.polygon([(16, 5), (23, 18), (16, 27), (9, 18)], fill=WHITE)
def _chev(d):    [d.line([(8 + o, 9), (16 + o, 16), (8 + o, 23)], fill=WHITE, width=2) for o in (0, 8)]
def _crosshair(d): (d.ellipse([8, 8, 24, 24], outline=WHITE, width=2), d.line([(16, 3), (16, 29)], fill=WHITE, width=2), d.line([(3, 16), (29, 16)], fill=WHITE, width=2))
def _hook(d):    (d.line([(16, 5), (16, 17)], fill=WHITE, width=2), d.arc([10, 13, 22, 27], 0, 180, fill=WHITE, width=2))
def _plus(d):    (d.rectangle([13, 7, 19, 25], fill=WHITE), d.rectangle([7, 13, 25, 19], fill=WHITE))
def _link(d):    (d.ellipse([6, 12, 16, 20], outline=WHITE, width=2), d.ellipse([16, 12, 26, 20], outline=WHITE, width=2))
def _uparrows(d): [d.line([(8, 24 - o), (16, 15 - o), (24, 24 - o)], fill=WHITE, width=2) for o in (0, 8)]
def _hex(d):     d.polygon([(16, 5), (26, 11), (26, 21), (16, 27), (6, 21), (6, 11)], outline=WHITE, width=2)

# (ability id, role, symbol) in Hero enum order, slot 0 then slot 1
ABILITY_ICONS = [
    ("bastion", "TANK", _shield),   ("shockwave", "TANK", _wave),
    ("charge", "TANK", _arrow),     ("taunt", "TANK", _bang),
    ("firestorm", "DAMAGE", _flame), ("emberdash", "DAMAGE", _chev),
    ("mark", "DAMAGE", _crosshair), ("grapple", "DAMAGE", _hook),
    ("healbloom", "SUPPORT", _plus), ("lifelink", "SUPPORT", _link),
    ("rally", "SUPPORT", _uparrows), ("barrier", "SUPPORT", _hex),
]
for aid, role, symbol in ABILITY_ICONS:
    img = Image.new("RGBA", (ASIZE, ASIZE), (0, 0, 0, 0))
    dd = ImageDraw.Draw(img)
    bg = ROLE_BG[role]
    dd.rectangle([1, 1, ASIZE - 2, ASIZE - 2], fill=(bg[0], bg[1], bg[2], 255),
                 outline=(245, 245, 245, 255), width=2)
    symbol(dd)
    img.save(os.path.join(fontdir, f"ability_{aid}.png"))

# ---- font definition ---------------------------------------------------------
fjson = ensure(PG, "font")
# (file, codepoint, ascent, height). Lower ascent => drawn lower on the action-bar line.
# The boss-bar payload tiles stay at the normal text line; the bottom HUD (health + hero
# portrait) is pushed well down and enlarged so it reads like an Overwatch nameplate.
bitmaps = [
    ("payloadgame:font/seg_fill.png",  0xE010, 7, 8),
    ("payloadgame:font/seg_empty.png", 0xE011, 7, 8),
    ("payloadgame:font/flag.png",      0xE002, 7, 8),
    ("payloadgame:font/frame.png",     0xE001, -1, 30),   # nameplate box (behind content)
    ("payloadgame:font/hp_full.png",   0xE012, -9, 14),   # health strip, pushed well down
    ("payloadgame:font/hp_empty.png",  0xE013, -9, 14),
]
for i, (key, role, label) in enumerate(HEROES):
    bitmaps.append((f"payloadgame:font/hero_{key}.png", 0xE020 + i, -3, 26))  # big, pushed down
for i, (aid, role, symbol) in enumerate(ABILITY_ICONS):
    bitmaps.append((f"payloadgame:font/ability_{aid}.png", 0xE030 + i, 14, 20))  # ability emblems

providers = [{"type": "bitmap", "file": fp, "ascent": asc, "height": h, "chars": [chr(cp)]}
             for fp, cp, asc, h in bitmaps]
# Spacing glyphs (advance = pixels the cursor moves). Negative = move left.
providers.append({"type": "space", "advances": {
    chr(0xE0F1): -1,     # seamless kern between bar tiles
    chr(0xE0F2): -117,   # rewind to box start after drawing the frame (frame advance = 116+1)
    chr(0xE0F3): 300,    # gap between the left-side abilities and the right-side hero nameplate
    chr(0xE0F4): 3,      # small inset / inter-element gap
    chr(0xE0F6): 10,     # gap from box edge to the role label
}})

with open(os.path.join(fjson, "hud.json"), "w") as f:
    json.dump({"providers": providers}, f, indent=2, ensure_ascii=True)

# remove obsolete v1 glyphs if present
for old in ("arrow_left.png", "arrow_right.png", "seg_red.png", "seg_blue.png"):
    p = os.path.join(fontdir, old)
    if os.path.exists(p):
        os.remove(p)

print("resource pack written to", ROOT)
