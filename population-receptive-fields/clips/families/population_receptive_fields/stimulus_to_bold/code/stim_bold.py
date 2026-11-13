"""Custom builders of the clip `stimulus_to_bold` (storyboard objects of `kind: custom`).

Reviewed code, not generated: `scianim codegen` writes `code/scene_stimulus_to_bold.py` and that module calls the
four builders below by name, `stim_bold:<function>`.

What the registry (0.5.0) cannot draw here, and so what these builders draw:

- `visual_field`: the field (a circle of radius 8 deg), the pRF as its one-sigma circle and the fixation cross.
- `response_rows`: two rows on one time axis, each on its own scale (neural -0.05 to 0.75, BOLD -0.3 to 0.9), with
  their row labels, ticks, zero lines and the time axis under the lower row.
- `stimulus_strip`: one band per sweep of the bar, read from the run's table, with an arrow for its direction.
- `run`: what moves on the run's one clock: the bar in the field, both traces drawn up to the cursor, the cursor
  and a dot on each trace. It is a `ParametricComponent`, so the registered `vary_parameter` action drives it.

Its two parameters, `t` (the run's clock, in seconds of the run) and `marks` (the ink of the cursor, its dots and
the bar: 0 before the run, 1 during it), are declared through the object's data binding, the only place a
`kind: custom` object can declare a parameter in manim8 bad3ae1: each is the `window` of a `smooth` transform whose
default is 0, which leaves the table as it is. The builder checks that this is so and never applies a swept value
as a smoothing window; the parameters are its own.

Geometry follows the original scene of the Coimbra pRF workshop (references/original_scene.py), in its scene units
(a frame 16 wide and 9 high), fitted as one piece into the style's safe area, so it is the same under every style.
Colours are palette roles, text takes the style's text roles; nothing here names a colour, a font or a text size.
Line weights and mark sizes come from the storyboard's arguments, in pixels at 1080p. Every rebuild is a pure
function of the parameters: no updaters, so checkpoints are exact.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from manim import DOWN, LEFT, PI, RIGHT, UP, Arrow, Circle, Dot, Line, Rectangle, Text, VGroup, VMobject

from scianim_bridge.components.base import Component, ParametricComponent
from scianim_bridge.data import apply_binding
from scianim_core.storyboard import DataBinding, ParameterRef

# The original scene's layout (references/original_scene.py), in its scene units: a frame 16 wide and 9 high with
# the origin at the centre. Rows are (bottom, height).
ORIGINAL: dict[str, Any] = {
    "field_centre": (-6.4, 0.3),  # VisualField((-6.4, 0.3), 1.45, deg=8.0)
    "field_radius": 1.45,
    "rows_left": -3.6,  # L
    "rows_width": 11.0,  # Wd
    "strip": (2.75, 0.8),  # S = Frame(L, 2.75, Wd, 0.8, ...)
    "neural": (0.05, 2.05),  # N = Frame(L, 0.05, Wd, 2.05, ...)
    "bold": (-2.85, 2.3),  # Bd = Frame(L, -2.85, Wd, 2.3, ...)
    "row_label_x": -4.45,  # L - 0.85
    "strip_label_gap": 0.3,
    "tick_gap": 0.12,
    "time_label_gap": 0.55,
    "arrow_half_length": 0.27,
    "arrow_tip_length": 0.14,
    "fixation_half_length": 0.13,
    "cursor_top": -0.08,  # in strip units: the cursor starts just under the strip, S(x, -0.08)
}
COMPOSITION = (-7.9, -3.9, 7.7, 3.6)
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
    """The visual field: `centre` and `radius` in scene units showing `radius_deg` degrees from fixation."""

    centre: np.ndarray
    radius: float
    radius_deg: float

    @property
    def per_deg(self) -> float:
        return self.radius / self.radius_deg

    def pt(self, x_deg: float, y_deg: float) -> np.ndarray:
        return self.centre + np.array([x_deg * self.per_deg, y_deg * self.per_deg, 0.0])


@dataclass(frozen=True)
class Row:
    """A row of the time axis: data (time, value) to scene coordinates."""

    left: float
    bottom: float
    width: float
    height: float
    t0: float
    t1: float
    y0: float
    y1: float

    def __call__(self, t: float, y: float) -> np.ndarray:
        return np.array(
            [
                self.left + (t - self.t0) / (self.t1 - self.t0) * self.width,
                self.bottom + (y - self.y0) / (self.y1 - self.y0) * self.height,
                0.0,
            ]
        )


def _weight(tokens: Any, arguments: dict[str, Any], name: str) -> float:
    return tokens.stroke_width(float(arguments["weights_px_at_1080p"][name]))


def _nothing() -> VMobject:
    """A member that draws nothing (no points), for a mark that is not shown."""
    return VMobject(stroke_width=0, fill_opacity=0)


# --- the run's table ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Run:
    """The columns of the run, one row per second: time, bar centre and direction (None in blanks), traces."""

    t: np.ndarray
    centre: list[float | None]
    direction: list[float | None]
    traces: dict[str, np.ndarray]

    @property
    def step(self) -> float:
        return float(self.t[1] - self.t[0])

    def sweeps(self) -> list[tuple[float, float, float]]:
        """(start, end, direction) of each sweep in seconds of the run: consecutive rows with one direction and a
        rising bar centre, as the original scene's `sweeps()`."""
        out: list[tuple[float, float, float]] = []
        k, n = 0, len(self.t)
        while k < n:
            d = self.direction[k]
            if d is None or self.centre[k] is None:
                k += 1
                continue
            j = k
            while (
                j + 1 < n
                and self.direction[j + 1] == d
                and self.centre[j + 1] is not None
                and self.centre[j + 1] > self.centre[j]  # type: ignore[operator]
            ):
                j += 1
            out.append((float(self.t[k]), float(self.t[j]) + self.step, float(d)))
            k = j + 1
        return out

    def bar_at(self, t: float) -> tuple[float, float] | None:
        """Bar centre and direction at run time t, or None in a blank: the centre of the row that holds t, moving
        linearly towards the next row's while the same sweep goes on (the original scene's `bar_at`)."""
        k = int(np.clip(np.searchsorted(self.t, t, side="right") - 1, 0, len(self.t) - 1))
        c, d = self.centre[k], self.direction[k]
        if c is None or d is None:
            return None
        if k + 1 < len(self.t):
            nxt = self.centre[k + 1]
            if nxt is not None and self.direction[k + 1] == d and nxt > c:
                c += (nxt - c) * (t - float(self.t[k])) / self.step
        return c, d

    def upto(self, name: str, t: float) -> list[tuple[float, float]]:
        """The samples of a trace up to t, and the linear interpolation at t when t falls between two samples."""
        ts, ys = self.t, self.traces[name]
        k = int(np.searchsorted(ts, t, side="right"))
        points = [(float(a), float(b)) for a, b in zip(ts[:k], ys[:k], strict=True)]
        if 0 < k < len(ts) and t > ts[k - 1]:
            points.append((t, float(np.interp(t, ts, ys))))
        return points

    def value_at(self, name: str, t: float) -> tuple[float, float]:
        """The point of a trace under the cursor; past the last sample the dot stays on the last sample."""
        x = float(min(max(t, self.t[0]), self.t[-1]))
        return x, float(np.interp(x, self.t, self.traces[name]))


