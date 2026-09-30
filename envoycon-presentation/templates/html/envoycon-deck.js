/* EnvoyCon 10 Years — HTML deck runtime.
   Scales the 1920×1080 slides to the window, handles navigation and fills slide numbers.
   Keys: → / Space / PageDown next · ← / PageUp previous · Home / End · F fullscreen · P print (PDF).
   The URL hash (#3) is the current slide, so links and reloads keep your place. */
(() => {
  const slides = [...document.querySelectorAll('.slide')];
  if (!slides.length) return;
  let stage = document.querySelector('.deck-stage');
  if (!stage) { stage = document.createElement('div'); stage.className = 'deck-stage'; slides[0].before(stage); slides.forEach(s => stage.append(s)); }

  // slide numbers: any .slide-num element gets its 2-digit position
  slides.forEach((s, i) => s.querySelectorAll('.slide-num').forEach(n => { n.textContent = String(i + 1).padStart(2, '0'); }));

  let cur = Math.min(Math.max(parseInt(location.hash.slice(1), 10) - 1 || 0, 0), slides.length - 1);
  const fit = () => {
    const k = Math.min(innerWidth / 1920, innerHeight / 1080);
    slides.forEach(s => {
      s.style.transform = `translate(${(innerWidth - 1920 * k) / 2}px, ${(innerHeight - 1080 * k) / 2}px) scale(${k})`;
    });
  };
  const show = i => {
    cur = Math.min(Math.max(i, 0), slides.length - 1);
    slides.forEach((s, j) => s.classList.toggle('is-active', j === cur));
    history.replaceState(null, '', '#' + (cur + 1));
  };
  addEventListener('keydown', e => {
    if (['ArrowRight', 'PageDown', ' '].includes(e.key)) { e.preventDefault(); show(cur + 1); }
    else if (['ArrowLeft', 'PageUp'].includes(e.key)) { e.preventDefault(); show(cur - 1); }
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(slides.length - 1);
    else if (e.key === 'f' || e.key === 'F') document.fullscreenElement ? document.exitFullscreen() : document.documentElement.requestFullscreen?.();
    else if (e.key === 'p' || e.key === 'P') print();
  });
  addEventListener('click', e => { if (!e.target.closest('a,button,input,textarea,select')) show(cur + (e.clientX < innerWidth / 3 ? -1 : 1)); });
  addEventListener('resize', fit);
  addEventListener('hashchange', () => show(parseInt(location.hash.slice(1), 10) - 1 || 0));
  fit(); show(cur);
})();
