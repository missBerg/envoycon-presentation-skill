#!/usr/bin/env bash
# Lay the repo's assets out the way the build scripts expect (scripts/assets/<theme>/...), so the
# pptx template can be rebuilt from this repo:
#   bash scripts/make-kit.sh && cd scripts && python3 build_template.py   # → EnvoyCon-10-Slides-Template.pptx
# Re-rendering lockups/numerals (render.mjs) or backgrounds (render-bg.mjs) also needs Playwright and the
# @fontsource packages unpacked next to assets.html (fontsource-<family>-5.3.0/files/...).
set -euo pipefail
cd "$(dirname "$0")"
R=..
mkdir -p assets/dark assets/light
for t in dark light; do
  for b in title photo speaker content statement break; do cp "$R/assets/backgrounds/$t/bg-$b.jpg" "assets/$t/"; done
  cp "$R/assets/brand/lockup-$t.png" "assets/$t/lockup.png"
  cp "$R/assets/brand/ten-lockup-$t.png" "assets/$t/ten-lockup.png"
  cp "$R/assets/headshot/glow-$t.png" "assets/$t/hex-glow.png"
  cp "$R/assets/headshot/photo-placeholder-$t.png" "assets/$t/photo-placeholder.png"
done
cp "$R/assets/backgrounds/bg-section.jpg" assets/
cp "$R/assets/brand/lockup-white.png" "$R/assets/brand/bar-h.png" "$R/assets/brand/bar-v.png" assets/
cp "$R/assets/brand/wordmark-white.png" assets/wordmark.png
cp "$R/assets/brand/wordmark-color.png" "$R/assets/brand/wordmark-black.png" assets/
cp "$R"/assets/numerals/num-*.png assets/
echo "kit ready in scripts/assets"
