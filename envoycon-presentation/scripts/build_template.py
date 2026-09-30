"""EnvoyCon 10 Years — slide template builder (dark + light layouts in one master).

Builds a 16:9 .pptx whose slide master carries named layouts (speaker + host),
theme colors and fonts from the EnvoyCon design tokens, then a sample slide per
layout plus an asset shelf. Upload to Google Drive with conversion to get a
native Google Slides template.
"""
import copy, json, os
from lxml import etree
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.opc.packuri import PackURI
from pptx.parts.slide import SlideLayoutPart
from pptx.oxml.ns import qn
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

A = 'assets/'
THEME, TA, PFX = 'dark', 'assets/dark/', 'Dark · '  # switched per theme by set_theme()
SLOTS = json.load(open('slots.json'))
from hexgeom import rhex_custgeom
NSDECL_A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
HEXGEOM = f'<a:prstGeom {NSDECL_A} prst="ellipse"><a:avLst/></a:prstGeom>'  # headshots: native circle (Slides: Crop → Mask → Oval)
HEX_LN = 8  # px outline
PX = 6350  # 1px of a 1920x1080 canvas in EMU
def px(v): return int(round(v * PX))

# ---- tokens (alpha tokens pre-blended over --bg-0 so Slides renders them exactly)
# keys are roles: bg0 canvas · bg1 panel · pinkL mono/meta ink · pink accent strokes · numfb numeral fallback
DARK = dict(bg0='10041C', bg1='1C0930', magenta='B31AAB', pink='D163CE', pinkL='EBA6E8',
            violet='8A12C4', text='FFFFFF', dim='BCB9BF', faint='88828D', line='461F4E',
            badge='270730', track='592860', trackText='FFFFFF', numfb='D163CE', hex='D163CE')
LIGHT = dict(bg0='FBF8FD', bg1='F3EAF6', magenta='B31AAB', pink='D163CE', pinkL='B31AAB',
             violet='8A12C4', text='10041C', dim='524859', faint='867E8D', line='E9C1E9',
             badge='F5E6F6', track='F3DDF5', trackText='10041C', numfb='B31AAB', hex='D163CE')
C = DARK
def set_theme(t):
    global THEME, TA, PFX, C
    THEME, TA, PFX, C = t, f'assets/{t}/', ('Dark · ' if t == 'dark' else 'Light · '), (DARK if t == 'dark' else LIGHT)
CODE = DARK  # code panels stay dark in both themes
DISPLAY, BODY, MONO = 'Space Grotesk', 'Inter', 'JetBrains Mono'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
NSDECL = 'xmlns:a="%s" xmlns:p="%s" xmlns:r="%s"' % (NS['a'], NS['p'], NS['r'])

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(px(1920)), Emu(px(1080))
master = prs.slide_masters[0]

# ---------------------------------------------------------------- theme
def patch_theme():
    tp = [r.target_part for r in master.part.rels.values() if r.reltype == RT.THEME][0]
    t = etree.fromstring(tp.blob)
    nm = 'EnvoyCon 10 Years'
    t.set('name', nm)
    cs = t.find('.//a:clrScheme', NS); cs.set('name', nm)
    darkc, lightc = (C['bg0'], C['text']) if THEME == 'dark' else (C['text'], C['bg0'])
    vals = dict(dk1=darkc, lt1=lightc, dk2='1C0930', lt2='F3EAF6', accent1=C['magenta'],
                accent2=C['pink'], accent3=C['violet'], accent4=C['pinkL'], accent5=C['line'],
                accent6=C['dim'], hlink=C['pinkL'], folHlink=C['pink'])
    for k, v in vals.items():
        el = cs.find('a:' + k, NS)
        for ch in list(el): el.remove(ch)
        etree.SubElement(el, qn('a:srgbClr')).set('val', v)
    fs = t.find('.//a:fontScheme', NS); fs.set('name', 'EnvoyCon 10 Years')
    fs.find('a:majorFont/a:latin', NS).set('typeface', DISPLAY)
    fs.find('a:minorFont/a:latin', NS).set('typeface', BODY)
    tp._blob = etree.tostring(t, xml_declaration=True, encoding='UTF-8', standalone=True)
patch_theme()

# ---------------------------------------------------------------- xml helpers
def rpr(font, size, color, bold=False, caps=False, spc=None, tag='a:defRPr'):
    s = f'<{tag} sz="{int(size*100)}" b="{1 if bold else 0}"'
    if caps: s += ' cap="all"'
    if spc is not None: s += f' spc="{int(spc)}"'
    s += f'><a:solidFill><a:srgbClr val="{color}"/></a:solidFill><a:latin typeface="{font}"/><a:ea typeface="{font}"/><a:cs typeface="{font}"/></{tag.split(" ")[0]}>'
    return s

def track(size_pt, em):  # letter-spacing em -> DrawingML spc (1/100 pt)
    return em * size_pt * 100

def lvl(n, font, size, color, bold=False, caps=False, spc=None, lnspc=None, algn='l', bullet=False, before=0):
    s = f'<a:lvl{n}pPr algn="{algn}"'
    if bullet: s += f' marL="{px(34 + (n-1)*40)}" indent="{-px(34)}"'
    else: s += ' marL="0" indent="0"'
    s += '>'
    if lnspc: s += f'<a:lnSpc><a:spcPct val="{int(lnspc*100000)}"/></a:lnSpc>'
    s += f'<a:spcBef><a:spcPts val="{int(before*100)}"/></a:spcBef>'
    if bullet:
        s += f'<a:buClr><a:srgbClr val="{C["pink"]}"/></a:buClr><a:buSzPct val="100000"/><a:buFont typeface="{BODY}"/><a:buChar char="{"—" if n>1 else "•"}"/>'
    else: s += '<a:buNone/>'
    s += rpr(font, size, color, bold, caps, spc) + f'</a:lvl{n}pPr>'
    return s

from xml.sax.saxutils import escape as esc
_id = [100]
def nid(): _id[0] += 1; return _id[0]

