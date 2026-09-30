---
name: envoycon-presentation
description: Build EnvoyCon 10 Year Anniversary slide decks (any 10-year EnvoyCon — virtual, KubeCon, regional; speaker talks and host run-of-show) in the dark or light theme — as Google Slides/.pptx from the official template, or as code-based HTML decks with the same layouts and out-of-focus-light backgrounds.
---

# EnvoyCon 10 Years — Presentation Builder

Builds decks for **any 10 Year Anniversary EnvoyCon** (EnvoyCon Virtual, EnvoyCon at
KubeCon, regional editions) on the official template, in a **dark** or **light** theme.
The template is event-agnostic: no event name beyond "EnvoyCon", no date, no "Virtual".

You fill the named layouts. You never design slides from scratch. That keeps every speaker's deck
and every host slide on the same system as the social assets.

Use this skill together with `envoycon-design-system`. That skill holds the
tokens and the seven rules. This one holds the slide mechanics and the light
theme, which applies to slides only. Social assets stay dark.

## 0. Skill files (GitHub: `missBerg/envoycon-presentation-skill`)

Everything this skill uses lives in one repo, so pptx and HTML decks share exactly the same assets:

```
envoycon-presentation/
  SKILL.md                     this file
  assets/backgrounds/{dark,light}/bg-{title,photo,speaker,content,statement,break}.jpg  +  bg-section.jpg
  assets/brand/                lockup-{dark,light,white}.png · ten-lockup-{dark,light}.png · wordmark-{white,color,black}.png · bar-{h,v}.png
  assets/numerals/num-01…10.png   gradient numerals for pptx
  assets/headshot/             photo-placeholder-{dark,light}.png · glow-{dark,light}.png
  templates/pptx/EnvoyCon-10-Slides-Template.pptx
  templates/html/              envoycon-deck.css · envoycon-deck.js · example.html (all 15 layouts)
  references/                  tokens.json · layouts.md · backgrounds.md · html-deck.md
  scripts/                     build-html-deck.py · backgrounds.html + render-bg.mjs · build_template.py (+ make-kit.sh) · render.mjs · assets.html
```

**Getting the files:**
1. Clone it with `git clone https://github.com/missBerg/envoycon-presentation-skill` if the shell has GitHub access.
2. Otherwise, use the GitHub connector: `get_file_contents` on `envoycon-presentation/...` for text files, and download binaries by path.
3. The local kit is a fallback: `~/Downloads/envoycon-design-system/slides/` has the pptx and `slides-kit/`.

Never redraw a background, lockup or numeral. Always use these files.
**Choose the renderer:** Google Slides or .pptx (the default for speakers) → §1–§8. A code-based deck (HTML, published page, PDF from code) → §9.

## 1. Pick the theme

There is **one template file** with every layout twice: `Dark · <name>` and
`Light · <name>` (one master, so Google Slides shows all of them in the Layout
menu). The pink `Section Divider` has no prefix and works in both.

| Theme | Use when |
|---|---|
| **Dark** (default) | Streamed talks, host run-of-show, anything shown next to the social assets |
| **Light** | The speaker asks for it: bright rooms, printing, dense diagrams, or accessibility preference |

If the user hasn't said which, ask once. If nobody's there to answer, use
Dark. Never mix themes in one deck (the Section Divider is the exception).
Both variants of a layout share the same placeholder indices.

## 2. Where the templates live

