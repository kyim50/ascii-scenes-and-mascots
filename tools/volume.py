"""Lit volumes -> fine-grid glyph art (bosses, creatures, big props, detailed backdrops).

Build a form from spheres, tapering tubes and flat polygons, lit from the upper left; it is mapped
through a glyph ramp, edges are traced in glyphs that follow them, hollows stay empty. Import it:

    import sys; sys.path.insert(0, "<skill>/tools"); from volume import Volume
    v = Volume(cols=240, rows=150)            # the fine grid (cells are ~1.66x taller than wide)
    v.sphere(120, 70, 40, 22, rough=0.15, seed=3)   # body: centre (col,row), radii (cols,rows)
    v.tube([(150, 60), (175, 40), (185, 30)], 9, 3) # neck tapering 9 -> 3 cols
    v.dark(v.ellipse(170, 32, 2, 1))           # an eye socket: solid dark
    rows = v.paint(glints=[(171, 32, "*")])    # list[str], one per grid row
    Volume.preview(rows, "out.png")            # light glyphs on the night ground

On a dark ground a denser glyph reads brighter, so RAMP runs sparse (shadow) -> dense (lit).
For a light/paper ground pass ramp=Volume.PAPER_RAMP (dense = dark). Thick forms read; thin tubes
look like wire. Detail comes from folds, cracks, scales: small spheres/tubes with base offsets.
"""
import numpy as np

ASPECT = 1.66  # row height / column width of a monospace cell
LIGHT = np.array([-0.55, -0.65, 0.52]); LIGHT = LIGHT / np.linalg.norm(LIGHT)


def _hash(a, b, seed):
    h = (a * 374761393 + b * 668265263 + seed * 2147483647) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFFFFFF) / 4294967296.0


class Volume:
    RAMP = list(" .`',:;-=+o*#")          # dark ground: lit side dense
    PAPER_RAMP = list(" .:-=+*#%@")[::1]   # paper ground: use tone directly (dark side dense)

    def __init__(self, cols, rows, light=LIGHT):
        self.cols, self.rows, self.light = cols, rows, light
        self.CY, self.CX = np.mgrid[0:rows, 0:cols].astype(np.float32)
        self.tone = np.zeros((rows, cols), np.float32)   # 0 lit .. 1 dark
        self.cover = np.zeros((rows, cols), bool)
        self.hollow = np.zeros((rows, cols), bool)

    def noise(self, seed, scale):
        """Smooth value noise over the grid in [0,1] (deterministic: seeded hash, never random)."""
        x, y = self.CX / scale, self.CY / (scale / ASPECT)
        xi, yi = np.floor(x).astype(int), np.floor(y).astype(int)
        fx, fy = x - xi, y - yi; fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
        h = np.vectorize(lambda a, b: _hash(int(a), int(b), seed))
        a, b, c, d = h(xi, yi), h(xi + 1, yi), h(xi, yi + 1), h(xi + 1, yi + 1)
        return a + (b - a) * fx + (c - a) * fy + (a - b - c + d) * fx * fy

    def _put(self, m, tone):
        self.tone = np.where(m, tone, self.tone); self.cover |= m; self.hollow &= ~m

    def ellipse(self, cx, cy, rx, ry):
        return ((self.CX + 0.5 - cx) / rx) ** 2 + ((self.CY + 0.5 - cy) / ry) ** 2 < 1

    def sphere(self, cx, cy, rx, ry, base=0.0, rough=0.0, seed=0):
        x, y = (self.CX + 0.5 - cx) / rx, (self.CY + 0.5 - cy) / ry
        d = x * x + y * y; m = d < 1
        nz = np.sqrt(np.clip(1 - d, 0, 1))
        lam = np.clip(x * self.light[0] + y * self.light[1] + nz * self.light[2], 0, 1)
        tone = np.clip(1 - lam + base, 0, 1)
        if rough: tone = np.clip(tone + (self.noise(seed, 18) - 0.5) * rough, 0, 1)
        self._put(m, tone); return m

    def tube(self, pts, r0, r1, base=0.0, rough=0.0, seed=0):
        pts = np.asarray(pts, float)
        seg = np.hypot(np.diff(pts[:, 0]), np.diff(pts[:, 1]) * ASPECT); total = seg.sum() or 1
        cum = np.concatenate([[0], np.cumsum(seg)])
        for d in np.linspace(0, total, max(2, int(total / 1.2))):
            i = min(len(seg) - 1, np.searchsorted(cum, d, side="right") - 1)
            c = pts[i] + (pts[i + 1] - pts[i]) * ((d - cum[i]) / (seg[i] or 1))
            r = r0 + (r1 - r0) * d / total
            self.sphere(c[0], c[1], max(0.7, r), max(0.5, r / ASPECT), base, rough, seed)

    def poly(self, points, tone_fn=lambda x, y: 0.4 + 0 * x, base=0.0):
        xs, ys = self.CX + 0.5, self.CY + 0.5; m = np.zeros(xs.shape, bool)
        for i in range(len(points)):
            (x0, y0), (x1, y1) = points[i], points[(i + 1) % len(points)]
            m ^= ((y0 > ys) != (y1 > ys)) & (xs < (x1 - x0) * (ys - y0) / ((y1 - y0) or 1e-9) + x0)
        self._put(m, np.clip(tone_fn(self.CX, self.CY) + base, 0, 1)); return m

    def dark(self, m):
        self.hollow |= m; self.cover |= m

    def paint(self, glints=(), ramp=None, outline=True):
        ramp = ramp or self.RAMP; n = len(ramp)
        g = np.full((self.rows, self.cols), " ", dtype="<U1")
        idx = np.clip(((1 - self.tone) * n).astype(int), 0, n - 1)
        for i, ch in enumerate(ramp):
            g[self.cover & ~self.hollow & (idx == i)] = ch
        if outline:
            gy, gx = np.gradient(self.cover.astype(np.float32))
            edge = self.cover & ~self.hollow & ((np.abs(gx) + np.abs(gy)) > 0.2)
            ang = np.degrees(np.arctan2(gy, gx)) % 180
            glyph = np.where((ang < 22.5) | (ang >= 157.5), "|", np.where(ang < 67.5, "\\", np.where(ang < 112.5, "_", "/")))
            g[edge] = glyph[edge]
        g[self.hollow] = " "
        for c, r, ch in glints:
            if 0 <= r < self.rows and 0 <= c < self.cols: g[r, c] = ch
        return ["".join(row) for row in g]

    @staticmethod
    def preview(rows, out, ink="#E8E6E3", bg="#15131A", cell=6, font=None):
        from pathlib import Path
        from PIL import Image, ImageDraw, ImageFont
        font = font or str(Path(__file__).with_name("JetBrainsMono-Regular.ttf"))
        f = ImageFont.truetype(font, int(cell / 0.6)); rh = cell * ASPECT
        img = Image.new("RGB", (int(len(rows[0]) * cell) + 8, int(len(rows) * rh) + 8), bg)
        d = ImageDraw.Draw(img)
        for r, row in enumerate(rows): d.text((4, 4 + r * rh), row, font=f, fill=ink)
        img.save(out); return out
