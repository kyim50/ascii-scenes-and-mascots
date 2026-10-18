# House style (Kimani's projects)

These are standing preferences. Apply them unless the person asks otherwise in the current request.

## Palette
- **Accent** `#D97757` (pressed `#C6613F`), used sparingly: one ribbon, one sign, an arrow, a target.
- **No gold.** Not in props, trim, stars, flames or metals. The exceptions are crowns and medals,
  and gold the user picked themselves (for example as banner trim). Detector: hue 38–56°,
  saturation > 0.5, lightness > 0.45.
  - Flames: `#EFA24E #D97757 #A8482E`. There is no yellow or white core; brightness comes from
    glyph density and light rings.
  - Metals: silver `#C8CCD0 #ECEFF1 #868C92`, steel `#9AA3A8 #6B7378`, bronze `#B07A4A`,
    copper `#B87333`, iron rods.
- **Muted, mid-dark hues** for props: books `#7E4E4A #5E6F5A #4F6A7A #6B5B7E #8A7A5A`,
  straw `#A89670`, parchment `#C8B48A` with ink `#4A3C28`.
- **Mascot (Clawd-style hiker):** body `#CB7C5E`, lit `#D3896B`, pack `#BE8D47 / #A47331`,
  dark `#6A4019`, ink `#251810`. A new creature gets its own muted palette (mascots.md § Palettes).

## Time of day
- Scenes are set at night or dusk by default. Dusk warms the sky; the colour layer keeps its hues.
- **Exception: an app with light screens.** When the app's direction has a light theme (a morning
  log, a daytime mode), its scenes may be set at dawn or in soft daylight to match, so they belong
  on the light page instead of sitting there as dark cards. Keep the same rules: glyph structure,
  form from light (the sun as a pixel disc with light rings, never a yellow blob), a value plan,
  no gold (sunlight is a pale warm ink, not saturated yellow), and dim, simple backdrops.

## Glyph-only grounds (hearth/Rami and similar ink styles)
- Backgrounds are drawn only with glyphs: ground, walls, furniture, trees. Form comes from density,
  lit edges, light pools and cleared shadows.
- Colour belongs to mascots and small props. Shapes are outlined with stroke glyphs that follow the
  edge (`/ \ ( ) | _ -`). The densest areas become solid ink bars, and interiors stay sparse.
- Scenes must feel alive: small animated creatures and details, never an empty set.

## Fine-grid over chunky
- Prefer fine-grid art (a small cell, many columns) over chunky ASCII, even for small UI tiles.
- Keep backdrops dim and simple so the subject reads. Thick forms read; thin tubes look like wire.

## Edges and boxes
- No faint outline strokes around panels or props; use soft fills or light instead.
- No halo rectangles around lights; the light rings do that job.

## Motion
- Smooth, deliberate motion. Steady phases (`sin(t*k)`), never a phase multiplied by a varying gust.
- Shading on moving cloth stays subtle and never darkens an emblem.

## Presentation
- Show the work in context ("with the whole phone"): a full-phone mockup (402×874 pt at 3×, the app
  theme, status bar and tab bar), or the simulator, before building further.
