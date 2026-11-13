# Plan: Population receptive fields, from stimulus to map

Slide list with planned minutes against the budget, `budget: 15` in the front matter of `slides.qmd`.
The build prints the same table from the `time=` attributes; keep them equal.

| # | Role | Min | Title (under 30 characters) | Visual (figure or clip, and its source) |
| --- | --- | --- | --- | --- |
| 1 | title | - | Population receptive fields, from stimulus to map | the title slide, from the front matter |
| 2 | concept | 3.5 | Stimulus and pRF predict BOLD | clip `stimulus_to_bold`; study still `traces_complete`; data simulated with prfmodel |
| 3 | concept | 3.5 | A model is a chain of stages | clip `model_as_chain`; study still `study`; data synthetic |
| 4 | example | 4 | Fits keep the best candidate | clip `grid_and_fit`; study still `result`; one measured voxel (7t-aot-visual, CC BY 4.0) |
| 5 | concept | 4 | Independent fits make a map | clip `fields_to_map`; study strip `eccentricity` and `end`; data simulated |
| 6 | explanation | - | References | `references.bib`: prfmodel, 7t-aot-visual |

Total: 15 of 15 minutes. The four titles are drafts of the claims the briefs make, for the lecturer to review.

## Clips

All four are manim8 projects in `clips/families/population_receptive_fields/`, rendered by `lk clips` (paper) and
`lk clips --mode dark` into `assets/clips/` and `assets/clips/dark/`, 1280 by 720 at 30 fps, in the bridged styles
`lecturekit_paper@0.1.0` and `lecturekit_dark@0.1.1` (the dark style's quiet roles lifted after review; README.md,
log). Each project's `README.md` has the evidence for its rung.

| Clip | Length | Frames | Rung | Kinds and motion | Stops |
| --- | --- | --- | --- | --- | --- |
| `stimulus_to_bold` | 12 s | 360 | R5 builder objects | 4 `custom` objects (4 builders); one `ParametricComponent` driven by three registered `vary_parameter` actions (the parametric route); the project override `motion.reveal_seconds: 0.1` | none |
| `model_as_chain` | 15.5 s | 465 | R5 builder objects | 16 `custom` objects (10 builders); seven `vary_parameter` and one `fade_object`, all registered | none |
| `grid_and_fit` | 20 s | 600 | R5 builder objects | 6 `custom` objects (5 builders); 64 registered `vary_parameter` (63 hops and the kept outline's removal) and one `fade_object` | none |
| `fields_to_map` | 18 s | 540 | R5 builder objects | 2 `custom` objects (2 builders) and 4 `text_caption`; two registered `vary_parameter` and one `fade_object` | `eccentricity`, 12.9 s, frame 387 (`stop: true`), held on slide 5 |

No clip needed a custom action, a pinned scene or a kit scene (R6 to R8), so `anim/` holds no clip. The parametric
route declares each builder's parameters through a zero-window data transform, the workaround the escalation plan
calls fragile; it is recorded in each project's README.

## Decisions

- The lecturer's decisions of 13 November 2026, answers to the session's questions (`SESSION.md`): a new project
  with a talk deck, one clip per slide; 1280 by 720 at 30 fps; the only key-press stop is `fields_to_map`'s hold at
  12.9 s. The session's own, open for the lecturer to confirm: the two bridged styles.
- The hold is on slide 5: `::: {.movie clip="fields_to_map" stops="eccentricity" study=strip}`, with the prompt in
  `:::: {.stop ref="eccentricity"}`; `time=` stays 4 (18 s of clip and one prompt). lecturekit 0.4.0 refused it: the
  stop's frame is a fresh keyframe whose re-coding differed from the still frames before it by 7 to 8 grey levels at
  160 px, against a tolerance of 6, so it measured 0 frames of rest. lecturekit 0.4.1 sets that tolerance at 16, from
  the keyframes of the expo's and the feature deck's manim8 clips (README.md, log), and measures 47 frames of rest
  before the stop in paper and 46 in dark. `lk review frags` holds frame 387 in both presets, pausing two frames
  early, inside the rest.
- No goals or takeaways slide: the deck is a talk in four clips, as asked. Nothing was moved to study-only pages.
- Open for the lecturer:
  - the four titles, drafts of the briefs' claims (slides 4 and 5 redrafted after review: they were "Grid search,
    then refinement" and "A map from independent fits", which name stages rather than state claims); and the deck's
    title, which sets on three lines on the paper title page with "MAP" alone (`lk review shoot` flags slide 1 in
    both presets): a title that breaks into two balanced lines of about 20 capitals is wanted;
  - the one decision the session took without asking (`SESSION.md`): the two bridged styles;
  - the hard milestones at 0 s, which no clip meets (frame 0 is the empty page; README.md, log): accept the
    deviation, or wait for manim8 to allow an object present from the first frame;
  - `model_as_chain`: the BOLD box shows the prediction from 5.5 s and loses it in one frame when the pulse starts
    (9.3 s), as `references/original_scene.py` does, where the brief puts the prediction last. Moving the action
    `clear_bold_prediction` from 9.3 s to 5.5 s would keep the box to the data until `draw_prediction` at 12.5 s;
    it departs from the original scene, so it waits for the lecturer;
  - `model_as_chain`: the HRF glyph is a canonical two-gamma shape (shapes 6 and 16, undershoot at a sixth) that the
    builder drew without data, since `original_layout.py` took it from `l2model`, not in the bundle. Either the
    lecturer accepts it as an illustrative, non-data glyph, or the lecture's kernel goes into `data/` as a column
    and the glyph draws it;
  - the dark style `lecturekit_dark@0.1.1` (manim8: a style change is a new version the person accepts), and the
    one dark weakness it does not reach: the `selection` fill of `model_as_chain`'s boxes and funnel is 1.08:1 on
    black, because the bridge mixes it as 8 per cent of `input` over the page in both presets;
  - the dataset's figshare DOI for `references.bib`;
  - the clips' builder code and storyboard proposals, which need the lecturer's scientific sign-off in manim8.
