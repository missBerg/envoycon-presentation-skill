#!/usr/bin/env python3
"""Bundle an EnvoyCon HTML deck into ONE self-contained .html file.

    python3 scripts/build-html-deck.py path/to/deck.html out.html [--theme light]

- Inlines <link rel="stylesheet" href="…"> (local files only) and <script src="…"> (local files only).
- Rewrites every url(...) in the CSS and every local <img src> to a data: URI, resolving paths relative
  to the file that referenced them. Only the images a deck actually uses are embedded: background
  rules for layouts/themes that no slide uses are dropped first.
- Google Fonts @import stays as a link, so the result works as a published Artifact and offline
  (with fallback fonts).
The deck.html is expected to live in templates/html/ (or anywhere, as long as its href/src paths resolve).
"""
import base64, mimetypes, re, sys
from pathlib import Path

def data_uri(p: Path) -> str:
    mt = mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
    return f'data:{mt};base64,' + base64.b64encode(p.read_bytes()).decode()

def used_selectors(html: str):
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    layouts = set(re.findall(r'class="[^"]*\bslide\b[^"]*\bl-([a-z-]+)', html))
    themes = set(re.findall(r'data-theme="(dark|light)"', html)) or {'dark'}
    return layouts, themes

def prune_css(css: str, layouts, themes) -> str:
    """Drop generated background/brand rules for layouts or themes the deck never uses (keeps output small)."""
    out = []
    for line in css.splitlines():
        m = re.search(r'bg-([a-z]+)\.jpg|lockup-(dark|light)|ten-lockup-(dark|light)|photo-placeholder-(dark|light)', line)
        if m and line.strip().endswith('}') and 'url(' in line:
            th = re.search(r'data-theme="(dark|light)"', line)
            if th and th.group(1) not in themes: continue
            lay = re.search(r'\.slide\.l-([a-z-]+)', line)
            if lay and lay.group(1) not in layouts: continue
        out.append(line)
    return '\n'.join(out)

def inline_css(css: str, base: Path) -> str:
    def rep(m):
        ref = m.group(2)
        if ref.startswith(('data:', 'http:', 'https:', '#')): return m.group(0)
        p = (base / ref).resolve()
        return f'url("{data_uri(p)}")' if p.exists() else m.group(0)
    return re.sub(r'url\((["\']?)([^)"\']+)\1\)', rep, css)

def main():
    src, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    theme = sys.argv[sys.argv.index('--theme') + 1] if '--theme' in sys.argv else None
    html = src.read_text()
    if theme: html = re.sub(r'(<body[^>]*data-theme=")(dark|light)(")', rf'\g<1>{theme}\3', html, count=1)
    layouts, themes = used_selectors(html)

    def link(m):
        href = m.group(1)
        if href.startswith('http'): return m.group(0)
        p = (src.parent / href).resolve()
        css = prune_css(p.read_text(), layouts, themes)
        return '<style>\n' + inline_css(css, p.parent) + '\n</style>'
    html = re.sub(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>', link, html)

    def script(m):
        s = m.group(1)
        if s.startswith('http'): return m.group(0)
        return '<script>\n' + (src.parent / s).read_text() + '\n</script>'
    html = re.sub(r'<script src="([^"]+)"></script>', script, html)

    def img(m):
        s = m.group(2)
        if s.startswith(('data:', 'http')): return m.group(0)
        p = (src.parent / s).resolve()
        return m.group(1) + data_uri(p) + m.group(3) if p.exists() else m.group(0)
    html = re.sub(r'(<img[^>]+src=")([^"]+)(")', img, html)

    out.write_text(html)
    print(f'{out}  {out.stat().st_size / 1e6:.2f} MB  layouts={sorted(layouts)} themes={sorted(themes)}')

if __name__ == '__main__':
    main()
