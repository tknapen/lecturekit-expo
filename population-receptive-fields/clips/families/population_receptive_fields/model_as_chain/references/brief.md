# Brief: the model as a chain of stages

Show that a computational model of an fMRI response is a chain of stages, some of which carry the parameters
that are fitted.

Start from the loop: a box "parameters θ" and a box "stimulus" feed a box "model" (with a small gear); under it
a panel shows the model's prediction lying on a noisy time course. Three dots travel along the arrows.

Then open the model. The loop shrinks to the top of the frame and stays there. Its model box gets a heavier
outline, and a light funnel opens from it to a row of seven boxes across the lower part of the frame:
stimulus S, features Φ(S), spatial pooling, transformation f, neural dynamics, HRF, BOLD. A dashed outline
holds the five middle boxes: they are the model. Arrows link the boxes. A copy of the θ box drops and splits
into four tags, on pooling, transformation, dynamics and HRF.

Last, a pulse runs from the stimulus through the stages to BOLD, each stage darkening as it passes, and the
prediction is drawn over the data in the BOLD box.

Each box holds a small glyph (a bar in an aperture, a filter bank, a Gaussian, a curve, a decaying response,
an HRF, a time course); `references/original_layout.py` has them, with every position and size.
`data/panel.csv` has the prediction and the noisy data (synthetic).
