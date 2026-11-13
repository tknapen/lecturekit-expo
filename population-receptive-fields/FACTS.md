# Facts: Population receptive fields, from stimulus to map

Every number, date and claim on a slide, with its source and the date it was checked. A claim that is not here is not on a slide.

Paths are under `clips/families/population_receptive_fields/`. "Seed" is the lecturer's `animation.yaml` of that clip
(its sources' citations, its scientific constraints and its timeline) and its `references/brief.md`, both unchanged.

| Claim | Slide | Source (page, table, figure) | Checked | Status |
| --- | --- | --- | --- | --- |
| A pRF model turns a stimulus into a predicted BOLD time course: the overlap of bar and pRF is the predicted neural response, and through the haemodynamic response it is the predicted BOLD response (title "Stimulus and pRF predict BOLD", a draft) | 2 | `stimulus_to_bold` seed: brief, first paragraph; equations `neural_response` and `bold_response` | 2026-11-13 | title to review |
| The data are simulated with prfmodel: one pRF (at (2.5, 1.5) deg, sigma 1 deg, Gaussian 2D model, two-gamma HRF) on one 300 s bar run, not a measurement (caption; notes) | 2 | `stimulus_to_bold/data/run.csv`, citation of source `run`; 300 rows, t 0 to 299 s | 2026-11-13 | checked |
| The BOLD trace follows the neural trace about 5 s later (notes) | 2 | `run.csv`: first sweep, neural peaks at t = 19 s (0.676), BOLD at t = 24 s (0.802); seed objective | 2026-11-13 | checked |
| The visual field reaches 8 deg (notes) | 2 | `stimulus_to_bold` seed, constraint `bar_from_data` | 2026-11-13 | checked |
| The BOLD trace has an undershoot in every blank (notes) | 2 | `stimulus_to_bold/data/run.csv`: the four blanks (t 60 to 74, 135 to 149, 210 to 224 and 285 to 299 s, empty bar cells) have a lowest BOLD of -0.04, -0.08, -0.04 and -0.21; seed objective | 2026-11-13 | checked |
| A computational model of an fMRI response is a chain of stages, some of which carry the fitted parameters (title "A model is a chain of stages", a draft) | 3 | `model_as_chain` seed: brief, first paragraph; constraints `stage_order` and `theta_tags` | 2026-11-13 | title to review |
| Seven stages (stimulus, features, spatial pooling, transformation, neural dynamics, HRF, BOLD); the model holds the middle five; theta on four: pooling, transformation, dynamics, HRF (notes) | 3 | `model_as_chain` seed, constraints `stage_order` and `theta_tags` | 2026-11-13 | checked |
| The panel is synthetic: a predicted BOLD response and the same plus noise, not a measurement (caption); the first 150 s of the bar run, peak 1, noise SD 0.12 (notes) | 3 | `model_as_chain/data/panel.csv`, citation of source `panel` | 2026-11-13 | checked |
| A pRF is fitted by trying candidate fields, keeping the one whose prediction matches best, then refining it (title "Fits keep the best candidate", a draft) | 4 | `grid_and_fit` seed: brief, first paragraph | 2026-11-13 | title to review |
| The time course is one measured voxel of prfmodel's example dataset 7t-aot-visual, sub-003 (Knapen 2026, figshare, CC BY 4.0); the predictions are the model's (caption) | 4 | `grid_and_fit/data/timecourses.csv`, citation of source `timecourses`; brief, last paragraph | 2026-11-13 | checked; the dataset's DOI to confirm |
| The visual field is shown out to 4 deg (notes) | 4 | `grid_and_fit` seed, timeline `layout` ("visual field of radius 4 deg") | 2026-11-13 | checked |
| 4 slow and 48 fast candidates; a grid of 147 (7 by 7 centres from -3 to 3 deg, sizes 0.5, 1 and 2 deg); 11 refinement steps (notes) | 4 | `grid_and_fit/data/candidates.csv` (phases: slow 4, fast 48, grid_best 1, refine 11), citation of source `candidates` | 2026-11-13 | checked |
| Best grid point (2, 1) deg, sigma 1 deg, R squared 0.84; optimum x 2.27, y 0.99, sigma 0.85 deg, R squared 0.86 (notes; in the clip) | 4 | `candidates.csv` rows 52 (r2 0.836) and 63 (2.27, 0.995, 0.847, r2 0.862); seed constraint `final_values` | 2026-11-13 | checked |
| A visual field map is not put in by the analysis: it appears when every voxel is fitted on its own and coloured by what its fit returned (title "Independent fits make a map", a draft) | 5 | `fields_to_map` seed: brief, first paragraph | 2026-11-13 | title to review |
| 690 simulated voxels, each fitted on its own with prfmodel, not measurements (caption); on a model sheet of early visual cortex (notes) | 5 | `fields_to_map/data/voxels.csv` (690 rows), citation of source `voxels`; constraint `simulation_label` | 2026-11-13 | checked |
| The field is the right half of the visual field (notes) | 5 | `fields_to_map` seed: brief, "Left: the right half of the visual field, out to 6.5 deg"; constraint `data_exact` | 2026-11-13 | checked |
| Recoloured by the direction of each centre from fixation, the bands run the other way (notes; the Ask) | 5 | `fields_to_map` seed: objective ("Recoloured by direction from fixation, the bands run the other way"); brief ("the bands now run across the first set") | 2026-11-13 | checked |
| The eccentricity map is complete and at rest at 12.9 s (notes; the study strip) | 5 | `fields_to_map` seed, `extensions.lecturekit.stops` and timeline `eccentricity_map`; the render's stop at frame 387 | 2026-11-13 | checked |
| prfmodel: on PyPI since 27 October 2026, Apache-2.0, documentation at popylar-org.github.io/prfmodel (references) | 6 | lecturekit's kickoff deck: `examples/kickoff/FACTS.md` for the PyPI date and the licence (checked there on 4 November 2026); `examples/kickoff/slides.qmd`, the Status note of the prfmodel slide (line 164), for the documentation address | 2026-11-13 | checked |
