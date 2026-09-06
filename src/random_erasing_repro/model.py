from __future__ import annotations

import math

import torch
from torch import nn


def _conv3x3(in_channels: int, out_channels: int, stride: int = 1) -> nn.Conv2d:
    return nn.Conv2d(
        in_channels,
        out_channels,
        kernel_size=3,
        stride=stride,
        padding=1,
        bias=False,
    )


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(
        self,
        in_channels: int,
        channels: int,
        stride: int = 1,
        downsample: nn.Module | None = None,
    ) -> None:
        super().__init__()
        self.conv1 = _conv3x3(in_channels, channels, stride)
        self.bn1 = nn.BatchNorm2d(channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = _conv3x3(channels, channels)
        self.bn2 = nn.BatchNorm2d(channels)
        self.downsample = downsample

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        residual = inputs
        outputs = self.relu(self.bn1(self.conv1(inputs)))
        outputs = self.bn2(self.conv2(outputs))
        if self.downsample is not None:
            residual = self.downsample(inputs)
        return self.relu(outputs + residual)


class CifarResNet(nn.Module):
    """Small-image ResNet matching the author's CIFAR/Fashion implementation."""

    def __init__(
        self,
        depth: int = 20,
        num_classes: int = 10,
        input_channels: int = 3,
        image_size: int = 32,
    ) -> None:
        super().__init__()
        if (depth - 2) % 6 != 0:
            raise ValueError("depth must be 6n+2")
        if depth >= 44:
            raise ValueError(
                "This modern path currently validates BasicBlock depths below 44 only; "
                "the author repository switches to Bottleneck at depth 44 and must be "
                "audited separately before reproducing deeper rows."
            )

        blocks_per_stage = (depth - 2) // 6
        self.in_channels = 16
        self.conv1 = nn.Conv2d(
            input_channels, 16, kernel_size=3, padding=1, bias=False
        )
        self.bn1 = nn.BatchNorm2d(16)
        self.relu = nn.ReLU(inplace=True)
        self.layer1 = self._make_layer(16, blocks_per_stage)
        self.layer2 = self._make_layer(32, blocks_per_stage, stride=2)
        self.layer3 = self._make_layer(64, blocks_per_stage, stride=2)
        if image_size not in {28, 32}:
            raise ValueError("verified image_size values are 28 and 32")
        self.avgpool = nn.AvgPool2d(image_size // 4)
        self.fc = nn.Linear(64, num_classes)

        for module in self.modules():
            if isinstance(module, nn.Conv2d):
                fan_out = (
                    module.kernel_size[0]
                    * module.kernel_size[1]
                    * module.out_channels
                )
                nn.init.normal_(module.weight, 0.0, math.sqrt(2.0 / fan_out))
            elif isinstance(module, nn.BatchNorm2d):
                nn.init.ones_(module.weight)
                nn.init.zeros_(module.bias)

    def _make_layer(
        self, channels: int, blocks: int, stride: int = 1
    ) -> nn.Sequential:
        downsample = None
        if stride != 1 or self.in_channels != channels:
            downsample = nn.Sequential(
                nn.Conv2d(
                    self.in_channels,
                    channels,
                    kernel_size=1,
                    stride=stride,
                    bias=False,
                ),
                nn.BatchNorm2d(channels),
            )
        layers: list[nn.Module] = [
            BasicBlock(self.in_channels, channels, stride, downsample)
        ]
        self.in_channels = channels
        layers.extend(BasicBlock(channels, channels) for _ in range(1, blocks))
        return nn.Sequential(*layers)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        outputs = self.relu(self.bn1(self.conv1(inputs)))
        outputs = self.layer1(outputs)
        outputs = self.layer2(outputs)
        outputs = self.layer3(outputs)
        outputs = self.avgpool(outputs)
        return self.fc(torch.flatten(outputs, 1))
