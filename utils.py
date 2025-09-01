# utils.py
# [CHECKPOINT-1..5 Active; Mirrors CHECKPOINTS.md]

from __future__ import annotations
from typing import Iterable, List, Tuple
import numpy as np
from manim import *
from manim_voiceover.services.base import SpeechService
import os
import subprocess
import glob
import config as CFG
from config import PACING

# =============================
# Animation & Pacing Helpers
# =============================

def narr_time(tr, min_rt=0.9, cap=2.2, extra=PACING["base_pad"]):
    """Tie motion to speech without dragging visuals."""
    d = getattr(tr, "duration", 0.0)
    return max(min_rt, min(d + extra, cap))

# =============================
# Mobject Creation Helpers
# =============================

def whiteboard(width: float, height: float) -> tuple[RoundedRectangle, RoundedRectangle]:
    """Creates a large white board with a border."""
    board = RoundedRectangle(
        width=width, height=height, corner_radius=0.4,
        stroke_width=3, color=GREY_B, fill_color=WHITE, fill_opacity=1
    )
    frame = RoundedRectangle(corner_radius=0.4, stroke_width=5, color=GREY_E)
    frame.match_width(board).match_height(board).move_to(board)
    return board, frame

def note_stack(*items: Mobject) -> VGroup:
    """Stacks mobjects vertically with left alignment and airy spacing."""
    group = VGroup(*[item.copy().scale(0.95) for item in items])
    group.arrange(DOWN, aligned_edge=LEFT, buff=0.7)
    return group

# =============================
# Piper SpeechService
# =============================

