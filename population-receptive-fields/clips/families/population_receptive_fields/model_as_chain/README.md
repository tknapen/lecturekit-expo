# model_as_chain: the model as a chain of stages

A manim8 clip of 15.5 s at 1280 by 720 and 30 fps, rendered under the bridged styles `lecturekit_paper@0.1.0`
and `lecturekit_dark@0.1.1` (`lecturekit_dark@0.1.0` before the review lifted its quiet roles). It plays through: no stop.

## What the clip shows

The loop of computational modelling opens its model box into the chain of stages that a pRF model is, the
fitted parameters land on the stages they belong to, and one pulse runs from the stimulus to the predicted BOLD.
Beats and times follow the original scene (`references/original_scene.py`), positions and sizes its layout
(`references/original_layout.py`):

| Time (s) | What happens |
| --- | --- |
| 0 to 0.85 | The loop fades in: 'parameters θ' and 'stimulus' above the 'model' box with its gear, arrows into it, and below it a panel with the prediction on the data. |
| 0.4 to 1.2 | Two dots run the curved arrows into the model while the gear turns a quarter. |
| 1.2 to 1.8 | A third dot runs from the model down to the panel. |
| 2.6 to 3.9 | The loop shrinks to 45 per cent and moves to the top centre, where it stays. |
| 3.9 | The model box gets a heavier outline, and a light funnel opens down to a dashed outline. |
| 4.9 to 6.35 | The seven boxes fade in left to right: stimulus S, features Φ(S), spatial pooling, transformation f, neural dynamics, HRF, BOLD. The dashed outline holds boxes two to six. |
| 6.4 | The arrows between the boxes fade in. |
| 7.3 to 8.3 | A copy of the θ box drops and splits into four θ tags over spatial pooling, transformation, neural dynamics and HRF. |
| 8.3 | The stems join the tags to their boxes; the pulse dot appears at the stimulus box's right edge. |
| 9.3 to 12.5 | The pulse runs at constant speed to the BOLD box's left edge; each stage darkens while the dot is inside it. As in the original, the BOLD box's prediction is taken away when the pulse starts. |
| 12.5 to 13.7 | The pulse fades and the prediction is drawn over the data in the BOLD box; the picture holds to the end. |

## How it is built: the escalation ladder

Rung reached: **R5, builder objects**, with their motion driven by registered actions through the parametric
route. Nothing above it: no `custom_action`, no pinned scene, no kit scene.

- Registered component kinds used: none. Every object is `kind: custom`, because no registered kind can draw what
  the clip is made of (refusals below).
- Registered actions used: the reveal (`reveal_at_seconds`) for every object, `vary_parameter` for seven motions,
  and one `fade_object` (the pulse fading at 12.5 s).
- Custom builders, all in this project's `code/` (none in the family's `components/`):
  - `code/chain_layout.py`: the geometry, drawn in the original's units (a frame 9 high) and brought into
    manim8's frame (8 high) with points and strokes scaled alike; colours by palette role; labels in the style's
    faces at the cap height the original had.
  - `code/chain_builders.py`: one function per object.

| Object | Builder | Kind of builder | What it draws |
| --- | --- | --- | --- |
| `modelling_loop` | `loop` | parametric: `feed`, `emit`, `shrink` | the loop, its three dots, the gear's quarter turn, the shrink to 45 per cent |
| `funnel` | `funnel` | static | the light funnel from the shrunken model box to the dashed outline, behind everything |
| `model_hull` | `hull` | static | the dashed outline round boxes two to six |
| `model_outline` | `model_outline` | static | the heavier outline of the shrunken model box (stroke 5 over 3), faded in |
| `box_stimulus` to `box_bold` | `stage_box` (`stage` 0 to 6) | static | one box with its label and glyph |
| `bold_prediction` | `bold_prediction` | parametric: `drawn` | the prediction in the BOLD box, drawn from its start |
| `links` | `links` | static | the six arrows between the boxes |
| `theta_split` | `theta_split` | parametric: `split` | the θ box copy that splits into the four tags (the original's FadeTransform) |
| `theta_stems` | `stems` | static | the four stems |
| `pulse` | `pulse` | parametric: `travel` | the pulse dot and the darkened copy of the stage it is in |

Why each climb was needed, with the validator's own words (each probe was a copy of the storyboard checked with
`scianim validate <file>`; the probes are not kept in the project):

- A label or a glyph at a given place: registered text and plot kinds are placed only at the nine safe-area
  anchors or below and beside one another. A caption at a point inside a box:
  `object 'box_features': invalid params for kind 'text_caption': position: Extra inputs are not permitted`.
- The loop's shrink: `move_object` translates, it does not scale:
  `scenes.0.actions.2.move_object.scale: Extra inputs are not permitted`.
- The gear's quarter turn: there is no rotation action:
  `Input tag 'rotate_object' found using 'kind' does not match any of the expected tags: 'vary_parameter',
  'orbit_camera', 'fade_axes', 'move_object', 'fade_object', 'transform_equation', 'emphasize'`.
