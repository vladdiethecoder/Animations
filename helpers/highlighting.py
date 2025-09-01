# [CHECKPOINT-1..5 Active; Mirrors CHECKPOINTS.md]
# WHY: Centralized highlight control avoids FM-2 (lingering updaters) and FM-4 (z-order).
# Manim CE v0.19.0-compatible.
from __future__ import annotations
from typing import Iterable, List, Optional
from manim import VGroup, SurroundingRectangle, AnimationGroup, FadeOut, Create


class HighlightGroupController:
    """
    Ensures only ONE highlight group is active at a time.
    - activate(targets): clears previous, highlights new targets
    - clear(): remove current highlights
    WHY: Checkpoint-1 Regression Guard; FM-2/4 safety.
    """
    def __init__(self, scene, color, stroke_width=4, fill_opacity=0.0, buff=0.08, z_index=10):
        self.scene = scene
        self.style = dict(color=color, stroke_width=stroke_width, fill_opacity=fill_opacity, buff=buff)
        self.active: Optional[VGroup] = None
        self.z_index = z_index

    def _build_group(self, targets: Iterable) -> VGroup:
        boxes: List[SurroundingRectangle] = []
        for t in targets:
            rect = SurroundingRectangle(t, **self.style)
            rect.set_z_index(self.z_index)
            boxes.append(rect)
        return VGroup(*boxes)

    def clear(self, fade_time: float = 0.2):
        if self.active:
            self.scene.play(AnimationGroup(*(FadeOut(m) for m in self.active), lag_ratio=0.0, run_time=fade_time))
            for m in list(self.active):
                try:
                    self.scene.remove(m)
                except Exception:
                    pass
            self.active = None

    def activate(self, targets: Iterable, run_time: float = 0.25):
        self.clear(fade_time=0.1)
        group = self._build_group(targets)
        self.active = group
        self.scene.add(group)
        self.scene.play(AnimationGroup(*(Create(m) for m in group), lag_ratio=0.05, run_time=run_time))
