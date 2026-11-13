# Grid search and refinement of a pRF fit (`grid_and_fit`)

A manim8 project of the population-receptive-fields talk: a Gaussian pRF fitted to one measured voxel, in two
stages. 20 s at 1280 by 720 and 30 fps (`animation.yaml`), rendered under `lecturekit_paper@0.1.0` and
`lecturekit_dark@0.1.0` with identical geometry, timing and frame count (600 frames). It plays through: no stops.

## What the clip shows

At the left, the visual field out to 4 deg (a circle) with a fixation cross, a 2 deg scale bar under it and the
heading of the stage that is running above it ("grid search", then "refinement"). The candidate field is a dot at
its centre with its one-sigma circle; its x, y and sigma are written out under the field. At the right, the
voxel's measured time course (label "measured voxel", axes "time (s)" and "BOLD (% signal change)") with the
candidate's predicted time course over it and the readout "R² = ..." at the top right.

Every candidate is a row of `data/candidates.csv`, in `seq` order, and its prediction is the matching column of
`data/timecourses.csv`. Four candidates hop slowly, then 48 quickly; the best grid candidate so far stays as a
dashed outline. The candidate lands on the best grid point (2, 1) deg, sigma 1 deg, R² 0.84. The heading changes
to "refinement", the outline goes, and the candidate slides in eleven small steps to the optimum, R² 0.86. The
line "fit: x 2.27°, y 0.99°, σ 0.85°, R² 0.86" fades in under the time course and the clip rests.