def _optional(cell: str) -> float | None:
    return None if cell.strip() == "" else float(cell)


def _table(scene: Any, data: dict[str, Any] | None, object_id: str) -> tuple[DataBinding, Any]:
    if data is None or scene.ctx is None:
        raise ValueError(f"object '{object_id}': a data binding to the run's table is required")
    binding = DataBinding.model_validate(data)
    return binding, scene.ctx.table(binding.source)


def _load_run(table: Any, columns: dict[str, str], traces: dict[str, str]) -> Run:
    t = np.array(table.numeric(columns["time"]), dtype=float)
    if len(t) < 2 or not np.allclose(np.diff(t), t[1] - t[0]):
        raise ValueError(f"{table.source}: column '{columns['time']}' must be evenly spaced")
    centre = [_optional(c) for c in table.column(columns["bar_centre"])]
    direction = [_optional(d) for d in table.column(columns["bar_direction"])]
    for k, (c, d) in enumerate(zip(centre, direction, strict=True)):
        if (c is None) != (d is None):
            raise ValueError(f"{table.source}: row {k + 1} has a bar centre or a direction, not both")
    return Run(t, centre, direction, {name: np.array(table.numeric(col), dtype=float) for name, col in traces.items()})


def _declared_parameters(binding: DataBinding, table: Any, expected: set[str], object_id: str) -> dict[str, float]:
    """The parameters the binding declares: each the zero window of a `smooth` transform, which leaves the table
    as it is. Anything else in the transforms is refused, so no declared transform is silently ignored."""
    for transform in binding.transforms:
        window = getattr(transform, "window", None)
        if transform.op != "smooth" or not isinstance(window, ParameterRef) or window.default != 0:
            raise ValueError(
                f"object '{object_id}': its transforms only declare parameters (op: smooth, window: "
                f"{{parameter: <name>, default: 0}}); got {transform.model_dump(mode='json')}"
            )
    declared = binding.parameters()
    if set(declared) != expected:
        raise ValueError(f"object '{object_id}': declare exactly the parameters {sorted(expected)}, not {sorted(declared)}")
    at_defaults = apply_binding(table, binding)  # the table as the binding gives it at the defaults
    raw = apply_binding(table, DataBinding(source=binding.source, encoding=binding.encoding))
    if [(s.x, s.y) for s in at_defaults] != [(s.x, s.y) for s in raw]:
        raise ValueError(f"object '{object_id}': the declaring transforms must leave the table unchanged")
    return declared


