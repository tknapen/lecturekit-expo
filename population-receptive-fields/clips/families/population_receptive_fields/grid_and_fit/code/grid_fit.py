"""Custom builders of the clip `grid_and_fit` (storyboard objects of `kind: custom`).

Reviewed code, not generated: `scianim codegen` writes `code/scene_grid_and_fit.py`, and that module calls the
five builders below by name, `grid_fit:<function>`.

What they draw, and why not a registered kind (manim8 bad3ae1, registry 0.5.0):

- `visual_field`: the visual field out to 4 deg as a circle, the fixation cross and a 2 deg scale bar with its
  label. No registered kind draws a circular field in degrees (`receptive_field_glyph` is a square box with three
  tinted contours and tick labels, and it cannot move).
- `field_heading`: a heading centred above the field (the stage that is running). A `text_caption` can only sit
  at an anchor of the safe area or left-aligned below or beside an earlier object (`place` in
  scianim_bridge.components.base), so it cannot be centred over the field, where the original scene has it; the
  change from one heading to the next is the registered `fade_object` and `reveal_at_seconds`.
- `time_course`: the measured voxel's time course in a fixed axes box, with its axes, the time ticks, the two axis
  labels and the label "measured voxel". The registered `scientific_plot` draws the same trace, but it is placed
  by the bounding box of its group, which holds its tick and axis labels, so its axes box moves with the font:
  1.21 px vertically and 0.28 px horizontally between lecturekit_paper (TeX Gyre Heros) and lecturekit_dark
  (Roboto), against the rule that geometry is identical under both styles. Its `data_label` is also always set
  under the x axis in `secondary_text`, where the reference has "measured voxel" at the top left in the trace's
  ink, and it writes value ticks the reference does not have.
- `panel_text`: a line of text centred under the time course at the original's place (the fit line). A
  `text_caption` placed `below` the panel would follow the panel's labels, and so the font, and be left-aligned
  where the original centres it.
- `candidate_path`: everything that moves. The candidate field (a dot at its centre and its one-sigma circle),
  the best grid candidate so far as a dashed outline, the candidate's x, y and sigma under the field, its
  predicted time course over the measured voxel, and the R squared readout at the top right of the panel. It is a
  `ParametricComponent`, so the registered `vary_parameter` action drives it, one hop per candidate.

The parameters of `candidate_path`:

- `candidate`: a position along the candidates in `seq` order. At an integer n the object shows row n of the
  candidates table exactly (x_deg, y_deg, sigma_deg, r2) and the column of the predictions table that belongs to
  it (`p` followed by n in two digits). Between two integers, while a hop runs, the centre, sigma, readouts and
  prediction are interpolated linearly between the two rows, as the original scene's trackers and Transform did.
- `retire_kept`: 0 shows the dashed outline of the best candidate so far, 1 has removed it; between, its ink
  falls linearly (the storyboard's action supplies the easing).

They are declared through the object's data binding, the only place a `kind: custom` object can declare a
parameter in manim8 bad3ae1: each is the `window` of a `smooth` transform whose default is 0, which leaves the
table as it is. The builder checks that this is so and never applies a swept value as a smoothing window; the
parameters are its own.

Geometry follows the original scene of the Coimbra pRF workshop (references/original_scene.py), in its scene
units (a frame 16 wide and 9 high), fitted as one piece into the style's safe area. Every mark and every text
anchor is a point of that mapping, never the extent of a text, so the geometry is the same under every style and
only the glyphs change with the font. Colours are palette roles named in the storyboard, text takes the style's
text roles; nothing here names a colour, a font or a text size. Line weights and mark sizes come from the
storyboard's arguments, in pixels at 1080p. Every rebuild is a pure function of the parameters: no updaters, so
checkpoints are exact.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from manim import DOWN, LEFT, PI, RIGHT, UP, Axes, Circle, DashedVMobject, Dot, Line, Text, VGroup, VMobject

from scianim_bridge.components.base import Component, ParametricComponent
from scianim_core.storyboard import DataBinding, ParameterRef

# The original scene's layout (references/original_scene.py), in its scene units: a frame 16 wide and 9 high
# with the origin at the centre.
ORIGINAL: dict[str, Any] = {
    "field_centre": (-5.2, 0.2),  # VisualField((-5.2, 0.2), 2.3, deg=4.0)
    "field_radius": 2.3,
    "fixation_half_length": 0.13,  # VisualField.fixation(size=0.13)
    "scale_bar_drop": 0.35,  # scale_bar: p = c + DOWN * (r + 0.35)
    "scale_bar_label_gap": 0.1,  # label(...).next_to(line, DOWN, buff=0.1)
    "params_centre": (-5.2, -3.35),  # params ... .move_to([-5.2, -3.35, 0])
    "heading_centre": (-5.2, 3.3),  # head = label('grid search', ...).move_to([-5.2, 3.3, 0])
    "plot_box": (-1.6, -2.0, 8.8, 4.4),  # D = Frame(-1.6, -2.0, 8.8, 4.4, ...): left, bottom, width, height
    "plot_label_rise": 0.35,  # 'measured voxel' and R squared at D.top + 0.35
    "plot_label_inset": 0.3,  # 'measured voxel' centred at D.left + 1.5: its left edge about 0.3 in
    "tick_label_gap": 0.12,  # Frame.axes: label(f'{u:g}').next_to(self(u, w0), DOWN, buff=0.12)
    "time_label_drop": 0.68,  # Frame.axes: u_label at (left + width / 2, bottom - 0.68)
    "value_label_left": 0.8,  # Frame.axes: w_label rotated at (left - 0.8, bottom + height / 2)
    "fit_line_drop": 1.25,  # fin ... .move_to([D.left + D.width / 2, D.bottom - 1.25, 0])
}
COMPOSITION = (-7.55, -3.6, 7.25, 3.6)
"""What the original scene draws, text included, as (x0, y0, x1, y1) in its scene units; fitted into the safe area."""


# --- geometry ----------------------------------------------------------------------------------
@dataclass(frozen=True)
class Page:
    """The original scene's units mapped into the style's safe area: a uniform scale `k` and an offset."""

    k: float
    ox: float
    oy: float

    def pt(self, x: float, y: float) -> np.ndarray:
        return np.array([self.ox + self.k * x, self.oy + self.k * y, 0.0])

    def length(self, d: float) -> float:
        return self.k * d


def page(tokens: Any) -> Page:
    x0, y0, x1, y1 = tokens.safe_rect()
    a0, b0, a1, b1 = COMPOSITION
    k = min((x1 - x0) / (a1 - a0), (y1 - y0) / (b1 - b0))
    return Page(k, (x0 + x1) / 2 - k * (a0 + a1) / 2, (y0 + y1) / 2 - k * (b0 + b1) / 2)


@dataclass(frozen=True)
class Field:
    """The visual field: `centre` and `radius` in frame units showing `radius_deg` degrees from fixation."""

    centre: np.ndarray
    radius: float
    radius_deg: float

    @property
    def per_deg(self) -> float:
        return self.radius / self.radius_deg

    def pt(self, x_deg: float, y_deg: float) -> np.ndarray:
        return self.centre + np.array([x_deg * self.per_deg, y_deg * self.per_deg, 0.0])


def _weight(tokens: Any, arguments: dict[str, Any], name: str) -> float:
    return tokens.stroke_width(float(arguments["weights_px_at_1080p"][name]))


def _role(arguments: dict[str, Any], name: str) -> str:
    return str(arguments["roles"][name])


def _nothing() -> VMobject:
    """A member that draws nothing (no points), for a mark that is not shown."""
    return VMobject(stroke_width=0, fill_opacity=0)


# --- the visual field -------------------------------------------------------------------------------
def visual_field(
    scene: Any,
    object_id: str,
    tokens: Any,
    arguments: dict[str, Any],
    *,
    style_role: str | None = None,
    data: dict[str, Any] | None = None,
    equation: dict[str, Any] | None = None,
) -> Component:
    """The field's outline, the fixation cross and a scale bar of `scale_bar_deg` degrees with its label.

    arguments: `radius_deg` (the field's radius in degrees), `scale_bar_deg`, `roles` (`outline`, `fixation`,
    `scale_bar`: palette roles), `weights_px_at_1080p` (`outline`, `fixation`, `scale_bar`).
    The component's `to_world` maps a point in degrees (x, y) to the frame, for `candidate_path`.
    """
    pg = page(tokens)
    radius_deg = float(arguments["radius_deg"])
    field = Field(pg.pt(*ORIGINAL["field_centre"]), pg.length(ORIGINAL["field_radius"]), radius_deg)
    ends = tokens.line_kwargs()
    outline = Circle(radius=field.radius, color=tokens.color(_role(arguments, "outline")))
    outline.set_stroke(tokens.color(_role(arguments, "outline")), _weight(tokens, arguments, "outline"))
    outline.set_fill(opacity=0).move_to(field.centre)
    half = pg.length(ORIGINAL["fixation_half_length"])
    fixation_colour = tokens.color(_role(arguments, "fixation"))
    fixation = VGroup(
        Line(field.centre + LEFT * half, field.centre + RIGHT * half, **ends),
        Line(field.centre + DOWN * half, field.centre + UP * half, **ends),
    ).set_stroke(fixation_colour, _weight(tokens, arguments, "fixation"))
    bar_deg = float(arguments["scale_bar_deg"])
    bar_colour = tokens.color(_role(arguments, "scale_bar"))
    foot = field.centre + DOWN * (field.radius + pg.length(ORIGINAL["scale_bar_drop"]))
    bar = Line(
        foot + LEFT * bar_deg * field.per_deg / 2,
        foot + RIGHT * bar_deg * field.per_deg / 2,
        color=bar_colour,
        stroke_width=_weight(tokens, arguments, "scale_bar"),
        **ends,
    )
    tick_face = tokens.typeface("tick_label")
    # the bar in its role (muted); its label in secondary_text, like the axes' numbers, for 4.5:1 on both pages
    bar_label = Text(f"{bar_deg:g}°", **tokens.text_kwargs(tick_face, tokens.color("secondary_text")))
    bar_label.next_to(bar, DOWN, buff=pg.length(ORIGINAL["scale_bar_label_gap"]))
    group = VGroup(outline, fixation, bar, bar_label)
    component = Component(
        object_id,
        "custom",
        group,
        text=bar_label.text,
        font_px=tokens.smallest_text_px("tick_label"),
        text_like=False,
    )
    component.to_world = lambda point: field.pt(float(point[0]), float(point[1]))
    return component


def _field_of(scene: Any, object_id: str, reference: str) -> Field:
    """The `Field` of a `visual_field` object declared earlier, read back from its `to_world`."""
    try:
        other = scene.objects[reference]
    except KeyError:
        raise ValueError(f"object '{object_id}': field '{reference}' is not an object declared before it") from None
    if other.to_world is None:
        raise ValueError(f"object '{object_id}': '{reference}' is not a visual_field (it maps no degrees)")
    centre = np.asarray(other.to_world((0.0, 0.0)), dtype=float)
    per_deg = float(np.asarray(other.to_world((1.0, 0.0)), dtype=float)[0] - centre[0])
    return Field(centre, per_deg, 1.0)


def _axes_of(scene: Any, object_id: str, reference: str) -> Axes:
    """The invisible `Axes` of a `time_course` object declared earlier: its group's first member."""
    try:
        other = scene.objects[reference]
    except KeyError:
        raise ValueError(f"object '{object_id}': panel '{reference}' is not an object declared before it") from None
    axes = other.group.submobjects[0] if other.group.submobjects else None
    if not isinstance(axes, Axes):
        raise ValueError(f"object '{object_id}': '{reference}' is not a time_course with axes to draw in")
    return axes