| Source | Location | Use for |
|---|---|---|
| Master `.pptx` | repo `templates/pptx/EnvoyCon-10-Slides-Template.pptx` (also at `~/Downloads/envoycon-design-system/slides/`) | **Always build from this** |
| Google Slides template | Drive: "EnvoyCon 10 — Slides Template" (search Drive by title; the link is in the project's Slides Template doc) | For humans: File → Make a copy |
| Build kit | repo `scripts/` (run `bash scripts/make-kit.sh` first); local copy in `…/slides/slides-kit/` | Regenerate backgrounds, lockups and numerals (`node render.mjs`), then rebuild the master (`python3 build_template.py`) |

If the master `.pptx` is not reachable, ask the user to attach it. Don't rebuild
the template by hand. The old per-theme "EnvoyCon Virtual 10" files are superseded,
so don't build from them.

## 3. Workflow

1. **Get the content first.** You need the talk title, speaker, role, track and
   level (from Sessionize: `Topic` → track, `Level` → level), and a headshot if
   there is one. For host decks, get the agenda from the schedule sheet.
2. **Pick the theme** (§1).
3. **Outline to layouts.** Map every slide to one layout from §4 before you
   write any code. Show the user the outline as a table (slide #, layout,
   headline) when the deck has more than 8 slides.
4. **Build with python-pptx** (§5). Open the master and delete all its slides.
   That removes the two guide slides at the front (How to use this template,
   Which layout when), the samples and the Asset Shelf. Then add slides by
   layout name and fill the placeholders by idx.
5. **Add headshots and numerals** (§6). Headshots go into the round image
   placeholder (idx 24). Numerals are gradient images.
6. **Render and check** (§7) with LibreOffice → PNG. Look at every slide.
7. **Deliver** (§8). Write a `.pptx` into the user's folder. If they asked for
   Slides, also upload it as native Google Slides.

## 4. Layouts and placeholder map

`L = {l.name: l for l in prs.slide_layouts}` and `lay(name)` (§5) adds the
`Dark · ` / `Light · ` prefix. The tables below use the bare names. `0` is always the title.
**24** is the round headshot image placeholder on photo layouts. It's a picture
placeholder (like the Diagram slide's 21) with circle geometry and a pink outline.

### Speaker layouts

| Layout | Use | Placeholders (idx → content) |
|---|---|---|
| `Talk Title` | Opening slide when there's no headshot. The anniversary lockup fills the right side | 13 track chip · 14 level chip · 0 talk title · 15 speaker name · 16 role · company |
| `Talk Title · Photo` | Opening slide with a headshot | same as above + 24 round headshot |
| `About Me` | Speaker intro | 24 round headshot · 10 kicker · 0 name · 15 role · 1 bio bullets · 16 handles |
| `Section Divider` | Chapter break. A **pink** full-bleed gradient canvas with white type, identical in both themes | 10 kicker · 0 section title. Add the section number as a white text box (§6) |
| `Title + Content` | The default content slide | 10 kicker · 0 title · 1 bullets (levels 0–2) |
| `Two Columns` | Compare, or before/after | 10 kicker · 0 title · 18, 19 column labels · 1, 2 column bodies |
| `Code` | Config, CLI, YAML. The code panel stays dark in both themes | 10 kicker · 0 title · 20 file label · 1 code (one line per paragraph) |
| `Diagram` | One diagram per slide | 10 kicker · 0 title · 21 picture placeholder |
| `Big Number` | One stat | 10 kicker · 0 what it means · 1 context/source. Add a gradient numeral image above the title (§6) |
| `Statement` | The takeaway, or a quote | 10 kicker · 0 statement · 15 attribution · 16 detail |
| `Thank You` | Close, Q&A | 22 badge · 0 "Thank you" · 15 name · 16 handles |

### Host run-of-show layouts

| Layout | Use | Placeholders |
|---|---|---|
| `Event Welcome` | Event opener | 22 badge · 0 welcome line · 1 sub |
| `Agenda` | Schedule | 10 kicker · 0 title · 1 body. Delete 1 and add a table (§5) |
| `Up Next` | Between sessions | 24 round headshot · 22 badge · 13 track chip · 0 session title · 15 speaker · 16 role · 23 start time |
| `Break` | Breaks | 22 badge · 0 "Back at HH:MM" · 1 sub |
| `Thank You` | Event closer | reuse it, with the badge set to "Wrap-up" |

### Copy rules

- **Mono placeholders** (kicker, chips, badge, handles, start time, file label):
  type the text in UPPERCASE yourself. Google Slides drops `cap="all"` and letter-spacing.
- **Titles** are Space Grotesk, 3 lines or fewer, with no quotation marks around
  session titles. If a talk title is over 62 characters, drop the size one step
  (`run.font.size = Pt(36)`).
- **Bullets:** 3–5 per slide, one line each where you can. Use level 1 only for detail.
- **Times** carry the event's time zone when the audience is remote (e.g. `13:40 ET`); in-person events can drop it.
- **Never** put emoji or a URL on a slide (virtual: "link in chat"; in person: a QR
  code or "slides on the schedule page"). The template carries no event date or
  city; add them only where the user gives them (e.g. the Event Welcome sub line).
- Say "EnvoyCon", not "EnvoyCon Virtual", unless the user is building for the virtual edition.

## 5. Build code

```python
import io
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
PX = 6350                                   # 1px on the 1920×1080 grid, in EMU
px = lambda v: Emu(int(round(v * PX)))
THEME = 'dark'                              # or 'light'
TEMPLATE = '.../EnvoyCon-10-Slides-Template.pptx'
C = {  # role → hex, per theme (alpha tokens pre-blended so Slides renders them exactly)
  'dark':  dict(canvas='10041C', panel='1C0930', ink='FFFFFF', dim='BCB9BF', faint='88828D', line='461F4E',
                meta='EBA6E8', accent='D163CE', track='592860', trackText='FFFFFF', numfb='D163CE'),
  'light': dict(canvas='FBF8FD', panel='F3EAF6', ink='10041C', dim='524859', faint='867E8D', line='E9C1E9',
                meta='B31AAB', accent='D163CE', track='F3DDF5', trackText='10041C', numfb='B31AAB'),
}[THEME]

prs = Presentation(TEMPLATE)
# harvest reusable images from the sample slides BEFORE deleting them
blobs = {}
for s in prs.slides:
    for sh in s.shapes:
        if sh.shape_type == 13: blobs.setdefault(sh.name, sh.image.blob)
# blobs: 'Gradient numeral 01'…'10', 'Header lockup', 'Accent bar (horizontal|vertical)'.
# The first sample set (dark) is harvested first; for a light deck take 'Header lockup' from a Light · slide
# (or use slides-kit/assets/light/lockup.png).
sldIdLst = prs.slides._sldIdLst
for sldId in list(sldIdLst):
    prs.part.drop_rel(sldId.rId); sldIdLst.remove(sldId)

L = {l.name: l for l in prs.slide_layouts}
PFX = 'Dark · ' if THEME == 'dark' else 'Light · '
lay = lambda n: L[n if n == 'Section Divider' else PFX + n]

def fill(slide, values):
    """values: {idx: str | [str | (str, level)] | None}. None deletes the placeholder."""
    for ph in list(slide.placeholders):
        i = ph.placeholder_format.idx
        if i not in values: continue
        v = values[i]
        if v is None: ph._element.getparent().remove(ph._element); continue
        tf = ph.text_frame
        for n, it in enumerate(v if isinstance(v, list) else [v]):
            t, lvl = (it, 0) if isinstance(it, str) else it
            p = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
            p.text, p.level = t, lvl
    # delete text placeholders left empty so no prompt text shows
    for ph in list(slide.placeholders):
        if ph.has_text_frame and not ph.text_frame.text.strip() and ph.placeholder_format.type != 18:
            ph._element.getparent().remove(ph._element)

s = prs.slides.add_slide(lay('Title + Content'))
fill(s, {10: 'LESSON 01', 0: 'Start with the traffic shape', 1: ['Point', ('Detail', 1), 'Point']})
s.notes_slide.notes_text_frame.text = 'Speaker notes here'
```

**Agenda table.** Delete placeholder 1. Add
`s.shapes.add_table(rows, 3, px(128), px(340), px(1664), px(rows*80))` with
column widths 240 / 924 / 500 px. Set `tblPr firstRow="0" bandRow="0"` with no
table style. Give every cell `fill.background()`, only a 1.5px bottom border in
`C['line']`, and a middle anchor. Style the columns like this:

- Time: JetBrains Mono 12pt bold, `C['meta']`.
- Session: Space Grotesk 17pt bold, `C['ink']`. Use `C['faint']` for breaks.
- Speaker: Inter 13pt, `C['dim']`.

Fit at most 8 rows per slide. If there are more, split them onto a second Agenda slide.

**Chips outside placeholders.** Use a rounded rect (`add_shape(5, …)`,
`adjustments[0]=0.5`, height 50px) with JetBrains Mono 8.5pt bold. Show two
chips at most, track first.

- Track chip: fill `C['track']`, border `C['accent']`, text `C['trackText']`.
- Level chip: fill `C['panel']`, border `C['line']`, text `C['meta']`.

## 6. Headshots and gradient numerals

**Round headshot.** Photo layouts have a round **picture placeholder** (idx 24).
It works like the Diagram slide: in Google Slides you click the image icon to
insert a photo, or use Replace image to swap one. It stays a circle with the
8px pink (`D163CE`) outline. When a deck is built with a photo, insert it into
the placeholder and re-apply the circle and outline on the picture:

```python
from lxml import etree
A_NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
SLOTS = {'title-photo': (1230, 280, 500, 500), 'about': (150, 276, 440, 440), 'upnext': (170, 317, 460, 460)}
def photo_slot(slide, key, photo_path=None):
    """No photo → leave the empty round placeholder (speaker clicks to add one)."""
    if photo_path is None: return None
    x, y, w, h = SLOTS[key]
    ph = [p for p in slide.placeholders if p.placeholder_format.idx == 24][0]
    pic = ph.insert_picture(photo_path)                       # auto-crops to the square box
    spPr = pic._element.spPr
    for ch in list(spPr): spPr.remove(ch)
    for xml in (f'<a:xfrm {A_NS}><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(h)}"/></a:xfrm>',
                f'<a:prstGeom {A_NS} prst="ellipse"><a:avLst/></a:prstGeom>',
                f'<a:ln {A_NS} w="{px(8)}"><a:solidFill><a:srgbClr val="D163CE"/></a:solidFill></a:ln>'):
        spPr.append(etree.fromstring(xml))
    return pic
```

Note that the `fill()` helper above keeps picture placeholders (`type != 18`),
so an empty headshot placeholder survives for the speaker to fill in.

- Photo prep: crop it square at 800×800 and remove any baked-in ring (a 0.82
  centre crop usually does it).
- If there is no headshot yet, leave placeholder 24 empty. It shows as the round
  frame with an insert-image button in Slides. For a final deck with no photo at
  all, use `Talk Title` (the no-photo variant).
- Headshots are always round on slides. (The social-asset kit still uses the
  rounded hexagon frame. That's a separate asset system.)

**Gradient numerals.** Text in Slides can't carry a gradient, so numerals are images.
- Section Divider: the number is **white text**, not a gradient image, because the canvas is already the gradient:
  `slide.shapes.add_textbox(px(112), px(250), px(900), px(340))` with the number in
  Space Grotesk Bold 180pt, `FFFFFF`, bottom-anchored, line spacing 0.85.
- Big Number `10`: add the blob at `(110, 230)`, height 400px.
- Any other stat (`3×`, `42%`): run `NUMS='42%,3×' node render.mjs` in the kit and use
  `assets/num-custom-*.png`. If you can't render, add a text box in Space Grotesk
  Bold ~170pt in solid `C['numfb']`. That's a fallback, not a second design.
  (The layouts have no numeral placeholder, because Slides shows a giant
  "Click to add" prompt in empty ones.)

The gradient does exactly three jobs: big numerals, accent bars, and the
anniversary lockup. The one deliberate exception is the `Section Divider`
canvas. Never put it on text blocks, panels or buttons.

### Backgrounds: out-of-focus lights

Every background is a scene of hexagonal out-of-focus lights. The hexagon is the lens aperture, so every light has the same orientation.

- **Depth:** each light has a depth d, where 0 is in focus and 1 is far away. Blur (2.5 to 57px), brightness and outline strength all follow d, so the step from the sharpest light to the next is gradual.
- **Haze:** three soft glow veils sit between the depth bands, and far lights fade toward the haze colour, like distance in real life.
- **Outlines** are thin, with a 45° gradient that is bright at the top-left and fades out at the bottom-right, plus a soft glow. **Fills** are 45° gradients too.
- **Placement:** near lights are placed by hand for balance. Only far lights are scattered.

| Background | Layouts | Composition |
|---|---|---|
| `bg-title.jpg` | Talk Title, Thank You | Lights on the right; the sharpest one sits bottom-right, below the 10-years lockup at (1330, 600) |
| `bg-photo.jpg` | Talk Title · Photo | Lights frame the headshot on the right |
| `bg-speaker.jpg` | About Me, Up Next | Lights frame the headshot on the left; no in-focus light, so the headshot is the focus |
| `bg-content.jpg` | Title + Content, Two Columns, Code, Diagram, Agenda | Three near lights in the bottom-right corner; the rest is haze |
| `bg-statement.jpg` | Big Number, Statement, Event Welcome | Near lights ring the edges; the middle stays quiet |
| `bg-break.jpg` | Break | Dense field; the sharpest light is top-right |
| `bg-section.jpg` | Section Divider | White lights on the pink gradient |

Rules:
- Never put text or gradient numerals over a light sharper than about 24px blur.
- Don't add hexagon shapes on slides. To change a scene, edit its `keys` in
  `slides-kit/backgrounds.html` and re-render with `node render-bg.mjs`, then
  export 1920×1080 JPEGs.

Keep every layout on the master colour map. A layout with its own colour map
(`overrideClrMapping`) makes Google Slides split it into a separate master.
New text boxes default to mid violet `#8C6CA6`, which reads on both canvases.
Recolour to ink or white.

## 7. Check before delivering

```bash
soffice --headless --convert-to pdf deck.pptx && pdftoppm -r 50 -png deck.pdf s
```

Tile the PNGs into a contact sheet and look at it:
- Nothing overlaps, and no text runs into the edge strips (roughly the outer 7%
  left and right, 10% top and bottom).
- Titles fit in 3 lines. On photo layouts the title stays left of x=1128 (Up Next: right of x=760).
- Every headshot is a perfect circle with a pink outline: a photo, or an empty placeholder waiting for one.
- In light decks, all small text uses `meta`/`ink`/`dim`, never `accent` pink (it's too light for small type on the light canvas).
- No empty text placeholders, no emoji, no URLs.
- Google Slides renders text slightly wider than LibreOffice (it has no
  letter-spacing), so leave about 10% slack.

## 8. Delivery

1. Write `<talk-slug>-envoycon10-<theme>.pptx` into the user's connected folder,
   next to the templates.
2. **Google Slides.** A deck with images is too large for the Drive connector
   upload, so upload through Chrome, with the user's OK:
   - In a fresh tab, open the Drive picker's upload-only URL from
     `slides-kit/README.md`.
   - Make the hidden `input[type=file]` visible with JS, `find` it, then call
     `file_upload` straight away (the picker re-renders, so refs go stale fast).
     `file_upload` accepts paths in the cloud working directory, not device
     paths. Upload one file per call.
   - If an upload silently does nothing, the tab is probably hidden
     (`document.visibilityState`); bring the Claude window to the current Space
     and retry with a fresh `find`.
   - Drive converts the file to native Slides. Confirm it with Drive
     `search_files`, then rename it with `update_file`.
   - Never navigate away from an open Slides *editor* tab, because its unload
     dialog freezes Chrome. Use `/embed?start=false` URLs to look at results.
   - If Chrome calls keep timing out, the Claude tab-group window is probably
     on another macOS Space, where Chrome throttles it. Use computer use
     (grant Chrome, read tier) and `app_bring_to_current_space` on that
     window, then retry.
3. If Chrome isn't available or keeps freezing, hand over the `.pptx`. Tell
   them: Drive → New → File upload, then open it with Google Slides.

## 9. Code-based decks (HTML)

Use `templates/html/`. It uses the same 15 layouts, the same geometry (pptx pt × 2 = px) and the same background JPEGs. The full guide is in `references/html-deck.md`.

1. Copy `templates/html/example.html` to `templates/html/<talk-slug>.html`, keeping it next to the CSS and JS. Delete the layouts you don't need.
2. Set `<body class="deck" data-theme="dark|light">`. Use one `<section class="slide l-<layout>">` per slide:
   `l-title`, `l-title-photo`, `l-about`, `l-section`, `l-content`, `l-two-col`, `l-code`, `l-diagram`, `l-big-number`, `l-statement`, `l-thanks`, `l-welcome`, `l-agenda`, `l-up-next` and `l-break`.
3. Fill in the same child classes as the example: `.kicker`, `.title`, `.bullets`, `.speaker`, `.role`, `.pill` (plus `.track`/`.level`), `.ec-photo` (with an `<img>`, or empty for the placeholder), `.big.grad-text` for numerals, and `.code pre` with `.k` keys.
4. The HTML copy rules are the same as §4. HTML keeps letter-spacing and uppercase, so type mono text in normal case.
5. Don't add inline positions, colours or backgrounds. If content doesn't fit, choose another layout.
6. **Bundle:** `python3 scripts/build-html-deck.py templates/html/<slug>.html out/<slug>-envoycon10.html`. That gives one self-contained file of about 1.5 MB that works offline and as an Artifact. For PDF, open it in Chrome, press P, and set margins to None.
7. **Check:** use Playwright at a 1920×1080 viewport, screenshot `#1…#n`, and run the §7 checklist.

## 10. Tokens (quick reference)

Machine-readable: `references/tokens.json`.

| Role | Dark | Light |
|---|---|---|
| Canvas | `#10041c` | `#fbf8fd` |
| Panel | `#1c0930` | `#f3eaf6` |
| Ink | `#ffffff` | `#10041c` |
| Dim | `#bcb9bf` | `#524859` |
| Faint | `#88828d` | `#867e8d` |
| Hairline | `#461f4e` | `#e9c1e9` |
| Mono / meta ink | `#eba6e8` | `#b31aab` |
| Accent strokes, headshot outline | `#d163ce` | `#d163ce` |
| Wordmark | official white horizontal | official **color** horizontal (CNCF artwork) |

Gradient (both themes): `#d163ce → #b31aab → #8a12c4`.

Fonts: Space Grotesk 700 (display), Inter 400/600 (body), and JetBrains Mono
400/700 in uppercase (meta).

Slide type scale in pt: talk title 44 · slide title 32 · section title 44 ·
statement 46 · body 18/16/14 · kicker 11 · chips 8.5 · footer 9.