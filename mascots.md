# Mascots, wearables, creatures, poses, emotes

## The sprite
- **Square pixels, drawn as rects.** One sprite pixel is `q` points square. Choose `q` from these
  rules, in priority order:
  1. Drawn height at least ~24 pt on a phone (smaller is unreadable).
  2. Drawn height at most ~5 glyph rows (larger becomes a poster, not a character in the scene).
  3. Within that range, prefer `q ≈ 0.75–0.85 × CW`, so the pixels are a little finer than the glyphs.

  So `q = clamp(0.8·CW, 24/H, 5·RH/H)` for a sprite `H` pixels tall. If rule 1 and rule 2 can't
  both hold, rule 1 wins. Tabi: CW 5.07, q 3.5–4.6 with depth.
- **Two sizes: in-scene and hero.** The rules above are for a character *inside a scene*, where
  it shares the frame with glyph structure. When the mascot is *the subject of the screen* (a
  home hero card, an empty state, onboarding, a celebration, a streak moment), draw it at **hero
  size**: the same sprite and palette at a larger `q`, so it stands 64–120 pt tall and is clearly
  the brightest, most saturated thing on screen. The scene around a hero mascot is a backdrop: a
  close crop (its patch of ground, a few stars, a light ring), never a wide landscape that shrinks
  it. Give it a pose and expression that tell the screen's state (sleepy, proud, waiting), and
  keep the 12-pt clear zone around nearby text. Test: at phone size, would someone point at the
  mascot first? On a hero screen they should.
- **Detail scales with size.** At hero size a 22 × 14 sprite reads as chunky; add a hero variant
  with more pixels (a finer face, paws, a lit edge, the wearable's folds) drawn from the same
  palette and anchors, rather than just scaling the small one up.
- Snap each pixel rect to device pixels (`round(x*scale)/scale`, both edges), or seams appear.
- **Rows of palette keys**, with `.` for empty. Keys index a palette, so a recolour is a palette swap.
  Example keys: `O` body, `L` lit body, `T/t` pack, `d` dark outline/hand, `k` ink (eyes, ties).
- **Three-quarter view**, facing right. Flipping mirrors it, and props that read in one hand swap with it.
- **Frames share their top rows.** `stride` and `sit` reuse `stand`'s first rows and differ only in
  the legs (`[...STAND.slice(0, 16), ...legs]`), so the head and face never jitter.
- **Named anchors** go in comments and constants: the eye blocks (for example (11–12, 5–6) and
  (19–20, 5–6)), the mouth rows, the hand that grips the held item, the head span, and the pack area.
  Everything else is placed against them.
- **Placement:** for a sprite `W × H` pixels whose feet are on its last drawn row `F`, place it at
  `left = x - (W/2)·q` and `top = feet - F·q`. (Tabi's 28 × 21 hiker: `x - 14q`, `feet - 19.5q`.)
- **Shadow:** two black rects under the feet, sized to the sprite width W: `0.65W·q × 1.2q` at 0.28
  and `0.43W·q × 0.9q` at 0.18. (Tabi's 28-wide hiker: 18q and 12q.)
- **Held items are separate** from the body (a stick, tool or flag). Each is drawn from a pivot at
  an angle, so it can plant, swing, wave and rest across the lap.

## Face and body variants (data, not new sprites)
- `EYES: Record<id, Cell[]>`: cells relative to each eye's anchor (near and far), e.g. dot, shine,
  big, happy `^ ^`, sleepy, hearts, wink, star. `EYES_SHUT` lists the styles a blink leaves alone.
- `BLINK`: a line along the bottom of each eye. Blink when `t % 3.7 < 0.14`.
- `MOUTHS`: cells in the rows under the eyes. Markings and a tail tip use an accent palette key.
- Clothes cover markings; face items cover the mouth.

## Wearables
```ts
type Wear = { at: [col, row]; rows: string[]; pal: Record<string, string>; hidesBedroll?: boolean };
const HEADWEAR: Record<string, Wear> = {
  beanie: { at: [6, -2], hidesBedroll: true, pal: { b: '#5E7FA6', B: '#46617F', o: '#F2EEE4' },
            rows: ['........oo', '....bbbbbbbb', '..bbbbbbbbbbbb', '.bbbbbbbbbbbbbb', '.BBBBBBBBBBBBBBB'] },
};
```
- **One table per slot**: head, face, neck, top, outer, bottom, feet, back, charm, held. A slot
  decides what it hides (a hat hides the bedroll; a coat covers markings).
- `at` is relative to the standing frame and can be negative (above the head). Every frame (stride,
  sit, flip) reuses the same `at`. The body's top rows don't move, so wearables stay put.
- **Two shades per material** (lit and shade, e.g. `b`/`B`), with the shade on the bottom row or brim.
- **Tints and dyes:** map palette keys through a tint table, so one sprite has colourways. Guild or
  team colours are applied live, never baked into the sprite.
- **Glass** (glasses, a visor) uses a `~` key drawn faintly over what is behind it, plus one glint cell.
- **Animated wearables** (a flag, a lantern flame, a cape) take the scene `t` and draw as live ops.

## Poses
```ts
type Pose = { rows; flip; dy; stick /*deg*/; stickLen; pivot; blink; eyes?; zs?; lean? };
function poseFor(action, s /*seconds into action*/, t /*scene time*/): Pose
```
- Each action is a pure function of `s`: walk (alternate stand/stride every 2 steps of 0.11 s, with
  the held item cycling through a list of angles), look (turn around mid-action, extra blinks),
  wave (held item overhead `150 + 25 sin(s*12)`, then a hop `dy = -sin(πp)*6`), rest (ease down
  0.5 s, sit, z's cycling, ease up).
- **Priority** when choosing the pose: playing emote > moving > asleep > idle cycle
  (`['look','look','wave','look']` on 8 s, offset by `hash(i)*8`). Leave rest out of idle so idling
  never looks like sleeping.

## Emotes
- An emote = a kind, a duration, `emotePose(kind, s, t)` (overrides of a base pose), and
  `drawEmoteFx(kind, s)` (a pixel speech bubble or particles over the head).
- Only `{kind, startedAt}` travels over the network. Every client derives the frames, so a shared
  scene stays in sync with no stored animation.
- A new emote: add it to the kind union and catalogue, write its pose overrides (reuse
  stand/stride/sit plus held-item angle, `dy`, `lean`, `eyes`), and give it an fx glyph or two.

## Palettes for a new mascot or creature
Give each its own palette of 4–6 muted keys: a body tone, a lit tone, a dark outline tone and
an ink tone, plus one or two feature colours. Keep the accent off the body; it may appear on one
wearable or feature. Never gold. Distinct species should differ in hue family, not just lightness.

## Creatures (pets, NPCs, bosses)
- **Small creatures** (pets, NPC guides): the same half-cell sprite format, in their own palette
  per species, with growth stages (baby → elder), colourways, and their own gear table. They follow
  the mascot with a lag and nap when idle.
- **Large creatures** (bosses): fine-grid glyph art from `tools/volume.py`, not pixels. They are lit
  from the upper left, with hollows dark and glowing points exported as lights. Defeat:
  shatter-and-fade. Hit: an accent flash.
- Every creature still meets the scene contract: deterministic, shadowed, depth-sorted, in palette.

## Preview
Write the frames and layers as JSON and run
`python3 tools/sprite.py spec.json out.png --px 12`. Put stand, stride, sit, flip, blink,
and each wearable on its own frame, and check the anchors line up across all of them. Then render
the mascot inside its scene at real scale (verify.md): a sprite that looks good at 12× can be lost
or oversized at 1×.
