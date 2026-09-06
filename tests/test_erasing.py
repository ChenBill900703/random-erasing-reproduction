import random

import torch

from random_erasing_repro.erasing import RandomErasing


def test_probability_zero_keeps_tensor_unchanged() -> None:
    image = torch.zeros(3, 32, 32)
    output = RandomErasing(probability=0.0)(image.clone())
    assert torch.equal(output, image)


def test_paper_random_changes_a_rectangular_region() -> None:
    random.seed(7)
    torch.manual_seed(7)
    image = torch.zeros(3, 32, 32)
    output = RandomErasing(
        probability=1.0,
        min_area=0.2,
        max_area=0.2,
        min_aspect=1.0,
        mode="paper_random",
    )(image)
    assert torch.count_nonzero(output) > 0
    assert output.min() >= 0.0
    assert output.max() <= 1.0


def test_author_constant_writes_exact_channel_values() -> None:
    random.seed(11)
    image = torch.zeros(3, 32, 32)
    values = (0.4914, 0.4822, 0.4465)
    output = RandomErasing(
        probability=1.0,
        min_area=0.2,
        max_area=0.2,
        min_aspect=1.0,
        mode="author_constant",
        channel_values=values,
    )(image)
    for channel, value in enumerate(values):
        assert torch.any(output[channel] == value)

