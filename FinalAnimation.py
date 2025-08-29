# FinalAnimation.py

from __future__ import annotations
from manim import *
from manim_voiceover import VoiceoverScene
import random
from contextlib import nullcontext

# Import our separated components
from config import USE_PIPER, RANDOM_SEED, PALETTE, PACING, VO
from utils import narr_time, whiteboard, note_stack, PiperService

# Set the random seed for determinism
random.seed(RANDOM_SEED)

class FinalAnimation(VoiceoverScene, Scene):
    def setup(self):
        """Initializes the scene, setting up the voice service and graph."""
        if USE_PIPER:
            base_dir, rt = os.path.dirname(__file__), "piper_runtime"
            piper_exe = os.path.join(base_dir, rt, "piper.exe")
            models = sorted(glob.glob(os.path.join(base_dir, rt, "*.onnx")))
            if not models: raise FileNotFoundError("Piper voice model not found in piper_runtime.")
            self.set_speech_service(PiperService(piper_exe, models[0], tempo=PACING["voice_tempo"]))

        self.axes = Axes(
            x_range=[-4, 4, 1], y_range=[-4, 7, 1], x_length=6.2, y_length=6.3,
            axis_config={"color": PALETTE["axis"], "stroke_width": 2}
        )
        self.grid = NumberPlane(
            x_range=[-4, 4, 1], y_range=[-4, 7, 1], x_length=6.2, y_length=6.3,
            background_line_style={"stroke_color": PALETTE["grid"], "stroke_width": 1, "stroke_opacity": 0.45}
        )
        self.graph_group = VGroup(self.grid, self.axes, self.axes.add_coordinates(font_size=24, num_decimal_places=0))
        self.graph_group.to_edge(LEFT, buff=0.5).set_z_index(1)
        self.caption = Mobject()

    def construct(self):
        """Main method to construct and run the animation."""
        self.whiteboard_intro()
        self.point_transformation_sequence()
        self.wait(2)

    def whiteboard_intro(self):
        """Creates and animates the introductory whiteboard sequence."""
        title = Tex(r"\textbf{Transformation Map (Function $\to$ Points)}", font_size=56, color=BLACK)
        g_eq = MathTex(r"g(x)=a\,f\!\big(k(x-d)\big)+c", color=BLACK).scale(1.2)
        mapping = MathTex(r"x'=\frac{x}{k}+d,\quad y'=a\,y+c", color=BLACK).scale(1.1)
        bullets = VGroup(
            Tex(r"Inside $\Rightarrow$ horizontal, acts on $x$", color=BLACK),
            Tex(r"Outside $\Rightarrow$ vertical, acts on $y$", color=BLACK),
            Tex(r"$a<0 \Rightarrow$ reflect across $x$-axis", color=BLACK),
            Tex(r"$k<0 \Rightarrow$ reflect across $y$-axis", color=BLACK)
        ).scale(0.9).arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        
        theory_content = VGroup(title, g_eq, mapping, bullets).arrange(DOWN, buff=0.5)
        board, frame = whiteboard(width=config.frame_width - 1.1, height=theory_content.height + 1.2)
        whiteboard_group = VGroup(board, frame, theory_content).to_edge(UP, buff=0.35).set_z_index(5)

        with self.voiceover(text=VO["theory"]) if USE_PIPER else nullcontext() as tr:
            self.play(FadeIn(board, shift=UP*0.1), Create(frame), run_time=0.6)
            self.play(Write(title), run_time=0.5)
            self.play(LaggedStart(Write(g_eq), Write(mapping), lag_ratio=0.25), run_time=1.0)
            self.play(LaggedStart(*[Write(b) for b in bullets], lag_ratio=0.2), run_time=(narr_time(tr, 1.2, 3.2) if USE_PIPER else 1.2))
            self.wait(0.3)
        
        self.play(FadeOut(bullets, scale=0.8, target_position=mapping), run_time=1.0)
        
        problem = VGroup(
            Tex(r"\textbf{Problem:}", color=BLACK),
            MathTex(r"g(x)=-\,f(-x-1)+3", color=BLACK),
            Tex(r"Given point on $f$: $(1,-2)$", color=BLACK)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.28).next_to(mapping, DOWN, buff=0.55).align_to(g_eq, LEFT).set_z_index(6)
        
        with self.voiceover(text=VO["announce_problem"]) if USE_PIPER else nullcontext() as tr:
            self.play(Write(problem), run_time=(narr_time(tr, 1.0, 2.6) if USE_PIPER else 1.0))
        
        self.play(FadeOut(VGroup(problem, title, g_eq, mapping, frame, board)), run_time=0.6)

    def point_transformation_sequence(self):
        """Animates the main sequence of point transformations on the graph."""
        self.add(self.graph_group)
        right_column = note_stack(
            MathTex(r"g(x)=-\,f(-x-1)+3", color=PALETTE["text"]),
            MathTex(r"x'=\frac{x}{k}+d,\;\;y'=a\,y+c", color=PALETTE["text"]),
            MathTex(r"(1,-2)\ \text{ on }f", color=PALETTE["text"])
        )
        right_column.move_to([self.graph_group.get_right()[0] + (config.frame_width / 2 - self.graph_group.get_right()[0]) / 2, 0, 0]).align_to(self.axes, UP)
        self.add(right_column)

        # Use a hardcoded position for the caption to ensure stability
        caption_position = [-3.5, -3.5, 0]
        self.caption = Tex("").move_to(caption_position)
        self.add(self.caption)

        point = Dot(self.axes.c2p(1, -2), color=PALETTE["start"], radius=0.09)
        label = MathTex(r"(1,-2)", color=PALETTE["text"]).scale(0.9).next_to(point, DR, buff=0.18)
        self.add(point, label)
        self.wait(PACING["hold_pad"])

        def update_caption(new_text_str):
            new_caption = Tex(new_text_str, color=PALETTE["text"])
            if new_caption.width > self.graph_group.width - 0.5:
                new_caption.set_width(self.graph_group.width - 0.5)
            new_caption.move_to(caption_position)
            self.play(ReplacementTransform(self.caption, new_caption))
            self.caption = new_caption
        
        # --- Transformation Steps ---
        with self.voiceover(text=VO["y_reflect"]) if USE_PIPER else nullcontext() as tr:
            update_caption("Reflect across the $y$-axis")
            target = self.axes.c2p(-1, -2)
            self.play(point.animate.move_to(target), label.animate.next_to(Dot(target), DR, buff=0.18), run_time=narr_time(tr))
            self.play(Transform(label, MathTex(r"(-1,-2)", color=PALETTE["text"]).scale(0.9).move_to(label.get_center())))
        self.wait(PACING["hold_pad"])

        with self.voiceover(text=VO["left_shift"]) if USE_PIPER else nullcontext() as tr:
            update_caption("Translate left by $1$")
            target = self.axes.c2p(-2, -2)
            self.play(point.animate.move_to(target), label.animate.next_to(Dot(target), DR, buff=0.18), run_time=narr_time(tr))
            self.play(Transform(label, MathTex(r"(-2,-2)", color=PALETTE["text"]).scale(0.9).move_to(label.get_center())))
        self.wait(PACING["hold_pad"])

        with self.voiceover(text=VO["x_reflect"]) if USE_PIPER else nullcontext() as tr:
            update_caption("Reflect across the $x$-axis")
            target = self.axes.c2p(-2, 2)
            self.play(point.animate.move_to(target), label.animate.next_to(Dot(target), DR, buff=0.18), run_time=narr_time(tr))
            self.play(Transform(label, MathTex(r"(-2,2)", color=PALETTE["text"]).scale(0.9).move_to(label.get_center())))
        self.wait(PACING["hold_pad"])

        with self.voiceover(text=VO["up_shift"]) if USE_PIPER else nullcontext() as tr:
            update_caption("Translate up by $3$")
            target = self.axes.c2p(-2, 5)
            self.play(point.animate.move_to(target), label.animate.next_to(Dot(target), DR, buff=0.18), run_time=narr_time(tr))
            self.play(Transform(label, MathTex(r"(-2,5)", color=PALETTE["final"]).scale(1.0).move_to(label.get_center())))
            self.play(point.animate.set_color(PALETTE["final"]))
        self.wait(PACING["hold_pad"])

        with self.voiceover(text=VO["wrap"]) if USE_PIPER else nullcontext() as tr:
            update_caption(r"Result: $(-2,\,5)$")
        self.wait(PACING["hold_pad"])