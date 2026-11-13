"""Geometry of the clip `model_as_chain`, shared by its custom builders (chain_builders.py).

Positions, sizes and stroke widths are those of the original Manim scene (references/original_scene.py) and of its
row of boxes (references/original_layout.py), in the original's units: a frame 9 units high and 16 wide, origin at
the centre. Everything is drawn in those units and then brought into the render's frame with `to_frame`, which
scales points and stroke widths alike (a manim8 frame is 8 units high), so the picture keeps the original's
proportions at any resolution. Colours are palette roles of the style, never values; text takes the style's faces
at the cap height the original's faces had at the original's font sizes.

Nothing here keeps state or installs updaters: the builders call these functions once, at build time.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
from manim import (
    DOWN,
    ITALIC,
    LEFT,
    NORMAL,
    ORIGIN,
    RIGHT,
    UP,
    Arrow,
    Circle,
    DashedVMobject,
    Line,
    Polygon,
    RoundedRectangle,
    Text,
    VGroup,
    VMobject,
    config,
)

# --- the original's frame and layout (original_scene.py, original_layout.py) -------------------------------------
ORIGINAL_FRAME_HEIGHT = 9.0
ROW = -2.32  # the row's height in the last frame
LOOP_C = np.array([0.0, 1.88, 0.0])  # where the loop's centre goes when it shrinks
LOOP_S = 0.45  # and how small it gets
XS = [-6.775, -4.6, -2.3, 0.0, 2.3, 4.6, 6.775]  # box centres, left to right
WS = [1.75, 2.0, 2.0, 2.0, 2.0, 2.0, 1.75]  # box widths
BOX_H = 1.6
TAG_RISE = 1.5  # theta tags sit this far above the row
FITTED = (2, 3, 4, 5)  # boxes with a theta tag: pooling, transformation, neural dynamics, HRF
MODEL = (1, 2, 3, 4, 5)  # boxes inside the dashed outline: features to HRF
PANEL_Y = (-0.5, 1.35)  # the y range of every BOLD panel

# Arrow settings of the original (AR between the loop's boxes, LINK between the row's boxes).
AR = dict(buff=0.06, stroke_width=3.5, tip_length=0.18, max_tip_length_to_length_ratio=0.45)
LINK = dict(buff=0.03, stroke_width=3.5, tip_length=0.15, max_tip_length_to_length_ratio=0.75)

# Capital height per font_size point of the original's faces (TeX Gyre Heros for words, TeX Gyre Pagella italic
# for symbols), measured with Manim 0.22: the original's text sizes are converted to the style's pixel sizes with
# these, so a label has the cap height it had in the original, whatever face the style names.
ORIGINAL_CAP_PER_POINT = {"sans": 0.010125, "serif": 0.009648}
CAP_HEIGHT_RATIO = 0.72  # scianim_bridge.tokens.CAP_HEIGHT_RATIO: the style's px sizes are em sizes


def frame_scale() -> float:
    """Render units per original unit."""
    return float(config.frame_height) / ORIGINAL_FRAME_HEIGHT


def to_frame(*mobjects: VMobject) -> None:
    """Bring mobjects drawn in the original's units into the render's frame: points and stroke widths alike."""
    VGroup(*mobjects).scale(frame_scale(), scale_stroke=True, about_point=ORIGIN)


def original_px(size: float, serif: bool) -> float:
    """The style's px size (an em size at 1080p) whose cap height equals the original's at Manim font_size `size`."""
    cap_units = size * ORIGINAL_CAP_PER_POINT["serif" if serif else "sans"]
    return cap_units / ORIGINAL_FRAME_HEIGHT * 1080.0 / CAP_HEIGHT_RATIO


@dataclass
class Look:
    """Palette roles and faces of the style, for drawing in the original's units."""

    tokens: Any
    sizes: list[float] = field(default_factory=list)
    """The px size at 1080p of every label drawn so far (after any shrink to fit), for the layout report."""

    def color(self, role: str) -> Any:
        return self.tokens.color(role)

    def text(self, s: str, size: float, *, serif: bool = False, role: str = "foreground", max_width: float | None = None) -> Text:
        """A label: words in the style's body face, symbols (serif) in its title face, italic. Built in the original's
        units, so `to_frame` brings it to the cap height the original had; `max_width` (original units) shrinks a
        label that a wider face would push past its box."""
        typeface = self.tokens.typeface("title" if serif else "body")
        px = original_px(size, serif)
        kwargs = self.tokens.text_kwargs(typeface, self.color(role), px)
        kwargs["font_size"] = kwargs["font_size"] / frame_scale()
        label = Text(s, slant=ITALIC if serif else NORMAL, **kwargs)
        if max_width is not None and label.width > max_width:
            px *= max_width / label.width
            label.scale(max_width / label.width)
        self.sizes.append(px)
        return label

    def stroke_px(self, px_at_1080p: float) -> float:
        """A stroke width in the original's units for a width the style gives in px at 1080p."""
        return self.tokens.stroke_width(px_at_1080p) / frame_scale()

    def line_kwargs(self) -> dict[str, Any]:
        return self.tokens.line_kwargs()

    def dot(self, radius: float, role: str = "foreground") -> Circle:
        """A dot of the original's radius, with the rim of the page the style asks for."""
        kwargs = self.tokens.dot_kwargs(self.color(role))
        if kwargs.get("stroke_width"):
            kwargs["stroke_width"] = kwargs["stroke_width"] / frame_scale()
        return Circle(radius=radius, **kwargs)


