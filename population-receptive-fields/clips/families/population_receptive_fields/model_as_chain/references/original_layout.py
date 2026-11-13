"""The lecture's encoding pipeline (slides 2, 3 and 24; clips A02 and A20), shared so that the clips and the static
figure (pipeline.tex) keep one layout. Seven boxes in a row, left to right:

    1 stimulus S   2 features Phi(S) (WHAT)   3 spatial pooling (WHERE)   4 transformation f (HOW)
    5 neural dynamics (WHEN)   6 HRF   7 BOLD

Boxes are ink outlines on light grey (ink at 10 per cent); model colours appear only inside a module that stands for a
model (the pooling box shows a small blue Gaussian; later clips tint the transformation box by model). theta tags sit
above boxes 3 to 6; a dashed outline (the opened model) holds boxes 2 to 6; the WHAT, WHERE, HOW and WHEN tiles of
slide 3 go below boxes 2 to 5 (TILE_Y), and are not drawn by A02.

Layout, scene units (frame 16 x 9, origin at the centre; 120 px per unit at 1920 x 1080):
    box centres x = XS = -6.775, -4.6, -2.3, 0, 2.3, 4.6, 6.775 at y = ROW_Y = 0; widths WS = 1.75 (stimulus, BOLD) and
    2.0 (the five modules), height BOX_H = 1.6, gaps 0.3; the row spans x from -7.65 to 7.65
    theta tags at y = TAG_Y = 1.5 over boxes 3-6; outline of the model around boxes 2-6, y from -1.05 to 1.05
    tiles at y = TILE_Y = -1.5 under boxes 2-5
    (all heights relative to the row: A02 ends with the row at y = -1.6, under the shrunken loop of Thursday)
"""
from kit import *

ROW_Y, BOX_H = 0.0, 1.6
XS = [-6.775, -4.6, -2.3, 0.0, 2.3, 4.6, 6.775]
WS = [1.75, 2.0, 2.0, 2.0, 2.0, 2.0, 1.75]
TAG_Y, TILE_Y = 1.5, -1.5
FITTED = (2, 3, 4, 5)                    # boxes with theta: pooling, transformation, neural dynamics, HRF
GREY = tint(INK, 10)
AR = dict(buff=0.06, stroke_width=3.5, color=INK, tip_length=0.18, max_tip_length_to_length_ratio=0.45)
LINK = dict(buff=0.03, stroke_width=3.5, color=INK, tip_length=0.15, max_tip_length_to_length_ratio=0.75)


def rbox(w=2.0, h=BOX_H):
    return RoundedRectangle(width=w, height=h, corner_radius=0.12).set_stroke(INK, 3).set_fill(GREY, 1)


def words(*lines, size=24, serif=()):
    return VGroup(*[label(s, size, INK, serif=(i in serif), slant=ITALIC if i in serif else NORMAL) for i, s in enumerate(lines)]).arrange(DOWN, buff=0.08)


def gear(radius=0.32, teeth=8, colour=INK):
    pts = []
    for i in range(4 * teeth):
        a = 2 * np.pi * (i + 0.5) / (4 * teeth); r = radius if i % 4 in (1, 2) else radius * 0.74
        pts.append([r * np.cos(a), r * np.sin(a), 0])
    return VGroup(Polygon(*pts).set_stroke(colour, 2.5).set_fill(GREY, 1), Circle(radius=radius * 0.3).set_stroke(colour, 2.5).set_fill(WHITE, 1))


def stimulus_icon(c, r=0.42):
    F = VisualField(c, r)
    return Group(F.outline(width=2.2), F.bar(2.0, 2.0, 0), F.fixation(size=0.06, width=1.8))


