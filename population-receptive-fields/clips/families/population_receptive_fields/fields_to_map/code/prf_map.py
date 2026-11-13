"""Custom builders of the clip `fields_to_map` (storyboard objects of `kind: custom`).

Reviewed code, not generated: `scianim codegen` writes `code/scene_fields_to_map.py`, and that module calls the two
builders below by name, `prf_map:<function>`.

What the registry (0.5.0) cannot draw here, and so what these builders draw:

- `visual_field`: the right half of the visual field out to its radius in degrees (a semicircle), the vertical
  meridian and the fixation cross. Static.
- `voxel_fits`: one dot per voxel at its fitted pRF centre in that field and one square per voxel on the model
  sheet of cortex, both in one colour, read row by row from the voxels table. It is a `ParametricComponent`, so the
  registered `vary_parameter` action drives it, with two parameters:
  - `fits` (0 to 1): how far the sequence of fits has run. Voxels arrive in the order of the table's `order`
    column, a square and its dot together, each fading in from small to full over the same share of the sequence;
    the starts are evenly spaced, as Manim's `LaggedStart` spaces them with the original scene's `lag_ratio`.
  - `recolour` (0 to 1): the colouring, from the first (by eccentricity) at 0 to the second (by polar angle) at 1.
    A square and its dot always take the same colour; positions never change when the colour does.

The two parameters are declared through the object's data binding, the only place a `kind: custom` object can
declare a parameter in manim8 bad3ae1: each is the `window` of a `smooth` transform whose default is 0, which leaves
the table as it is. The builder checks that this is so and never applies a swept value as a smoothing window; the
parameters are its own.

Colours: each colouring is a ramp through three palette roles of the active style, ordered in lightness in both
bridged styles. The ramp is interpolated in CIELAB, so lightness changes monotonically along it (an interpolation in
sRGB between orange and teal dips in lightness and would break the order). A value outside the colouring's range
takes the colour of the nearer end. Nothing here names a colour, a font or a text size: colours are palette roles,
line weights come from the storyboard's arguments in pixels at 1080p, and dots take the style's rim
(`Tokens.dot_kwargs`).

Geometry follows the original scene (references/original_scene.py) in its own units, a frame 16 wide and 9 high with
the origin at the centre, mapped onto the frame by one uniform scale (the frame's height over 9, times `zoom`) and an
offset given in those units (`page`), so it is the same under every style. Mark sizes that belong to the drawing (the
dots' radius) are in those units too; line weights are in pixels at 1080p. Every rebuild is a pure function of the parameters:
no updaters, so checkpoints and stops are exact.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
from manim import PI, Arc, Dot, Line, ManimColor, Square, VGroup

from scianim_bridge.components.base import Component, ParametricComponent
from scianim_bridge.data import apply_binding
from scianim_bridge.scene import state_easing
from scianim_core.storyboard import DataBinding, ParameterRef

PARAMETERS = ("fits", "recolour")
"""The parameters `voxel_fits` declares through its binding, in this order: the sequence of fits, the colouring."""


# --- geometry ----------------------------------------------------------------------------------
@dataclass(frozen=True)
class Page:
    """The original scene's units mapped onto the frame: a uniform scale `k` and an offset in the original units."""

    k: float
    dx: float
    dy: float

    def pt(self, x: float, y: float) -> np.ndarray:
        return np.array([self.k * (x + self.dx), self.k * (y + self.dy), 0.0])

    def length(self, d: float) -> float:
        return self.k * d


@dataclass(frozen=True)
class FieldGeometry:
    """Where the field lies on the page: its centre, its radius in frame units and in degrees."""

    page: Page
    centre: np.ndarray
    radius: float
    radius_deg: float

    def pt(self, x_deg: float, y_deg: float) -> np.ndarray:
        scale = self.radius / self.radius_deg
        return self.centre + np.array([x_deg * scale, y_deg * scale, 0.0])


def _page(tokens: Any, arguments: dict[str, Any]) -> Page:
    """`original_frame_height` maps the original frame onto this one; `zoom` enlarges the drawing beyond that, so it
    fills the room between the labels and the key line, which sit at the style's safe-area anchors."""
    spec = arguments["page"]
    k = tokens.frame_height / float(spec["original_frame_height"]) * float(spec.get("zoom", 1.0))
    dx, dy = (float(v) for v in spec.get("offset", (0.0, 0.0)))
    return Page(k, dx, dy)


