"""Preview pixel sprites (mascots, wearables, creatures, emote frames) zoomed up, side by side.

Input JSON: {"pal": {"O": "#CB7C5E", ...}, "frames": [{"label": "stand", "rows": [...],
  "layers": [{"at": [col, row], "rows": [...], "pal": {...}}], "flip": false}], "bg": "#1D1A23"}
Rows are strings of palette keys; "." is empty. Layers are drawn over the frame in order, offset by
"at" (may be negative: a hat above the head). Usage: python3 sprite.py sprite.json out.png [--px 12]
--px is pixels per sprite cell. Sprite pixels are square (mascots.md); --tall only for odd
non-square sprite formats.
"""
import argparse, json
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

ap = argparse.ArgumentParser(); ap.add_argument("spec"); ap.add_argument("out")
ap.add_argument("--px", type=int, default=12); ap.add_argument("--tall", type=float, default=1)
o = ap.parse_args(); spec = json.load(open(o.spec))
col = lambda c: tuple(int(c.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))
def cells(frame):
    out = {}
    def put(rows, pal, c0, r0):
        for r, row in enumerate(rows):
            for c, k in enumerate(row):
                if k != "." and k in pal: out[(c0 + c, r0 + r)] = pal[k]
    put(frame["rows"], spec["pal"], 0, 0)
    for L in frame.get("layers", []): put(L["rows"], {**spec["pal"], **L.get("pal", {})}, *L["at"])
    if frame.get("flip"):
        w = max(len(r) for r in frame["rows"]) - 1
        out = {(w - c, r): v for (c, r), v in out.items()}
    return out
frames = [cells(f) for f in spec["frames"]]
allc = [c for f in frames for c in f]
c0, c1 = min(c for c, _ in allc), max(c for c, _ in allc); r0, r1 = min(r for _, r in allc), max(r for _, r in allc)
pw, ph = o.px, int(o.px * o.tall); fw, fh = (c1 - c0 + 3) * pw, (r1 - r0 + 3) * ph + 18
img = Image.new("RGB", (fw * len(frames), fh), col(spec.get("bg", "#1D1A23"))); d = ImageDraw.Draw(img)
font = ImageFont.truetype(str(Path(__file__).with_name("JetBrainsMono-Regular.ttf")), 12)
for i, (f, meta) in enumerate(zip(frames, spec["frames"])):
    for (c, r), v in f.items():
        x, y = i * fw + (c - c0 + 1) * pw, (r - r0 + 1) * ph
        d.rectangle([x, y, x + pw - 1, y + ph - 1], fill=col(v))
    d.text((i * fw + 6, fh - 16), meta.get("label", str(i)), font=font, fill=(160, 152, 170))
img.save(o.out); print(o.out, f"{len(frames)} frames")