def ph_xml(kind, idx, name, x, y, w, h, style, prompt, anchor='t', fill=None, line=None,
           geom='rect', ins=(0, 0, 0, 0), autofit='norm', lnw=1.5):
    """kind: title|body|pic|sldNum. style: list of lvl() strings or ''."""
    phattr = f'type="{kind}"' if kind in ('title', 'pic', 'sldNum') else 'type="body"'
    if kind != 'title': phattr += f' idx="{idx}"'
    if kind == 'body' and idx >= 10: phattr += ' hasCustomPrompt="1"'
    if kind == 'title': phattr += ' hasCustomPrompt="1"'
    sp = f'<a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>'
    if geom == 'roundRect': sp = '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 50000"/></a:avLst></a:prstGeom>'
    if geom == 'hexagon': sp = HEXGEOM
    fillx = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
    linex = f'<a:ln w="{px(lnw)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>' if line else '<a:ln><a:noFill/></a:ln>'
    fit = '<a:normAutofit/>' if autofit == 'norm' else '<a:noAutofit/>'
    tag = 'p:pic' if False else 'p:sp'
    paras = ''.join(f'<a:p><a:r><a:rPr lang="en-US" dirty="0"/><a:t>{esc(t)}</a:t></a:r></a:p>' for t in prompt.split('\n')) if prompt else '<a:p><a:endParaRPr lang="en-US"/></a:p>'
    if kind == 'sldNum':
        paras = f'<a:p><a:fld id="{{B6F15528-21DE-4FAA-801E-634DDDAF4B2B}}" type="slidenum"><a:rPr lang="en-US"/><a:t>‹#›</a:t></a:fld></a:p>'
    return f'''<p:sp {NSDECL}><p:nvSpPr><p:cNvPr id="{nid()}" name="{name}"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>
<p:nvPr><p:ph {phattr}/></p:nvPr></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(h)}"/></a:xfrm>{sp}{fillx}{linex}</p:spPr>
<p:txBody><a:bodyPr vert="horz" wrap="square" lIns="{px(ins[0])}" tIns="{px(ins[1])}" rIns="{px(ins[2])}" bIns="{px(ins[3])}" anchor="{anchor}" rtlCol="0">{fit}</a:bodyPr>
<a:lstStyle>{''.join(style)}</a:lstStyle>{paras}</p:txBody></p:sp>'''

def static_text_xml(name, x, y, w, h, runs, algn='l', anchor='t'):
    """runs: list of (text, font, size, color, bold, spc)"""
    RT_ = 'a:rPr lang="en-US"'
    r = ''.join('<a:r>' + rpr(f, s, c, b, False, sp, tag=RT_) + f'<a:t>{esc(t)}</a:t></a:r>' for t, f, s, c, b, sp in runs)
    return f'''<p:sp {NSDECL}><p:nvSpPr><p:cNvPr id="{nid()}" name="{name}"/><p:cNvSpPr txBox="1"/><p:nvPr userDrawn="1"/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="{anchor}"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr algn="{algn}"/>{r}</a:p></p:txBody></p:sp>'''

def rect_xml(name, x, y, w, h, fill=None, line=None, geom='rect'):
    fillx = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else '<a:noFill/>'
    linex = f'<a:ln w="{px(1.5)}"><a:solidFill><a:srgbClr val="{line}"/></a:solidFill></a:ln>' if line else '<a:ln><a:noFill/></a:ln>'
    av = '<a:avLst><a:gd name="adj" fmla="val 3200"/></a:avLst>' if geom == 'roundRect' else '<a:avLst/>'
    return f'''<p:sp {NSDECL}><p:nvSpPr><p:cNvPr id="{nid()}" name="{name}"/><p:cNvSpPr/><p:nvPr userDrawn="1"/></p:nvSpPr>
<p:spPr><a:xfrm><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(h)}"/></a:xfrm><a:prstGeom prst="{geom}">{av}</a:prstGeom>{fillx}{linex}</p:spPr>
<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US"/></a:p></p:txBody></p:sp>'''

def line_xml(name, x1, y1, x2, y2, color):
    return f'''<p:cxnSp {NSDECL}><p:nvCxnSpPr><p:cNvPr id="{nid()}" name="{name}"/><p:cNvCxnSpPr/><p:nvPr userDrawn="1"/></p:nvCxnSpPr>
<p:spPr><a:xfrm><a:off x="{px(x1)}" y="{px(y1)}"/><a:ext cx="{px(x2-x1)}" cy="{px(max(y2-y1,0))}"/></a:xfrm><a:prstGeom prst="line"><a:avLst/></a:prstGeom>
<a:ln w="{px(1.5)}"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:ln></p:spPr></p:cxnSp>'''

def pic_xml(part, path, name, x, y, w=None, h=None):
    from PIL import Image
    iw, ih = Image.open(path).size
    if w is None: w = h * iw / ih
    if h is None: h = w * ih / iw
    _, rId = part.get_or_add_image_part(path)
    return f'''<p:pic {NSDECL}><p:nvPicPr><p:cNvPr id="{nid()}" name="{name}" descr="{name}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr userDrawn="1"/></p:nvPicPr>
<p:blipFill><a:blip r:embed="{rId}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
<p:spPr><a:xfrm><a:off x="{px(x)}" y="{px(y)}"/><a:ext cx="{px(w)}" cy="{px(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'''

def set_bg(part, cSld, path):
    _, rId = part.get_or_add_image_part(path)
    old = cSld.find(qn('p:bg'))
    if old is not None: cSld.remove(old)
    bg = etree.fromstring(f'<p:bg {NSDECL}><p:bgPr><a:blipFill dpi="0" rotWithShape="1"><a:blip r:embed="{rId}"/><a:srcRect/><a:stretch><a:fillRect/></a:stretch></a:blipFill><a:effectLst/></p:bgPr></p:bg>')
    cSld.insert(0, bg)

# ---------------------------------------------------------------- master
def style_master():
    el = master._element
    set_bg(master.part, el.find(qn('p:cSld')), TA + 'bg-content.jpg')
    tx = el.find(qn('p:txStyles'))
    ts = tx.find(qn('p:titleStyle')); [ts.remove(c) for c in list(ts)]
    ts.append(etree.fromstring(f'<a:lvl1pPr {NSDECL} algn="l"><a:lnSpc><a:spcPct val="98000"/></a:lnSpc><a:spcBef><a:spcPct val="0"/></a:spcBef><a:buNone/>' + rpr(DISPLAY, 32, C['text'], True, spc=track(32, -0.015)).replace('<a:defRPr', f'<a:defRPr') + '</a:lvl1pPr>'))
    bs = tx.find(qn('p:bodyStyle')); [bs.remove(c) for c in list(bs)]
    for n, sz, col in [(1, 18, C['text']), (2, 16, C['dim']), (3, 14, C['dim'])]:
        bs.append(etree.fromstring(f'<wrap {NSDECL}>' + lvl(n, BODY, sz, col, lnspc=1.3, bullet=True, before=10) + '</wrap>')[0])
    os_ = tx.find(qn('p:otherStyle')); [os_.remove(c) for c in list(os_)]
    os_.append(etree.fromstring(f'<wrap {NSDECL}>' + lvl(1, BODY, 16, C['text']) + '</wrap>')[0])
    # master placeholders: keep title/body, position them on the content grid
    for sh in list(master.shapes):
        t = sh.placeholder_format.type
        name = str(t)
        if 'TITLE' in name: sh.left, sh.top, sh.width, sh.height = Emu(px(128)), Emu(px(150)), Emu(px(1480)), Emu(px(170))
        elif 'BODY' in name: sh.left, sh.top, sh.width, sh.height = Emu(px(128)), Emu(px(350)), Emu(px(1560)), Emu(px(560))
        else: sh._element.getparent().remove(sh._element)
style_master()
# master colour map is dark (text = lt1 white); Light · layouts override it (text = dk1 ink)
_cm = master._element.find(qn('p:clrMap'))
for k, v in dict(bg1='dk1', tx1='lt1', bg2='dk2', tx2='lt2').items(): _cm.set(k, v)
_tx = etree.tostring(master._element.find(qn('p:txStyles'))).decode()
_new = etree.fromstring(_tx)
# Google Slides seeds new text boxes from bodyStyle. Every layout placeholder sets its own colours, so the
# master body/other text uses a mid violet that reads on both canvases (4.5:1 on dark, 4.2:1 on light).
for _st in (_new.find(qn('p:bodyStyle')), _new.find(qn('p:otherStyle'))):
    for _c in _st.iter(qn('a:srgbClr')): _c.set('val', '8C6CA6')
