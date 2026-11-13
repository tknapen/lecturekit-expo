# Brief: grid search and refinement of a pRF fit

Show how a population receptive field is fitted to one measured voxel: try many candidate fields, keep the
one whose prediction matches best, then refine it.

Left: the visual field out to 4 deg, with a fixation cross and a 2 deg scale bar. The candidate is a dot at its
centre with a one-sigma circle. Above the field a heading says which stage is running ("grid search", then
"refinement"); below it the candidate's x, y and σ are written out and update as it moves.

Right: the voxel's measured time course (340 s, per cent signal change) with the candidate's predicted time
course over it, and an R² readout at the top right.

Motion: four candidates slowly, so the viewer can connect field and prediction; then 48 more in quick
succession; the best so far stays as a dashed outline. The candidate lands on the best grid point
(R² 0.84). The heading changes and the candidate slides in eleven small steps to the optimum (R² 0.86). A
line with the fitted values appears and the clip rests.

`data/candidates.csv` lists the 64 candidates in order with their phase; `data/timecourses.csv` has the
measurement and one predicted time course per candidate. The voxel is measured data (prfmodel's example
dataset 7t-aot-visual, CC BY 4.0); the predictions are the model's.
