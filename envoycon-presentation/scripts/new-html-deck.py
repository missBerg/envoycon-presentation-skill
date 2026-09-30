#!/usr/bin/env python3
"""Scaffold an EnvoyCon HTML deck in any folder (your talk repo, a scratch dir, ...).

    python3 scripts/new-html-deck.py <deck-dir> [--slug my-talk] [--theme dark|light]

Creates:
    <deck-dir>/<slug>.html          starts as a copy of templates/html/example.html (all 15 layouts)
    <deck-dir>/theme/envoycon-deck.css, envoycon-deck.js
    <deck-dir>/assets/...            backgrounds, brand, headshot pieces (only what the CSS needs)
Nothing is written inside the skill folder, so plugin updates never clobber a talk.
Then edit <slug>.html and bundle it:
    python3 scripts/build-html-deck.py <deck-dir>/<slug>.html <deck-dir>/<slug>-envoycon10.html
"""
import re, shutil, sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent

def main():
    args = sys.argv[1:]
    if not args or args[0].startswith('-'):
        sys.exit(__doc__)
    dest = Path(args[0]).expanduser().resolve()
    slug = args[args.index('--slug') + 1] if '--slug' in args else 'deck'
    theme = args[args.index('--theme') + 1] if '--theme' in args else 'dark'
    (dest / 'theme').mkdir(parents=True, exist_ok=True)

    css = (SKILL / 'templates/html/envoycon-deck.css').read_text().replace('../../assets/', '../assets/')
    (dest / 'theme/envoycon-deck.css').write_text(css)
    shutil.copy(SKILL / 'templates/html/envoycon-deck.js', dest / 'theme/envoycon-deck.js')
    for sub in ('backgrounds', 'brand', 'headshot'):
        shutil.copytree(SKILL / 'assets' / sub, dest / 'assets' / sub, dirs_exist_ok=True)

    html = (SKILL / 'templates/html/example.html').read_text()
    html = html.replace('href="envoycon-deck.css"', 'href="theme/envoycon-deck.css"')
    html = html.replace('src="envoycon-deck.js"', 'src="theme/envoycon-deck.js"')
    html = re.sub(r'(<body class="deck" data-theme=")(dark|light)(")', rf'\g<1>{theme}\3', html, count=1)
    out = dest / f'{slug}.html'
    if out.exists():
        sys.exit(f'{out} already exists; pick another --slug')
    out.write_text(html)
    print(f'deck:   {out}\ntheme:  {dest / "theme"}\nassets: {dest / "assets"}')

if __name__ == '__main__':
    main()
