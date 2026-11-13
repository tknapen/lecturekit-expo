# Plan: Population receptive fields, from stimulus to map

Slide list with planned minutes against the budget, `budget: 15` in the front matter of `slides.qmd`.
The build prints the same table from the `time=` attributes; keep them equal.

| # | Role | Min | Title (under 30 characters) | Visual (figure or clip, and its source) |
| --- | --- | --- | --- | --- |
| 1 | title | - | Population receptive fields, from stimulus to map | the title slide, from the front matter |
| 2 | concept | 3.5 | Stimulus and pRF predict BOLD | clip `stimulus_to_bold`; study still `traces_complete`; data simulated with prfmodel |
| 3 | concept | 3.5 | A model is a chain of stages | clip `model_as_chain`; study still `study`; data synthetic |
| 4 | example | 4 | Grid search, then refinement | clip `grid_and_fit`; study still `result`; one measured voxel (7t-aot-visual, CC BY 4.0) |
| 5 | concept | 4 | A map from independent fits | clip `fields_to_map`; study strip `eccentricity` and `end`; data simulated |
| 6 | explanation | - | References | `references.bib`: prfmodel, 7t-aot-visual |

Total: 15 of 15 minutes. The four titles are drafts of the claims the briefs make, for the lecturer to review.

## Clips

All four are manim8 projects in `clips/families/population_receptive_fields/`, rendered by `lk clips` (paper) and
`lk clips --mode dark` into `assets/clips/` and `assets/clips/dark/`, 1280 by 720 at 30 fps, in the bridged styles
`lecturekit_paper@0.1.0` and `lecturekit_dark@0.1.0`. Each project's `README.md` has the evidence for its rung.

| Clip | Length | Frames | Rung | Kinds and motion | Stops |
| --- | --- | --- | --- | --- | --- |
| `stimulus_to_bold` | 12 s | 360 | R5 builder objects | 4 `custom` objects (4 builders); one `ParametricComponent` driven by three registered `vary_parameter` actions (the parametric route) | none |
| `model_as_chain` | 15.5 s | 465 | R5 builder objects | 16 `custom` objects (10 builders); seven `vary_parameter` and one `fade_object`, all registered | none |
| `grid_and_fit` | 20 s | 600 | R5 builder objects | 6 `custom` objects (5 builders); 64 registered `vary_parameter` (63 hops and the kept outline's removal) and one `fade_object` | none |
| `fields_to_map` | 18 s | 540 | R5 builder objects | 2 `custom` objects (2 builders) and 4 `text_caption`; two registered `vary_parameter` and one `fade_object` | `eccentricity`, 12.9 s, frame 387 (`stop: true`), not held on the slide yet |

No clip needed a custom action, a pinned scene or a kit scene (R6 to R8), so `anim/` holds no clip. The parametric
route declares each builder's parameters through a zero-window data transform, the workaround the escalation plan
calls fragile; it is recorded in each project's README.

## Decisions

- The lecturer's decisions of 13 November 2026 (`SESSION.md`): a new project with a talk deck, one clip per slide;
  1280 by 720 at 30 fps; the two bridged styles; the only key-press stop is `fields_to_map`'s hold at 12.9 s.
- The hold is not on the slide yet. lecturekit 0.4.0 measures 0 frames of unchanged picture before it (the stop's
  frame is a fresh keyframe whose re-coding differs from the still frames before it by 7 to 8 grey levels, against a
  tolerance of 6; `README.md`, log), and the build refuses a stop with fewer than 3. The slide plays the clip through,
  the presenter pauses it with Space at 12.9 s for the prompt, and the study PDF prints the stop's frame and the end
  (`study="eccentricity end"`). When the engine accepts the stop, the slide becomes
  `::: {.movie clip="fields_to_map" stops="eccentricity" study=strip}` with the prompt in `:::: {.stop ref="eccentricity"}`,
  and `time=` stays 4 (18 s of clip and one prompt).
- No goals or takeaways slide: the deck is a talk in four clips, as asked. Nothing was moved to study-only pages.
- Open: the four titles; the dataset's figshare DOI for `references.bib`; the clips' builder code and storyboard
  proposals, which need the lecturer's scientific sign-off in manim8.
