"""Clip A02 (slide 2): every pRF is an encoding model. Thursday's loop (parameters and stimulus feed a model whose
prediction is set against the data) opens its model box into the pipeline that recurs through the lecture: stimulus S,
features Phi(S), spatial pooling, transformation f, neural dynamics, HRF, BOLD. theta tags drop onto the fitted modules,
and a pulse runs from the stimulus to BOLD, where the prediction is drawn over the data.

Beats:
  1. Thursday's loop: parameters theta and the stimulus feed the model (gear); its prediction (blue) lies on the data.
  2. The loop shrinks to the top and stays there, its model box outlined; a light funnel opens from that box to a
     dashed outline holding five modules (features to HRF), between the stimulus box and the BOLD box; a copy of the
     theta box drops and splits into tags on pooling, transformation, dynamics and the HRF.
  3. A pulse runs from the stimulus through the modules to BOLD; the prediction is drawn over the data.
Boxes in ink and grey, as the coordinator asked: Thursday's teal, blue and orange are model colours on Friday. Model
colour appears only where a module stands for a model: the blue Gaussian in the pooling box and the prediction. Layout
of the loop after lecture 1's make_assets.py loop_core; of the row, anim/l2pipe.py (shared with A20 and pipeline.tex);
the last frame has the row at y = -2.32 under the loop (scale 0.45, centre y = 1.88): centred, about 75 per cent of the
frame height, as the coordinator asked.
Data: the Gaussian voxel's BOLD for the first 150 s of the D0 bar run (anim/l2model.py), normalised, plus Gaussian noise
(SD 0.12, seed 20261106): synthetic. Storyboard: STORYBOARD.md slide 02; PLAN.md slide 2 and clip A02.
"""
from kit import *
import l2model as M
import l2pipe as L

KEYFRAMES = (2.0, 8.5, 10.6)
T = 150                                                     # seconds of the run in the panel
ROW, LOOP_C, LOOP_S = -2.32, np.array([0.0, 1.88, 0.0]), 0.45  # the row's height; where and how small the loop stays


def tbox(w, h, *items):
    r = L.rbox(w, h)
    return VGroup(r, VGroup(*items).arrange(RIGHT, buff=0.14).move_to(r))


class ModelBox(Scene):
    def construct(self):
        rng = np.random.default_rng(M.SEED)
        pred = M.to_bold(M.run_cov())[:T]; pred = pred / pred.max(); data = pred + rng.normal(0, 0.12, T)
        boxes = L.modules(pred, data, ROW)
        for b in boxes:
            for m in b[1:]: m.set_z_index(1)                  # contents above their grey box, whatever the order added
        # beat 1: Thursday's loop
        theta = tbox(3.2, 0.95, label('parameters', 30), label('θ', 34, serif=True, slant=ITALIC)).move_to([-2.15, 2.95, 0])
        stim = tbox(3.2, 0.95, label('stimulus', 30)).move_to([2.15, 2.95, 0])
        model = tbox(5.0, 1.25, label('model', 34), L.gear()).move_to([0, 1.0, 0])
        panel = L.bold_panel(pred, data, w=4.8, h=1.75, c=np.array([0, -2.35, 0]))
        a1 = Arrow(theta.get_bottom(), model[0].get_top() + LEFT * 1.0, path_arc=0.4, **L.AR)
        a2 = Arrow(stim.get_bottom(), model[0].get_top() + RIGHT * 1.0, path_arc=-0.4, **L.AR)
        a3 = Arrow(model.get_bottom(), panel.get_top() + UP * 0.12, **L.AR)
        self.add(theta, stim, model, a1, a2, a3, panel)
        dots = [Dot(radius=0.1, color=INK) for _ in range(3)]
        self.wait(0.4)
        self.play(MoveAlongPath(dots[0], a1.copy()), MoveAlongPath(dots[1], a2.copy()), Rotate(model[1][1], -PI / 2), run_time=0.8, rate_func=smooth)
        self.remove(dots[0], dots[1])
        self.play(MoveAlongPath(dots[2], Line(model.get_bottom(), panel.get_top())), run_time=0.6, rate_func=smooth)
        self.remove(dots[2]); self.wait(0.8)

        # beat 2: the loop shrinks to the top and stays; its model box opens into the row below
        loop = Group(theta, stim, model, a1, a2, a3, panel)
        self.play(loop.animate.scale(LOOP_S).move_to(LOOP_C), run_time=1.3)
        hull = L.hull(ROW); mb = model[0]
        funnel = Polygon(mb.get_corner(DL), mb.get_corner(DR), hull.get_corner(UR), hull.get_corner(UL)).set_stroke(width=0).set_fill(tint(INK, 7), 1).set_z_index(-2)
        self.play(FadeIn(funnel), Create(hull), mb.animate.set_stroke(INK, 5), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(boxes[k], scale=0.85) for k in range(7)], lag_ratio=0.14), run_time=1.5)
        links = L.links(boxes)
        self.play(LaggedStart(*[GrowArrow(a) for a in links], lag_ratio=0.12), run_time=0.9)
        tags, stems = L.tags(boxes, ROW)
        self.play(FadeTransform(theta.copy(), VGroup(*tags)), run_time=1.0)
        self.play(*[Create(s) for s in stems], run_time=0.4); self.wait(0.6)

        # beat 3: the pulse runs to BOLD
        pulse = Dot(radius=0.13, color=INK).move_to(boxes[0][0].get_right()).set_z_index(3)
        redraw = boxes[6][1][2].copy(); self.remove(boxes[6][1][2])
        for k in range(1, 6): boxes[k][0].add_updater(lambda r: r.set_fill(tint(INK, 28) if abs(pulse.get_x() - r.get_x()) < 1.0 else L.GREY, 1))
        self.add(pulse)
        self.play(pulse.animate.move_to(boxes[6][0].get_left()), run_time=3.2, rate_func=linear)
        for k in range(1, 6): boxes[k][0].clear_updaters(); boxes[k][0].set_fill(L.GREY, 1)
        self.play(FadeOut(pulse), Create(redraw), run_time=1.2)
        self.wait(1.8)
