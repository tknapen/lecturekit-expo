"""Clip A04b (slide 5, second stage): fitting the Gaussian pRF to a measured voxel. Left, the visual field (±4°) with the
candidate Gaussian (centre and one-sigma circle); right, the voxel's BOLD time course (ink) with the candidate's
prediction (blue) and an R² readout. Beats:
  1. Grid search: the candidate hops over a coarse grid of centres and sizes (147 candidates, a few shown slowly, the rest
     fast); the best so far is kept (dashed outline) and its R² rises.
  2. Refinement: from the best grid point the centre and size slide to the least-squares optimum; the prediction
     settles onto the data, R² 0.84 to 0.86.
  3. Hold on the fit: x 2.27°, y 0.99°, σ 0.85°.
Numbers: assets/data/fitpath.json (scratchpad fitpath.py: prfmodel Gaussian2DPRFModel with the fitted HRF on the
practical's bar design; amplitude and baseline by least squares per candidate, a prediction stored for every grid point;
the voxel of sim01 part 2).
"""
from kit import *

KEYFRAMES = (3.0, 8.5, 13.0)
FP = json.loads((DATA / 'fitpath.json').read_text())
T = np.array(FP['t_s'], float); Y = np.array(FP['data'], float); T_END = float(T[-1] + 0.9)
GRID = FP['grid']; SHOWN = FP['grid_shown']; PATH = FP['path']; FIT = FP['fit']


class FitSearch(Scene):
    def construct(self):
        F = VisualField((-5.2, 0.2), 2.3, deg=4.0)
        self.add(F.outline(HAIR, 3.0).set_z_index(-3), F.fixation().set_z_index(1))
        self.add(F.scale_bar(2.0))
        D = Frame(-1.6, -2.0, 8.8, 4.4, (0, T_END), (float(Y.min()) - 0.5, float(Y.max()) + 0.5))
        self.add(D.axes(u_ticks=(0, 100, 200, 300), u_label='time (s)', w_label='BOLD (% signal change)'))
        data = D.polyline(list(zip(T, Y)), INK, 2.5); self.add(data)
        self.add(label('measured voxel', 26, INK).move_to([D.left + 1.5, D.top + 0.35, 0]))
        head = label('grid search', 30, MUTED).move_to([-5.2, 3.3, 0]); self.add(head)

        x = ValueTracker(SHOWN[0]['x']); y = ValueTracker(SHOWN[0]['y']); s = ValueTracker(SHOWN[0]['s']); r2 = ValueTracker(SHOWN[0]['r2'])
        cand = always_redraw(lambda: F.prf(x.get_value(), y.get_value(), s.get_value(), GAUSS, 4.0))
        dot = always_redraw(lambda: Dot(F.pt(x.get_value(), y.get_value()), radius=0.06, color=GAUSS))
        readout = always_redraw(lambda: label(f'R² = {r2.get_value():.2f}', 34, GAUSS).move_to([D.right - 1.2, D.top + 0.35, 0]))
        params = always_redraw(lambda: label(f'x {x.get_value():+.2f}°   y {y.get_value():+.2f}°   σ {s.get_value():.2f}°', 26, GAUSS).move_to([-5.2, -3.35, 0]))
        pred = D.polyline(list(zip(T, SHOWN[0]['pred'])), GAUSS, 3.5)
        self.add(cand, dot, readout, params, pred)
        best = {'r2': -1}
        kept = F.prf(0, 0, 0.01, MUTED, 2.0, dash=True).set_opacity(0)
        self.add(kept)

        def jump(c, run=0.5, show_pred=True):
            anims = [x.animate.set_value(c['x']), y.animate.set_value(c['y']), s.animate.set_value(c['s']), r2.animate.set_value(c['r2'])]
            if show_pred and 'pred' in c: anims.append(Transform(pred, D.polyline(list(zip(T, c['pred'])), GAUSS, 3.5)))
            self.play(*anims, run_time=run, rate_func=smooth)
            if c['r2'] > best['r2']:
                best.update(c); self.remove(kept)
                kept.become(F.prf(c['x'], c['y'], c['s'], MUTED, 2.0, dash=True)); self.add(kept)

        # beat 1: a few candidates slowly, with their predictions
        for c in SHOWN[:4]: jump(c, run=0.9); self.wait(0.5)
        # the rest of the grid fast, every hop with its own prediction and R²
        rest = [g for g in GRID if g not in SHOWN]
        rng = np.random.default_rng(4); rng.shuffle(rest)
        for c in rest[::3]: jump(c, run=0.07)
        jump(SHOWN[4], run=0.8)   # the grid's best
        self.wait(0.6)
        # beat 2: refinement
        self.play(Transform(head, label('refinement', 30, MUTED).move_to([-5.2, 3.3, 0])), FadeOut(kept), run_time=0.5)
        for c in PATH[1:]: jump(c, run=0.35)
        self.wait(0.4)
        fin = label(f'fit: x {FIT["x"]:.2f}°, y {FIT["y"]:.2f}°, σ {FIT["sigma"]:.2f}°, R² {FIT["r2"]:.2f}', 28, INK).move_to([D.left + D.width / 2, D.bottom - 1.25, 0])
        self.play(FadeIn(fin), run_time=0.5)
        self.wait(2.5)
