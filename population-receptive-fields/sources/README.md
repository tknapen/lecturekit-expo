# Sources

The documents this lecture is built from. A redistributable document goes in this folder; anything else is a
link here and digitised values in `assets/data`, with the method of digitising in `MANIFEST.md`.

- `prf-clips/`: the lecturer's upload of 13 November 2026, four pRF clips as manim8 project seeds. This folder keeps
  the bundle's `README.md` (written for a website, which the lecturer's decisions in `SESSION.md` override) and the
  four briefs. The seeds themselves (each `animation.yaml`, `data/*.csv` and `references/`: the brief, the original
  hand-written Manim scene, for the chain its layout, and the original render's last frame) are the manim8 projects
  under `clips/families/population_receptive_fields/`, unchanged.
- The data: `stimulus_to_bold/data/run.csv` (simulated with prfmodel), `model_as_chain/data/panel.csv` (synthetic),
  `grid_and_fit/data/candidates.csv` and `timecourses.csv` (one measured voxel of prfmodel's example dataset
  7t-aot-visual, sub-003, Knapen 2026, figshare, CC BY 4.0, and the candidates fitted to it with prfmodel),
  `fields_to_map/data/voxels.csv` (690 simulated voxels, each fitted with prfmodel). Each file's citation is in its
  project's `animation.yaml`.
