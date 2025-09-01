# utils.py

from manim import *
from manim_voiceover.services.base import SpeechService
import os
import subprocess
import glob
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
    
# ─────────────────────────────────────────────────────────────────────────────
# HighlightController
# Keeps original colors, lets us clear all highlights before a new narration beat
# Compatible with Manim CE v0.19.0
# ─────────────────────────────────────────────────────────────────────────────
class HighlightController:
    def __init__(self):
        self._tracked = []

    def track(self, *mobjects: Mobject):
        \"\"\"Register mobjects so we can restore their original color later.\"\"\"
        for m in mobjects:
            if m is None:
                continue
            # Store (mobject, original_color)
            self._tracked.append((m, m.get_color()))
        return self

    def highlight(self, mobjects, color=YELLOW, run_time=0.3):
        \"\"\"Set color on a sequence of mobjects with a short animation.\"\"\"
        anims = []
       for m in mobjects:
            if m is None:
                continue
            anims.append(m.animate.set_color(color))
        return AnimationGroup(*anims, lag_ratio=0.05, run_time=run_time)

    def clear(self, run_time=0.3):
        \"\"\"Restore original colors for all tracked mobjects.\"\"\"
        anims = []
        for m, original in self._tracked:
            anims.append(m.animate.set_color(original))
        return AnimationGroup(*anims, lag_ratio=0.02, run_time=run_time)