"""Custom builders of the clip `model_as_chain` (`kind: custom`, `builder: chain_builders:<name>`).

What the component registry cannot draw: boxes with glyphs at given places, the gear, arrows between boxes, the
funnel, the dashed outline, the theta tags and the pulse. Geometry is in chain_layout.py (the original scene's
positions and sizes); colours are palette roles; data come through each object's declared binding.

Four builders return a `ParametricComponent`, so that a registered `vary_parameter` action drives the motion the
original drew over time (the parametric route of the escalation ladder): `loop` (feed, emit, shrink),
`theta_split` (split), `pulse` (travel) and `bold_prediction` (drawn). manim8 accepts `vary_parameter` on a custom
object only through a data binding whose transforms name the parameter, so each of these bindings declares its
parameters as transforms that are the identity at their defaults (`smooth` with window 0, `scale` by 1). The
builders read the bound columns with the transforms at those defaults, that is unchanged, and use the parameters
for geometry only. Every rebuild is a pure function of the parameters: it sets points (and, for the split, the
opacities of the two halves of a cross-fade) from copies taken at build time, adds and removes no member, and
installs no updater, so checkpoints are exact.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from manim import DOWN, LEFT, RIGHT, UP, Line, Polygon, VGroup, VMobject

import chain_layout as L  # the project's code/ is on the path when manim8 loads a builder
from scianim_bridge.components.base import Component, ParametricComponent
from scianim_core.storyboard import DataBinding, ParameterRef

EMPTY = np.zeros((0, 3))


# --- data -------------------------------------------------------------------------------------------------------
def _setting(value: float | ParameterRef, defaults: dict[str, float]) -> float:
    return float(defaults[value.parameter]) if isinstance(value, ParameterRef) else float(value)


def bound_columns(scene: Any, data: dict[str, Any] | None, *extra: str) -> tuple[dict[str, list[float]], DataBinding]:
    """The bound table's x and y columns (and any `extra` columns), after the binding's transforms at their
    defaults. Returns ({'x': ..., 'y': ..., <extra>: ...}, binding)."""
    if data is None:
        raise ValueError("this builder needs a data binding to the panel source")
    binding = DataBinding.model_validate(data)
    table = scene.ctx.table(binding.source)
    defaults = binding.parameters()
    for transform in binding.transforms:
        if transform.op == "filter":
            table = table.filter_equals(transform.column, transform.equals)
        elif transform.op == "normalize":
            table = table.normalize(transform.column, transform.by)
        elif transform.op == "sort":
            table = table.sort_by(transform.column, transform.descending)
        elif transform.op == "scale":
            table = table.scale(transform.column, _setting(transform.by, defaults))
        elif transform.op == "smooth":
            table = table.smooth(transform.column, _setting(transform.window, defaults))
    columns = {"x": table.numeric(binding.encoding.x), "y": table.numeric(binding.encoding.y)}
    for name in extra:
        columns[name] = table.numeric(name)
    return columns, binding


def _font_px(tokens: Any, look: L.Look, factor: float = 1.0) -> float | None:
    return tokens.output_px(min(look.sizes) * factor) if look.sizes else None


def _points(mob: VMobject) -> list[tuple[VMobject, np.ndarray]]:
    return [(m, m.points.copy()) for m in mob.get_family() if len(m.points)]


def _parametric(object_id: str, group: VGroup, binding: DataBinding, rebuild: Any, font_px: float | None) -> ParametricComponent:
    component = ParametricComponent(
        object_id, "custom", group, font_px=font_px, parameters=dict(binding.parameters()), rebuild=rebuild
    )
    return component


# --- the loop ------------------------------------------------------------------------------------------------------
def loop(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """The first beat's loop (parameters theta and stimulus feed a model with a gear; its prediction lies on the
    data), with its three dots. Parameters: `feed` (0 to 1: the dots from theta and stimulus run their arrows and the
    gear turns a quarter), `emit` (0 to 1: the third dot runs from the model to the panel) and `shrink` (0 to 1: the
    loop shrinks to 45 per cent and moves to the top centre). A dot shows only while its parameter is strictly
    between 0 and 1, as the original added it for its run and removed it after."""
    look = L.Look(tokens)
    cols, binding = bound_columns(scene, data, arguments.get("prediction_column", "prediction"))
    lp = L.loop_in_frame(look, cols["x"], cols["y"], cols[arguments.get("prediction_column", "prediction")])
    center = lp.center()
    dots = []
    for _ in range(3):
        dot = look.dot(0.1)
        L.to_frame(dot)
        dot.move_to(np.zeros(3))
        dots.append(dot)
    path3 = Line(lp.model.get_bottom(), lp.panel.get_top())
    paths = [(dots[0], lp.a1, "feed"), (dots[1], lp.a2, "feed"), (dots[2], path3, "emit")]
    gear = lp.gear
    gear_center = gear.get_center()
    gear_parts = _points(gear)
    gear_ids = {id(m) for m, _ in gear_parts}
    fixed = [(m, p) for m, p in _points(VGroup(*lp.members)) if id(m) not in gear_ids]
    dot_bases = [(dot, _points(dot)) for dot in dots]
    group = VGroup(*lp.members, *dots)
    base_px = min(look.sizes)

    def rebuild(values: dict[str, float]) -> list[str]:
        shrink = values["shrink"]
        apply = lp.shrink_map(shrink, center)
        for member, base in fixed:
            member.points = apply(base)
        angle = -math.pi / 2 * values["feed"]  # Rotate(gear, -PI/2)
        c, s = math.cos(angle), math.sin(angle)
        rotation = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
        for member, base in gear_parts:
            member.points = apply((base - gear_center) @ rotation.T + gear_center)
        for (dot, path, name), (_, parts) in zip(paths, dot_bases, strict=True):
            progress = values[name]
            if 0.0 < progress < 1.0:
                where = path.point_from_proportion(progress)
                for member, base in parts:
                    member.points = apply(base + where)
            else:
                for member, _base in parts:
                    member.points = EMPTY
        component.font_px = tokens.output_px(base_px * (1.0 - (1.0 - L.LOOP_S) * shrink))
        return []

    component = ParametricComponent(
        object_id,
        "custom",
        group,
        font_px=tokens.output_px(base_px),
        parameters=dict(binding.parameters()),
        rebuild=rebuild,
    )
    component.set_parameters()
    return component


def model_outline(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """The heavier outline of the shrunken loop's model box (the original's stroke from 3 to 5): an outline of
    width 5 over the box, which a reveal fades in."""
    look = L.Look(tokens)
    cols, _ = bound_columns(scene, data, "prediction")
    lp = L.loop_in_frame(look, cols["x"], cols["y"], cols["prediction"])
    rect = L.shrunk_copy(lp, lp.model_rect)
    rect.set_fill(opacity=0).set_stroke(look.color("foreground"), 5 * L.frame_scale())
    return Component(object_id, "custom", VGroup(rect))


def funnel(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """The light funnel from the shrunken model box down to the dashed outline of the opened model, behind
    everything (z_index -2, as in the original)."""
    look = L.Look(tokens)
    cols, _ = bound_columns(scene, data, "prediction")
    lp = L.loop_in_frame(look, cols["x"], cols["y"], cols["prediction"])
    mb = L.shrunk_copy(lp, lp.model_rect)
    outline = L.hull(look)
    L.to_frame(outline)
    shape = Polygon(mb.get_corner(DOWN + LEFT), mb.get_corner(DOWN + RIGHT), outline.get_corner(UP + RIGHT), outline.get_corner(UP + LEFT))
    shape.set_stroke(width=0).set_fill(look.color("selection"), 1)
    group = VGroup(shape)
    group.set_z_index(-2)
    return Component(object_id, "custom", group)


def hull(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """The dashed outline round boxes two to six: the opened model."""
    look = L.Look(tokens)
    group = L.hull(look)
    L.to_frame(group)
    return Component(object_id, "custom", group)


# --- the row -------------------------------------------------------------------------------------------------------
def stage_box(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """One box of the row, `arguments.stage` 0 (stimulus S) to 6 (BOLD), with its label and glyph. The BOLD box
    needs the data binding (its trace is the `y` column); its prediction is the object `bold_prediction`. Contents
    sit above the box and its darkened copy (z_index 1, as in the original)."""
    look = L.Look(tokens)
    k = int(arguments["stage"])
    t: list[float] = []
    ys: list[float] = []
    if k == 6:
        cols, _ = bound_columns(scene, data)
        t, ys = cols["x"], cols["y"]
    rect, content = L.stage_box(look, k, t, ys)
    content.set_z_index(1)
    group = VGroup(rect, content)
    L.to_frame(group)
    return Component(object_id, "custom", group, font_px=_font_px(tokens, look))


def bold_prediction(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """The prediction in the BOLD box (the binding's `y` column), drawn from its start over the fraction `drawn`
    (1: whole, 0: nothing), as Manim's Create draws a curve. Above the data trace (z_index 1.5)."""
    look = L.Look(tokens)
    cols, binding = bound_columns(scene, data)
    curve = L.bold_box_prediction(look, cols["x"], cols["y"])
    L.to_frame(curve)
    full = curve.copy()
    curve.set_z_index(1.5)

    def rebuild(values: dict[str, float]) -> list[str]:
        drawn = values["drawn"]
        if drawn <= 0.0:
            curve.points = EMPTY
        elif drawn >= 1.0:
            curve.points = full.points.copy()
        else:
            curve.pointwise_become_partial(full, 0.0, drawn)
        return []

    component = _parametric(object_id, VGroup(curve), binding, rebuild, None)
    component.set_parameters()  # draw the state at the defaults
    return component


def links(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """The six arrows that link the boxes of the row."""
    look = L.Look(tokens)
    group = L.links(look)
    L.to_frame(group)
    return Component(object_id, "custom", group)


def theta_split(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """A copy of the shrunken loop's theta box that drops and splits into the four theta tags over the fitted
    stages, as the original's FadeTransform(theta.copy(), tags) does: at `split` a, the copy and the tags share the
    bounding box interpolated from the copy's to the tags', the copy at 1 - a of its ink and the tags at a. At 0 the
    copy lies exactly on the loop's theta box; at 1 only the tags are seen."""
    look = L.Look(tokens)
    cols, binding = bound_columns(scene, data, "prediction")
    lp = L.loop_in_frame(look, cols["x"], cols["y"], cols["prediction"])
    source_px = min(look.sizes) * L.LOOP_S  # the loop's smallest label, shrunk
    look.sizes.clear()
    source = L.shrunk_copy(lp, lp.theta)
    target = VGroup(*L.tags(look))
    L.to_frame(target)
    target_px = min(look.sizes)
    src_box, dst_box = L.bbox(source), L.bbox(target)

    def inks(mob: VMobject) -> list[tuple[VMobject, np.ndarray, float, float]]:
        return [(m, m.points.copy(), float(m.get_fill_opacity()), float(m.get_stroke_opacity())) for m in mob.get_family() if len(m.points)]

    source_parts, target_parts = inks(source), inks(target)
    group = VGroup(source, target)

    def rebuild(values: dict[str, float]) -> list[str]:
        a = min(1.0, max(0.0, values["split"]))
        box = src_box + (dst_box - src_box) * a
        for parts, origin, ink in ((source_parts, src_box, 1.0 - a), (target_parts, dst_box, a)):
            for member, base, fill, stroke in parts:
                member.points = L.map_box(base, origin, box)
                member.set_fill(opacity=fill * ink, family=False)
                member.set_stroke(opacity=stroke * ink, family=False)
        component.font_px = tokens.output_px(target_px if a >= 1.0 else source_px)
        return []

    component = _parametric(object_id, group, binding, rebuild, tokens.output_px(source_px))
    component.set_parameters()  # draw the state at the defaults
    return component


def stems(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """The four stems from the theta tags down to their boxes."""
    look = L.Look(tokens)
    group = L.stems(look)
    L.to_frame(group)
    return Component(object_id, "custom", group)


def pulse(scene, object_id, tokens, arguments, *, style_role=None, data=None, equation=None):
    """The pulse: a dot that runs from the stimulus box's right edge to the BOLD box's left edge as `travel` goes
    from 0 to 1, and a darkened copy of the stage box (fill `neutral`) under the contents of the stage the dot is in,
    as the original's updater darkened a module while |dot x - box x| < 1. The dot is above everything (z_index 3),
    the darkened box between a box and its contents (0.5)."""
    look = L.Look(tokens)
    _, binding = bound_columns(scene, data)
    scale = L.frame_scale()
    dot = look.dot(0.13)
    dark = L.rbox(look, 2.0).set_fill(look.color("neutral"), 1)
    L.to_frame(dot, dark)
    dot.move_to(np.zeros(3))
    dark.move_to(np.zeros(3))
    dot.set_z_index(3)
    dark.set_z_index(0.5)
    dot_parts, dark_parts = _points(dot), _points(dark)
    x0 = (L.XS[0] + L.WS[0] / 2) * scale
    x1 = (L.XS[6] - L.WS[6] / 2) * scale
    y = L.ROW * scale

    def rebuild(values: dict[str, float]) -> list[str]:
        x = x0 + (x1 - x0) * values["travel"]
        for member, base in dot_parts:
            member.points = base + np.array([x, y, 0.0])
        inside = [k for k in L.MODEL if abs(x - L.XS[k] * scale) < 1.0 * scale]
        for member, base in dark_parts:
            member.points = base + np.array([L.XS[inside[0]] * scale, y, 0.0]) if inside else EMPTY
        return []

    component = _parametric(object_id, VGroup(dark, dot), binding, rebuild, None)
    component.set_parameters()  # draw the state at the defaults
    return component


__all__ = [
    "bold_prediction",
    "funnel",
    "hull",
    "links",
    "loop",
    "model_outline",
    "pulse",
    "stage_box",
    "stems",
    "theta_split",
]