# --- the frame of a small panel (lecturekit's kit `Frame`, as the original used it) ---------------------------------
@dataclass
class PanelFrame:
    left: float
    bottom: float
    width: float
    height: float
    u_range: tuple[float, float]
    w_range: tuple[float, float]

    def __call__(self, u: float, w: float) -> np.ndarray:
        u0, u1 = self.u_range
        w0, w1 = self.w_range
        return np.array(
            [self.left + (u - u0) / (u1 - u0) * self.width, self.bottom + (w - w0) / (w1 - w0) * self.height, 0.0]
        )

    def polyline(self, us: list[float], ws: list[float], color: Any, width: float, look: Look) -> VMobject:
        m = VMobject(stroke_color=color, stroke_width=width, **look.line_kwargs())
        m.set_points_as_corners([self(u, w) for u, w in zip(us, ws, strict=True)])
        m.set_fill(opacity=0)
        return m


def bold_panel(
    look: Look, t: list[float], data: list[float], pred: list[float] | None, *, w: float, h: float, c: np.ndarray
) -> VGroup:
    """The data (foreground) and the prediction (primary_signal) over a baseline (hairline): VGroup(baseline, data,
    prediction), the prediction left out when `pred` is None. u runs over [0, number of rows], as in the original."""
    frame = PanelFrame(c[0] - w / 2, c[1] - h / 2, w, h, (0.0, float(len(t))), PANEL_Y)
    parts = [
        Line(frame(0, 0), frame(len(t), 0), stroke_color=look.color("hairline"), stroke_width=2, **look.line_kwargs()),
        frame.polyline(t, data, look.color("foreground"), 2.2, look),
    ]
    if pred is not None:
        parts.append(frame.polyline(t, pred, look.color("primary_signal"), 4, look))
    return VGroup(*parts)


def prediction_curve(look: Look, t: list[float], pred: list[float], *, w: float, h: float, c: np.ndarray) -> VMobject:
    """The prediction alone, on the frame `bold_panel` uses."""
    frame = PanelFrame(c[0] - w / 2, c[1] - h / 2, w, h, (0.0, float(len(t))), PANEL_Y)
    return frame.polyline(t, pred, look.color("primary_signal"), 4, look)


# --- boxes and glyphs (original_layout.py) --------------------------------------------------------------------------
def rbox(look: Look, w: float = 2.0, h: float = BOX_H) -> RoundedRectangle:
    """A box: foreground outline on the faint fill (selection)."""
    r = RoundedRectangle(width=w, height=h, corner_radius=0.12)
    return r.set_stroke(look.color("foreground"), 3).set_fill(look.color("selection"), 1)


def tbox(look: Look, w: float, h: float, *items: VMobject) -> VGroup:
    r = rbox(look, w, h)
    return VGroup(r, VGroup(*items).arrange(RIGHT, buff=0.14).move_to(r))


