import torch

from random_erasing_repro.model import CifarResNet


def test_resnet20_shape_and_parameter_count() -> None:
    model = CifarResNet(depth=20, num_classes=10)
    assert sum(parameter.numel() for parameter in model.parameters()) == 272_474
    assert model(torch.randn(2, 3, 32, 32)).shape == (2, 10)


def test_resnet32_cifar100_shape() -> None:
    model = CifarResNet(depth=32, num_classes=100)
    assert model(torch.randn(2, 3, 32, 32)).shape == (2, 100)


def test_resnet20_fashion_shape_and_parameter_count() -> None:
    model = CifarResNet(
        depth=20, num_classes=10, input_channels=1, image_size=28
    )
    assert sum(parameter.numel() for parameter in model.parameters()) == 272_186
    assert model(torch.randn(2, 1, 28, 28)).shape == (2, 10)
