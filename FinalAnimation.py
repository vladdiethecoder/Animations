# [CHECKPOINT-1 | STATUS: Active | Title: Regression Guard | Must-Preserve: preserve prior fixes; minimal-diff edits; rollback ready | Notes: confirm after each change]
# [CHECKPOINT-2 | STATUS: Active | Title: Readability & Accessibility | Must-Preserve: ≥28px labels at 1080p, high contrast, aligned math | Notes: academic style]
# [CHECKPOINT-3 | STATUS: Active | Title: Determinism/Consistency | Must-Preserve: fixed seed; fps/resolution pinned; stable timings | Notes: use _set_determinism()]
# [CHECKPOINT-4 | STATUS: Active | Title: Camera Behavior | Must-Preserve: tasteful zoom/pan; no abrupt jumps | Notes: ties to FM-8]
# [CHECKPOINT-5 | STATUS: Active | Title: Eraser Effect Integrity | Must-Preserve: natural wipe; no background lightening; no jitter | Notes: FM-1]
# Rotation check performed — header decluttered as needed.
# Failure Modes: FM-1…FM-8 (see /docs/CHECKPOINTS.md) | Version: Manim CE v0.19.0

from __future__ import annotations

import glob
import os
import random
from contextlib import nullcontext

import numpy as np
from manim import (
    BLACK,
    DR, DL, UL, UR,
    LEFT, RIGHT, UP, DOWN,
    Axes,
    Create,
    Dot,
    FadeIn,
    FadeOut,
    Indicate,
    LaggedStart,
    Mobject,
    NumberPlane,
    Tex,
    VGroup,
    Write,
    config,
    MathTex,
)
from manim_voiceover import VoiceoverScene

from config import USE_PIPER, RANDOM_SEED, PALETTE, PACING, VO
from utils import narr_time, whiteboard, note_stack, PiperService

# -----------------------------
# Debug harness / determinism
# -----------------------------
DEBUG = False

def _guard_label_readable(label: Mobject, min_px: int = 28):
    assert label.height * 1080 >= min_px, (
        f"[GUARD] Too small: {label.height * 1080:.1f}px < {min_px}px"
    )

def _guard_no_lingering_updaters(mobj: Mobject):
    assert len(mobj.updaters) == 0, f"[GUARD] Lingering updaters: {mobj}"

def _set_determinism():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    config.frame_rate = 30
    config.pixel_height = 1080
    config.pixel_width = 1920

# Quadrant-aware label placement
LABEL_BUFF = 0.32

def _label_direction_for(point_xy: tuple[float, float]):
    x, y = point_xy
    if x >= 0 and y >= 0:
        return UR
    if x >= 0 and y < 0:
        return DR
    if x < 0 and y >= 0:
        return UL
    return DL

def pulse(scene: "FinalAnimation", mobj: Mobject, run_time: float = 0.6):
    scene.play(
        Indicate(
            mobj,
            scale_factor=1.05,
            color=PALETTE.get("final", "#90BE6D"),
        ),
        run_time=run_time,
    )

# Semantic highlight colors
HIL_VAR_X = "#4CC9F0"   # x′
HIL_EXPR_X = "#F77F00"  # x/k, d
HIL_VAR_Y = "#B5179E"   # y′
HIL_EXPR_Y = "#F9C74F"  # a y, c
HIL_FUNC   = "#90BE6D"  # provenance in g(x)