# --- builders ----------------------------------------------------------------------------------
def visual_field(
    scene: Any, object_id: str, tokens: Any, arguments: dict[str, Any], *, style_role=None, data=None, equation=None
) -> Component:
    """The field as a circle in the page colour, the pRF's one-sigma circle and the fixation cross. Never rebuilt,
    so the pRF outline cannot move or change (constraint prf_fixed)."""
    pg = page(tokens)
    field = Field(pg.pt(*ORIGINAL["field_centre"]), pg.length(ORIGINAL["field_radius"]), float(arguments["radius_deg"]))
    line = tokens.line_kwargs()
    disc = Circle(radius=field.radius, **line).move_to(field.centre)
    disc.set_stroke(tokens.color("hairline"), _weight(tokens, arguments, "outline"))
    disc.set_fill(tokens.color("background"), 1.0)
    disc.set_z_index(-3)  # under the bar, which the `run` object draws at z -2
    prf = arguments["prf"]
    ring = Circle(radius=float(prf["sigma_deg"]) * field.per_deg, **line)
    ring.move_to(field.pt(float(prf["x_deg"]), float(prf["y_deg"])))
    ring.set_stroke(tokens.color("foreground"), _weight(tokens, arguments, "prf")).set_fill(opacity=0.0)
    h = pg.length(ORIGINAL["fixation_half_length"])
    f = field.pt(0.0, 0.0)
    cross = VGroup(Line(f + LEFT * h, f + RIGHT * h, **line), Line(f + DOWN * h, f + UP * h, **line))
    cross.set_stroke(tokens.color("muted"), _weight(tokens, arguments, "fixation"))
    marks = VGroup(ring, cross)
    marks.set_z_index(1)  # over the bar
    component = Component(object_id, "custom", VGroup(disc, marks))
    component.field = field  # type: ignore[attr-defined]  # read by `run` for the bar
    return component


