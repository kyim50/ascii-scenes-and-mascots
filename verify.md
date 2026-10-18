# Verify before calling it done

Run these in order. Each catches what the one before it can't.

1. **Render the app's own ops.** Add a dump entry point (a test or a tsx/node script) that calls
   the real renderer at a fixed `t` with sample characters and writes the op list as JSON. Then:
   `python3 tools/render_ops.py ops.json out.png --size <W> <H> --cell <CW> --bg <bg>`.
   Don't judge a separately drawn image; it isn't what ships.
2. **Look at it closely.** Open the PNG at phone size and a 2× crop of the subject. At phone size,
   can you name the focal subject, midground and far plane? Check for the common mistakes
   in SKILL.md: boxes, banding, gold, flat silhouettes, the mascot's scale.
3. **Montage.** Render several `t` values (motion), levels or variants, and palettes, then run
   `python3 tools/montage.py sheet.png a.png b.png …`. Variants must be clearly distinct, and the
   motion must read across frames. A variant you only tested by digest has not been looked at:
   render it into the montage.
4. **In context.** Show it on the simulator or device. If the app can't run, make a full-phone
   mockup (402×874 pt at 3×, the app theme, status bar and tab bar). UI text drawn with `render_ops.py`
   uses `z` to scale from the cell-sized font. Show the person the image or
   artifact before building further on it.
5. **Pin it with tests.** In the project's test runner:
   - op count above a floor (e.g. > 800 for a full room);
   - the digest of the op list is distinct per scene or variant;
   - the same `t` gives the same digest, and a different `t` gives a different one (deterministic and animated);
   - a no-gold detector over every colour (hue 38–56°, saturation > 0.5, lightness > 0.45), with a
     self-test proving it catches `#F6D27A`; colours the user picked are exempt;
   - characters' feet fall inside the floor band at every corner;
   - pose and state changes (walking, asleep, flipped, emoting, wearing X) change the digest;
   - input order doesn't change the result.
6. **Lint and type-check** the touched files, then render the preview once more after the last edit.