# -----------------------------
# Scene
# -----------------------------
class FinalAnimation(VoiceoverScene):
    def setup(self):
        _set_determinism()

        if USE_PIPER:
            base_dir, rt = os.path.dirname(__file__), "piper_runtime"
            piper_exe = os.path.join(base_dir, rt, "piper.exe")
            models = sorted(glob.glob(os.path.join(base_dir, rt, "*.onnx")))
            if not models:
                raise FileNotFoundError("Piper voice model not found in piper_runtime.")
            self.set_speech_service(
                PiperService(piper_exe, models[0], tempo=PACING["voice_tempo"])
            )

        self.axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 7, 1],
            x_length=6.2,
            y_length=6.3,
            axis_config={"color": PALETTE["axis"], "stroke_width": 2},
        )
        self.grid = NumberPlane(
            x_range=[-4, 4, 1],
            y_range=[-4, 7, 1],
            x_length=6.2,
            y_length=6.3,
            background_line_style={
                "stroke_color": PALETTE["grid"],
                "stroke_width": 1,
                "stroke_opacity": 0.45,
            },
        )
        coords = self.axes.add_coordinates(font_size=24, num_decimal_places=0)
        self.graph_group = VGroup(self.grid, self.axes, coords)
        self.graph_group.to_edge(LEFT, buff=0.5).set_z_index(1)

        self.caption = Mobject()

    def construct(self):
        random.seed(RANDOM_SEED)
        self.whiteboard_intro()
        self.point_transformation_sequence()
        self.wait(2)

    def whiteboard_intro(self):
        title = Tex(
            r"\textbf{Transformation Map (Function $\to$ Points)}",
            font_size=56, color=BLACK,
        )

        g_eq = MathTex(
            r"g(x)", "=", "a", r"f(", "k", r"(x-d)", ")", "+", "c",
            color=BLACK
        ).scale(1.2)

        mapping = MathTex(
            r"x'", "=", r"\frac{x}{k}", "+", "d", r",\quad",
            r"y'", "=", r"a\,y", "+", "c",
            color=BLACK
        ).scale(1.1)

        bullets = (
            VGroup(
                Tex(r"Inside $\Rightarrow$ horizontal, acts on $x$", color=BLACK),
                Tex(r"Outside $\Rightarrow$ vertical, acts on $y$", color=BLACK),
                Tex(r"$a<0 \Rightarrow$ reflect across $x$-axis", color=BLACK),
                Tex(r"$k<0 \Rightarrow$ reflect across $y$-axis", color=BLACK),
            )
            .scale(0.9)
            .arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        )

        theory_content = VGroup(title, g_eq, mapping, bullets).arrange(DOWN, buff=0.5)
        board, frame = whiteboard(
            width=config.frame_width - 1.1, height=theory_content.height + 1.2
        )
        VGroup(board, frame, theory_content).to_edge(UP, buff=0.35).set_z_index(5)

        g_a, g_k, g_xd, g_c = g_eq[2], g_eq[4], g_eq[5], g_eq[8]
        m_xp, m_x_over_k, m_d = mapping[0], mapping[2], mapping[4]
        m_yp, m_ay, m_c      = mapping[6], mapping[8], mapping[10]

        def reset_parts(*parts):
            for p in parts:
                p.set_color(BLACK)

        with self.voiceover(text=VO.get("theory_intro", "")) if USE_PIPER else nullcontext() as tr_intro:
            self.play(FadeIn(board, shift=UP * 0.1), Create(frame), run_time=0.6)
            self.play(Write(title), run_time=0.5)
            self.play(LaggedStart(Write(g_eq), Write(mapping), lag_ratio=0.25), run_time=1.0)
            reset_parts(g_eq, mapping)

        # x′ narration — highlight x′ + (x/k, d), and provenance (k, x-d)
        with self.voiceover(text=VO.get("theory_x", "")) if USE_PIPER else nullcontext() as tr_x:
            reset_parts(m_xp, m_x_over_k, m_d, m_yp, m_ay, m_c, g_a, g_k, g_xd, g_c)
            m_xp.set_color(HIL_VAR_X)
            m_x_over_k.set_color(HIL_EXPR_X)
            m_d.set_color(HIL_EXPR_X)
            g_k.set_color(HIL_FUNC)
            g_xd.set_color(HIL_FUNC)
            pulse(self, VGroup(m_xp, m_x_over_k, m_d), run_time=0.45 if USE_PIPER else 0.5)
            self.wait(narr_time(tr_x) if USE_PIPER else 0.2)

        # y′ narration — highlight y′ + (a y, c), and provenance (a, c)
        with self.voiceover(text=VO.get("theory_y", "")) if USE_PIPER else nullcontext() as tr_y:
            reset_parts(m_xp, m_x_over_k, m_d, g_a, g_k, g_xd, g_c)
            m_yp.set_color(HIL_VAR_Y)
            m_ay.set_color(HIL_EXPR_Y)
            m_c.set_color(HIL_EXPR_Y)
            g_a.set_color(HIL_FUNC)
            g_c.set_color(HIL_FUNC)
            pulse(self, VGroup(m_yp, m_ay, m_c), run_time=0.45 if USE_PIPER else 0.5)
            self.wait(narr_time(tr_y) if USE_PIPER else 0.2)

        with self.voiceover(text=VO.get("theory_bullets", "")) if USE_PIPER else nullcontext() as tr_bul:
            self.play(
                LaggedStart(*[Write(b) for b in bullets], lag_ratio=0.2),
                run_time=(narr_time(tr_bul, 1.2, 3.2) if USE_PIPER else 1.2),
            )
            self.wait(0.3)

        reset_parts(g_a, g_k, g_xd, g_c, m_xp, m_x_over_k, m_d, m_yp, m_ay, m_c)
        self.play(FadeOut(bullets, scale=0.8, target_position=mapping), run_time=1.0)
        self.play(FadeOut(VGroup(title, g_eq, mapping, frame, board)), run_time=0.6)

    def point_transformation_sequence(self):
        self.add(self.graph_group)

        # ---------- Right column tokenized ----------
        r_g = MathTex("g(x)", "=", "-", "f(", r"-x-1", ")", "+", "3",
                      color=PALETTE["text"])
        r_map = MathTex(r"x'", "=", r"\frac{x}{k}", "+", "d", r",\quad",
                        r"y'", "=", r"a\,y", "+", "c",
                        color=PALETTE["text"])
        r_point = MathTex(r"(1,-2)\ \text{ on }f", color=PALETTE["text"])
        right_column = VGroup(r_g, r_map, r_point).arrange(DOWN, aligned_edge=LEFT, buff=0.45)

        rc_x = self.graph_group.get_right()[0]
        right_column.move_to([rc_x + (config.frame_width / 2 - rc_x) / 2, 0, 0])\
                    .align_to(self.axes, UP)
        self.add(right_column)

        g_minus, g_inside, g_plus3 = r_g[2], r_g[4], r_g[7]
        mxp, mx_over_k, md = r_map[0], r_map[2], r_map[4]
        myp, may, mc        = r_map[6], r_map[8], r_map[10]

        def r_reset(*parts):
            if not parts:
                parts = (r_g, r_map, r_point)
            for p in parts:
                p.set_color(PALETTE["text"])

        # ---------- "Show steps" panel (pinned bottom-right, math terms, mirrored order) ----------
        steps_anchor = Tex("Steps", color=PALETTE["text"]).scale(0.6).set_opacity(0.75)
        steps_items = VGroup().arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        steps_panel = VGroup(steps_anchor, steps_items).arrange(
            DOWN, aligned_edge=LEFT, buff=0.22
        ).scale(0.9)

        def _pin_steps():
            steps_panel.to_edge(RIGHT, buff=0.45)
            steps_panel.to_edge(DOWN, buff=0.55)
            steps_panel.set_z_index(5)

        _pin_steps()
        self.add(steps_panel)

        def add_step_math(latex: str):
            """Append a compact math justification item (keeps order top→bottom)."""
            item = MathTex(latex, color=PALETTE["text"]).scale(0.58)
            steps_items.add(item)  # append so the visual order matches the timeline
            steps_panel.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
            _pin_steps()
            self.play(FadeIn(item, shift=UP * 0.1), run_time=0.35)

        # Caption
        caption_position = [-3.5, -3.5, 0]
        self.caption = Tex("").move_to(caption_position)
        self.add(self.caption)

        point = Dot(self.axes.c2p(1, -2), color=PALETTE["start"], radius=0.09)

        def _purge_stray_dots():
            for m in list(self.mobjects):
                if isinstance(m, Dot) and m is not point:
                    self.remove(m)

        def relabel(text: str, color=PALETTE["text"]) -> MathTex:
            lbl = MathTex(text, color=color).scale(0.9)
            px, py = self.axes.p2c(point.get_center())
            lbl.next_to(point, _label_direction_for((px, py)), buff=LABEL_BUFF)
            _guard_label_readable(lbl, 28)
            return lbl

        label = relabel(r"(1,-2)")
        self.add(point, label)
        self.wait(PACING["hold_pad"])

        def update_caption(new_text_str: str):
            new_caption = Tex(new_text_str, color=PALETTE["text"])
            if new_caption.width > self.graph_group.width - 0.5:
                new_caption.set_width(self.graph_group.width - 0.5)
            new_caption.move_to(caption_position)
            self.play(self.caption.animate.become(new_caption))

        # --- Steps (order mirrored top→bottom) ---
        # 1) Reflect across y-axis  → k < 0
        with self.voiceover(text=VO["y_reflect"]) if USE_PIPER else nullcontext() as tr:
            update_caption("Reflect across the $y$-axis")
            r_reset()
            mxp.set_color(HIL_VAR_X)
            mx_over_k.set_color(HIL_EXPR_X)
            g_inside.set_color(HIL_FUNC)
            pulse(self, VGroup(mxp, mx_over_k, g_inside), run_time=0.35 if USE_PIPER else 0.4)
            add_step_math(r"k<0")
            target = self.axes.c2p(-1, -2)
            _purge_stray_dots()
            self.play(point.animate.move_to(target), run_time=narr_time(tr))
            new_label = relabel(r"(-1,-2)")
            self.play(label.animate.become(new_label))
            self.wait(PACING["hold_pad"])

        # 2) Translate left by 1   → d = -1
        with self.voiceover(text=VO["left_shift"]) if USE_PIPER else nullcontext() as tr:
            update_caption("Translate left by $1$")
            r_reset()
            mxp.set_color(HIL_VAR_X)
            md.set_color(HIL_EXPR_X)
            g_inside.set_color(HIL_FUNC)
            pulse(self, VGroup(md, g_inside), run_time=0.35 if USE_PIPER else 0.4)
            add_step_math(r"d=-1")
            target = self.axes.c2p(-2, -2)
            _purge_stray_dots()
            self.play(point.animate.move_to(target), run_time=narr_time(tr))
            new_label = relabel(r"(-2,-2)")
            self.play(label.animate.become(new_label))
            self.wait(PACING["hold_pad"])

        # 3) Reflect across x-axis → a < 0
        with self.voiceover(text=VO["x_reflect"]) if USE_PIPER else nullcontext() as tr:
            update_caption("Reflect across the $x$-axis")
            r_reset()
            myp.set_color(HIL_VAR_Y)
            may.set_color(HIL_EXPR_Y)
            g_minus.set_color(HIL_FUNC)
            pulse(self, VGroup(myp, may, g_minus), run_time=0.35 if USE_PIPER else 0.4)
            add_step_math(r"a<0")
            target = self.axes.c2p(-2, 2)
            _purge_stray_dots()
            self.play(point.animate.move_to(target), run_time=narr_time(tr))
            new_label = relabel(r"(-2,2)")
            self.play(label.animate.become(new_label))
            self.wait(PACING["hold_pad"])

        # 4) Translate up by 3     → c = 3
        with self.voiceover(text=VO["up_shift"]) if USE_PIPER else nullcontext() as tr:
            update_caption("Translate up by $3$")
            r_reset()
            myp.set_color(HIL_VAR_Y)
            mc.set_color(HIL_EXPR_Y)
            g_plus3.set_color(HIL_FUNC)
            pulse(self, VGroup(mc, g_plus3), run_time=0.35 if USE_PIPER else 0.4)
            add_step_math(r"c=3")
            target = self.axes.c2p(-2, 5)
            _purge_stray_dots()
            self.play(point.animate.move_to(target), run_time=narr_time(tr))
            new_label = relabel(r"(-2,5)", color=PALETTE["final"])
            self.play(label.animate.become(new_label))
            self.play(point.animate.set_color(PALETTE["final"]))
            self.wait(PACING["hold_pad"])

        if DEBUG:
            _guard_no_lingering_updaters(point)
            _guard_no_lingering_updaters(label)