def _weight(tokens: Any, weights: dict[str, Any], name: str) -> float:
    return tokens.stroke_width(float(weights[name]))


# --- colour ramps in CIELAB ---------------------------------------------------------------------
_WHITE = np.array([0.95047, 1.0, 1.08883])  # D65
_RGB_TO_XYZ = np.array(
    [[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]]
)
_XYZ_TO_RGB = np.linalg.inv(_RGB_TO_XYZ)


def _srgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb, dtype=float)
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    xyz = linear @ _RGB_TO_XYZ.T / _WHITE
    f = np.where(xyz > 216 / 24389, np.cbrt(xyz), (24389 / 27 * xyz + 16) / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], axis=-1)


def _lab_to_srgb(lab: np.ndarray) -> np.ndarray:
    lab = np.asarray(lab, dtype=float)
    fy = (lab[..., 0] + 16) / 116
    fx = fy + lab[..., 1] / 500
    fz = fy - lab[..., 2] / 200
    f = np.stack([fx, fy, fz], axis=-1)
    xyz = np.where(f**3 > 216 / 24389, f**3, (116 * f - 16) / (24389 / 27)) * _WHITE
    linear = np.clip(xyz @ _XYZ_TO_RGB.T, 0.0, 1.0)
    return np.where(linear <= 0.0031308, 12.92 * linear, 1.055 * linear ** (1 / 2.4) - 0.055).clip(0.0, 1.0)


@dataclass(frozen=True)
class Colouring:
    """One colouring: a column mapped from `start` (first role of the ramp) to `end` (last role), clipped."""

    id: str
    column: str
    start: float
    end: float
    ramp: tuple[str, ...]

    def lab(self, tokens: Any, values: np.ndarray) -> np.ndarray:
        stops = _srgb_to_lab(np.array([tokens.color(role).to_rgb() for role in self.ramp], dtype=float))
        t = np.clip((values - self.start) / (self.end - self.start), 0.0, 1.0) * (len(stops) - 1)
        index = np.minimum(t.astype(int), len(stops) - 2)
        f = (t - index)[:, None]
        return stops[index] * (1.0 - f) + stops[index + 1] * f


def _colourings(arguments: dict[str, Any]) -> list[Colouring]:
    found = []
    for spec in arguments["colourings"]:
        ramp = tuple(spec["ramp"])
        if not 2 <= len(ramp) <= 4:
            raise ValueError(f"colouring '{spec['id']}': a ramp has two to four palette roles, not {len(ramp)}")
        found.append(Colouring(spec["id"], spec["column"], float(spec["from"]), float(spec["to"]), ramp))
    if len(found) != 2:
        raise ValueError("voxel_fits draws two colourings, the first before `recolour` and the second after it")
    return found


# --- the voxels table ---------------------------------------------------------------------------
def _table(scene: Any, data: dict[str, Any] | None, object_id: str) -> tuple[DataBinding, Any]:
    if data is None or scene.ctx is None:
        raise ValueError(f"object '{object_id}': a data binding to the voxels table is required")
    binding = DataBinding.model_validate(data)
    return binding, scene.ctx.table(binding.source)


def _declared_parameters(binding: DataBinding, table: Any, object_id: str) -> dict[str, float]:
    """The parameters the binding declares: each the zero window of a `smooth` transform, which leaves the table
    unchanged. Any other transform, or a table changed at the defaults, is refused."""
    for transform in binding.transforms:
        window = getattr(transform, "window", None)
        if transform.op != "smooth" or not isinstance(window, ParameterRef) or window.default != 0:
            raise ValueError(
                f"object '{object_id}': its binding may only declare parameters, as smooth transforms whose window "
                f"is a parameter with default 0; got {transform.model_dump()}"
            )
    declared = binding.parameters()
    if set(declared) != set(PARAMETERS):
        raise ValueError(f"object '{object_id}': the binding must declare {list(PARAMETERS)}, not {sorted(declared)}")
    at_defaults = apply_binding(table, binding)
    raw = apply_binding(table, DataBinding(source=binding.source, encoding=binding.encoding))
    if [(s.x, s.y) for s in at_defaults] != [(s.x, s.y) for s in raw]:
        raise ValueError(f"object '{object_id}': the declaring transforms must leave the table unchanged")
    return declared