def response_rows(
    scene: Any, object_id: str, tokens: Any, arguments: dict[str, Any], *, style_role=None, data=None, equation=None
) -> Component:
    """The neural and BOLD rows: a value axis with ticks and a zero line each, on its own scale; the time axis with
    its ticks and label under the lower row; a label for each row."""
    pg = page(tokens)
    t0, t1 = (float(v) for v in arguments["time_range"])
    left = float(pg.pt(ORIGINAL["rows_left"], 0.0)[0])
    width = pg.length(ORIGINAL["rows_width"])
    line = tokens.line_kwargs()
    axis_w, zero_w = _weight(tokens, arguments, "axis"), _weight(tokens, arguments, "zero_line")
    muted, grid, ink = tokens.color("muted"), tokens.color("grid"), tokens.color("foreground")
    # strokes in muted, as direction.prefer asks; their numbers and the time label in secondary_text, the text
    # role that reaches 4.5:1 on both pages (muted is about 3:1 for text)
    words = tokens.color("secondary_text")
    tick_face, label_face = tokens.typeface("tick_label"), tokens.typeface("axis_label")
    tick_gap = pg.length(ORIGINAL["tick_gap"])
    group = VGroup()
    rows: dict[str, Row] = {}
    for spec in arguments["rows"]:
        name = spec["id"]
        bottom_o, height_o = ORIGINAL[name]
        y0, y1 = (float(v) for v in spec["value_range"])
        row = Row(left, float(pg.pt(0.0, bottom_o)[1]), width, pg.length(height_o), t0, t1, y0, y1)
        rows[name] = row
        group.add(Line(row(t0, 0.0), row(t1, 0.0), stroke_color=grid, stroke_width=zero_w, **line))
        group.add(Line(row(t0, y0), row(t0, y1), stroke_color=muted, stroke_width=axis_w, **line))
        for v in spec["ticks"]:
            tick = Text(f"{float(v):g}", **tokens.text_kwargs(tick_face, words))
            group.add(tick.next_to(row(t0, float(v)), LEFT, buff=tick_gap))
        label = Text(spec["label"], **tokens.text_kwargs(label_face, ink)).rotate(PI / 2)
        label.move_to([float(pg.pt(ORIGINAL["row_label_x"], 0.0)[0]), row.bottom + row.height / 2, 0.0])
        group.add(label)
    base = rows[arguments["time_axis_under"]]
    group.add(Line(base(t0, base.y0), base(t1, base.y0), stroke_color=muted, stroke_width=axis_w, **line))
    for v in arguments["time_ticks"]:
        tick = Text(f"{float(v):g}", **tokens.text_kwargs(tick_face, words))
        group.add(tick.next_to(base(float(v), base.y0), DOWN, buff=tick_gap))
    title = Text(arguments["time_label"], **tokens.text_kwargs(label_face, words))
    group.add(title.next_to(base((t0 + t1) / 2, base.y0), DOWN, buff=pg.length(ORIGINAL["time_label_gap"])))
    component = Component(
        object_id, "custom", group, font_px=tokens.smallest_text_px("tick_label", "axis_label")
    )
    component.rows = rows  # type: ignore[attr-defined]  # read by `stimulus_strip` and `run`
    return component


