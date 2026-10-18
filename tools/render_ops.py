"""Render a scene's op list (JSON) to a PNG, so a glyph scene can be judged without a device.

Ops are what the scene code emits each frame, in draw order:
  {"k": "rect", "x", "y", "w", "h", "c": "#RRGGBB", "a": 0..1}
  {"k": "text", "x", "y", "s": "glyphs", "c", "a", "z": scale (optional)}
x/y are in scene points; text y is the top of the cell. Compositing is per-op alpha over, which is
close to (not identical to) Skia/canvas. Usage:
  python3 render_ops.py ops.json out.png --size 956 566 [--scale 2] [--cell 5.07] [--bg "#000000"] [--font F.ttf]
--cell is the glyph advance in points (font size = cell / 0.6 for JetBrains Mono).
"""
import argparse, json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("ops"); ap.add_argument("out")
ap.add_argument("--size", nargs=2, type=float, default=[956, 566])
ap.add_argument("--scale", type=int, default=2)
ap.add_argument("--cell", type=float, default=5.0687)
ap.add_argument("--bg", default="#000000")
ap.add_argument("--font", default=str(Path(__file__).with_name("JetBrainsMono-Regular.ttf")))
o = ap.parse_args()
S = o.scale; W, H = int(round(o.size[0])), int(round(o.size[1])); FONT = o.cell / 0.6
col = lambda c: tuple(int(c.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
fonts = {}
def font(z):
    if z not in fonts: fonts[z] = ImageFont.truetype(o.font, max(1, int(round(FONT * S * z))))
    return fonts[z]
base = Image.new("RGBA", (W * S, H * S), col(o.bg) + (255,))
def paste(layer, x0, y0):
    cx, cy = max(0, x0), max(0, y0)
    if cx >= W * S or cy >= H * S: return
    layer = layer.crop((cx - x0, cy - y0, min(layer.width, W * S - x0), min(layer.height, H * S - y0)))
    if layer.width > 0 and layer.height > 0: base.alpha_composite(layer, dest=(cx, cy))
for op in json.load(open(o.ops)):
    a = max(0.0, min(1.0, op.get("a", 1)))
    if a <= 0: continue
    fill = col(op["c"]) + (int(a * 255),)
    x0, y0 = int(round(op["x"] * S)), int(round(op["y"] * S))
    if op["k"] == "rect":
        # round both edges (not origin + size) so abutting fractional rects never leave seams
        w = max(1, int(round((op["x"] + op["w"]) * S)) - x0); h = max(1, int(round((op["y"] + op["h"]) * S)) - y0)
        if x0 + w > 0 and y0 + h > 0: paste(Image.new("RGBA", (w, h), fill), x0, y0)
    else:
        z = op.get("z") or 1; f = font(z)
        w, h = int(f.getlength(op["s"])) + 4, int(FONT * S * z * 1.4) + 4
        if x0 + w <= 0 or y0 + h <= 0: continue
        layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((0, FONT * 0.8 * S * z), op["s"], font=f, fill=fill, anchor="ls")
        paste(layer, x0, y0)
base.convert("RGB").save(o.out)
print(f"{o.out}: {len(json.load(open(o.ops)))} ops")
