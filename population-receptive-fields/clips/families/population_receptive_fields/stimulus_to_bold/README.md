# From stimulus to predicted BOLD signal (`stimulus_to_bold`)

A manim8 project of the population-receptive-fields talk: one voxel, one bar-mapping run, one cursor. 12 s at
1280 by 720 and 30 fps (`animation.yaml`), rendered under `lecturekit_paper@0.1.0` and `lecturekit_dark@0.1.0`
with identical geometry, timing and frame count. It plays through: no stops.

## What the clip shows

At the left, the visual field (a circle of radius 8 deg) with a fixation cross and the voxel's pRF as its
one-sigma circle at (2.5, 1.5) deg, radius 1 deg. At the right, three rows on one time axis, 0 to 300 s: the
stimulus as a strip of eight sweep bands (two sweeps, a 15 s blank, four times), each with an arrow for the
bar's direction; the predicted neural response (axis -0.05 to 0.75); the predicted BOLD response (axis -0.3 to
0.9). After the layout has appeared, one cursor runs through the run at constant speed: the bar moves in the
field, both traces are drawn up to the cursor and a dot rides each. The neural trace rises each time the bar
crosses the pRF; the BOLD trace follows about 5 s later, smoother, and dips below zero after each pair of
sweeps. The cursor fades at the end and the clip rests on the complete traces.

| Clip time | Run time | What happens |
| --- | --- | --- |
| 0 to 0.85 s | | the style's reveal: every object fades in from an empty first frame |
| 0.85 to 1.0 s | | rest on the layout |
| 1.0 s | 0 s | the clock starts; the bar, the cursor and the dots fade in over 0.2 s |
| 1.0 to 11.0 s | 0 to 300 s | the run at constant speed, one second of the run per frame |
| 11.0 to 11.35 s | 300 s | the cursor and its dots fade |
| 11.35 to 12.0 s | | rest on the complete traces |

The labels are the ones the brief names: "stimulus", "predicted neural", "predicted BOLD", the tick values and
"time (s)". No title, caption or equation is drawn; the page carries them (constraint `equations_not_drawn`).

## How it is built, and the rung on the ladder

The storyboard (`storyboard.yaml`, written by the applied proposals under `proposals/applied/`) has one scene,
`one_run`, with four objects of `kind: custom` and three registered `vary_parameter` actions.

| Object | Builder (`code/stim_bold.py`) | Draws | Data |
| --- | --- | --- | --- |
| `visual_field` | `visual_field` | field circle, pRF circle, fixation cross; never rebuilt (constraint `prf_fixed`) | the spec's numbers |
| `response_rows` | `response_rows` | both rows' value axes, ticks, zero lines and labels; the time axis | the spec's ranges |
| `stimulus_strip` | `stimulus_strip` | a band per sweep with its arrow, the "stimulus" label | source `run` |
| `run` | `run` | the bar in the field, both traces up to the cursor, the cursor, the two dots | source `run` |

| Action | Target, parameter | Window | Easing |
| --- | --- | --- | --- |
| `clock` | `run.t`, 0 to 300 (seconds of the run) | 1.0 to 11.0 s | linear (constraint `one_clock`) |
| `marks_on` | `run.marks`, 0 to 1 | 1.0 to 1.2 s | the style's |
| `marks_off` | `run.marks`, 1 to 0 | 11.0 to 11.35 s | the style's |

**Rung R5 (builder objects), with the motion through a registered action.** Everything the clock moves is one
`ParametricComponent`, so the bar, both traces, the cursor and its dots share one clock by construction, driven
by one registered `vary_parameter`. No custom action, pinned scene or kit scene was needed, so the clip keeps
manim8's checkpoints, revisions, proposals, lockfile and restyle by re-render.

Evidence for the climb from R4 (registered kinds only), quoted from `scianim propose validate` on probe storyboards:

- a trace cut at a swept time through a registered `scientific_plot` (a `filter` on `t_s` whose value is a
  parameter): refused, `scenes.0.objects.0.data.transforms.0.filter.equals.float: Input should be a valid number`
  (and the same for string, integer and boolean);