def _box(axes: Axes) -> tuple[float, float, float, float]:
    """The panel's axes box as (left, bottom, right, top) in frame units."""
    (x0, x1), (y0, y1) = axes.x_range[:2], axes.y_range[:2]
    left, bottom = (float(v) for v in axes.c2p(x0, y0)[:2])
    right, top = (float(v) for v in axes.c2p(x1, y1)[:2])
    return left, bottom, right, top


# --- the measured time course ---------------------------------------------------------------------------
def time_course(
    scene: Any,
    object_id: str,
    tokens: Any,
    arguments: dict[str, Any],
    *,
    style_role: str | None = None,
    data: dict[str, Any] | None = None,
    equation: dict[str, Any] | None = None,
) -> Component:
    """The bound series (encoding x: time, y: value) as a line in the object's `style_role`, in the original's axes
    box, with thin L-shaped axes, the time ticks and the two axis labels, and `label` above the box's top left.

    arguments: `time_range`, `value_range` (the box's data limits), `time_ticks`, `time_label`, `value_label`,
    `label`, `roles` (`axes`, `ticks`, `axis_labels`: palette roles), `weights_px_at_1080p` (`axes`, `trace`).
    The binding may not transform the table. The group's first member is an invisible `Axes` that maps data to the
    frame, for `candidate_path`; the panel never changes (constraint measured_fixed).
    """
    if data is None:
        raise ValueError(f"object '{object_id}' needs a data binding (the measured time course)")
    if scene.ctx is None:
        raise RuntimeError("no job context")
    binding = DataBinding.model_validate(data)
    if binding.transforms or binding.encoding.group:
        raise ValueError(f"object '{object_id}': the measured time course is drawn as it is; no transforms or groups")
    table = scene.ctx.table(binding.source)
    t = table.numeric(binding.encoding.x)
    v = table.numeric(binding.encoding.y)
    t0, t1 = (float(a) for a in arguments["time_range"])
    v0, v1 = (float(a) for a in arguments["value_range"])
    if min(t) < t0 or max(t) > t1 or min(v) < v0 or max(v) > v1:
        raise ValueError(f"object '{object_id}': the data leave the box [{t0:g}, {t1:g}] x [{v0:g}, {v1:g}]")
    pg = page(tokens)
    bx, by, bw, bh = ORIGINAL["plot_box"]
    left, bottom = (float(c) for c in pg.pt(bx, by)[:2])
    width, height = pg.length(bw), pg.length(bh)
    axes = Axes(
        x_range=[t0, t1, t1 - t0],
        y_range=[v0, v1, v1 - v0],
        x_length=width,
        y_length=height,
        tips=False,
        axis_config={"stroke_width": 0, "stroke_opacity": 0, "include_ticks": False, "include_numbers": False},
    )
    axes.shift(np.array([left, bottom, 0.0]) - axes.c2p(t0, v0))
    ends = tokens.line_kwargs()
    axis_colour = tokens.color(_role(arguments, "axes"))
    w_axes = _weight(tokens, arguments, "axes")
    frame = VGroup(
        Line(axes.c2p(t0, v0), axes.c2p(t1, v0), color=axis_colour, stroke_width=w_axes, **ends),
        Line(axes.c2p(t0, v0), axes.c2p(t0, v1), color=axis_colour, stroke_width=w_axes, **ends),
    )
    tick_face = tokens.typeface("tick_label")
    tick_colour = tokens.color(_role(arguments, "ticks"))
    ticks = VGroup()
    for u in arguments["time_ticks"]:
        label = Text(f"{float(u):g}", **tokens.text_kwargs(tick_face, tick_colour))
        label.next_to(axes.c2p(float(u), v0), DOWN, buff=pg.length(ORIGINAL["tick_label_gap"]))
        ticks.add(label)
    axis_face = tokens.typeface("axis_label")
    axis_label_colour = tokens.color(_role(arguments, "axis_labels"))
    time_label = Text(str(arguments["time_label"]), **tokens.text_kwargs(axis_face, axis_label_colour))
    time_label.move_to(np.array([left + width / 2, bottom - pg.length(ORIGINAL["time_label_drop"]), 0.0]))
    value_label = Text(str(arguments["value_label"]), **tokens.text_kwargs(axis_face, axis_label_colour))
    value_label.rotate(PI / 2).move_to(
        np.array([left - pg.length(ORIGINAL["value_label_left"]), bottom + height / 2, 0.0])
    )
    ink = tokens.color(style_role or "foreground")
    trace = VMobject(**ends)
    trace.set_points_as_corners([axes.c2p(a, b) for a, b in zip(t, v, strict=True)])
    trace.set_stroke(ink, _weight(tokens, arguments, "trace")).set_fill(opacity=0)
    name = Text(str(arguments["label"]), **tokens.text_kwargs(tokens.typeface("annotation"), ink))
    name.move_to(
        np.array(
            [
                left + pg.length(ORIGINAL["plot_label_inset"]),
                bottom + height + pg.length(ORIGINAL["plot_label_rise"]),
                0.0,
            ]
        ),
        aligned_edge=LEFT,
    )
    name.set_y(bottom + height + pg.length(ORIGINAL["plot_label_rise"]))
    group = VGroup(axes, frame, ticks, time_label, value_label, trace, name)
    return Component(
        object_id,
        "custom",
        group,
        text=None,
        font_px=tokens.smallest_text_px("tick_label", "axis_label", "annotation"),
        text_like=False,
    )