def words(look: Look, *lines: str, size: float, serif: tuple[int, ...] = (), max_width: float | None = None) -> VGroup:
    return VGroup(
        *[look.text(s, size, serif=i in serif, max_width=max_width) for i, s in enumerate(lines)]
    ).arrange(DOWN, buff=0.08)


def gear(look: Look, radius: float = 0.32, teeth: int = 8) -> VGroup:
    pts = []
    for i in range(4 * teeth):
        a = 2 * np.pi * (i + 0.5) / (4 * teeth)
        r = radius if i % 4 in (1, 2) else radius * 0.74
        pts.append([r * np.cos(a), r * np.sin(a), 0])
    ink = look.color("foreground")
    return VGroup(
        Polygon(*pts).set_stroke(ink, 2.5).set_fill(look.color("selection"), 1),
        Circle(radius=radius * 0.3).set_stroke(ink, 2.5).set_fill(look.color("background"), 1),
    )


def stimulus_icon(look: Look, c: np.ndarray, r: float = 0.42, deg: float = 8.0) -> VGroup:
    """A circular window onto the visual field (radius `deg` degrees) with a bar 2 deg wide at 2 deg right of the
    centre (the kit's VisualField.bar(2.0, 2.0, 0)) and the fixation cross."""
    k = r / deg
    outline = Circle(radius=r).set_stroke(look.color("hairline"), 2.2).set_fill(look.color("background"), 1).move_to(c)
    pos, width = 2.0, 2.0
    a, b = max(pos - width / 2, -deg), min(pos + width / 2, deg)
    ha, hb = math.sqrt(max(deg * deg - a * a, 0)), math.sqrt(max(deg * deg - b * b, 0))
    ta, tb = math.atan2(ha, a), math.atan2(hb, b)
    top = [(deg * math.cos(x), deg * math.sin(x)) for x in np.linspace(ta, tb, 48)]
    bottom = [(deg * math.cos(x), -deg * math.sin(x)) for x in np.linspace(tb, ta, 48)]
    uv = [(a, -ha), *top, *bottom]
    corners = [c + np.array([u * k, v * k, 0.0]) for u, v in uv]
    bar = VMobject(fill_color=look.color("neutral"), fill_opacity=1, stroke_width=0)
    bar.set_points_as_corners([*corners, corners[0]])
    size = 0.06
    fixation = VGroup(
        Line(c + LEFT * size, c + RIGHT * size), Line(c + DOWN * size, c + UP * size)
    ).set_stroke(look.color("muted"), 1.8)
    return VGroup(outline, bar, fixation)


def gauss_icon(look: Look, c: np.ndarray, size: float = 0.78, rings: int = 40) -> VGroup:
    """A Gaussian of SD 1 seen over a disc of radius 3 SD: the page colour at zero, primary_signal at the peak (the
    kit's colour_ramp of gauss2d), drawn as concentric discs, outermost first."""
    radius = size / 2
    base, peak = look.color("background"), look.color("primary_signal")
    discs = []
    for i in range(rings):
        outer = radius * (1 - i / rings)
        middle = radius * (1 - (i + 0.5) / rings)
        d = 3.0 * middle / radius
        value = math.exp(-d * d / 2)
        discs.append(Circle(radius=outer, stroke_width=0).set_fill(base.interpolate(peak, value), 1).move_to(c))
    return VGroup(*discs)


def hrf_curve() -> tuple[list[float], list[float]]:
    """A glyph of the haemodynamic response: the canonical two-gamma shape (peak gamma of shape 6, undershoot of
    shape 16 at a sixth of its height, unit scale), sampled every 0.25 s over 24 s and normalised to a peak of 1.
    Schematic: no axis and no value is shown with it (see README.md)."""
    ts = np.arange(0.0, 24.0, 0.25)
    peak = ts**5 * np.exp(-ts) / math.gamma(6)
    under = ts**15 * np.exp(-ts) / math.gamma(16)
    k = peak - under / 6.0
    k = k / k.max()
    u = np.linspace(0, 1, len(k))
    return [float(x) for x in u], [float(y) for y in k]


