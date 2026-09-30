"""Rounded brand hexagon (pointy-top, w:h = 1:1.12) as DrawingML custom geometry."""
PATH = [('M', .425, .0375), ('Q', .5, 0, .575, .0375), ('L', .925, .2125), ('Q', 1, .25, 1, .325), ('L', 1, .675),
        ('Q', 1, .75, .925, .7875), ('L', .575, .9625), ('Q', .5, 1, .425, .9625), ('L', .075, .7875),
        ('Q', 0, .75, 0, .675), ('L', 0, .325), ('Q', 0, .25, .075, .2125)]
def rhex_custgeom(ns=''):
    W = H = 100000
    pt = lambda x, y: f'<a:pt x="{int(x*W)}" y="{int(y*H)}"/>'
    body = ''
    for seg in PATH:
        if seg[0] == 'M': body += f'<a:moveTo>{pt(*seg[1:])}</a:moveTo>'
        elif seg[0] == 'L': body += f'<a:lnTo>{pt(*seg[1:])}</a:lnTo>'
        else: body += f'<a:quadBezTo>{pt(*seg[1:3])}{pt(*seg[3:5])}</a:quadBezTo>'
    return (f'<a:custGeom {ns}><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
            f'<a:pathLst><a:path w="{W}" h="{H}">{body}<a:close/></a:path></a:pathLst></a:custGeom>')