# --- a line of text under the panel ------------------------------------------------------------------
def panel_text(
    scene: Any,
    object_id: str,
    tokens: Any,
    arguments: dict[str, Any],
    *,
    style_role: str | None = None,
    data: dict[str, Any] | None = None,
    equation: dict[str, Any] | None = None,
) -> Component:
    """`text` in the text role `text_role`, centred under the axes box of the `time_course` named `panel`, where the
    original scene sets its fit line; in the object's `style_role` (default foreground)."""
    pg = page(tokens)
    axes = _axes_of(scene, object_id, str(arguments["panel"]))
    left, bottom, right, _ = _box(axes)
    role = str(arguments.get("text_role", "body"))
    text = Text(str(arguments["text"]), **tokens.text_kwargs(tokens.typeface(role), tokens.color(style_role or "foreground")))
    text.move_to(np.array([(left + right) / 2, bottom - pg.length(ORIGINAL["fit_line_drop"]), 0.0]))
    return Component(object_id, "custom", VGroup(text), text=text.text, font_px=tokens.smallest_text_px(role), text_like=True)


# --- a heading over the field -----------------------------------------------------------------------
def field_heading(
    scene: Any,
    object_id: str,
    tokens: Any,
    arguments: dict[str, Any],
    *,
    style_role: str | None = None,
    data: dict[str, Any] | None = None,
    equation: dict[str, Any] | None = None,
) -> Component:
    """`text` in the text role `text_role`, centred above the visual field `field` at the original scene's height,
    in the object's `style_role` (default muted). A `text_caption` can only sit at an anchor of the safe area or
    left-aligned below or beside an earlier object (`place` in scianim_bridge.components.base), so it cannot be
    centred over the field as the original's heading is; the change of heading stays a registered fade and reveal."""
    pg = page(tokens)
    field = _field_of(scene, object_id, str(arguments["field"]))
    role = str(arguments.get("text_role", "body"))
    text = Text(str(arguments["text"]), **tokens.text_kwargs(tokens.typeface(role), tokens.color(style_role or "muted")))
    text.move_to(np.array([float(field.centre[0]), float(pg.pt(*ORIGINAL["heading_centre"])[1]), 0.0]))
    return Component(
        object_id,
        "custom",
        VGroup(text),
        text=text.text,
        font_px=tokens.smallest_text_px(role),
        text_like=True,
    )