def stimulus_strip(
    scene: Any, object_id: str, tokens: Any, arguments: dict[str, Any], *, style_role=None, data=None, equation=None
) -> Component:
    """One band per sweep on the rows' time axis, an arrow in each for the bar's direction (counter-clockwise from
    rightward), and the row's label at its left."""
    pg = page(tokens)
    binding, table = _table(scene, data, object_id)
    run = _load_run(
        table,
        {"time": binding.encoding.x, "bar_direction": binding.encoding.y, "bar_centre": arguments["bar_centre_column"]},
        {},
    )
    rows = scene.objects[arguments["rows"]].rows
    any_row = next(iter(rows.values()))
    bottom_o, height_o = ORIGINAL["strip"]
    bottom, height = float(pg.pt(0.0, bottom_o)[1]), pg.length(height_o)
    neutral, ink = tokens.color("neutral"), tokens.color("foreground")
    half, tip = pg.length(ORIGINAL["arrow_half_length"]), pg.length(ORIGINAL["arrow_tip_length"])
    group = VGroup()
    arrows = VGroup()
    sweeps = run.sweeps()
    seam = tokens.units(1.5)  # a band that meets the next one runs this far under it, so no seam shows
    for index, (start, end, direction) in enumerate(sweeps):
        x0, x1 = float(any_row(start, 0.0)[0]), float(any_row(end, 0.0)[0])
        meets_next = index + 1 < len(sweeps) and abs(sweeps[index + 1][0] - end) < 1e-9
        reach = x1 + (seam if meets_next else 0.0)
        band = Rectangle(width=reach - x0, height=height, stroke_width=0, fill_color=neutral, fill_opacity=1.0)
        band.move_to([(x0 + reach) / 2, bottom + height / 2, 0.0])
        group.add(band)
        u = np.array([math.cos(math.radians(direction)), math.sin(math.radians(direction)), 0.0])
        c = np.array([(x0 + x1) / 2, bottom + height / 2, 0.0])
        arrows.add(
            Arrow(
                c - u * half,
                c + u * half,
                buff=0,
                color=ink,
                stroke_width=_weight(tokens, arguments, "arrow"),
                tip_length=tip,
                max_tip_length_to_length_ratio=0.5,
                max_stroke_width_to_length_ratio=1000.0,
            )
        )
    group.add(arrows)
    label = Text(arguments["label"], **tokens.text_kwargs(tokens.typeface("axis_label"), ink))
    group.add(label.next_to(np.array([any_row.left, bottom + height / 2, 0.0]), LEFT, buff=pg.length(ORIGINAL["strip_label_gap"])))
    component = Component(object_id, "custom", group, font_px=tokens.smallest_text_px("axis_label"))
    component.strip = (bottom, height)  # type: ignore[attr-defined]  # read by `run` for the cursor's top
    component.sweeps = sweeps  # type: ignore[attr-defined]
    return component


