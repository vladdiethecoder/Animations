from __future__ import annotations
from typing import Dict, Iterable, Set
from manim import *

class Highlighter:
    """
    v0.19.0-safe highlight controller.
    Register mobjects under one or more tags, then call highlight_only(tags).
    """
    def __init__(self, scene: Scene, dim_opacity: float = 0.35, bright_opacity: float = 1.0,
                 dim_scale: float = 1.00, bright_scale: float = 1.00,
                 bright_color: str = YELLOW, dim_color: str | None = None,
                 run_time: float = 0.35):
        self.scene = scene
        self.run_time = run_time
        self.dim_opacity = dim_opacity
        self.bright_opacity = bright_opacity
        self.dim_scale = dim_scale
        self.bright_scale = bright_scale
        self.bright_color = bright_color
        self.dim_color = dim_color
        self._registry: Dict[str, VGroup] = {}

    def register(self, tag: str, *mobs: Mobject) -> None:
        if tag not in self._registry:
            self._registry[tag] = VGroup()
        self._registry[tag].add(*mobs)

    def register_many(self, mapping: Dict[str, Iterable[Mobject]]) -> None:
        for tag, it in mapping.items():
            self.register(tag, *list(it))

    def all_mobs(self) -> VGroup:
        vg = VGroup()
        for g in self._registry.values():
            vg.add(*g.submobjects)
        return vg

    def unhighlight_all(self) -> AnimationGroup:
        anims = []
        for mob in self.all_mobs():
            anims.append(
                AnimationGroup(
                    mob.animate.set_opacity(self.dim_opacity).set_sheen(0),
                    mob.animate.scale(self.dim_scale),
                )
            )
            if self.dim_color is not None:
                anims[-1].animations.append(mob.animate.set_color(self.dim_color))
        return AnimationGroup(*anims, lag_ratio=0.0, run_time=self.run_time)

    def highlight_only(self, tags: Iterable[str]) -> AnimationGroup:
        tags_set: Set[str] = set(tags)
        on = VGroup()
        for t in tags_set:
            if t in self._registry:
                on.add(*self._registry[t].submobjects)
        off = VGroup(*[m for m in self.all_mobs() if m not in on.submobjects])

        anims = []
        # Dim non-selected
        for mob in off:
            anims.append(mob.animate.set_opacity(self.dim_opacity).scale(self.dim_scale))
            if self.dim_color is not None:
                anims[-1].set_anim_args(run_time=self.run_time)
        # Brighten selected
        for mob in on:
            anims.append(
                mob.animate.set_opacity(self.bright_opacity)
                   .set_color(self.bright_color)
                   .scale(self.bright_scale)
            )
        return AnimationGroup(*anims, lag_ratio=0.0, run_time=self.run_time, rate_func=smooth)