class PiperService(SpeechService):
    """Uses piper.exe to synthesize WAV, then converts to MP3 via bundled ffmpeg."""
    def __init__(self, piper_path: str, model_path: str, speaker: int | None = None, tempo: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.piper_path = piper_path
        self.model_path = model_path
        self.speaker = speaker
        self.tempo = float(tempo)
        if not os.path.exists(self.piper_path):
            raise FileNotFoundError(f"Piper EXE not found: {self.piper_path}")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Piper model not found: {self.model_path}")
        base_dir = os.path.dirname(self.piper_path)
        self.ffmpeg_path = os.path.join(base_dir, "ffmpeg", "bin", "ffmpeg.exe")
        if not os.path.exists(self.ffmpeg_path):
            raise FileNotFoundError("ffmpeg.exe not found at piper_runtime\\ffmpeg\\bin\\ffmpeg.exe")

    def _ffmpeg_atempo_args(self):
        t = self.tempo
        if abs(t - 1.0) < 1e-3: return []
        if 0.5 <= t <= 2.0: return ["-af", f"atempo={t}"]
        import math
        a = math.sqrt(max(0.01, min(4.0, t)))
        return ["-af", f"atempo={a},atempo={a}"]

    def generate_from_text(self, text: str, cache_dir: str | None = None, path: str | None = None) -> dict:
        cache_dir = cache_dir or self.cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        stem = self.get_audio_basename({"input_text": text, "model": self.model_path})
        wav_path = os.path.join(cache_dir, stem + ".wav")
        mp3_path = os.path.join(cache_dir, stem + ".mp3")
        cmd = [self.piper_path, "--model", self.model_path, "--output_file", wav_path]
        if self.speaker is not None:
            cmd += ["--speaker", str(self.speaker)]
        proc = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Piper failed (exit {proc.returncode}).\nCmd: {' '.join(cmd)}\nSTDOUT:\n{proc.stdout.decode(errors='ignore')}\nSTDERR:\n{proc.stderr.decode(errors='ignore')}")
        if os.path.exists(mp3_path): os.remove(mp3_path)
        ff = [self.ffmpeg_path, "-y", "-v", "error", "-i", wav_path] + self._ffmpeg_atempo_args() + ["-acodec", "libmp3lame", "-b:a", "192k", mp3_path]
        proc2 = subprocess.run(ff, capture_output=True)
        if proc2.returncode != 0 or not os.path.exists(mp3_path):
            raise RuntimeError(f"ffmpeg failed converting WAV->MP3.\nSTDOUT:\n{proc2.stdout.decode(errors='ignore')}\nSTDERR:\n{proc2.stderr.decode(errors='ignore')}")
        rel_mp3 = os.path.relpath(mp3_path, cache_dir).replace("\\", "/")
        return {"path": mp3_path, "original_audio": rel_mp3, "input_data": {"input_text": text}}
    
# ---- Determinism helper (Checkpoint-3) ----
def _set_determinism(scene):
    # NOTE: In CE 0.19.0, seeding numpy is sufficient for most randomness in layout jitters.
    np.random.seed(CFG.SEED)

# ---- Steps Panel (bottom-right, hard coordinates) ----
class StepsPanel(VGroup):
    def __init__(self, title: str = "Steps", width: float = CFG.PANEL_WIDTH, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.bg = RoundedRectangle(corner_radius=0.2, width=width, height=3.8)
        self.title = Text(title, font_size=CFG.FONT_SIZE_STEPS)
        self.title.next_to(self.bg.get_top(), direction=np.array([0, -1, 0]), buff=0.15)
        self.lines = VGroup()
        self.add(self.bg, self.title, self.lines)
        self.move_to(CFG.ANCHOR_STEPS)
        self._next_y = self.title.get_bottom()[1] - 0.35

    def add_line(self, latex: str):
        idx = len(self.lines) + 1
        m = MathTex(rf"{idx}.\; {latex}", font_size=CFG.FONT_SIZE_STEPS)
        # Fixed-width panel; multiline will wrap via MathTex layout; we stack by y.
        m.align_to(self.bg, direction=np.array([-1, 0, 0])).shift(np.array([CFG.PANEL_PADDING - self.bg.width/2 + 0.3, 0, 0]))
        if idx == 1:
            m.next_to(self.title, direction=np.array([0, -1, 0]), buff=0.25)
        else:
            m.next_to(self.lines[-1], direction=np.array([0, -1, 0]), buff=CFG.LINE_SPACING)
        self.lines.add(m)
        m.set_opacity(0.0)
        return m  # return for staged reveal

    def reveal_last(self, run_time: float = 0.2):
        if len(self.lines) == 0:
            return
        self.scene.play(FadeIn(self.lines[-1], run_time=run_time))

    @property
    def scene(self):
        # Convenience to access scene play() in reveal methods via self.get_scene()
        # In practice we will call animations from the Scene directly; property kept for symmetry.
        from manim import Scene
        Scene  # silence lint
        # Real scene reference is not stored; callers should play on Scene.
        return None

# ---- Right Transform Pane ----
class RightTransformPane(VGroup):
    def __init__(self, title: str = "Transform", width: float = CFG.PANEL_WIDTH, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.bg = RoundedRectangle(corner_radius=0.2, width=width, height=3.5)
        self.title = Text(title, font_size=CFG.FONT_SIZE_RIGHT)
        self.title.next_to(self.bg.get_top(), direction=np.array([0, -1, 0]), buff=0.15)
        self.slot = VGroup()  # where we place the per-step token/equation fragment
        self.add(self.bg, self.title, self.slot)
        self.move_to(CFG.ANCHOR_RIGHT_PANE)

    def show_fragment(self, *tex_strings: str, scene=None, run_time: float = 0.25):
        new_line = MathTex(*tex_strings, font_size=CFG.FONT_SIZE_RIGHT)
        new_line.next_to(self.title, direction=np.array([0, -1, 0]), buff=0.25)
        if len(self.slot) > 0:
            old = self.slot[-1]
            if scene:
                scene.play(FadeIn(new_line, run_time=run_time))
                scene.remove(old)
        else:
            if scene:
                scene.play(FadeIn(new_line, run_time=run_time))
        self.slot.add(new_line)
        return new_line

# ---- Token helpers ----
def parts_by_substrings(mathtex: MathTex, substrings: Iterable[str]) -> List:
    """Return a list of submobjects that match any given TeX substring(s)."""
    hits = []
    for s in substrings:
        try:
            hits.extend(mathtex.get_parts_by_tex(s))
        except Exception:
            pass
    # De-dupe while keeping order
    seen = set()
    uniq = []
    for m in hits:
        if id(m) not in seen:
            uniq.append(m); seen.add(id(m))
    return uniq