def hrf_icon(look: Look, c: np.ndarray, w: float = 1.2, h: float = 0.45) -> VGroup:
    frame = PanelFrame(c[0] - w / 2, c[1] - h * 0.3, w, h, (0.0, 1.0), (-0.3, 1.0))
    u, k = hrf_curve()
    return VGroup(
        Line(frame(0, 0), frame(1, 0), stroke_color=look.color("hairline"), stroke_width=2, **look.line_kwargs()),
        frame.polyline(u, k, look.color("foreground"), 3, look),
    )


def theta_tag(look: Look) -> VGroup:
    t = look.text("θ", 32, serif=True)
    r = RoundedRectangle(width=0.6, height=0.56, corner_radius=0.1)
    r.set_stroke(look.color("foreground"), 2.5).set_fill(look.color("background"), 1)
    return VGroup(r, t.move_to(r))


def stage_box(look: Look, k: int, t: list[float], data: list[float], y: float = ROW) -> tuple[RoundedRectangle, VGroup]:
    """Box k of the row (0 stimulus to 6 BOLD) with its contents. The BOLD box holds the data trace only; its
    prediction is a separate object (chain_builders.bold_prediction), drawn over the data."""
    c = np.array([XS[k], y, 0.0])
    r = rbox(look, WS[k]).move_to(c)
    fit = WS[k] - 0.24  # a label keeps 0.12 units clear of each side of its box, whatever the face
    if k == 0:
        name = VGroup(look.text("stimulus", 22), look.text("S", 26, serif=True)).arrange(RIGHT, buff=0.1)
        content = VGroup(stimulus_icon(look, c + UP * 0.25), name.move_to(c + DOWN * 0.5))
    elif k == 1:
        content = VGroup(words(look, "features", "Φ(S)", size=22, serif=(1,), max_width=fit).move_to(c))
    elif k == 2:
        content = VGroup(
            gauss_icon(look, c + UP * 0.28), words(look, "spatial", "pooling", size=22, max_width=fit).move_to(c + DOWN * 0.42)
        )
    elif k == 3:
        content = VGroup(words(look, "transformation", "f", size=20, serif=(1,), max_width=fit).move_to(c))
    elif k == 4:
        content = VGroup(words(look, "neural", "dynamics", size=22, max_width=fit).move_to(c))
    elif k == 5:
        content = VGroup(hrf_icon(look, c + UP * 0.22), look.text("HRF", 26).move_to(c + DOWN * 0.42))
    else:
        panel = bold_panel(look, t, data, None, w=1.45, h=0.8, c=c + UP * 0.2)
        content = VGroup(panel, look.text("BOLD", 24).move_to(c + DOWN * 0.5))
    return r, content


def bold_box_prediction(look: Look, t: list[float], pred: list[float], y: float = ROW) -> VMobject:
    c = np.array([XS[6], y, 0.0])
    return prediction_curve(look, t, pred, w=1.45, h=0.8, c=c + UP * 0.2)


def box_rect(look: Look, k: int, y: float = ROW) -> RoundedRectangle:
    return rbox(look, WS[k]).move_to(np.array([XS[k], y, 0.0]))


def links(look: Look, y: float = ROW) -> VGroup:
    rects = [box_rect(look, k, y) for k in range(7)]
    return VGroup(
        *[
            Arrow(rects[k].get_right(), rects[k + 1].get_left(), color=look.color("foreground"), **LINK)
            for k in range(6)
        ]
    )


def hull(look: Look, y: float = ROW) -> VGroup:
    """The outline of the opened model around boxes 2 to 6 (dashed, muted), 2.1 units high."""
    w = XS[5] - XS[1] + WS[1] + 0.3
    r = RoundedRectangle(width=w, height=2.1, corner_radius=0.2).move_to([(XS[1] + XS[5]) / 2, y, 0])
    r.set_stroke(look.color("muted"), 2.5)
    return VGroup(DashedVMobject(r, num_dashes=80))


def tags(look: Look, y: float = ROW) -> list[VGroup]:
    return [theta_tag(look).move_to([XS[k], y + TAG_RISE, 0]) for k in FITTED]


def stems(look: Look, y: float = ROW) -> VGroup:
    out = []
    for tag, k in zip(tags(look, y), FITTED, strict=True):
        top = box_rect(look, k, y).get_top()
        out.append(Line(tag.get_bottom(), top, stroke_color=look.color("foreground"), stroke_width=2.5, **look.line_kwargs()))
    return VGroup(*out)