@dataclass(frozen=True)
class Voxels:
    rank: np.ndarray  # the `order` column: the place of each row in the sequence of fits
    u: np.ndarray
    v: np.ndarray
    x_deg: np.ndarray
    y_deg: np.ndarray
    columns: dict[str, np.ndarray]


def _load(table: Any, binding: DataBinding, columns: dict[str, str], colourings: list[Colouring], step: float) -> Voxels:
    (series,) = apply_binding(table, DataBinding(source=binding.source, encoding=binding.encoding))
    rank = np.array(table.numeric(columns["order"]), dtype=float)
    n = len(rank)
    if sorted(rank.tolist()) != list(range(n)):
        raise ValueError(f"{table.source}: column '{columns['order']}' must number the rows 0 to {n - 1}, once each")
    u = np.array(table.numeric(columns["sheet_u"]), dtype=float)
    v = np.array(table.numeric(columns["sheet_v"]), dtype=float)
    cells = set()
    for name, values in ((columns["sheet_u"], u), (columns["sheet_v"], v)):
        steps = (values - values.min()) / step
        if np.max(np.abs(steps - np.round(steps))) > 1e-6:
            raise ValueError(f"{table.source}: column '{name}' is not on the grid of step {step:g}")
    for a, b in zip(np.round((u - u.min()) / step), np.round((v - v.min()) / step), strict=True):
        cells.add((int(a), int(b)))
    if len(cells) != n:
        raise ValueError(f"{table.source}: two rows share a cell of the sheet")
    values = {c.column: np.array(table.numeric(c.column), dtype=float) for c in colourings}
    return Voxels(rank.astype(int), u, v, np.array(series.x, dtype=float), np.array(series.y, dtype=float), values)


# --- builders -----------------------------------------------------------------------------------
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
    """The right half of the visual field: the outline out to `radius_deg`, the vertical meridian and fixation."""
    page = _page(tokens, arguments)
    spec = arguments["field"]
    roles = arguments["roles"]
    weights = arguments["weights_px_at_1080p"]
    centre = page.pt(*spec["centre"])
    radius = page.length(float(spec["radius"]))
    lines = tokens.line_kwargs()
    outline = Arc(
        radius=radius,
        start_angle=-PI / 2,
        angle=PI,
        color=tokens.color(roles["outline"]),
        stroke_width=_weight(tokens, weights, "outline"),
        **lines,
    ).move_arc_center_to(centre)
    meridian = Line(
        centre + radius * np.array([0.0, -1.0, 0.0]),
        centre + radius * np.array([0.0, 1.0, 0.0]),
        color=tokens.color(roles["meridian"]),
        stroke_width=_weight(tokens, weights, "meridian"),
        **lines,
    )
    half = page.length(float(spec["fixation_half_length"]))
    fixation_kwargs = {"color": tokens.color(roles["fixation"]), "stroke_width": _weight(tokens, weights, "fixation")}
    fixation = VGroup(
        Line(centre + half * np.array([-1.0, 0.0, 0.0]), centre + half * np.array([1.0, 0.0, 0.0]), **fixation_kwargs, **lines),
        Line(centre + half * np.array([0.0, -1.0, 0.0]), centre + half * np.array([0.0, 1.0, 0.0]), **fixation_kwargs, **lines),
    )
    component = Component(object_id, "custom", VGroup(outline, meridian, fixation))
    component.geometry = FieldGeometry(page, centre, radius, float(spec["radius_deg"]))  # read by voxel_fits
    return component


