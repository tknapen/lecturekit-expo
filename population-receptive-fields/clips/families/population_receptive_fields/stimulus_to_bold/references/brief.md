# Brief: from stimulus to predicted BOLD signal

Show how a population receptive field model turns a stimulus into a predicted fMRI time course. One voxel, one
run, one moving cursor.

Left: the visual field (a circle, radius 8 deg) with a fixation cross and the voxel's pRF as a one-sigma circle
at (2.5, 1.5) deg, sigma 1 deg. A bar 2 deg wide sweeps across the field in eight directions.

Right, three rows on one time axis (0 to 300 s): the stimulus (one grey band per sweep, an arrow in it for the
direction of motion; two sweeps, then a 15 s blank, four times), the predicted neural response (overlap of bar
and pRF), and the predicted BOLD response (the neural response through the haemodynamic response).

Motion: after a short rest on the empty panels, the cursor runs through the run at constant speed in about
10 s; the bar moves in the field, the traces are drawn up to the cursor, a dot rides each trace. The cursor
fades at the end and the clip rests on the complete traces.

`data/run.csv` has one row per second: bar centre and direction (empty in blanks), neural, bold. The values are
a simulation with prfmodel, not a measurement.