# --- the loop of the first beat --------------------------------------------------------------------------------------
@dataclass
class Loop:
    theta: VGroup
    stim: VGroup
    model: VGroup
    a1: Arrow
    a2: Arrow
    a3: Arrow
    panel: VGroup
    in_frame: bool = False
    """True once `to_frame` has brought the loop into the render's frame."""

    @property
    def members(self) -> list[VMobject]:
        return [self.theta, self.stim, self.model, self.a1, self.a2, self.a3, self.panel]

    @property
    def gear(self) -> VGroup:
        return self.model[1][1]

    @property
    def model_rect(self) -> RoundedRectangle:
        return self.model[0]

    def center(self) -> np.ndarray:
        """The loop's centre as the original's `loop.get_center()` saw it before it shrank (Manim's bounding box)."""
        return VGroup(*self.members).get_center()

    def shrink_map(self, s: float, center: np.ndarray | None = None):
        """The shrink at progress s in [0, 1]: scale about the centre from 1 to LOOP_S while the centre moves to
        LOOP_C (in the units the loop is drawn in), as `loop.animate.scale(LOOP_S).move_to(LOOP_C)` interpolates
        every point."""
        c0 = self.center() if center is None else center
        target = LOOP_C * frame_scale() if self.in_frame else LOOP_C
        k = 1.0 - (1.0 - LOOP_S) * s
        shift = (target - c0) * s

        def apply(points: np.ndarray) -> np.ndarray:
            return c0 + (points - c0) * k + shift

        return apply


def loop(look: Look, t: list[float], data: list[float], pred: list[float]) -> Loop:
    """The loop of the first beat at full size (original_scene.py, beat 1), in the original's units."""
    theta = tbox(look, 3.2, 0.95, look.text("parameters", 30), look.text("θ", 34, serif=True)).move_to([-2.15, 2.95, 0])
    stim = tbox(look, 3.2, 0.95, look.text("stimulus", 30)).move_to([2.15, 2.95, 0])
    model = tbox(look, 5.0, 1.25, look.text("model", 34), gear(look)).move_to([0, 1.0, 0])
    panel = bold_panel(look, t, data, pred, w=4.8, h=1.75, c=np.array([0, -2.35, 0]))
    ink = look.color("foreground")
    a1 = Arrow(theta.get_bottom(), model[0].get_top() + LEFT * 1.0, path_arc=0.4, color=ink, **AR)
    a2 = Arrow(stim.get_bottom(), model[0].get_top() + RIGHT * 1.0, path_arc=-0.4, color=ink, **AR)
    a3 = Arrow(model.get_bottom(), panel.get_top() + UP * 0.12, color=ink, **AR)
    return Loop(theta, stim, model, a1, a2, a3, panel)


def loop_in_frame(look: Look, t: list[float], data: list[float], pred: list[float]) -> Loop:
    """The loop brought into the render's frame, with the path of the third dot (model to panel)."""
    lp = loop(look, t, data, pred)
    to_frame(*lp.members)
    lp.in_frame = True
    return lp


def shrunk_copy(lp: Loop, mob: VMobject) -> VMobject:
    """A copy of one of the loop's parts as it stands once the loop has shrunk (strokes keep their width)."""
    out = mob.copy()
    apply = lp.shrink_map(1.0)
    for member in out.get_family():
        if len(member.points):
            member.points = apply(member.points)
    return out


def bbox(mob: VMobject) -> np.ndarray:
    """[x0, y0, x1, y1] of Manim's bounding box (the one `replace` and `get_corner` use)."""
    dl, ur = mob.get_corner(DOWN + LEFT), mob.get_corner(UP + RIGHT)
    return np.array([dl[0], dl[1], ur[0], ur[1]])


def map_box(points: np.ndarray, src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    """Points stretched from one bounding box onto another (Mobject.replace with stretch=True)."""
    out = points.copy()
    sw, sh = max(src[2] - src[0], 1e-9), max(src[3] - src[1], 1e-9)
    out[:, 0] = dst[0] + (points[:, 0] - src[0]) * (dst[2] - dst[0]) / sw
    out[:, 1] = dst[1] + (points[:, 1] - src[1]) * (dst[3] - dst[1]) / sh
    return out
