# Manifest: Population receptive fields, from stimulus to map

Every image and clip in the deck: where it came from, which script makes it,
and under what licence it is shown. A figure redrawn from a publication cites
the source and says it was redrawn from digitised values.

The clips are the lecturer's, rebuilt in manim8 from the hand-written Manim scenes in each project's `references/`
(read for geometry and timing, not run). `lk clips` renders each manim8 project in
`clips/families/population_receptive_fields/<clip>/` into `assets/clips/` (paper, style `lecturekit_paper@0.1.0`)
and `lk clips --mode dark` into `assets/clips/dark/` (style `lecturekit_dark@0.1.1`, the dark brand's hairline lifted
after review; 0.1.0 before): the movie `<clip>.mp4`, every
checkpoint as `<clip>.<id>.png`, the poster and end frames as `<clip>.fNNNN.png`, and the entry in `clips.json`.

| File | Made by | From (data, source) | Licence | Notes |
| --- | --- | --- | --- | --- |
| `assets/clips/stimulus_to_bold.*`, `assets/clips/dark/stimulus_to_bold.*` | `lk clips` from `stimulus_to_bold` (jobs `job_20261113T164047_e407f0` paper, `job_20261113T164551_e2b774` dark); builders `code/stim_bold.py` | `data/run.csv`: simulated with prfmodel, a pRF at (2.5, 1.5) deg, sigma 1 deg, on a 300 s bar run; not a measurement | CC BY 4.0 (Tomas Knapen) | 12 s, 360 frames; still `traces_complete`; slide 2 |
| `assets/clips/model_as_chain.*`, `assets/clips/dark/model_as_chain.*` | `lk clips` from `model_as_chain` (jobs `job_20261113T144725_c414f9`, `job_20261113T164532_90a923`); builders `code/chain_builders.py`, `code/chain_layout.py` | `data/panel.csv`: synthetic, a predicted BOLD response and the same plus Gaussian noise; not a measurement | CC BY 4.0 (Tomas Knapen) | 15.5 s, 465 frames; still `study`; the HRF glyph is the canonical two-gamma shape drawn as a schematic, with no data behind it (for the lecturer: PLAN.md); slide 3 |
| `assets/clips/grid_and_fit.*`, `assets/clips/dark/grid_and_fit.*` | `lk clips` from `grid_and_fit` (jobs `job_20261113T163736_2e8ebc`, `job_20261113T164154_5eb199`); builders `code/grid_fit.py` | `data/timecourses.csv` column `measured`: one voxel of 7t-aot-visual, sub-003 (Knapen 2026, figshare), measured; columns `p00` to `p63` and `data/candidates.csv`: the candidates fitted with prfmodel | the clip CC BY 4.0 (Tomas Knapen); the measured voxel CC BY 4.0 (Knapen 2026, 7t-aot-visual, figshare), credited on the slide | 20 s, 600 frames; still `result`; slide 4 |
| `assets/clips/fields_to_map.*`, `assets/clips/dark/fields_to_map.*` | `lk clips` from `fields_to_map` (jobs `job_20261113T151059_565b6c`, `job_20261113T164059_717a45`); builders `code/prf_map.py` | `data/voxels.csv`: 690 simulated voxels, each fitted on its own with prfmodel; not measurements | CC BY 4.0 (Tomas Knapen) | 18 s, 540 frames; one stop, `eccentricity` at frame 387 (`f0387.png`); the study strip prints it and the end; slide 5 |
| `assets/figures/example.tex` | `make_assets.py:example` | none (placeholder) | CC BY 4.0 | the scaffold's; on no slide |
