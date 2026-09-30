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

## Install in Claude Code

```bash
claude plugin marketplace add missBerg/envoycon-presentation-skill
claude plugin install envoycon-presentation@envoycon
```

Or run it inside a session: `/plugin marketplace add missBerg/envoycon-presentation-skill`, then `/plugin install envoycon-presentation@envoycon`, then `/reload-plugins`.
Update later with `claude plugin marketplace update envoycon`.

## Quick start (HTML)

```bash
python3 envoycon-presentation/scripts/new-html-deck.py ~/talks/my-talk --slug my-talk
# edit ~/talks/my-talk/my-talk.html, keep the layout classes
python3 envoycon-presentation/scripts/build-html-deck.py ~/talks/my-talk/my-talk.html ~/talks/my-talk/my-talk-envoycon10.html
open ~/talks/my-talk/my-talk-envoycon10.html   # → / ← to move between slides, P to print a PDF
```

## Rebuild the pptx

```bash
bash envoycon-presentation/scripts/make-kit.sh
cd envoycon-presentation/scripts && python3 build_template.py
```

The wordmarks are the official CNCF EnvoyCon artwork. The backgrounds were designed for EnvoyCon's 10th anniversary, so don't restyle them per deck.
