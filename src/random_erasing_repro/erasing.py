from __future__ import annotations

import math
import random
from collections.abc import Sequence

import torch


class RandomErasing:
    """Random Erasing geometry from Algorithm 1 and the paper-time author code.

    ``paper_random`` writes independent U(0, 1) values to a tensor before
    normalization, corresponding to the paper's Rand(0, 255) on raw pixels.
    ``author_constant`` writes fixed channel values after normalization, matching
    commit ddae4ed's training pipeline and transforms.py.
    """

    def __init__(
        self,
        probability: float = 0.5,
        min_area: float = 0.02,
        max_area: float = 0.4,
        min_aspect: float = 0.3,
        mode: str = "paper_random",
        channel_values: Sequence[float] = (0.4914, 0.4822, 0.4465),
        trials: int = 100,
    ) -> None:
        if not 0.0 <= probability <= 1.0:
            raise ValueError("probability must be in [0, 1]")
        if not 0.0 < min_area <= max_area <= 1.0:
            raise ValueError("area bounds must satisfy 0 < min_area <= max_area <= 1")
        if not 0.0 < min_aspect <= 1.0:
            raise ValueError("min_aspect must be in (0, 1]")
        if mode not in {"paper_random", "author_constant"}:
            raise ValueError(f"unsupported erasing mode: {mode}")
        if trials < 1:
            raise ValueError("trials must be positive")

        self.probability = probability
        self.min_area = min_area
        self.max_area = max_area
        self.min_aspect = min_aspect
        self.mode = mode
        self.channel_values = tuple(float(value) for value in channel_values)
        self.trials = trials

    def __call__(self, image: torch.Tensor) -> torch.Tensor:
        if image.ndim != 3:
            raise ValueError("RandomErasing expects a CHW tensor")
        if random.uniform(0.0, 1.0) > self.probability:
            return image

        channels, height, width = image.shape
        area = height * width

        for _ in range(self.trials):
            target_area = random.uniform(self.min_area, self.max_area) * area
            aspect_ratio = random.uniform(self.min_aspect, 1.0 / self.min_aspect)
            erase_height = int(round(math.sqrt(target_area * aspect_ratio)))
            erase_width = int(round(math.sqrt(target_area / aspect_ratio)))

            # Algorithm 1 and the 2017-09-25 author commit both use <=.
            if erase_width <= width and erase_height <= height:
                top = random.randint(0, height - erase_height)
                left = random.randint(0, width - erase_width)
                region = image[:, top : top + erase_height, left : left + erase_width]

                if self.mode == "paper_random":
                    region.copy_(torch.rand_like(region))
                else:
                    if len(self.channel_values) not in {1, channels}:
                        raise ValueError(
                            "channel_values must contain one value or one per channel"
                        )
                    values = self.channel_values
                    if len(values) == 1:
                        values = values * channels
                    fill = image.new_tensor(values).view(channels, 1, 1)
                    region.copy_(fill.expand_as(region))
                return image

        return image