# --- the candidates ---------------------------------------------------------------------------------
@dataclass(frozen=True)
class Candidates:
    """The candidates in `seq` order, with the prediction of each on the time axis of the predictions table."""

    x: np.ndarray
    y: np.ndarray
    sigma: np.ndarray
    r2: np.ndarray
    phase: tuple[str, ...]
    t: np.ndarray
    predictions: np.ndarray  # one row per candidate

    def __len__(self) -> int:
        return len(self.x)

    def at(self, position: float) -> tuple[int, int, float]:
        """The two rows a position lies between and the fraction of the way: (i, j, f), j = i when exact."""
        last = len(self) - 1
        position = min(max(position, 0.0), float(last))
        i = int(math.floor(position + 1e-9))
        f = position - i
        if f <= 1e-9 or i >= last:
            return min(i, last), min(i, last), 0.0
        return i, i + 1, f


def _parameter_carriers(binding: DataBinding, object_id: str) -> dict[str, float]:
    """The parameters the binding declares, after checking that every transform only carries one: a `smooth` whose
    window is a parameter with default 0, which leaves the table as it is."""
    for transform in binding.transforms:
        window = getattr(transform, "window", None)
        if transform.op != "smooth" or not isinstance(window, ParameterRef) or window.default != 0:
            raise ValueError(
                f"object '{object_id}': its binding may only declare parameters, as smooth transforms whose window "
                f"is a parameter with default 0; found {transform.model_dump()}"
            )
    return dict(binding.parameters())