_old = master._element.find(qn('p:txStyles')); _old.getparent().replace(_old, _new)

# ---------------------------------------------------------------- layouts
blank_src = master.slide_layouts[6]
orig_layouts = list(master.slide_layouts)
LAYOUTS = {}

def new_layout(name, bg):
    n = len(prs.part.package.iter_parts.__self__.__class__.__name__) if False else len(LAYOUTS) + 12
    el = copy.deepcopy(blank_src._element)
    part = SlideLayoutPart(PackURI(f'/ppt/slideLayouts/slideLayout{n}.xml'), blank_src.part.content_type, prs.part.package, el)
    part.relate_to(master.part, RT.SLIDE_MASTER)
    rId = master.part.relate_to(part, RT.SLIDE_LAYOUT)
    lst = master._element.find(qn('p:sldLayoutIdLst'))
    ids = [int(x.get('id')) for x in lst]
    e = etree.SubElement(lst, qn('p:sldLayoutId')); e.set('id', str(max(ids) + 1)); e.set(qn('r:id'), rId)
    if name != 'Section Divider': name = PFX + name
    cSld = el.find(qn('p:cSld')); cSld.set('name', name)
    ov = el.find(qn('p:clrMapOvr'))
    if ov is not None:
        for ch in list(ov): ov.remove(ch)
        ov.append(etree.fromstring(f'<a:masterClrMapping {NSDECL_A}/>'))   # one colour map for all layouts, so Slides keeps them in ONE master
    el.set('preserve', '1'); el.set('userDrawn', '1')
    if 'type' in el.attrib: del el.attrib['type']
    tree = cSld.find(qn('p:spTree'))
    for ch in list(tree):
        if ch.tag not in (qn('p:nvGrpSpPr'), qn('p:grpSpPr')): tree.remove(ch)
    set_bg(part, cSld, TA + bg)
    LAYOUTS[name] = part
    add = lambda xml: tree.append(etree.fromstring(xml))
    return part, add

# shared layout pieces --------------------------------------------------------
KICK = lambda: [lvl(1, MONO, 11, C['pinkL'], True, True, track(11, 0.22))]
def footer(part, add, dark=False):
    add(line_xml('Footer rule', 128, 968, 1792, 968, C['line']))
    add(static_text_xml('Footer meta', 128, 994, 1100, 30, [
        ('ENVOYCON', MONO, 9, C['pinkL'], True, track(9, .14)),
        ('  ·  ', MONO, 9, C['faint'], False, 0),
        ('10 YEARS OF ENVOY', MONO, 9, C['pinkL'], False, track(9, .14))]))
    add(ph_xml('sldNum', 12, 'Slide number', 1592, 990, 200, 34,
               [lvl(1, MONO, 9, C['pinkL'], True, False, track(9, .14), algn='r')], '', anchor='t', autofit='none'))

def header_lockup(part, add, x=128, y=92, h=66):
    add(pic_xml(part, TA + 'lockup.png', 'EnvoyCon 10 Years lockup', x, y, h=h))

def badge(part, add, idx, text, x, y, w, prompt=True):
    """Pill badge: centred mono label (editable placeholder). No decorative dot: in Google Slides a
    slide's placeholder fill paints over layout shapes, so the dot vanished and left the text off-centre."""
    add(ph_xml('body', idx, 'Badge', x, y, w, 50,
               [lvl(1, MONO, 8.5, C['pinkL'], True, True, track(8.5, .14), algn='ctr')], text,
               anchor='ctr', fill=C['badge'], line=C['line'], geom='roundRect', ins=(16, 2, 16, 0), autofit='none'))

def kicker_title(part, add, kicker='SECTION · TOPIC', title='Slide title in Space Grotesk', w=1440, title_h=180):
    add(pic_xml(part, A + 'bar-h.png', 'Accent bar', 128, 118, w=96, h=6.4))
    add(ph_xml('body', 10, 'Kicker', 128, 148, w, 40, KICK(), kicker, autofit='none'))
    add(ph_xml('title', 0, 'Title', 128, 196, w, title_h,
               [lvl(1, DISPLAY, 32, C['text'], True, spc=track(32, -.015), lnspc=0.98)], title, anchor='t'))

BODY_STYLE = [lvl(1, BODY, 18, C['text'], lnspc=1.3, bullet=True, before=12),
              lvl(2, BODY, 16, C['dim'], lnspc=1.3, bullet=True, before=6),
              lvl(3, BODY, 14, C['dim'], lnspc=1.3, bullet=True, before=4)]


def hex_pic_xml(part, path, name, x, y, w, h):
    """Picture masked to a circle (native ellipse geometry) with a native outline.
    Google Slides imports this as a masked image; Replace image keeps mask + outline."""
    xml = pic_xml(part, path, name, x, y, w=w, h=h)
    from PIL import Image
    iw, ih = Image.open(path).size
    c = (1 - (w / h) * ih / iw) / 2 if iw / ih > w / h else 0          # centre-crop to hex box
    cv = (1 - (iw / (w / h)) / ih) / 2 if iw / ih < w / h else 0
    xml = xml.replace('<a:stretch>', f'<a:srcRect l="{int(c*1e5)}" r="{int(c*1e5)}" t="{int(cv*1e5)}" b="{int(cv*1e5)}"/><a:stretch>')
    xml = xml.replace('<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>',
                      HEXGEOM.replace(' ' + NSDECL_A, '') + f'<a:ln w="{px(HEX_LN)}"><a:solidFill><a:srgbClr val="{C["hex"]}"/></a:solidFill></a:ln></p:spPr>')
    return xml

def hex_photo_ph(part, add, key):
    """Layout: soft glow + a visible round frame (masked placeholder image + pink outline).
    Slides put the real headshot, masked the same way, exactly on top."""
    s = SLOTS[key]; x, y, w, h = s['x'], s['y'], s['w'], s['h']; k = w / 600
    add(pic_xml(part, TA + 'hex-glow.png', 'Headshot glow', x - 110 * k, y - 110 * k, w=820 * k, h=820 * k))
    add(ph_xml('pic', 24, 'Headshot (round)', x, y, w, h, [], '', anchor='ctr', fill=C['bg1'], line=C['hex'],
               geom='hexagon', autofit='none', lnw=HEX_LN))   # geom 'hexagon' → HEXGEOM (ellipse)