- sweeping a `scientific_plot` of the table without a parameterised transform: refused, `action 'clock': target
  'neural_trace' is a scientific_plot; vary_parameter needs one of ['function_image', 'function_plot',
  'surface_plot'] or a data binding whose transforms name parameters`. The transforms that take a parameter are
  `scale` and `smooth`, which change the values, and constraint `data_exact` forbids that;
- registry 0.5.0 (`scianim registry`) has no kind for an aperture in a visual field, a strip of sweep bands with
  arrows, or rows on a shared time axis with their own scales.

How `run` takes its parameters: manim8 bad3ae1 lets a `kind: custom` object declare a parameter only through its
data binding (the route section 4.2 of lecturekit's animation-integration plan calls undocumented). The binding
of `run` therefore carries two `smooth` transforms of `t_s` whose `window` is a parameter with default 0 (`t` and
`marks`), which leave the table as it is. The builder refuses any other transform, checks that the binding at
its defaults equals the raw table, and never uses a swept value as a smoothing window.

The price, in three lines:

- *gives up*: nothing of T, M, C, R or Y; line weights and the cursor's opacity are object arguments (from the
  original scene) rather than style tokens; the binding carries two declaring transforms that read as smoothing;
- *needs sign-off on*: the code in `code/stim_bold.py`, the claims in `proposals/applied/prop_storyboard.yaml`;
  no stops;
- *way back*: no revision exists yet; the climb is undone when manim8 has declared builder parameters (plan 4.4,
  phase 3), a data-bound trace that draws up to a swept time, and an aperture kind for a visual field.

Patterns named: `let_time_run` and `linked_views` (one clock driving the field and the traces).

## Colour and type