def _load(scene: Any, object_id: str, binding: DataBinding, arguments: dict[str, Any]) -> Candidates:
    if scene.ctx is None:
        raise RuntimeError("no job context")
    columns = arguments["columns"]
    table = scene.ctx.table(binding.source)
    seq = table.numeric(binding.encoding.x)
    if seq != [float(i) for i in range(len(seq))]:
        raise ValueError(f"object '{object_id}': column '{binding.encoding.x}' must run 0, 1, 2, ... in row order")
    if columns["r2"] != binding.encoding.y:
        raise ValueError(f"object '{object_id}': columns.r2 must be the binding's y, '{binding.encoding.y}'")
    spec = arguments["predictions"]
    other = scene.ctx.table(str(spec["source"]))
    t = np.asarray(other.numeric(str(spec["time"])), dtype=float)
    prefix = str(spec["prefix"])
    predictions = np.array([other.numeric(f"{prefix}{i:02d}") for i in range(len(seq))], dtype=float)
    return Candidates(
        x=np.asarray(table.numeric(columns["x"]), dtype=float),
        y=np.asarray(table.numeric(columns["y"]), dtype=float),
        sigma=np.asarray(table.numeric(columns["sigma"]), dtype=float),
        r2=np.asarray(table.numeric(columns["r2"]), dtype=float),
        phase=tuple(table.column(columns["phase"])),
        t=t,
        predictions=predictions,
    )