def build_layouts():
    global p, add, BODY_STYLE
    BODY_STYLE = [lvl(1, BODY, 18, C['text'], lnspc=1.3, bullet=True, before=12),
                  lvl(2, BODY, 16, C['dim'], lnspc=1.3, bullet=True, before=6),
                  lvl(3, BODY, 14, C['dim'], lnspc=1.3, bullet=True, before=4)]
    # 1. Talk Title -------------------------------------------------------------
    p, add = new_layout('Talk Title', 'bg-title.jpg')
    header_lockup(p, add)
    add(ph_xml('body', 13, 'Track chip', 128, 330, 300, 50, [lvl(1, MONO, 8.5, C['trackText'], True, True, track(8.5, .14), algn='ctr')],
               'TRACK', anchor='ctr', fill=C['track'], line=C['pink'], geom='roundRect', ins=(16, 2, 16, 0), autofit='none'))
    add(ph_xml('body', 14, 'Level chip', 444, 330, 240, 50, [lvl(1, MONO, 8.5, C['pinkL'], True, True, track(8.5, .14), algn='ctr')],
               'LEVEL', anchor='ctr', fill=C['bg1'], line=C['line'], geom='roundRect', ins=(16, 2, 16, 0), autofit='none'))
    add(ph_xml('title', 0, 'Talk title', 128, 410, 1180, 330, [lvl(1, DISPLAY, 44, C['text'], True, spc=track(44, -.02), lnspc=0.98)],
               'Your talk title goes here, set tight in Space Grotesk', anchor='t'))
    add(pic_xml(p, A + 'bar-v.png', 'Accent bar', 128, 806, w=8, h=112))
    add(ph_xml('body', 15, 'Speaker name', 164, 804, 1000, 60, [lvl(1, DISPLAY, 22, C['text'], True, spc=track(22, -.01))], 'Speaker Name', autofit='none'))
    add(ph_xml('body', 16, 'Speaker role', 164, 866, 1000, 50, [lvl(1, BODY, 14, C['dim'])], 'Role · Company', autofit='none'))
    add(pic_xml(p, TA + 'ten-lockup.png', 'Anniversary lockup', 1330, 600, w=440))
    add(static_text_xml('Footer meta', 128, 994, 1100, 30, [('ENVOYCON', MONO, 9, C['pinkL'], True, track(9, .14)), ('  ·  ', MONO, 9, C['faint'], False, 0), ('10 YEARS OF ENVOY  ·  2016 — 2026', MONO, 9, C['pinkL'], False, track(9, .14))]))

    # 2. Talk Title · Photo -----------------------------------------------------
    p, add = new_layout('Talk Title · Photo', 'bg-photo.jpg')
    header_lockup(p, add)
    add(ph_xml('body', 13, 'Track chip', 128, 330, 300, 50, [lvl(1, MONO, 8.5, C['trackText'], True, True, track(8.5, .14), algn='ctr')],
               'TRACK', anchor='ctr', fill=C['track'], line=C['pink'], geom='roundRect', ins=(16, 2, 16, 0), autofit='none'))
    add(ph_xml('body', 14, 'Level chip', 444, 330, 240, 50, [lvl(1, MONO, 8.5, C['pinkL'], True, True, track(8.5, .14), algn='ctr')],
               'LEVEL', anchor='ctr', fill=C['bg1'], line=C['line'], geom='roundRect', ins=(16, 2, 16, 0), autofit='none'))
    hex_photo_ph(p, add, 'title-photo')
    add(ph_xml('title', 0, 'Talk title', 128, 410, 1000, 330, [lvl(1, DISPLAY, 40, C['text'], True, spc=track(40, -.02), lnspc=0.98)],
               'Your talk title goes here, set tight in Space Grotesk', anchor='t'))
    add(pic_xml(p, A + 'bar-v.png', 'Accent bar', 128, 806, w=8, h=112))
    add(ph_xml('body', 15, 'Speaker name', 164, 804, 900, 60, [lvl(1, DISPLAY, 22, C['text'], True, spc=track(22, -.01))], 'Speaker Name', autofit='none'))
    add(ph_xml('body', 16, 'Speaker role', 164, 866, 900, 50, [lvl(1, BODY, 14, C['dim'])], 'Role · Company', autofit='none'))
    add(static_text_xml('Footer meta', 128, 994, 1100, 30, [('ENVOYCON', MONO, 9, C['pinkL'], True, track(9, .14)), ('  ·  ', MONO, 9, C['faint'], False, 0), ('10 YEARS OF ENVOY  ·  2016 — 2026', MONO, 9, C['pinkL'], False, track(9, .14))]))

    # 3. About Me ---------------------------------------------------------------
    p, add = new_layout('About Me', 'bg-speaker.jpg')
    hex_photo_ph(p, add, 'about')
    add(ph_xml('body', 10, 'Kicker', 720, 250, 1000, 40, KICK(), 'ABOUT ME', autofit='none'))
    add(ph_xml('title', 0, 'Name', 720, 298, 1000, 110, [lvl(1, DISPLAY, 36, C['text'], True, spc=track(36, -.015))], 'Speaker Name'))
    add(ph_xml('body', 15, 'Role', 720, 410, 1000, 50, [lvl(1, BODY, 16, C['pinkL'], True)], 'Role · Company', autofit='none'))
    add(ph_xml('body', 1, 'Bio', 720, 490, 1000, 300, BODY_STYLE, 'Maintainer of …\nBuilding …\nPreviously …'))
    add(ph_xml('body', 16, 'Handles', 720, 820, 1000, 44, [lvl(1, MONO, 9.5, C['pinkL'], False, True, track(9.5, .14))], 'GITHUB @HANDLE  ·  LINKEDIN /IN/HANDLE', autofit='none'))
    footer(p, add)

    if THEME == 'dark':
        # 4. Section ----------------------------------------------------------------
        # Pink, full-bleed divider: the one place the brand gradient fills the canvas, so chapter breaks pop in both themes
        p, add = new_layout('Section Divider', '../bg-section.jpg')
        add(pic_xml(p, A + 'lockup-white.png', 'EnvoyCon 10 Years lockup (white)', 128, 92, h=66))
        add(ph_xml('body', 10, 'Kicker', 128, 640, 1400, 40, [lvl(1, MONO, 12, 'FFFFFF', True, True, track(12, 0.22))], 'PART TWO', autofit='none'))
        add(ph_xml('title', 0, 'Section title', 128, 692, 1500, 230, [lvl(1, DISPLAY, 60, 'FFFFFF', True, spc=track(60, -.02), lnspc=0.96)], 'Section title'))

    # 5. Title + Content --------------------------------------------------------
    p, add = new_layout('Title + Content', 'bg-content.jpg')
    kicker_title(p, add)
    add(ph_xml('body', 1, 'Content', 128, 400, 1560, 530, BODY_STYLE, 'First point, in Inter\nSecond point\nSupporting detail'))
    footer(p, add)

    # 6. Two Columns ------------------------------------------------------------
    p, add = new_layout('Two Columns', 'bg-content.jpg')
    kicker_title(p, add, title='Compare two ideas side by side')
    for i, (x, lab) in enumerate([(128, 'BEFORE'), (976, 'AFTER')]):
        add(ph_xml('body', 18 + i, f'Column {i+1} label', x, 400, 760, 44, [lvl(1, MONO, 10, C['pinkL'], True, True, track(10, .14))], lab, autofit='none'))
        add(line_xml(f'Column {i+1} rule', x, 452, x + 760, 452, C['line']))
        add(ph_xml('body', 1 + i if i == 0 else 2, f'Column {i+1}', x, 476, 760, 460, BODY_STYLE, 'Point\nPoint\nPoint'))
    footer(p, add)

    # 7. Code -------------------------------------------------------------------
    p, add = new_layout('Code', 'bg-content.jpg')
    kicker_title(p, add, kicker='CONFIG', title='Show the config that does the work', title_h=110)
    add(rect_xml('Code panel', 128, 330, 1664, 600, fill=CODE['bg1'], line=CODE['line'] if THEME == 'dark' else '2A1240', geom='roundRect'))
    for i, c in enumerate([CODE['pink'], CODE['pinkL'], CODE['faint']]):
        add(rect_xml('Window dot', 160 + i * 30, 360, 14, 14, fill=c, geom='ellipse'))
    add(ph_xml('body', 20, 'Code label', 1392, 352, 370, 34, [lvl(1, MONO, 8.5, CODE['faint'], True, True, track(8.5, .14), algn='r')], 'YAML', autofit='none'))
    add(ph_xml('body', 1, 'Code', 168, 410, 1584, 500,
               [lvl(1, MONO, 13, CODE['text'], lnspc=1.35), lvl(2, MONO, 13, CODE['pinkL'], lnspc=1.35)],
               'apiVersion: gateway.networking.k8s.io/v1\nkind: HTTPRoute\nmetadata:\n  name: backend'))
    footer(p, add)

    # 8. Diagram / Image --------------------------------------------------------
    p, add = new_layout('Diagram', 'bg-content.jpg')
    kicker_title(p, add, kicker='ARCHITECTURE', title='One diagram, one idea', title_h=110)
    add(ph_xml('pic', 21, 'Diagram', 128, 330, 1664, 600, [], '', anchor='ctr', fill=C['bg1'], line=C['line'], autofit='none'))
    footer(p, add)

    # 9. Big Number -------------------------------------------------------------
    p, add = new_layout('Big Number', 'bg-statement.jpg')
    add(ph_xml('body', 10, 'Kicker', 128, 150, 1400, 40, KICK(), 'BY THE NUMBERS', autofit='none'))
    add(ph_xml('title', 0, 'What the number means', 128, 650, 1300, 140, [lvl(1, DISPLAY, 32, C['text'], True, spc=track(32, -.015), lnspc=0.98)], 'What the number means'))
    add(ph_xml('body', 1, 'Context', 128, 800, 1300, 120, [lvl(1, BODY, 16, C['dim'], lnspc=1.35)], 'One line of context or the source.'))
    footer(p, add)

    # 10. Statement -------------------------------------------------------------
    p, add = new_layout('Statement', 'bg-statement.jpg')
    add(ph_xml('body', 10, 'Kicker', 128, 230, 1400, 40, KICK(), 'THE TAKEAWAY', autofit='none'))
    add(ph_xml('title', 0, 'Statement', 128, 290, 1500, 420, [lvl(1, DISPLAY, 46, C['text'], True, spc=track(46, -.02), lnspc=1.02)],
               'One sentence the audience should remember after the talk.', anchor='t'))
    add(pic_xml(p, A + 'bar-v.png', 'Accent bar', 128, 760, w=8, h=100))
    add(ph_xml('body', 15, 'Attribution', 164, 760, 1200, 50, [lvl(1, DISPLAY, 18, C['text'], True)], 'Name', autofit='none'))
    add(ph_xml('body', 16, 'Attribution detail', 164, 812, 1200, 46, [lvl(1, BODY, 13, C['dim'])], 'Role · Company', autofit='none'))
    footer(p, add)

    # 11. Thank You / Q&A -------------------------------------------------------
    p, add = new_layout('Thank You', 'bg-title.jpg')
    header_lockup(p, add)
    badge(p, add, 22, 'Q & A', 128, 300, 200)
    add(ph_xml('title', 0, 'Thank you', 128, 380, 1300, 260, [lvl(1, DISPLAY, 72, C['text'], True, spc=track(72, -.03), lnspc=0.95)], 'Thank you'))
    add(pic_xml(p, A + 'bar-v.png', 'Accent bar', 128, 680, w=8, h=112))
    add(ph_xml('body', 15, 'Speaker name', 164, 678, 1000, 60, [lvl(1, DISPLAY, 22, C['text'], True)], 'Speaker Name', autofit='none'))
    add(ph_xml('body', 16, 'Handles', 164, 744, 1100, 50, [lvl(1, MONO, 10, C['pinkL'], False, True, track(10, .14))], 'GITHUB @HANDLE  ·  LINKEDIN /IN/HANDLE', autofit='none'))
    add(pic_xml(p, TA + 'ten-lockup.png', 'Anniversary lockup', 1330, 600, w=440))

    # ---- HOST layouts ---------------------------------------------------------
    # 12. Event Welcome
    p, add = new_layout('Event Welcome', 'bg-statement.jpg')
    header_lockup(p, add)
    badge(p, add, 22, '10 Year Anniversary Edition', 1300, 100, 490)
    add(pic_xml(p, TA + 'ten-lockup.png', 'Anniversary lockup', 128, 300, w=820))
    add(ph_xml('title', 0, 'Welcome line', 1010, 360, 780, 300, [lvl(1, DISPLAY, 44, C['text'], True, spc=track(44, -.02), lnspc=0.98)], 'Welcome to EnvoyCon'))
    add(ph_xml('body', 1, 'Sub', 1010, 680, 780, 160, [lvl(1, BODY, 16, C['dim'], lnspc=1.4)], 'A decade of the proxy that runs the cloud-native world.'))
    add(static_text_xml('Footer meta', 128, 994, 1400, 30, [('ENVOYCON', MONO, 9, C['pinkL'], True, track(9, .14)), ('  ·  ', MONO, 9, C['faint'], False, 0), ('10 YEAR ANNIVERSARY EDITION', MONO, 9, C['pinkL'], False, track(9, .14))]))

    # 13. Agenda
    p, add = new_layout('Agenda', 'bg-content.jpg')
    kicker_title(p, add, kicker='TODAY · ALL TIMES LOCAL', title='Agenda', title_h=110)
    add(ph_xml('body', 1, 'Agenda', 128, 330, 1664, 600,
               [lvl(1, BODY, 16, C['text'], lnspc=1.25, before=10), lvl(2, BODY, 13, C['dim'], lnspc=1.25)],
               '13:00  Welcome & opening\n13:10  Session title — Speaker'))
    footer(p, add)

    # 14. Up Next
    p, add = new_layout('Up Next', 'bg-speaker.jpg')
    header_lockup(p, add)
    hex_photo_ph(p, add, 'upnext')
    badge(p, add, 22, 'Up next', 760, 330, 210)
    add(ph_xml('body', 13, 'Track chip', 990, 330, 300, 50, [lvl(1, MONO, 8.5, C['trackText'], True, True, track(8.5, .14), algn='ctr')],
               'TRACK', anchor='ctr', fill=C['track'], line=C['pink'], geom='roundRect', ins=(16, 2, 16, 0), autofit='none'))
    add(ph_xml('title', 0, 'Session title', 760, 410, 1030, 300, [lvl(1, DISPLAY, 40, C['text'], True, spc=track(40, -.015), lnspc=0.98)], 'Session title goes here'))
    add(pic_xml(p, A + 'bar-v.png', 'Accent bar', 760, 730, w=8, h=112))
    add(ph_xml('body', 15, 'Speaker name', 796, 728, 1000, 60, [lvl(1, DISPLAY, 22, C['text'], True)], 'Speaker Name', autofit='none'))
    add(ph_xml('body', 16, 'Speaker role', 796, 790, 1000, 50, [lvl(1, BODY, 14, C['dim'])], 'Role · Company', autofit='none'))
    add(ph_xml('body', 23, 'Start time', 760, 880, 1000, 44, [lvl(1, MONO, 10, C['pinkL'], True, True, track(10, .14))], 'STARTS 13:40', autofit='none'))

    # 15. Break
    p, add = new_layout('Break', 'bg-break.jpg')
    header_lockup(p, add)
    badge(p, add, 22, 'Short break', 128, 330, 260)
    add(ph_xml('title', 0, 'Back at', 128, 410, 1500, 300, [lvl(1, DISPLAY, 80, C['text'], True, spc=track(80, -.03), lnspc=0.95)], 'Back at 14:30'))
    add(ph_xml('body', 1, 'Sub', 128, 720, 1300, 120, [lvl(1, BODY, 18, C['dim'], lnspc=1.4)], 'Stretch, refill, and bring your questions.'))


