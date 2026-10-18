---
name: ascii-scenes-and-mascots
description: Use when making ASCII, glyph or fine-grid character-art scenes (rooms, landscapes, backdrops, bosses, big props) or pixel mascots and their wearables, creatures, pets, poses and emotes, in any project (Tabi/quests, hearth, vault-hud, new apps); also when such art looks chunky, flat, boxy, banded, noisy or off-style
---

# ASCII scenes and pixel mascots

## Overview

A scene is **glyph structure + a separate colour layer + live motion ops**, drawn in a fixed order,
fully deterministic, and judged from a render of **the exact ops the app draws**. A mascot is a
**palette-keyed pixel sprite on a half-cell grid** with named anchor cells; everything it wears or
does is data placed against those anchors. Built this way the art is detailed, consistent and testable.

## Before drawing

1. If the project already has a scene kit, mascot sprite or recipe doc (grep `scene`, `mascot`,
   `recipe`, `palette`, `ops`), **extend it**: reuse its grid, palette, draw order and preview tool.
2. Read the house style: [house-style.md](house-style.md). It overrides defaults (no gold, night/dusk,
   colour rules, accent).
3. Pick the reference for the job:

| Making | Read |
| --- | --- |
| A room, landscape, backdrop | [scenes.md](scenes.md) |
| A boss, creature, large prop, detailed fine-grid backdrop | [scenes.md](scenes.md) § Lit volumes + `tools/volume.py` |
| A mascot, wearable, pet, NPC, pose, emote | [mascots.md](mascots.md) |
| Any of the above, before calling it done | [verify.md](verify.md) |

## The contract (every piece meets all of these)

- **Layers:** structure in glyph grids; hue in a separate colour layer; motion and user-specific
  colour (banner, tint) as live ops. Never one monolithic paint function.
- **Draw order is fixed** and written at the top of the renderer (scenes.md § Draw order).
- **Deterministic:** seeded `hash`/value noise only, as a function of `(t, seed)`. No `Math.random`,
  no unseeded RNG, no wall-clock reads inside the renderer.
- **Form from light, not fills:** density ramps, lit edges, light rings, cleared shadows. No flat
  silhouettes, no single-glyph walls, no hard-edged rects as halos or shadows.
- **A value plan:** a bright focal subject, a legible midground, a sparse far layer and open space
  (scenes.md § Value plan). Dim means quiet, not murky.
- **Mascots sit in the scene:** square pixels, at least ~24 pt and at most ~5 glyph rows tall
  inside a scene; at **hero size** (64–120 pt, a detailed variant) when the mascot is the
  subject of the screen (mascots.md § The sprite).
- **Scenes inside app UI get more punch:** higher values, one large focal point, a tight crop,
  checked beside the screen's text (scenes.md § Value plan).
- **Verified:** rendered from the op list, compared in a montage, viewed on the device or a
  full-phone mockup, and pinned by tests (verify.md).

## Tools (Python 3 + Pillow + numpy; run with `python3 <skill>/tools/X.py --help`)

- `render_ops.py`: op-list JSON → PNG (the app's own draw calls, offline).
- `sprite.py`: palette-keyed sprite frames + wearable layers → zoomed sheet.
- `volume.py`: lit spheres/tubes/polygons → fine-grid glyph art (import it).
- `montage.py`: tile previews with labels to compare variants.
- `JetBrainsMono-Regular.ttf`: bundled so previews match a monospace app.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Gold/yellow star, crown, trim or flame core | house-style.md palette: flame `#EFA24E #D97757 #A8482E`, silver/steel/bronze metals |
| Grey/coloured block behind the moon, a sign, a halo | Remove the block; light with rings, occlude with the background colour only |
| Rectangle shadow under a sprite | Two stacked low-alpha ellipse-ish rects (wide 0.28, narrow 0.18) |
| `vYvYvY` / `====` rows reading as text | Mix 2–3 glyphs per density step by seeded hash; drop density with distance |
| Flat, unlit hero shapes (the nearest tree, the rock, the boss) | Lit volumes (volume.py) or a lit-edge pass: dense on the light side, sparse in shadow |
| Mascot drawn huge in a scene, or too tiny to read | In a scene: `q = clamp(0.8·CW, 24/H, 5·RH/H)`. As a screen's subject: hero size, 64–120 pt, detailed variant (mascots.md) |
| Scene in a UI card reads as grey noise beside the text | Raise the value ladder, one large focal point, crop tight (scenes.md § Value plan) |
| Whole scene murky, every plane the same value | Value plan: focal brightest, midground 0.18–0.30, far 0.08–0.14 and sparser |
| Forest of outlined volumes reads as `\|/=` noise | Volumes for 1–3 hero shapes only; silhouette band behind, outline the mass not each tree |
| Moon or orb is a clump of `*#o` | Pixel disc in the colour layer + glyph light rings (scenes.md § Small round lights) |
| Hat hard-coded into the body sprite | A `Wear` entry `{at, rows, pal, hides}` against the anchors (mascots.md) |
| Judging a hand-made image, not the app's ops | Dump the renderer's ops → `render_ops.py` |
| "Looks fine" from one still | Montage several `t` values and variants; then device/mockup |