def gauss_icon(c, size=0.78):
    X, Y = grid(3.0, 121)
    im = ImageMobject(np.flipud(colour_ramp(gauss2d(X, Y, 0, 0, 1.0), GAUSS, alpha=(np.hypot(X, Y) <= 3.0).astype(float))))
    return im.set_resampling_algorithm(RESAMPLING_ALGORITHMS['bilinear']).set_width(size).move_to(c)


def hrf_icon(c, w=1.2, h=0.45):
    import l2model as M
    k = M.hrf(0.25, 24.0); k = k / k.max(); t = np.linspace(0, 1, len(k))
    F = Frame(c[0] - w / 2, c[1] - h * 0.3, w, h, (0, 1), (-0.3, 1))
    return VGroup(Line(F(0, 0), F(1, 0)).set_stroke(HAIR, 2), F.polyline(list(zip(t, k)), INK, 3))


def bold_panel(pred, data, w=1.6, h=0.8, c=ORIGIN):
    """The data (ink) and the prediction (blue) in a small panel; returns VGroup(baseline, data, prediction)."""
    T = len(pred); F = Frame(c[0] - w / 2, c[1] - h / 2, w, h, (0, T), (-0.5, 1.35))
    return VGroup(Line(F(0, 0), F(T, 0)).set_stroke(HAIR, 2), F.polyline(list(enumerate(data)), INK, 2.2), F.polyline(list(enumerate(pred)), GAUSS, 4))


def theta_tag():
    t = label('θ', 32, INK, serif=True, slant=ITALIC)
    r = RoundedRectangle(width=0.6, height=0.56, corner_radius=0.1).set_stroke(INK, 2.5).set_fill(WHITE, 1)
    return VGroup(r, t.move_to(r))


def modules(pred, data, y=ROW_Y):
    """The seven boxes with their contents, in order, on the row at height y; box k is modules(...)[k], a
    Group(rect, content...)."""
    out = []
    for k, x in enumerate(XS):
        c = np.array([x, y, 0]); r = rbox(WS[k]).move_to(c)
        if k == 0: content = Group(stimulus_icon(c + UP * 0.25), VGroup(label('stimulus', 22), label('S', 26, serif=True, slant=ITALIC)).arrange(RIGHT, buff=0.1).move_to(c + DOWN * 0.5))
        elif k == 1: content = Group(words('features', 'Φ(S)', size=22, serif=(1,)).move_to(c))
        elif k == 2: content = Group(gauss_icon(c + UP * 0.28), words('spatial', 'pooling', size=22).move_to(c + DOWN * 0.42))
        elif k == 3: content = Group(words('transformation', 'f', size=20, serif=(1,)).move_to(c))
        elif k == 4: content = Group(words('neural', 'dynamics', size=22).move_to(c))
        elif k == 5: content = Group(hrf_icon(c + UP * 0.22), label('HRF', 26).move_to(c + DOWN * 0.42))
        else: content = Group(bold_panel(pred, data, w=1.45, c=c + UP * 0.2), label('BOLD', 24).move_to(c + DOWN * 0.5))
        out.append(Group(r, *content))
    return out


def links(boxes):
    return [Arrow(boxes[k][0].get_right(), boxes[k + 1][0].get_left(), **LINK) for k in range(6)]


def hull(y=ROW_Y, dashed=True):
    """The outline of the opened model around boxes 2 to 6 (dashed), 2.1 units high."""
    w = XS[5] - XS[1] + WS[1] + 0.3
    r = RoundedRectangle(width=w, height=2.1, corner_radius=0.2).move_to([(XS[1] + XS[5]) / 2, y, 0]).set_stroke(MUTED, 2.5)
    return DashedVMobject(r, num_dashes=80) if dashed else r


def tags(boxes, y=ROW_Y):
    ts = [theta_tag().move_to([XS[k], y + TAG_Y - ROW_Y, 0]) for k in FITTED]
    stems = [Line(t.get_bottom(), boxes[k][0].get_top()).set_stroke(INK, 2.5) for t, k in zip(ts, FITTED)]
    return ts, stems