for _t in ('dark', 'light'):
    set_theme(_t); build_layouts()
set_theme('dark')
# remove the stock Office layouts
lst = master._element.find(qn('p:sldLayoutIdLst'))
for lay in orig_layouts:
    for e in list(lst):
        if master.part.related_part(e.get(qn('r:id'))) is lay.part:
            master.part.drop_rel(e.get(qn('r:id'))); lst.remove(e)


# ================================================================ sample slides
from pptx.util import Emu as E_
L = {l.name: l for l in prs.slide_layouts}
lay = lambda n: L[n if n == 'Section Divider' else PFX + n]

def fill(slide, values):
    """values: {placeholder idx: text | list[str|(text, level)] | None (delete)}"""
    for ph in list(slide.placeholders):
        i = ph.placeholder_format.idx
        if i not in values: continue
        v = values[i]
        if v is None: ph._element.getparent().remove(ph._element); continue
        tf = ph.text_frame
        items = v if isinstance(v, list) else [v]
        for n, it in enumerate(items):
            t, level = (it, 0) if isinstance(it, str) else it
            para = tf.paragraphs[0] if n == 0 else tf.add_paragraph()
            para.text = t; para.level = level

def add_img(slide, path, x, y, w=None, h=None, name=None):
    pic = slide.shapes.add_picture(path, E_(px(x)), E_(px(y)), E_(px(w)) if w else None, E_(px(h)) if h else None)
    if name: pic.name = name
    return pic

