# Scenes: structure, colour, light, motion

## The model
The renderer emits an **op list** each frame: `rect(x, y, w, h, colour, alpha)` and
`text(x, y, glyphs, colour, alpha, z?)`. Everything below produces ops. Any engine works (Skia, a
canvas, a terminal), as long as the scene code only appends ops and a host draws them.

## Grid
- Monospace cell: width `CW`, height `RH ≈ 1.66 × CW` (JetBrains Mono: font size = CW / 0.6).
- Fix the rows once and share them across scenes in a family. Example side-view room, 190 × 66:
  beam rows 0–3, wall 4–37, wainscot 38–43, floor 44–65. Characters' feet land on the floor band.
- A **CharGrid** is `rows: string[]` plus a tone (alpha) per grid. Solid areas become rows of one
  glyph only at low alpha; textured areas mix glyphs.

## Kit builders (write once per project, reuse in every scene)
- `beam`: solid `#` with `==-` grain at 0.3 density and a shadow row of `'` and `` ` ``.
- `plankWall`: a `_` seam every 6 rows, `|` joints every ~47 columns, `.~` grain at 1.5%.
- `stoneWall`: 2-row courses, `_` beds, staggered `|` joints 7–9 wide, `.:` pitting.
- `wainscot`: an `=` rail with `|` boards every N columns. `skirting`. `clear(box)` blanks the cells
  behind furniture.
- **Tones** `tone(alpha, glyph)`: wall 0.13 `-`, stone 0.18 `.`, frame 0.30 `=`, front 0.50 `=`,
  floor 0.20 `.`.

## Glyphs by material
| Material | Glyphs |
| --- | --- |
| Wood | `=` slabs, `\|` posts, turned legs `(#) )#( \|#\|`, aprons `[====]` |
| Stone | `_` beds, `\|` joints, `.:` pitting, plinth flutes `\|` every 3 columns |
| Glass | outline `\|` and `_`; glints are 4-cell `/` runs at alpha 0.12 |
| Metal | `-+-` guards, `\|` blades, `(\ /)` handles; bowls as metal-colour blocks at 0.45–0.55 |
| Fabric, straw | blocks plus `/;,\|\` texture |
| Books | 1 column each: block 0.5, `\|` spine, `=` band, `_` page top |
| Foliage | ramp `.,:;!` by density; lit side denser; `^` tips only at the very top |
| Fire | stacked flame glyphs `^ ( ) ' ,` in the three flame colours; smoke `( )` at 0.25 |

**Against walls of text:** each density step gets 2–3 glyphs, chosen by `hash(col, row, seed)`.
Density falls off with distance from the viewer and from light. Never tile one glyph across a lit area.

## Colour layer (Paint)
- **Which style is this project?** If its docs or memory say backgrounds are glyph-only (ink styles
  like hearth), the colour layer holds only mascots and small props. Otherwise (Tabi rooms), any
  hued object may go in it. Without a stated style: one muted ink per glyph layer, hue on props.
- Cells with a glyph colour, an optional background block colour, and alpha.
- `bake(lights, ambient)`: light each cell with linear falloff (y squashed × 1.5), round alpha to
  0.05, then merge each row into one text run per colour and alpha, plus one rect per run of blocks.
  Cache the result. Bake lights are static and larger than the live ones (r 330–420).
- Keep separate Paints: **back** (on the wall), **backing** (dark silhouettes of front furniture,
  unlit blocks in the background colour), **front** (what sits on furniture). A backing block must
  never cover its own fill.

## Value plan (decide before drawing)
"Dim backdrop" means quiet, not murky. Give every scene a readable value ladder:
- **Focal subject + its light:** the brightest values and the only saturated hues (the fire,
  the mascot, a lit doorway).
- **Midground structure:** glyph alpha 0.18–0.30, clearly legible.
- **Far layers:** 0.08–0.14 and *sparser glyphs*, not just lower alpha.
- These alphas assume a light ink (lightness ~88%, e.g. `#E8E6E3`) on a near-black ground. With a
  darker or tinted ink, keep the *ratio* between the planes and raise the alphas, or the ink's
  lightness, until the midground reads.
- **Sky:** mostly empty, with one strong, clean element (a moon, a planet) and a few stars.
- **Empty space is a tool.** Clear wide bands (the sky, a clearing, a path) so masses read as shapes.
Check at phone size: if you can't name the three planes in a thumbnail, raise the midground and thin the far layer.

## Repeated masses (forests, crowds of rocks, rooftops)
- Don't run every tree through full lit-volume shading with outlines: a hundred outlined volumes
  become a wall of `|/\=` noise. Use volumes for the 1–3 hero shapes nearest the viewer.
- **What makes a treeline read** against the sky is a faint horizon glow wash behind it, cut out
  along the silhouette at half-row resolution. The dark mass then reads by contrast. Collapse the
  nested wash steps into one rect per row run with the summed alpha, to keep the op count low.
- For the mass behind them, use a **silhouette band**: one sparse ramp (`.,:;` by density) with
  `^`/`/\` only along the top edge, plus a lit rim on the side facing the light. Outline only the
  outer silhouette of the mass, never each member.
- Vary the members by seeded height and spacing, and leave gaps of sky between groups.

## Small round lights (moon, lamp globes, orbs, eyes)
- A small disc can't carry a glyph ramp: letters, `*` and `#` clump into text. Draw it in the
  **colour layer** as a pixel disc (solid rects, 2–3 tones: lit limb, face, shade). For a crescent,
  clear the shade.
- Give it 2–3 maria/crater cells in the shade tone, then **glyph light around it** with `drawLit`
  rings on the sky's star/cloud grid. No background block and no halo rect.
- Over roughly 14 cells across it becomes a big prop: lit volume with a 3-glyph ramp (`.:o`) and
  the outline turned off.

## Light
- `drawLit(grid, light, a)`: redraw *the grid's own glyphs* inside three circular masks at radius
  r, 0.66r and 0.36r (y squashed × 1.5), each pass at alpha `a` in the light's colour. The centre
  gets three passes, so it reads brightest. The passes are glyphs only, never rects. Use `a ≈ 0.22`
  for structure grids at tone 0.13–0.30; on faint grids (haze, water) use `a ≈ 1–1.5 ×` the grid's
  own tone.
- **Radii scale with the scene:** give them as fractions of the scene width `SW`. Live candle
  0.16–0.27 SW, torch 0.18–0.25 SW; baked lights 0.35–0.45 SW. (Tabi's 956-pt rooms: candle
  r 150–260, bake 330–420.)
  Live radius flicker: `r * (0.85 + 0.15 * vnoise(t))`.
- Washes over **sky** or **open air** (a horizon glow, the warmth of a hearth) may use many very
  faint nested rects; anything that outlines a single object must not.
- Keep big lights (the moon) off the back grids, or everything glows.
- Washes: many very faint nested rects (12 × 0.006). A few stronger steps show their edges.
- **Backing** can also be done by blanking the hidden glyph cells instead of drawing a block. Prefer
  that when the furniture isn't a solid colour.
- Spotlights: stacked rects from the ceiling to the floor at 0.03, with a floor pool of 3 rects.
- Glints: `+ *` in white, visible for 18% of a `(t*0.35 + hash) % 1` cycle.

## Draw order (every frame)
1. Background rect.
2. What is seen through openings: sky, stars, moon.
3. Back grids, with the live lights.
4. Back Paint.
5. Live wall items (banners).
6. Backing Paint.
7. Front grid and floor.
8. Front Paint.
9. Live animated props.
10. People, mascots and creatures, depth-sorted by feet, each with its shadow.

## Motion recipes
| Effect | How |
| --- | --- |
| Candle | flame from `vnoise(t*7)`, lean from `vnoise(t*2.3)` (±0.4 CW) |
| Torch | 3–4 flame columns × 4–6 rows, flame palette, z 1.1–1.6 |
| Smoke | `(` `)` rising 10 rows at 0.25 |
| Lantern sway | `sin(t*0.7) * 0.4` columns |
| Dust motes | life `(t*0.07 + hash) % 1`, rising 160 px, alpha `sin(life*π)` |
| Clouds | 6 px/s at 0.12 |
| Pulse | `0.6 + 0.4 sin(t*2.4)` |
| Breathe | `0.85 + 0.15 sin(t*0.8)` |
| Stars | twinkle in steps of `floor(t*2)` |
| Banner wave | steady phase `t*2.4`; a gust scales amplitude only; fold ≤ 0.06 |

**Seed blocks:** give each scene its own seed range (600s, 700s and so on) so props never correlate.

## Lit volumes (bosses, creatures, big props, detailed backdrops)
Use `tools/volume.py`: build the form from `sphere`, `tube` (tapering) and `poly` (membranes,
robes). It is lit from the upper left by default; pass `light=` to match the scene's key light.
The default ramp ends in `o*#`, which suits big forms. For a small hero prop, pass a quieter
`ramp=` (e.g. `" .,:;-="`) so it doesn't read as text. `dark()` marks hollows (eyes, mouth, inside a hood). `paint()` maps
tone through the ramp (the lit side dense on a dark ground) and traces edges in `| \ _ /`. Export
light positions (glowing eyes, runes) for the scene's `drawLit`, and add ground mist as sparse
punctuation that thins downwards. Detail comes from many small volumes with `base` offsets: folds,
cracks, scales, moss.

## Pitfalls
- A halo rect around a light reads as a box. Delete it.
- Moonlight on a sand-coloured floor bands. Drop the pool.
- Lit wainscot under a table reads as a railing. Back the table down to the floor.
- Dense reference rows make hills noisy. Use sparser rows at tone ~0.09.
- A shared-kit import missing at runtime. Render a preview after every edit.