Colour by palette role only, every role present in both bridged styles, as `direction.prefer` asks: pRF circle,
labels and arrows in `foreground`; traces and dots in `primary_signal`; bar and sweep bands in `neutral`; axes,
ticks, the fixation cross, the cursor and "time (s)" in `muted`; zero lines in `grid`; the field's edge in
`hairline` (the original scene's colour for it) over a `background` fill. Text takes the styles' roles:
`axis_label` for the row labels and "time (s)", `tick_label` for the ticks. The dots take the style's rim.

Geometry follows `references/original_scene.py` in its 16 by 9 scene units, scaled as one piece into the
style's safe area (both styles inherit the same margin), so the field, rows, bands and traces sit where the
original put them relative to each other; an overlay on `references/last_frame.jpg` at matched scale shows the
field, pRF, fixation, bands, arrows, traces and axes on top of the original's. Line weights and mark sizes,
in pixels at 1080p, are the original's: field edge and pRF 3.6, fixation 3.1, axes 1.9, zero lines 2.4,
arrows 3.2, cursor 2.4 at opacity 0.6, neural trace 4.8, BOLD trace 7.2, dot radius 9.

## Snapshots

| Id | Clip time | Frame | Run time | Shows |
| --- | --- | --- | --- | --- |
| `layout` | 1.0 s | 30 | 0 s | the layout, before the clock starts (timeline `layout`) |
| `run_starts` | 1.2 s | 36 | 6 s | cursor started, bar entering, dots at zero (timeline `run_starts`) |
| `bar_on_prf` | 1.6 s | 48 | 18 s | bar on the pRF, neural near its first peak, BOLD barely risen |
| `bold_follows` | 1.8 s | 54 | 24 s | neural back near zero, BOLD at its first peak (0.80) |
| `first_blank` | 3.0 s | 90 | 60 s | the first blank: no bar, BOLD below zero after its second peak |
| `diagonal_crossing` | 6.6 s | 198 | 168 s | the 45 deg bar on the pRF, the fifth neural rise |
| `run_ends` | 11.0 s | 330 | 300 s | cursor at the end, before it fades (timeline `run_ends`) |
| `traces_complete` | 11.9 s | 357 | | the end state and study still |

## Data and provenance

`data/run.csv`, source `run`: one row per second (t_s 0 to 299), bar centre and direction (empty in the four
blanks), neural and bold. Its citation: simulated with prfmodel (Gaussian2DPRFModel, two-gamma HRF) for a pRF at
(2.5, 1.5) deg, sigma 1 deg, on a 300 s bar run; not a measurement. The clip calls both traces predicted
(constraint `prediction_not_measurement`). The pRF's centre and size, the field's radius, the bar's width and
the rows' ranges are the spec's (`animation.yaml`: equations, constraints, citation). Nothing else is drawn.

Between two rows of a sweep the bar centre moves linearly to the next row's value, and a sweep is a run of rows
with one direction and a rising centre, as the original scene's `bar_at` and `sweeps` do.

## Checks made

- `scianim validate .`: valid, 0 errors, 4 warnings, all accepted: the clock is linear (constraint `one_clock`
  and `direction.avoid` ask for it); `marks_off` starts as the clock ends (the timeline says the cursor reaches
  300 s and fades; the style asks for 0.5 s, which the 12 s clip would take from the final rest); the two
  patterns are staged by a custom builder, not by their registered components.
- `scianim inspect` on the final snapshots and videos under both styles: no findings.
- The builders against the table, every frame of the clock, under both styles: every drawn vertex of both traces
  lies on the CSV's linear interpolation (largest difference 1e-14), every sample up to the cursor is a vertex,
  nothing is drawn beyond the cursor; dots on the trace at the cursor; cursor at the clock; the bar 2 deg wide
  along its direction, within the 8 deg field, absent in every blank row; the pRF circle at (2.5, 1.5) deg,
  radius 1 deg; the eight sweeps (0 to 30, 30 to 60, 75 to 105, 105 to 135, 150 to 180, 180 to 210, 225 to 255,
  255 to 285 s at 0, 180, 90, 270, 45, 225, 135, 315 deg). The drawn geometry of all four objects is identical
  under both styles (text positions differ by under 0.03 scene units, from the two styles' fonts).
- The final videos, decoded: 360 frames, 12.000 s, 30 fps under both styles; the cursor moves 2.65 px per frame
  (one run second), within 0.65 px of a straight line; every CSV sample of both traces lies within 1.2 px of a
  trace pixel in the last frame; no cursor after 11.35 s; no bar in blank frames.

## Left for the lecturer

- Frame 0 is empty and the layout is complete at 0.85 s, because the styles reveal every object over 0.85 s; the
  timeline's hard milestone `layout` sits at 0 s and the original shows the layout from its first frame. A
  project override `motion.reveal_seconds` in `animation.yaml` (an allowed one) would shorten the fade; the
  `layout` snapshot sits at 1.0 s, when the clock starts. The run therefore starts at 1.0 s and ends at 11.0 s
  (timeline 0.75 s and 10.75 s, within their tolerances).
- The row labels read "predicted neural" and "predicted BOLD", where the original reads "neural" and "BOLD",
  because constraint `prediction_not_measurement` asks any label to call the traces predicted.
- Text is about three quarters of the original's size relative to the drawing: the styles' text roles (axis
  label 30 px, tick label 26 px at 1080p, from `default@0.5.0`) are smaller than the original scene's type. A
  larger size would be a new style version for all clips, not a change here.
- The zero lines are in `grid`, as `direction.prefer` asks; under `lecturekit_dark@0.1.0` that is #151515 on a
  black page, and the lines are only just visible. `hairline` (the original's colour) would show them better.
- The cursor's fade is 0.35 s (0.4 s in the original), so that it ends before the style's closing 0.65 s.

## Reproduce

```sh
scianim validate .
scianim codegen .
scianim snapshot . --all --profile final --style lecturekit_paper@0.1.0
scianim snapshot . --all --profile final --style lecturekit_dark@0.1.0
scianim render . --profile final --style lecturekit_paper@0.1.0
scianim render . --profile final --style lecturekit_dark@0.1.0
```