def photo_slot(slide, key, photo=None):
    """Keep the layout's round image placeholder (idx 24) on the slide, empty, like the Diagram slide.
    In Google Slides it shows the insert-image button; Replace image works the same way.
    With a photo: fill it via insert_picture and re-apply the circle + outline."""
    if photo is None: return None
    ph = [p for p in slide.placeholders if p.placeholder_format.idx == 24][0]
    pic = ph.insert_picture(photo)
    spPr = pic._element.spPr
    sl = SLOTS[key]
    for ch in list(spPr): spPr.remove(ch)
    for xml in (f'<a:xfrm {NSDECL}><a:off x="{px(sl["x"])}" y="{px(sl["y"])}"/><a:ext cx="{px(sl["w"])}" cy="{px(sl["h"])}"/></a:xfrm>', HEXGEOM,
                f'<a:ln {NSDECL} w="{px(HEX_LN)}"><a:solidFill><a:srgbClr val="{C["hex"]}"/></a:solidFill></a:ln>'):
        spPr.append(etree.fromstring(xml))
    return pic

def numeral(slide, n, x, y, h):
    return add_img(slide, A + f'num-{n}.png', x, y, h=h, name=f'Gradient numeral {n}')

def tbox(slide, x, y, w, h, paras, anchor=MSO_ANCHOR.TOP, lsp=1.2):
    """paras: list of paragraphs; each paragraph = list of (text, font, pt, color, bold) runs (+ optional spacing)."""
    tb = slide.shapes.add_textbox(E_(px(x)), E_(px(y)), E_(px(w)), E_(px(h)))
    tf = tb.text_frame; tf.word_wrap = True; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, runs in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        before = 0
        if runs and isinstance(runs[0], (int, float)): before, runs = runs[0], runs[1:]
        p.space_before = Pt(before); p.line_spacing = lsp
        for t, font, pt, col, bold in runs:
            r = p.add_run(); r.text = t; f = r.font
            f.name, f.size, f.bold = font, Pt(pt), bold; f.color.rgb = RGBColor.from_string(col)
    return tb

def panel(slide, x, y, w, h, fill_c, line_c, radius=0.06):
    sh = slide.shapes.add_shape(5, E_(px(x)), E_(px(y)), E_(px(w)), E_(px(h)))
    sh.adjustments[0] = radius; sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fill_c)
    sh.line.color.rgb = RGBColor.from_string(line_c); sh.line.width = E_(px(1.5)); sh.shadow.inherit = False
    sh.text_frame.text = ''
    st = sh._element.find(qn('p:style'))
    if st is not None: sh._element.remove(st)          # no theme shadow/effects
    return sh

def notes(slide, text): slide.notes_slide.notes_text_frame.text = text