def run(
    scene: Any, object_id: str, tokens: Any, arguments: dict[str, Any], *, style_role=None, data=None, equation=None
) -> ParametricComponent:
    """What moves on the run's clock `t`: the bar in the field (2 deg wide at the row's centre and direction,
    clipped to the field, none in blanks), both traces drawn up to the cursor (samples joined by straight lines, on
    their rows' own scales), the cursor from under the strip to the time axis, and a dot on each trace at the
    cursor. `marks` is the ink of the cursor, its dots and the bar."""
    pg = page(tokens)
    binding, table = _table(scene, data, object_id)
    parameters = _declared_parameters(binding, table, {"t", "marks"}, object_id)
    columns = dict(arguments["columns"])
    if columns["time"] != binding.encoding.x:
        raise ValueError(f"object '{object_id}': columns.time must be the binding's x ({binding.encoding.x})")
    traces = {name: spec["column"] for name, spec in arguments["traces"].items()}
    run_table = _load_run(table, columns, traces)
    field: Field = scene.objects[arguments["field"]].field
    rows: dict[str, Row] = scene.objects[arguments["rows"]].rows
    strip_bottom, strip_height = scene.objects[arguments["strip"]].strip
    for name, spec in arguments["traces"].items():
        row = rows[spec["row"]]
        ys = run_table.traces[name]
        if float(ys.min()) < row.y0 or float(ys.max()) > row.y1:
            raise ValueError(
                f"object '{object_id}': trace '{name}' ({ys.min():g} to {ys.max():g}) leaves its row's range "
                f"[{row.y0:g}, {row.y1:g}]; it is drawn as it is, never clipped or rescaled"
            )
    bar_width = float(arguments["bar_width_deg"])
    line = tokens.line_kwargs()
    neutral, signal, muted = tokens.color("neutral"), tokens.color("primary_signal"), tokens.color("muted")
    cursor_opacity = float(arguments["cursor_opacity"])
    dot_radius = tokens.units(float(arguments["dot_radius_px_at_1080p"]))
    bottom_row = rows[arguments["cursor_to"]]

    def bar(t: float, ink: float) -> VMobject:
        at = run_table.bar_at(t)
        if at is None or ink <= 0.0:
            return _nothing()
        pos, theta = at
        r = field.radius_deg
        a, b = max(pos - bar_width / 2, -r), min(pos + bar_width / 2, r)
        if b - a <= 1e-4:
            return _nothing()
        ha, hb = math.sqrt(max(r * r - a * a, 0.0)), math.sqrt(max(r * r - b * b, 0.0))
        ta, tb = math.atan2(ha, a), math.atan2(hb, b)
        top = [(r * math.cos(s), r * math.sin(s)) for s in np.linspace(ta, tb, 48)]
        bottom = [(r * math.cos(s), -r * math.sin(s)) for s in np.linspace(tb, ta, 48)]
        th = math.radians(theta)
        points = [
            field.pt(u * math.cos(th) - v * math.sin(th), u * math.sin(th) + v * math.cos(th))
            for u, v in [(a, -ha), *top, *bottom, (a, -ha)]
        ]
        shape = VMobject(stroke_width=0, fill_color=neutral, fill_opacity=ink)
        shape.set_points_as_corners(points)
        return shape.set_z_index(-2)

    def trace(name: str, t: float) -> VMobject:
        spec = arguments["traces"][name]
        points = run_table.upto(name, t)
        if len(points) < 2:
            return _nothing()
        row = rows[spec["row"]]
        curve = VMobject(stroke_color=signal, stroke_width=tokens.stroke_width(float(spec["weight_px_at_1080p"])), **line)
        curve.set_points_as_corners([row(x, y) for x, y in points])
        return curve.set_fill(opacity=0.0)

    def cursor(t: float, ink: float) -> VMobject:
        if ink <= 0.0:
            return _nothing()
        top = np.array([float(bottom_row(t, 0.0)[0]), strip_bottom + ORIGINAL["cursor_top"] * strip_height, 0.0])
        foot = bottom_row(t, bottom_row.y0)
        return Line(top, foot, stroke_color=muted, stroke_width=_weight(tokens, arguments, "cursor"), stroke_opacity=cursor_opacity * ink, **line)

    def dot(name: str, t: float, ink: float) -> VMobject:
        if ink <= 0.0:
            return _nothing()
        x, y = run_table.value_at(name, t)
        marker = Dot(rows[arguments["traces"][name]["row"]](x, y), radius=dot_radius, **tokens.dot_kwargs(signal))
        return marker.set_fill(opacity=ink).set_stroke(opacity=ink)

    names = list(arguments["traces"])

    def members(values: dict[str, float]) -> dict[str, VMobject]:
        t, ink = float(values["t"]), min(1.0, max(0.0, float(values["marks"])))
        fresh = {"bar": bar(t, ink)}
        fresh.update({f"trace:{name}": trace(name, t) for name in names})
        fresh["cursor"] = cursor(t, ink)
        fresh.update({f"dot:{name}": dot(name, t, ink) for name in names})
        return fresh

    current = members(parameters)
    group = VGroup(*current.values())

    def rebuild(values: dict[str, float]) -> list[str]:
        for key, new in members(values).items():
            scene.swap_member(group, current[key], new)
            current[key] = new
        return []

    return ParametricComponent(object_id, "custom", group, parameters=dict(parameters), rebuild=rebuild)