| Clip time | Rows | What happens |
| --- | --- | --- |
| 0 to 0.85 s | seq 0 | the style's reveal: every object fades in from an empty first frame |
| 1.4 to 5.6 s | seq 1 to 3 | phase `slow`: three hops of 0.9 s, each followed by a 0.5 s rest (seq 0 is shown from the start) |
| 5.6 to 10.4 s | seq 4 to 51 | phase `fast`: 48 hops of 0.1 s (3 frames), each with its own prediction and R² |
| 10.4 to 11.2 s | seq 52 | phase `grid_best`: the hop to the best grid point; rest to 11.8 s |
| 11.8 to 12.65 s | | "grid search" fades out, "refinement" fades in, the dashed outline fades out (0.85 s, the style's reveal time) |
| 12.7 to 16.55 s | seq 53 to 63 | phase `refine`: eleven hops of 0.35 s (10 or 11 frames) |
| 17.0 to 17.85 s | | the fit line fades in; rest to 20 s |

During a hop the centre, sigma, the readouts and the prediction move linearly between the two rows (with the
style's easing), as the original scene's trackers and `Transform` did; every hop ends on its row exactly, and the
rests show it.

Colours are palette roles present in both bridged styles: the measured trace, its label and the fit line in
`foreground`; the candidate, its prediction and the readouts in `primary_signal`; the headings, the dashed
outline, the fixation cross, the scale bar and the axes in `muted`; tick and axis labels in `secondary_text`; the
field outline in `hairline` (see below). No title, caption or equation is drawn beyond the labels the brief names.

## How it is built, and the rung on the ladder

The storyboard (`storyboard.yaml`, written by the three applied proposals in `proposals/applied/`) has one scene,
`fit` (pattern `linked_views`: one value, the candidate's position, drives the field and the time course), with
six objects, all `kind: custom` from `code/grid_fit.py`, and 65 registered actions.

| Object | Builder | Draws | Data |
| --- | --- | --- | --- |
| `visual_field` | `visual_field` | field circle (4 deg), fixation cross, 2 deg scale bar and its label | the brief's numbers |
| `time_course` | `time_course` | the measured trace in the original's axes box, thin axes, time ticks, both axis labels, "measured voxel"; never changes (constraint `measured_fixed`) | `timecourses`: `t_s`, `measured`, untransformed |
| `heading_grid`, `heading_refine` | `field_heading` | "grid search", "refinement", centred above the field | |
| `candidate_path` | `candidate_path` (a `ParametricComponent`) | candidate dot and circle, dashed best-so-far outline, x/y/σ readout, prediction, R² readout | `candidates`; `timecourses` columns `p00` to `p63` |
| `fit_line` | `panel_text` | the fit line, centred under the time axis | the constraint `final_values` |

| Actions | Kind | Target, parameter | Window |
| --- | --- | --- | --- |
| `hop_01` to `hop_63` | `vary_parameter` | `candidate_path.candidate`, n-1 to n | as in the table above; style easing |
| `kept_out` | `vary_parameter` | `candidate_path.retire_kept`, 0 to 1 | 11.8 to 12.65 s |
| `heading_out` | `fade_object` | `heading_grid` | 11.8 to 12.65 s |
| (reveal) | `reveal_at_seconds` | `heading_refine` at 11.8 s, `fit_line` at 17.0 s | the style's reveal, 0.85 s |

The two parameters of `candidate_path` are declared through its data binding, the only place a `kind: custom`
object can declare one in manim8 bad3ae1: each is the `window` of a `smooth` transform on `seq` with default 0,
which leaves the table as it is. The builder refuses any other transform and never applies a swept value as a
smoothing window.

**Rung R5 (builder objects), with the motion through registered actions (the parametric route).** What moves is
one `ParametricComponent` driven by registered `vary_parameter` actions, one per hop, so every candidate is an
action in the storyboard that names its row (`to: n`); the heading change and the reveals are registered too. No
custom action, pinned scene or kit scene was needed, so the clip keeps manim8's exact checkpoints, revisions,
proposals, lockfile and restyle by re-render. The builders read colours from palette roles and text from the
style's text roles; line weights and sizes are storyboard arguments in pixels at 1080p. Every mark and every text
anchor is a point of one mapping of the original scene into the safe area, never the extent of a text, so the
geometry does not depend on the font. Every rebuild is a pure function of the parameters, with no updaters.

Evidence for each builder (probe proposals validated with `scianim propose validate` and not applied, measured
renders, or the bridge's code):

- The candidate and its prediction, moving: no registered kind can step a prediction through the columns `p00`
  to `p63`. A `filter` whose value is a parameter is refused:
  `scenes.0.objects.7.data.transforms.0.filter.equals.float: Input should be a valid number` (and the same for
  string, integer and boolean); only `scale` and `smooth` take a parameter. A registered glyph cannot move:
  `action 'probe_move': target 'probe_glyph' is a receptive_field_glyph; vary_parameter needs one of
  ['function_image', 'function_plot', 'surface_plot'] or a data binding whose transforms name parameters`.
- The visual field: the registry has no circular field in degrees; `receptive_field_glyph` draws a square box with
  three tinted contours and tick labels (`components/schematic.py`).
- The headings: a `text_caption` sits only at an anchor of the safe area, or left-aligned below or beside an
  earlier object (`place` in `components/base.py`). The first checkpoints had them in the top-left corner, far from
  the field (applied proposal `prop_headings_over_field`); the original centres them just above it.
- The time course: the first storyboard drew it with the registered `scientific_plot` (and "measured voxel" with a
  small label builder, since its `data_label` is always set under the x axis in `secondary_text`). Its final
  renders put the axes box 1.21 px apart vertically and 0.28 px horizontally under the two styles (paper: left
  532.54 px, bottom 506.16 px; dark: 532.26 px, 504.95 px): the registry places a plot by the bounding box of its
  group, which holds the tick and axis labels, so the box follows the font (TeX Gyre Heros against Roboto). That
  breaks the rule of identical geometry, so the panel moved to `time_course` (applied proposal
  `prop_fixed_panel`). On the checkpoints the drawn pixels of the plot area of the two styles went from an overlap
  of 0.68 to 0.77 to 0.99 (intersection over union). It also brought the panel to the reference frame: muted axes,
  no value ticks, the label at the top left.
- The fit line: a `text_caption` placed `below` the panel would follow the panel's labels, and so the font, and be
  left-aligned where the original centres it.

*Gives up:* nothing of T (tokens), M (motion), C (checkpoints), R, P, L or Y; the builders are code the lecturer
reviews. *Needs sign-off on:* `code/grid_fit.py` and the data bindings (the storyboard proposal and
`prop_fixed_panel` are marked `touches_science`). *Way back:* the needs, in manim8's vocabulary: a plot whose shown
column is a parameter (or a transform that selects a column by a parameter), a plot placed by its axes box rather
than its labels, text placed "above, centred" on another object, and a circular field kind. When they exist, the
registered version can be written and compared with `scianim compare`.

## Snapshots

Snapshots at the timeline's moments, each at a rest or at the end of a hop so the still is an exact row; the
latest, `result`, is the study still. Frames are 0-based movie frames, the same in both final renders.

| Snapshot | Time | Frame | Shows |
| --- | --- | --- | --- |
| `layout` | 1.2 s | 36 | the layout fully revealed; seq 0 (x -1, y -3, σ 2, R² 0.00) |
| `slow_candidates` | 5.4 s | 162 | rest on seq 3 (x +1, y 0, σ 0.5, R² 0.33), also the best so far |
| `fast_grid` | 6.3 s | 189 | seq 10 (x -2, y -2, σ 2, R² 0.00); dashed outline on the best so far, seq 7 (x +1, y +1, σ 0.5, R² 0.47) |
| `grid_best` | 11.5 s | 345 | rest on seq 52, the best grid point (x +2, y +1, σ 1, R² 0.84) |
| `refinement` | 12.7 s | 381 | heading "refinement", outline gone, before the first refinement step |
| `optimum` | 16.8 s | 504 | rest on seq 63 (x +2.27, y +0.99, σ 0.85, R² 0.86), before the fit line |
| `result` | 19.9 s | 597 | the end state with the fit line (study still) |

## Data and provenance

- `data/candidates.csv` (source `candidates`, empirical): the 64 candidates in the order the clip shows them, with
  their phase: 4 slow, 48 fast, the best of a grid of 147 (7 by 7 centres from -3 to 3 deg, sizes 0.5, 1 and 2
  deg), 11 refinement steps. Fitted with prfmodel (`Gaussian2DPRFModel`; amplitude and baseline by least squares
  per candidate).
- `data/timecourses.csv` (source `timecourses`, empirical): column `measured` is one voxel of prfmodel's example
  dataset 7t-aot-visual, sub-003 (Knapen 2026, figshare, CC BY 4.0), in per cent signal change; columns `p00` to
  `p63` are the model's predictions for the candidates. The clip labels the time course "measured voxel" and
  leaves the prediction unlabelled (constraint `measured_label`).
- `references/original_scene.py` and `references/last_frame.jpg`: the hand-written scene of the Coimbra pRF
  workshop and its last frame, read for geometry, timing and the target layout. The panel's value range, -3.36 to
  8.07, is the original's (the measured minimum minus 0.5 to the maximum plus 0.5); its time range is 0 to 306 s.

## Checks made

- Every candidate, outside a render, with each job's style and tables: at `candidate = n` for n = 0 to 63 the
  circle's centre and radius equal row n (to 1e-6 deg), the prediction polyline equals column `p<n>` on `t_s` (to
  1e-6), the readouts are `x {x:+.2f}° y {y:+.2f}° σ {σ:.2f}°` and `R² = {r2:.2f}` of row n, and the dashed outline
  is the best of the grid phases reached so far (gone in refinement). The measured trace equals `measured` (to
  1e-14). 0 failures under each style; the field, the axes box and every text anchor are at the same pixel under
  both.
- Both final movies, on the pixels: at the frame each hop ends, the candidate's centre and radius found from the
  candidate ink in the field match the row within 0.06 deg (about 1 px), and the candidate ink in the plot lies on
  the predicted column (median distance at most 0.5 px); 64 of 64 candidates under each style, and 63 of 63 hops
  land on a new candidate.
- Both final renders: 600 frames, 20.000 s, 1280 by 720 at 30 fps, no warnings, no stops; the checkpoints on the
  same frames. `scianim inspect` on the paper render: no findings.

## Left for the lecturer

- **Sign-off.** The storyboard proposals add data bindings and are marked `touches_science`; the builders in
  `code/grid_fit.py` are code to review.
- **Field outline role.** `direction.prefer` names `grid` for the field outline, but `grid` is `#151515` on the
  dark page (about 1.1 to 1) and nearly invisible; the outline uses `hairline`, the role of the original's `HAIR`,
  present in both styles.
- **Label inks.** Tick and axis labels take `secondary_text` rather than the original's muted grey, so they read on
  the dark page (`muted` is about 3.5 to 1 there). The headings and the dashed outline keep `muted`, as the
  direction asks; on the dark page they are quiet but legible.
- **Frame 0.** manim8 reveals every object at a scene's start over the style's reveal time, so frame 0 is the page
  colour and the layout of the hard milestone `layout` (0 s) is complete at 0.85 s.
- **Heading change.** It takes the style's reveal time, 0.85 s (the original's took 0.5 s), so the refinement steps
  start at 12.7 s (timeline 12.3 s, tolerance 0.7 s) and the fit line at 17.0 s (timeline 16.7 s). The two headings
  cross-fade in place.
- **Rests.** `scianim validate` gives 251 warnings that the fast hops and the refinement steps follow one another
  without the style's 0.5 s rest; the timeline asks for about 0.1 s and 0.35 s steps, so they stand. It also warns
  that `linked_views` is realized with registered plots, not custom ones.
- **Time column.** `t_s` is the scan time truncated to whole seconds (the floor of 0.9 s times the sample index),
  so 34 pairs of samples share a second; the traces are drawn against `t_s` as given (a shift of at most 0.9 s,
  under 3 px). The citation says "340 s" for 340 samples that span 0 to 305 s.
- **Large candidates.** A sigma of 2 deg near the field's edge reaches outside the field and crosses the scale bar
  (seq 0 in `layout`), as in the original scene.
- **Inspector.** On a snapshot job `scianim inspect` reports `heading_grid` missing from 12.7 s on; it was faded out
  on purpose (`heading_out`), which the inspector does not follow there.