class CandidatePath(ParametricComponent):
    """The candidate, the kept best, the readouts and the prediction, all a function of `candidate`."""


def candidate_path(
    scene: Any,
    object_id: str,
    tokens: Any,
    arguments: dict[str, Any],
    *,
    style_role: str | None = None,
    data: dict[str, Any] | None = None,
    equation: dict[str, Any] | None = None,
) -> CandidatePath:
    """Everything that moves with the candidate.

    arguments:
    - `field`, `panel`: the `visual_field` and the `time_course` declared before this object;
    - `columns`: the candidates table's columns `x`, `y`, `sigma`, `r2` (the binding's y) and `phase`;
    - `predictions`: `source` (a declared csv source), `time` (its time column, on the panel's time axis) and `prefix`
      (the prediction of candidate n is the column prefix + n in two digits);
    - `kept_phases`: the phases whose candidates compete for the dashed outline (the grid search);
    - `roles`: palette roles of `candidate` (circle, dot, prediction, readouts) and `kept` (the dashed outline);
    - `text_roles`: `params` (x, y, sigma under the field) and `r2` (the readout above the panel);
    - `weights_px_at_1080p`: `candidate`, `kept`, `prediction`; `dot_radius_px_at_1080p`; `dash_px_at_1080p`
      (the length of one dash and its gap of the kept outline).
    """
    if data is None:
        raise ValueError(f"object '{object_id}' needs a data binding (the candidates table)")
    binding = DataBinding.model_validate(data)
    parameters = _parameter_carriers(binding, object_id)
    for name in ("candidate", "retire_kept"):
        if name not in parameters:
            raise ValueError(f"object '{object_id}': its binding must declare the parameter '{name}'")
    cands = _load(scene, object_id, binding, arguments)
    field = _field_of(scene, object_id, str(arguments["field"]))
    axes = _axes_of(scene, object_id, str(arguments["panel"]))
    left, bottom, right, top = _box(axes)
    y_low, y_high = float(axes.y_range[0]), float(axes.y_range[1])
    t_low, t_high = float(axes.x_range[0]), float(axes.x_range[1])
    if cands.t.min() < t_low or cands.t.max() > t_high:
        raise ValueError(f"object '{object_id}': the predictions' time axis leaves the panel's time range")
    if cands.predictions.min() < y_low or cands.predictions.max() > y_high:
        raise ValueError(f"object '{object_id}': a prediction leaves the panel's value range [{y_low:g}, {y_high:g}]")
    pg = page(tokens)
    kept_phases = {str(p) for p in arguments["kept_phases"]}
    candidate_colour = tokens.color(_role(arguments, "candidate"))
    kept_colour = tokens.color(_role(arguments, "kept"))
    w_candidate = _weight(tokens, arguments, "candidate")
    w_kept = _weight(tokens, arguments, "kept")
    w_prediction = _weight(tokens, arguments, "prediction")
    dot_radius = tokens.units(float(arguments["dot_radius_px_at_1080p"]))
    dash = tokens.units(float(arguments["dash_px_at_1080p"]))
    ends = tokens.line_kwargs()
    params_face = tokens.typeface(str(arguments["text_roles"]["params"]))
    r2_face = tokens.typeface(str(arguments["text_roles"]["r2"]))
    params_centre = pg.pt(*ORIGINAL["params_centre"])
    params_centre[0] = float(field.centre[0])  # centred under the field, wherever the field is
    r2_anchor = np.array([right, top + pg.length(ORIGINAL["plot_label_rise"]), 0.0])
    xs = np.array([axes.c2p(t, 0.0)[0] for t in cands.t], dtype=float)
    # Readouts are fresh `Text` objects in every frame (ADR-029); a string seen before is copied, not reset.
    texts: dict[tuple[str, str], Text] = {}

    def text(kind: str, value: str) -> Text:
        key = (kind, value)
        if key not in texts:
            face = params_face if kind == "params" else r2_face
            texts[key] = Text(value, **tokens.text_kwargs(face, candidate_colour))
        return texts[key].copy()

    def state(position: float) -> tuple[float, float, float, float, np.ndarray]:
        i, j, f = cands.at(position)
        mix = lambda a: float(a[i] + (a[j] - a[i]) * f)  # noqa: E731
        prediction = cands.predictions[i] + (cands.predictions[j] - cands.predictions[i]) * f
        return mix(cands.x), mix(cands.y), mix(cands.sigma), mix(cands.r2), prediction

    def kept_index(position: float) -> int | None:
        """The best candidate reached so far among the kept phases (the first of equals, as the original kept)."""
        reached, _, _ = cands.at(position)  # during a hop the candidate it heads for is not reached yet
        best: int | None = None
        for n in range(reached + 1):
            if cands.phase[n] in kept_phases and (best is None or cands.r2[n] > cands.r2[best]):
                best = n
        return best

    def circle(x: float, y: float, sigma: float) -> Circle:
        c = Circle(radius=sigma * field.per_deg)
        c.set_stroke(candidate_colour, w_candidate).set_fill(opacity=0)
        return c.move_to(field.pt(x, y))

    def kept_outline(n: int | None, ink: float) -> VMobject:
        if n is None or ink <= 0.0:
            return _nothing()
        radius = float(cands.sigma[n]) * field.per_deg
        ring = Circle(radius=radius).move_to(field.pt(float(cands.x[n]), float(cands.y[n])))
        count = max(8, int(round(2 * math.pi * radius / (2 * dash))))
        dashed = DashedVMobject(ring, num_dashes=count, dashed_ratio=0.5)
        dashed.set_stroke(kept_colour, w_kept, opacity=ink).set_fill(opacity=0)
        return dashed

    def prediction_line(values: np.ndarray) -> VMobject:
        line = VMobject(**ends)
        line.set_points_as_corners(
            [np.array([x, float(axes.c2p(0.0, v)[1]), 0.0]) for x, v in zip(xs, values, strict=True)]
        )
        return line.set_stroke(candidate_colour, w_prediction).set_fill(opacity=0)

    def members(values: dict[str, float]) -> list[VMobject]:
        position = float(values["candidate"])
        x, y, sigma, r2, prediction = state(position)
        ink = 1.0 - min(1.0, max(0.0, float(values["retire_kept"])))
        params = text("params", f"x {x:+.2f}°   y {y:+.2f}°   σ {sigma:.2f}°").move_to(params_centre)
        readout = text("r2", f"R² = {r2:.2f}")
        readout.move_to(r2_anchor, aligned_edge=RIGHT)
        readout.set_y(float(r2_anchor[1]))
        dot = Dot(field.pt(x, y), radius=dot_radius, **tokens.dot_kwargs(candidate_colour))
        return [
            kept_outline(kept_index(position), ink),
            circle(x, y, sigma),
            dot,
            prediction_line(prediction),
            params,
            readout,
        ]

    initial = members(parameters)
    group = VGroup(*initial)
    current = list(initial)

    def rebuild(values: dict[str, float]) -> list[str]:
        fresh = members(values)
        for index, (old, new) in enumerate(zip(current, fresh, strict=True)):
            scene.swap_member(group, old, new)
            current[index] = new
        return []

    return CandidatePath(
        object_id,
        "custom",
        group,
        text=None,
        font_px=tokens.smallest_text_px(str(arguments["text_roles"]["params"]), str(arguments["text_roles"]["r2"])),
        text_like=False,
        parameters=dict(parameters),
        rebuild=rebuild,
    )
