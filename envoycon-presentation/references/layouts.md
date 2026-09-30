# Layouts: one spec, two renderers

Every layout exists in the Google Slides/.pptx template, as `Dark · <name>` and `Light · <name>`, and in the HTML deck as `.slide.l-<class>`.
Positions are in px on the 1920×1080 grid, and the two renderers use the same numbers. pptx points × 2 = HTML px.

| pptx layout | HTML class | Background | Placeholders (pptx idx → content) |
|---|---|---|---|
| Talk Title | `l-title` | title | 13 track · 14 level · 0 title · 15 speaker · 16 role |
| Talk Title · Photo | `l-title-photo` | photo | as above + 24 round headshot |
| About Me | `l-about` | speaker | 24 headshot · 10 kicker · 0 name · 15 role · 1 bio · 16 handles |
| Section Divider | `l-section` | section (pink, shared) | 10 kicker · 0 title · number = white text box |
| Title + Content | `l-content` | content | 10 kicker · 0 title · 1 bullets |
| Two Columns | `l-two-col` | content | 10 · 0 · 18/19 labels · 1/2 bodies |
| Code | `l-code` | content | 10 · 0 · 20 file label · 1 code |
| Diagram | `l-diagram` | content | 10 · 0 · 21 picture |
| Big Number | `l-big-number` | statement | 10 kicker · 0 meaning · 1 context · numeral image/text |
| Statement | `l-statement` | statement | 10 · 0 statement · 15 name · 16 detail |
| Thank You | `l-thanks` | title | 22 badge · 0 title · 15 name · 16 handles |
| Event Welcome | `l-welcome` | statement | 22 badge · 0 welcome · 1 sub |
| Agenda | `l-agenda` | content | 10 · 0 · table (max 8 rows) |
| Up Next | `l-up-next` | speaker | 24 headshot · 22 badge · 13 track · 0 title · 15 · 16 · 23 start |
| Break | `l-break` | break | 22 badge · 0 "Back at HH:MM" · 1 sub |

## Geometry (px)

| Element | x, y, w × h | Notes |
|---|---|---|
| Header lockup | 128, 92, h 66 | on title, photo, thank-you, welcome, up-next and break slides; white on the section divider |
| Kicker | 128, 148 (content family) | mono 11pt caps, meta ink |
| Slide title | 128, 196, w 1440 | Space Grotesk 32pt; 3 lines max |
| Accent bar (horizontal) | 128, 118, 96 × 6.4 | gradient, above the kicker |
| Talk title | 128, 410, w 1180 (photo: w 1000) | 44pt (photo: 40pt) |
| Chips | 128, 330, h 50 | track 300 wide, level 240 wide; centred text, 16px insets |
| Speaker block | bar 128, 806, 8 × 112; name 164, 804; role 164, 866 | |
| Anniversary lockup | 1330, 600, w 440 | title and thank-you slides; the title background keeps its focus light below it |
| Headshots (circle) | title-photo 1230, 280, 500; about 150, 276, 440; up-next 170, 317, 460 | 8px #d163ce outline |
| Section number | 112, 250, 900 × 340, bottom-anchored | white 180pt, line spacing 0.85 |
| Section title | 128, 692, w 1500 | white 60pt |
| Code panel | 128, 330, 1664 × 600 | dark in both themes |
| Big numeral | 110, 230, h 400 | gradient; the HTML deck uses gradient text |
| Statement | 128, 290, w 1500 | 46pt |
| Footer | rule y 968 from 128 to 1792; meta text 128, 994; slide number right-aligned at 1792 | |

## Safe zones for text

Keep text out of the outer 7% at left and right, and the outer 10% at top and bottom.
Each background keeps sharp lights out of these text boxes:
title `[100,320,1340,940]` · photo `[100,320,1150,930]` · speaker `[740,320,1820,930]` · content `[100,130,1720,640]` ·
statement `[100,210,1680,880]` · break `[100,330,1320,790]` · section `[90,230,1500,940]`.
