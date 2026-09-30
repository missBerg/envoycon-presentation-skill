# Code-based decks (HTML)

Use this when the talk is authored in code rather than Google Slides: a deck in a repo, a deck published as a page, or a deck you generate programmatically.
It uses the same backgrounds, tokens and layout geometry as the pptx template, so both versions of a talk look identical.

## Files

- `templates/html/envoycon-deck.css`: tokens (dark and light), all 15 layouts, backgrounds, pills, headshot and print rules. Asset paths are relative to this file (`../../assets/...`).
- `templates/html/envoycon-deck.js`: scales the 1920×1080 stage to the window. Keys: → ← Space, Home/End, F for fullscreen, P to print/PDF. `#n` in the URL is the current slide. It also fills `.slide-num`.
- `templates/html/example.html`: every layout, ready to copy. Add `?theme=light` to preview light.
- `scripts/new-html-deck.py`: scaffolds a deck folder with the theme, assets and a copy of the example.
- `scripts/build-html-deck.py`: bundles a deck into one self-contained HTML file. CSS and JS are inlined and images become data URIs. It only embeds the backgrounds the deck uses.

## Authoring

1. Scaffold the deck wherever the talk lives:
   `python3 scripts/new-html-deck.py <deck-dir> --slug <talk-slug> --theme dark|light`.
   That creates `<talk-slug>.html` from the example, plus `theme/` and `assets/`. Keep only the layouts the outline needs.
   In Claude Code, `scripts/` is `${CLAUDE_SKILL_DIR}/scripts/`.
2. Set `<body class="deck" data-theme="dark">` (or `light`). Use one theme per deck. A single slide can override it with its own `data-theme`.
3. Use one `<section class="slide l-<layout>">` per slide, with the same child classes as the example: `.kicker`, `.title`, `.bullets`, `.speaker`, `.role`, `.pill` (plus `.track`/`.level`), `.ec-photo`, `.ec-lockup`, `.ec-ten`, `.bar-v`, `.bar-h`, `.footer`, `.slide-num`.
4. **Headshots:** `<div class="ec-photo"><img src="speaker.jpg" alt="Speaker Name"></div>`. Leave the div empty to show the placeholder.
5. **Big numbers:** `<div class="big grad-text">42%</div>`. Gradient text is live in HTML, so no image is needed.
6. **Code:** use `<pre>` inside `.code` and wrap keys in `<span class="k">`. The panel stays dark in both themes.
7. Don't add positioning, colours or backgrounds of your own. If a layout doesn't fit the content, pick a different layout.

## Deliver

```bash
python3 scripts/build-html-deck.py <deck-dir>/<talk-slug>.html <deck-dir>/<talk-slug>-envoycon10.html [--theme light]
```

- **One file:** about 1.5 MB with all 15 layouts in one theme. Fonts load from Google Fonts, which Artifact pages allow.
- **Artifact / shareable page:** publish the bundled file.
- **PDF:** open the file in Chrome, press P, and choose Save as PDF with margins set to None. It prints one slide per 1920×1080 page.
- **Screenshot check:** open the bundle with Playwright at a 1920×1080 viewport, step `#1…#n`, and screenshot each slide. Review the contact sheet with the same checklist as SKILL.md §7.
