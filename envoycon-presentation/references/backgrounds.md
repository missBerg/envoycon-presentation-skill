# Backgrounds: out-of-focus lights

Every background is a scene of hexagonal out-of-focus lights. The hexagon is the lens aperture, so every light has the same orientation.
The final set was designed over six review rounds with Erica. Don't redesign it in a deck.

| File (`assets/backgrounds/<theme>/`) | Scene (`scripts/backgrounds.html?v=`) | Used by |
|---|---|---|
| `bg-title.jpg` | `hero2` | Talk Title, Thank You |
| `bg-photo.jpg` | `speakerR` | Talk Title · Photo (headshot on the right) |
| `bg-speaker.jpg` | `speaker` | About Me, Up Next (headshot on the left, no in-focus light: the face is the focus) |
| `bg-content.jpg` | `content` | Title + Content, Two Columns, Code, Diagram, Agenda |
| `bg-statement.jpg` | `statement` | Big Number, Statement, Event Welcome |
| `bg-break.jpg` | `break` | Break |
| `assets/backgrounds/bg-section.jpg` | `section&th=pink` | Section Divider (both themes) |

## How a scene is built

- **Depth:** every light has a depth d, where 0 is the focus plane and 1 is far away. Blur is `2.5 + 55·d^1.4` px. Brightness, outline strength and fade toward the haze colour all follow d. There's no jump between the sharpest light and the next one.
- **Near lights (d < .45)** are placed by hand in `keys: [x, y, r, d]` for balance. Only the far lights are scattered, and they use a fixed seed, 1310.
- **Haze:** three glow veils (`HZ` + `HAZE`) sit between the depth bands, so each band further back is washed out a little more.
- **Outline:** thin, about `r × 0.018`. It has a 45° gradient, lightened 30% at the top-left and fading out at the bottom-right, with a soft glow copy about 5× wider.
- **Fill:** a 45° gradient from the light's colour into its neighbour in the palette.
- **Text boxes (`AV`)** never get a light sharper than about 24px blur.
- **Title scene:** the focus light sits at (1800, 885), below the anniversary lockup.

## Re-rendering

```bash
cd scripts && node render-bg.mjs               # 2x PNGs (about 15 s each); ONLY=title,photo limits the set
# downscale each bg-*@2x.png to 1920×1080 and save as JPEG quality 90 (4:4:4) → bg-<name>.jpg
```

Preview any scene with sample text on top: `scripts/backgrounds.html?v=hero2&th=dark&txt=1`.