def build_samples():
    # --- speaker deck samples
    s = prs.slides.add_slide(lay('Talk Title'))
    fill(s, {0: 'Ten years of Envoy: what the proxy taught us about platforms', 13: 'PLATFORM', 14: 'INTERMEDIATE', 15: 'Speaker Name', 16: 'Maintainer · Company'})
    notes(s, 'Layout: Talk Title — use when you have no headshot. The anniversary lockup fills the right side.')

    s = prs.slides.add_slide(lay('Talk Title · Photo'))
    fill(s, {0: 'Routing LLM traffic with Envoy AI Gateway', 13: 'AI INFRASTRUCTURE', 14: 'ADVANCED', 15: 'Speaker Name', 16: 'Maintainer · Company'})
    photo_slot(s, 'title-photo')
    notes(s, 'Headshot: click the round image placeholder to insert a photo (same as the Diagram slide). It stays round with the pink border. To swap later: select it → Replace image.')

    s = prs.slides.add_slide(lay('About Me'))
    fill(s, {10: 'ABOUT ME', 0: 'Speaker Name', 15: 'Role · Company', 1: ['Maintainer of an Envoy ecosystem project', 'Works on gateways, routing, and policy', 'Previously built platforms at scale'], 16: 'GITHUB @HANDLE  ·  LINKEDIN /IN/HANDLE'})
    photo_slot(s, 'about')

    s = prs.slides.add_slide(lay('Section Divider'))
    fill(s, {10: 'PART ONE', 0: 'Where Envoy came from'})
    tbox(s, 112, 250, 900, 340, [[('01', DISPLAY, 180, 'FFFFFF', True)]], anchor=MSO_ANCHOR.BOTTOM, lsp=0.85)
    notes(s, 'Section divider: duplicate this slide for each new section and change the number and title. The big number is a normal text box.')

    s = prs.slides.add_slide(lay('Title + Content'))
    fill(s, {10: 'LESSON 01', 0: 'Start with the traffic shape, not the feature list', 1: ['Long-running, body-dependent requests break request-count limits', ('Price by tokens, not by calls', 1), 'Route on what the request contains', 'Make the policy observable before you enforce it']})

    s = prs.slides.add_slide(lay('Two Columns'))
    fill(s, {10: 'BEFORE / AFTER', 0: 'From sidecar sprawl to one gateway', 18: 'BEFORE', 19: 'AFTER', 1: ['Per-team ingress configs', 'Policy copied into every service', 'No shared view of traffic'], 2: ['Gateway API as the contract', 'Policy attached once, at the edge', 'One place to observe and debug']})

    s = prs.slides.add_slide(lay('Code'))
    fill(s, {10: 'CONFIG', 0: 'Attach a route in five lines', 20: 'HTTPROUTE.YAML', 1: ['apiVersion: gateway.networking.k8s.io/v1', 'kind: HTTPRoute', 'metadata:', '  name: backend', 'spec:', '  parentRefs:', '    - name: eg', '  rules:', '    - backendRefs:', '        - name: backend', '          port: 3000']})

    s = prs.slides.add_slide(lay('Diagram'))
    fill(s, {10: 'ARCHITECTURE', 0: 'One diagram, one idea'})
    notes(s, 'Click the picture placeholder to insert a diagram. Export diagrams on a transparent background.')

    s = prs.slides.add_slide(lay('Big Number'))
    fill(s, {10: 'BY THE NUMBERS', 0: 'years of Envoy in production', 1: '2016 — 2026'})
    numeral(s, '10', 110, 230, 400)
    notes(s, 'For a custom stat, ask the EnvoyCon presentation skill to render a gradient numeral, or add a text box in Space Grotesk Bold, pink.')

    s = prs.slides.add_slide(lay('Statement'))
    fill(s, {10: 'THE TAKEAWAY', 0: 'The best infrastructure disappears — until the day you need to explain it.', 15: 'Speaker Name', 16: 'Maintainer · Company'})

    s = prs.slides.add_slide(lay('Thank You'))
    fill(s, {22: 'Q & A', 0: 'Thank you', 15: 'Speaker Name', 16: 'GITHUB @HANDLE  ·  LINKEDIN /IN/HANDLE'})

    # --- host run-of-show samples
    s = prs.slides.add_slide(lay('Event Welcome'))
    fill(s, {22: '10 Year Anniversary Edition', 0: 'Welcome to EnvoyCon', 1: 'One community, and a decade of the proxy that runs the cloud-native world.'})

    s = prs.slides.add_slide(lay('Agenda'))
    fill(s, {10: 'TODAY · ALL TIMES LOCAL', 0: 'Agenda', 1: None})
    rows = [('13:00', 'Welcome & opening', 'Hosts'), ('13:10', 'Keynote: ten years of Envoy', 'Speaker Name'),
            ('13:40', 'Session title goes here', 'Speaker Name'), ('14:10', 'Session title goes here', 'Speaker Name'),
            ('14:20', 'Break', ''), ('14:30', 'Lightning talks', 'Various'), ('15:50', 'Closing', 'Hosts')]
    tb = s.shapes.add_table(len(rows), 3, E_(px(128)), E_(px(340)), E_(px(1664)), E_(px(len(rows) * 80))).table
    tb.columns[0].width, tb.columns[1].width, tb.columns[2].width = E_(px(240)), E_(px(924)), E_(px(500))
    tblPr = tb._tbl.tblPr
    for k in ('firstRow', 'bandRow'): tblPr.set(k, '0')
    for st in tblPr.findall(qn('a:tableStyleId')): tblPr.remove(st)
    for r, row in enumerate(rows):
        tb.rows[r].height = E_(px(80))
        for c, val in enumerate(row):
            cell = tb.cell(r, c); cell.fill.background()
            cell.margin_left = E_(px(0 if c == 0 else 16)); cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            tcPr = cell._tc.get_or_add_tcPr()
            for side in ('lnL', 'lnR', 'lnT'):
                tcPr.append(etree.fromstring(f'<a:{side} {NSDECL} w="0"><a:noFill/></a:{side}>'))
            tcPr.append(etree.fromstring(f'<a:lnB {NSDECL} w="{px(1.5)}"><a:solidFill><a:srgbClr val="{C["line"]}"/></a:solidFill></a:lnB>'))
            # tcPr children order: borders before fill
            nf = tcPr.find(qn('a:noFill'))
            if nf is not None: tcPr.remove(nf); tcPr.append(nf)
            p_ = cell.text_frame.paragraphs[0]; run = p_.add_run(); run.text = val
            f = run.font
            if c == 0: f.name, f.size, f.bold, f.color.rgb = MONO, Pt(12), True, RGBColor.from_string(C['pinkL'])
            elif c == 1: f.name, f.size, f.bold, f.color.rgb = DISPLAY, Pt(17), True, RGBColor.from_string(C['text'] if val != 'Break' else C['faint'])
            else: f.name, f.size, f.color.rgb = BODY, Pt(13), RGBColor.from_string(C['dim'])

    s = prs.slides.add_slide(lay('Up Next'))
    fill(s, {22: 'Up next', 13: 'AI INFRASTRUCTURE', 0: 'Routing LLM traffic with Envoy AI Gateway', 15: 'Speaker Name', 16: 'Maintainer · Company', 23: 'STARTS 13:40'})
    photo_slot(s, 'upnext')

    s = prs.slides.add_slide(lay('Break'))
    fill(s, {22: 'Short break', 0: 'Back at 14:30', 1: 'Stretch, refill, and bring your questions.'})

    s = prs.slides.add_slide(lay('Thank You'))
    fill(s, {22: 'Wrap-up', 0: 'Thanks for joining', 15: 'EnvoyCon Hosts', 16: 'RECORDINGS & SLIDES TO FOLLOW'})

    # --- asset shelf
    s = prs.slides.add_slide(lay('Title + Content'))
    fill(s, {10: 'ASSET SHELF · COPY & PASTE', 0: 'Gradient numerals, chips and a round headshot', 1: None})
    for i, n in enumerate(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']):
        numeral(s, n, 128 + (i % 5) * 196, 360 + (i // 5) * 170, 130)
    bx = 1150
    for j, (lab, fillc, linec, col) in enumerate([('TRACK', C['track'], C['pink'], C['trackText']), ('LEVEL', C['bg1'], C['line'], C['pinkL'])]):
        sh = s.shapes.add_shape(5, E_(px(bx + j * 250)), E_(px(380)), E_(px(230)), E_(px(50)))
        sh.adjustments[0] = 0.5; sh.fill.solid(); sh.fill.fore_color.rgb = RGBColor.from_string(fillc)
        sh.line.color.rgb = RGBColor.from_string(linec); sh.line.width = E_(px(1.5)); sh.shadow.inherit = False
        tf = sh.text_frame; tf.paragraphs[0].alignment = PP_ALIGN.CENTER
        r_ = tf.paragraphs[0].add_run(); r_.text = lab; r_.font.name = MONO; r_.font.size = Pt(8.5); r_.font.bold = True; r_.font.color.rgb = RGBColor.from_string(col)
    hx = s.shapes.add_picture(TA + 'photo-placeholder.png', E_(px(1260)), E_(px(470)), E_(px(420)), E_(px(420)))
    hx.name = 'Round headshot (copy me)'
    _sp = hx._element.spPr
    _sp.remove(_sp.find(qn('a:prstGeom')))
    _sp.append(etree.fromstring(HEXGEOM))
    _sp.append(etree.fromstring(f'<a:ln {NSDECL} w="{px(HEX_LN)}"><a:solidFill><a:srgbClr val="{C["hex"]}"/></a:solidFill></a:ln>'))
    add_img(s, TA + 'lockup.png', 128, 740, h=56, name='Header lockup')
    add_img(s, A + 'bar-h.png', 128, 850, w=96, h=6.4, name='Accent bar (horizontal)')
    add_img(s, A + 'bar-v.png', 260, 820, w=8, h=112, name='Accent bar (vertical)')
    notes(s, 'Copy what you need onto your slides. The gradient is only for big numerals, photo rims and accent bars.')


for _t in ('dark', 'light'):
    set_theme(_t); build_samples()
set_theme('dark')

# --- guide slides (moved to the front of the deck) -------------------------
def to_front(slide, pos=0):
    lst = prs.slides._sldIdLst; el = [e for e in lst if prs.part.related_part(e.rId) is slide.part][0]
    lst.remove(el); lst.insert(pos, el)

# 1) How to use this template
g = prs.slides.add_slide(lay('Title + Content'))
fill(g, {10: 'START HERE · DELETE BEFORE YOU PRESENT', 0: 'How to use this template', 1: None})
STEPS = [
    ('01', 'Make a copy',
     'File → Make a copy. Work in your copy, never the original. Pick Dark or Light for the whole deck.'),
    ('02', 'Add slides',
     'Click ▾ next to + and pick a layout. Every layout comes as “Dark ·” and “Light ·”.'),
    ('03', 'Add a photo',
     'Click the image button in the round frame and upload a square photo. Swap it later with Replace image.'),
    ('04', 'Finish up',
     'New section? Duplicate the pink divider and change its number. Then delete the guide and sample slides.'),
]
cw, gap, cy, ch = 392, 32, 340, 470
for i, (n, head, body) in enumerate(STEPS):
    cx = 128 + i * (cw + gap)
    panel(g, cx, cy, cw, ch, C['bg1'], C['line'])
    numeral(g, n, cx + 28, cy + 30, 96)
    tbox(g, cx + 36, cy + 170, cw - 72, 50, [[(head, DISPLAY, 18, C['text'], True)]])
    tbox(g, cx + 36, cy + 236, cw - 72, 210, [[(body, BODY, 12.5, C['dim'], False)]])
# rules strip
panel(g, 128, 836, 1664, 96, C['badge'], C['line'], radius=0.5)
rules = [('HEADLINES', True), (' SPACE GROTESK', False), ('   ·   ', None), ('BODY', True), (' INTER', False), ('   ·   ', None),
         ('LABELS', True), (' JETBRAINS MONO, ALL CAPS', False), ('   ·   ', None), ('NO EMOJI', True), ('   ·   ', None),
         ('NO URLS ON SLIDES', True)]
tbox(g, 168, 836, 1584, 96, [[(t, MONO, 9, C['faint'] if b is None else C['pinkL'], bool(b)) for t, b in rules]], anchor=MSO_ANCHOR.MIDDLE)
notes(g, 'This guide slide and the Layout guide are for you, not your audience. Delete them (and the sample slides you do not use) before presenting.')

# 2) Layout guide
g2 = prs.slides.add_slide(lay('Title + Content'))
fill(g2, {10: 'START HERE · LAYOUT GUIDE', 0: 'Which layout when', 1: None})
SPK = [('Talk Title', 'opening slide, no photo'), ('Talk Title · Photo', 'opening slide with your headshot'),
       ('About Me', 'who you are, with headshot'), ('Section Divider', 'pink chapter break, big number'),
       ('Title + Content', 'the everyday slide: title + 3–5 bullets'), ('Two Columns', 'compare, before / after'),
       ('Code', 'YAML, config, CLI on a dark panel'), ('Diagram', 'one picture, one idea'),
       ('Big Number', 'one stat, gradient numeral'), ('Statement', 'the takeaway or a quote'),
       ('Thank You', 'close and Q&A')]
HST = [('Event Welcome', 'event opener'), ('Agenda', 'the day at a glance (table)'),
       ('Up Next', 'between sessions, with speaker photo'), ('Break', '“Back at 14:30”'),
       ('Thank You', 'event closer, badge “Wrap-up”')]
for x, lab, rows in [(128, 'SPEAKER LAYOUTS', SPK), (1040, 'HOST RUN-OF-SHOW', HST)]:
    tbox(g2, x, 336, 700, 34, [[(lab, MONO, 10, C['pinkL'], True)]])
    ln = g2.shapes.add_connector(1, E_(px(x)), E_(px(378)), E_(px(x + (820 if x == 128 else 752))), E_(px(378)))
    ln.line.color.rgb = RGBColor.from_string(C['line']); ln.line.width = E_(px(1.5))
    st = ln._element.find(qn('p:style'))
    if st is not None: ln._element.remove(st)
    tbox(g2, x, 392, 820, 560, [[6, (name, DISPLAY, 13, C['text'], True), ('   ' + use, BODY, 11.5, C['dim'], False)] for name, use in rows])
tbox(g2, 1040, 700, 752, 200, [[('Change a slide’s layout any time: ', BODY, 11.5, C['dim'], False), ('Slide → Apply layout', DISPLAY, 11.5, C['text'], True), ('.', BODY, 11.5, C['dim'], False)],
                               [10, ('Every layout comes twice: ', BODY, 11.5, C['dim'], False), ('Dark ·', DISPLAY, 11.5, C['text'], True), (' and ', BODY, 11.5, C['dim'], False), ('Light ·', DISPLAY, 11.5, C['text'], True), ('. Keep one theme per deck; the pink divider works in both.', BODY, 11.5, C['dim'], False)],
                               [10, ('Theme colors and fonts are built in: ', BODY, 11.5, C['dim'], False), ('Slide → Edit theme', DISPLAY, 11.5, C['text'], True), (' shows every layout.', BODY, 11.5, C['dim'], False)]])
to_front(g2, 0); to_front(g, 0)

prs.save('EnvoyCon-10-Slides-Template.pptx')
print('slides:', len(prs.slides), 'layouts:', [l.name for l in prs.slide_layouts])