def voxel_fits(
    scene: Any,
    object_id: str,
    tokens: Any,
    arguments: dict[str, Any],
    *,
    style_role: str | None = None,
    data: dict[str, Any] | None = None,
    equation: dict[str, Any] | None = None,
) -> ParametricComponent:
    """One dot in the field and one square on the sheet per voxel, arriving in order and recoloured on request."""
    binding, table = _table(scene, data, object_id)
    parameters = _declared_parameters(binding, table, object_id)
    try:
        field = scene.objects[arguments["field"]].geometry
    except (KeyError, AttributeError):
        raise ValueError(f"object '{object_id}': 'field' must name a visual_field object declared before it") from None
    page = field.page
    sheet = arguments["sheet"]
    step = float(sheet["step"])
    colourings = _colourings(arguments)
    voxels = _load(table, binding, arguments["columns"], colourings, step)
    n = len(voxels.rank)

    # The sheet, as the original scene lays it out: v = 0 at the centre's height, the columns from the left edge.
    scale = float(sheet["height"]) / (voxels.v.max() - voxels.v.min() + step)
    left = float(sheet["centre_x"]) - (voxels.u.max() - voxels.u.min()) * scale / 2
    side = page.length(step * scale * float(sheet["fill"]))
    # The dot's radius is in the original units, like the field it sits in. The style's page-coloured rim is drawn
    # centred on the outline and covers the outer half of its width, so the radius grows by that half and the
    # visible fill keeps the original's radius.
    dot_radius = page.length(float(arguments["dot_radius"])) + tokens.units(tokens.t.geometry.marker_rim_px_at_1080p) / 2

    labs = [c.lab(tokens, voxels.columns[c.column]) for c in colourings]
    rim = tokens.dot_kwargs(tokens.color("background"))  # the style's page-coloured rim; the fill is set below

    order = np.argsort(voxels.rank)  # the sequence of fits; later voxels are drawn above earlier ones
    squares: list[Square] = []
    dots: list[Dot] = []
    centres: list[tuple[np.ndarray, np.ndarray]] = []
    for row in order:
        at_square = page.pt(left + (voxels.u[row] - voxels.u.min()) * scale, float(sheet["centre_y"]) + voxels.v[row] * scale)
        at_dot = field.pt(voxels.x_deg[row], voxels.y_deg[row])
        squares.append(Square(side_length=side, stroke_width=0, fill_opacity=0.0).move_to(at_square))
        dot = Dot(at_dot, radius=dot_radius, **rim)
        dot.set_fill(opacity=0.0).set_stroke(opacity=0.0)
        dots.append(dot)
        centres.append((at_square, at_dot))
    base = [(s.points.copy(), d.points.copy()) for s, d in zip(squares, dots, strict=True)]
    lab_first = labs[0][order]
    lab_second = labs[1][order]

    # The sequence of fits: each voxel fades in over the same share of it, and the starts are evenly spaced, as
    # Manim's LaggedStart spaces them with `lag_ratio` (the original scene's 0.012 over 690 voxels).
    lag_ratio = float(arguments["arrival"]["lag_ratio"])
    start_scale = float(arguments["arrival"]["start_scale"])
    share = 1.0 / (1.0 + lag_ratio * (n - 1))
    starts = np.arange(n) * lag_ratio * share
    ease = state_easing(tokens.t.motion.easing)

    state: dict[str, Any] = {"progress": np.full(n, -1.0), "recolour": None}

    def rebuild(values: dict[str, float]) -> list[str]:
        warnings: list[str] = []
        fits = float(values["fits"])
        recolour = float(values["recolour"])
        if not (0.0 <= fits <= 1.0 and 0.0 <= recolour <= 1.0):
            warnings.append(f"object '{object_id}': fits and recolour run from 0 to 1; values were clipped")
            fits, recolour = min(max(fits, 0.0), 1.0), min(max(recolour, 0.0), 1.0)
        progress = np.array([ease(q) for q in np.clip((fits - starts) / share, 0.0, 1.0)])
        recoloured = recolour != state["recolour"]
        if recoloured:
            rgb = _lab_to_srgb(lab_first * (1.0 - recolour) + lab_second * recolour)
            state["recolour"] = recolour
        for i in range(n):
            changed = progress[i] != state["progress"][i]
            if not (changed or recoloured):
                continue
            ink = float(progress[i])
            square, dot = squares[i], dots[i]
            if changed:
                size = start_scale + (1.0 - start_scale) * ink
                for mobject, points, centre in ((square, base[i][0], centres[i][0]), (dot, base[i][1], centres[i][1])):
                    mobject.points = centre + (points - centre) * size
            colour = ManimColor(rgb[i]) if recoloured else square.get_fill_color()
            square.set_fill(colour, opacity=ink)
            dot.set_fill(colour, opacity=ink)
            dot.set_stroke(opacity=ink)
        state["progress"] = progress
        return warnings

    group = VGroup(*squares, *dots)
    component = ParametricComponent(object_id, "custom", group, parameters=dict(parameters), rebuild=rebuild)
    rebuild(dict(parameters))
    return component