- Dots along curved arrows, a box that splits into four, the darkening that follows the pulse: none is a
  registered action. Doing the darkening with fades of five overlay objects would keep ten absolute times in sync
  with the dot by hand, and a reveal takes 0.85 s while the dot crosses a box in 0.44 s; the ladder counts that as
  a fragile workaround. So these motions are parameters of builders that `vary_parameter` drives.
- `vary_parameter` on a custom object without a data binding:
  `action 'feed_loop': target 'modelling_loop' is a custom; vary_parameter needs one of ['function_image',
  'function_plot', 'surface_plot'] or a data binding whose transforms name parameters`.
  The four parametric objects therefore carry a binding to `panel` whose transforms name their parameters and are
  the identity at the defaults: `smooth` with window 0 (`feed`, `emit`, `shrink`, `split`, `travel`) and `scale`
  by 1 (`drawn`, on the `data` column, which `bold_prediction` does not draw). The builders read the bound columns
  with the transforms at those defaults, that is unchanged, and use the parameters for geometry only. This is the
  dummy-binding route the integration plan calls fragile (`docs/plans/animation-integration.md`, 4.2, R5); it is
  the only way manim8 bad3ae1 lets a builder move under a registered action.

The price, in three lines:

- Gives up: little of T and Y (colours and faces come from the style's roles, so the dark style re-renders it;
  sizes and stroke widths are the original's, not the style's tokens), part of M (the actions ease by the style,
  but what a parameter does to the picture is code), and the regeneration of the picture from YAML (the glyphs
  and the motions' geometry live in reviewed code).
- Needs sign-off on: the builders' code in `code/`, the data bindings, and the uncertainties below.
- Way back: none needed to a lower rung of this clip; it would come down when manim8 has a builder `parameters`
  contract (a declared parameter without a dummy binding), a rotation or scale action and a stroke-drawing reveal.

Every rebuild is a pure function of its parameters: it sets points (and, for the split, the inks of the two
halves of the cross-fade) from copies taken at build time, adds and removes no member and installs no updater, so
every checkpoint is exact (`fidelity: exact` in every manifest).

## Colours

Palette roles present in both bridged styles, never a value:

| Role | Used for |
| --- | --- |
| `foreground` | box outlines, labels, arrows, stems, the data traces, the HRF glyph, the dots |
| `selection` | the faint fill of every box and of the funnel |
| `neutral` | the stage the pulse is in (the original's ink at 28 per cent), the stimulus bar (ink at 20 per cent) |
| `background` | the fill of the θ tags, the gear's hub and the visual field |
| `hairline` | the panels' baselines, the visual field's outline |
| `muted` | the dashed outline, the fixation cross |
| `primary_signal` | the prediction (loop panel and BOLD box) and the Gaussian in the pooling box, nowhere else |

## Snapshots

| Id | s | Frame | Shows |
| --- | --- | --- | --- |
| `dots_travel` | 0.9 | 27 | the loop, two dots on the arrows, the gear turning (the `loop` milestone at 0 s, once the loop has faded in) |
| `loop` | 2.0 | 60 | the loop at rest after the dots (the original's first keyframe) |
| `shrink` | 3.9 | 117 | the loop shrunk to 45 per cent at the top centre |
| `open` | 7.3 | 219 | outline, funnel, dashed outline, seven boxes and arrows |
| `tags` | 8.3 | 249 | the four θ tags |
| `pulse` | 9.3 | 279 | stems in; the pulse at the stimulus box; the BOLD box still with its prediction |
| `pulse_in_transformation` | 10.9 | 327 | the pulse inside the transformation box, darkened |
| `prediction` | 12.5 | 375 | the pulse at the BOLD box; the prediction about to be drawn |
| `drawing` | 13.1 | 393 | the prediction half drawn |
| `study` | 15.4 | 462 | the end state, the study still and the website's poster |

The original's keyframe at 10.6 s falls between the pooling and transformation boxes, where no stage is dark;
`pulse_in_transformation` at 10.9 s shows the darkening instead.

## Data and provenance

- `data/panel.csv` (source `panel`, `illustrative_data`): 150 rows, `t_s` 0 to 149, `prediction` (the Gaussian
  pRF voxel's predicted BOLD for the first 150 s of the bar run, normalised to a peak of 1) and `data` (the same
  plus Gaussian noise of SD 0.12, seed 20261106). Synthetic: simulated, not a measurement. The clip's labels make
  no claim about it.
- The loop's panel draws both columns on the original's frame (u over 0 to 150, w over -0.5 to 1.35); the BOLD
  box draws `data` (`box_bold`) and `prediction` (`bold_prediction`) on the original's smaller frame.
- The HRF glyph is not data: a schematic of the canonical two-gamma shape (see below).

## Checks

- `scianim validate .`: valid, 0 errors, 3 warnings, each kept on purpose: `run_pulse` is linear (the brief asks
  for constant speed); `emit_prediction` starts as `feed_loop` ends (the original chains the three dots, the
  output leaving as the inputs arrive); the scene names `reveal_in_reading_order`, whose registered components the
  clip does not use (custom builders stage it).
- Hard constraints, checked on the builders' geometry at the end state under both styles: the loop's two traces
  and the BOLD box's two traces have 150 points each and are the CSV columns up to an axis-aligned scale and shift
  (largest residual 3e-15 scene units); seven boxes left to right with the labels of `stage_order`; the dashed
  outline holds boxes two to six exactly; four θ tags, centred over boxes three to six, and four stems; the loop
  at 0.45 of its width, centred at (0, 1.88) in the original's units; `primary_signal` on the loop's prediction,
  the Gaussian and the BOLD prediction only.
- Final renders, `--profile final` under each style: 1280 by 720, 30 fps, 465 frames decoded, 15.5 s, no stop,
  no warning; the 37 plays have the same start times and frame counts under both styles, and every checkpoint the
  same frame.
- Layout warnings, as in the target frame: the stimulus and BOLD boxes reach past the style's 6 per cent safe
  margin (the row spans the frame, as in `last_frame.jpg`), and the shrunken loop's labels are 22.8 px at 1080p
  against the style's minimum of 26.
- The end state matches `references/last_frame.jpg` in layout and sizes to about a pixel at the reference's
  scale; it differs in the fill (a faint `selection` tint where the original had grey) and in the HRF glyph's
  curve.

## Left for the lecturer

- The brief names a glyph in every box (a filter bank, a curve, a decaying response among them), but
  `original_layout.py` and `last_frame.jpg` draw glyphs in four boxes only and words alone in features,
  transformation and neural dynamics. The clip follows the layout and the frame. Three more glyphs need the
  lecturer to say what they show: a curve for f would claim a particular nonlinearity.
- The HRF glyph: the original computed it with `l2model.hrf`, which is not in the bundle. It is the canonical
  two-gamma shape (gamma shapes 6 and 16, undershoot at a sixth), normalised, with no axis or value. Replace it
  with the lecture's kernel if that matters, as a column in `data/`.
- The BOLD box shows the prediction from 5.5 s until the pulse starts, then loses it in one frame, as the original
  did. The lecturer may prefer the BOLD box to hold the data alone until the prediction is drawn.
- manim8 fades every object in over the style's reveal (0.85 s), so frame 0 is blank and the loop is complete at
  0.85 s; the original showed the loop from frame 0. The dots still start at 0.4 s, while the loop is half faded
  in. The timeline's milestone `loop` is hard, at 0 s with tolerance 0. This misses a hard milestone, and manim8 bad3ae1 cannot meet it: every object gets a reveal from alpha 0 at the scene start (`src/scianim/codegen/generate.py`: `begins = scene.start_seconds if obj.reveal_at_seconds is None ...`) and `motion.reveal_seconds` must be greater than 0 (`scianim_core/style.py`: `reveal_seconds: float = Field(gt=0)`). It is a deviation that waits on the lecturer's decision (the deck's README, log). The 0.85 s stays
  here: the row's boxes, the arrows and the tags are later reveals of the same length.
- Arrows, the dashed outline and the stems fade in where the original drew them along their length; the boxes
  fade in without the original's slight growth; the dots carry the style's rim of the page colour.
- On the dark style the stimulus bar and the stage that the pulse is in (`neutral`) and the visual field's outline
  (`hairline`) were faint on black under `lecturekit_dark@0.1.0` (1.46 to 1); `lecturekit_dark@0.1.1` lifts them to
  2.6 to 1. The box fill and the funnel (`selection`) stay barely above black (1.08 to 1), because the bridge mixes
  `selection` as 8 per cent of `input` over the page in both presets; the funnel that constraint `loop_stays` asks
  for is therefore hard to see on a dark projector. Lifting it needs the bridge (lecturekit) or the lecturer's
  choice of another role (`direction.prefer` names `selection` or `neutral` for the box fill).
- The storyboard proposal is marked as touching science (it declares data bindings): it needs the lecturer's
  sign-off, as does the builders' code.

## Files and commands

- `animation.yaml` (given), `storyboard.yaml` (written by `scianim propose apply . proposals/prop_create_storyboard.yaml`;
  the record is `proposals/applied/prop_create_storyboard.yaml`), `code/chain_layout.py`, `code/chain_builders.py`,
  `code/scene_model_as_chain.py` (generated by `scianim codegen .`; do not edit).
- Review: `scianim snapshot . --all --style lecturekit_paper@0.1.0` (and `lecturekit_dark@0.1.1`).
- Render: `scianim render . --profile final --style lecturekit_paper@0.1.0` (and `lecturekit_dark@0.1.1`);
  `lk clips` does this for the deck.
