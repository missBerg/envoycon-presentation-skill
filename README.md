# EnvoyCon 10 Years: presentation skill

This repo is the agent skill and design assets for **10 Year Anniversary EnvoyCon** decks: EnvoyCon Virtual, EnvoyCon at KubeCon, and regional editions.
One design system has two renderers, and both use the same backgrounds, tokens and layouts:

| Renderer | Where | Use for |
|---|---|---|
| Google Slides / .pptx | `envoycon-presentation/templates/pptx/` | Speaker decks, host run-of-show. Every layout comes in `Dark ·` and `Light ·` versions |
| HTML deck | `envoycon-presentation/templates/html/` | Code-based talks, published pages, PDF from code |

```
envoycon-presentation/
  SKILL.md        instructions for the agent (the envoycon-presentation skill)
  assets/         backgrounds (out-of-focus lights), brand lockups, wordmarks, numerals, headshot pieces
  templates/      pptx master + HTML deck theme/runtime/example
  references/     tokens.json, layouts.md, backgrounds.md, html-deck.md
  scripts/        build-html-deck.py (bundle to one file), background renderer, pptx builder
```

## Quick start (HTML)

```bash
cp envoycon-presentation/templates/html/example.html envoycon-presentation/templates/html/my-talk.html
# edit the slides, keep the layout classes
python3 envoycon-presentation/scripts/build-html-deck.py envoycon-presentation/templates/html/my-talk.html my-talk.html
open my-talk.html   # → / ← to move between slides, P to print a PDF
```

## Rebuild the pptx

```bash
bash envoycon-presentation/scripts/make-kit.sh
cd envoycon-presentation/scripts && python3 build_template.py
```

The wordmarks are the official CNCF EnvoyCon artwork. The backgrounds were designed for EnvoyCon's 10th anniversary, so don't restyle them per deck.
