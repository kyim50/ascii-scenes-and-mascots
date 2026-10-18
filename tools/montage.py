"""Tile previews into one labelled sheet to judge variants side by side (distinctness, levels, palettes).
Usage: python3 montage.py out.png a.png b.png ... [--cols 3] [--width 640]  (label = file stem)"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("imgs", nargs="+")
ap.add_argument("--cols", type=int, default=3); ap.add_argument("--width", type=int, default=640)
o = ap.parse_args()
ims = [Image.open(p).convert("RGB") for p in o.imgs]
ims = [im.resize((o.width, int(im.height * o.width / im.width))) for im in ims]
h = max(im.height for im in ims) + 24; rows = -(-len(ims) // o.cols)
sheet = Image.new("RGB", (o.cols * (o.width + 8) + 8, rows * (h + 8) + 8), (21, 19, 26)); d = ImageDraw.Draw(sheet)
font = ImageFont.truetype(str(Path(__file__).with_name("JetBrainsMono-Regular.ttf")), 14)
for i, (im, p) in enumerate(zip(ims, o.imgs)):
    x, y = 8 + (i % o.cols) * (o.width + 8), 8 + (i // o.cols) * (h + 8)
    sheet.paste(im, (x, y)); d.text((x, y + im.height + 4), Path(p).stem, font=font, fill=(200, 192, 210))
sheet.save(o.out); print(o.out, len(ims), "images")
