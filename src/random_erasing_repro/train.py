from __future__ import annotations

import argparse
import csv
import json
import platform
import random
import sys
import time
import tomllib
from pathlib import Path
from typing import Any

import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from .erasing import RandomErasing
from .model import CifarResNet


CIFAR10_MEAN = (0.4914, 0.4822, 0.4465)
CIFAR10_STD = (0.2023, 0.1994, 0.2010)
FASHION_MNIST_MEAN = (0.1307,)
FASHION_MNIST_STD = (0.3081,)


DATASETS: dict[str, dict[str, Any]] = {
    "cifar10": {
        "loader": datasets.CIFAR10,
        "num_classes": 10,
        "image_size": 32,
        "input_channels": 3,
        "mean": CIFAR10_MEAN,
        "std": CIFAR10_STD,
    },
    "cifar100": {
        "loader": datasets.CIFAR100,
        "num_classes": 100,
        "image_size": 32,
        "input_channels": 3,
        # The paper-time author code deliberately uses the CIFAR-10 values.
        "mean": CIFAR10_MEAN,
        "std": CIFAR10_STD,
    },
    "fashionmnist": {
        "loader": datasets.FashionMNIST,
        "num_classes": 10,
        "image_size": 28,
        "input_channels": 1,
        # These are the constants in the paper-time Fashion-MNIST script.
        "mean": FASHION_MNIST_MEAN,
        "std": FASHION_MNIST_STD,
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--device", choices=("auto", "cpu", "cuda"), default="auto")
    parser.add_argument(
        "--smoke",
        action="store_true",
        help="Use deterministic synthetic data for one epoch; does not test accuracy.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def select_device(requested: str) -> torch.device:
    if requested == "cpu":
        return torch.device("cpu")
    if requested == "cuda":
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available")
        return torch.device("cuda")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def seed_everything(seed: int, deterministic: bool) -> None:
    random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = not deterministic
    torch.backends.cudnn.deterministic = deterministic
    if deterministic:
        torch.use_deterministic_algorithms(True)


def seed_worker(worker_id: int) -> None:
    del worker_id
    # DataLoader derives a new deterministic seed from its generator each time
    # workers start. Mirroring it into Python's RNG keeps augmentation varied
    # across epochs but reproducible across equivalent runs.
    random.seed(torch.initial_seed() % (2**32))


def build_transforms(config: dict[str, Any]) -> tuple[transforms.Compose, transforms.Compose]:
    augmentation = config["augmentation"]
    erasing = config["erasing"]
    dataset_name = config["dataset"]["name"]
    if dataset_name not in DATASETS:
        raise ValueError(f"unsupported dataset: {dataset_name}")
    dataset_spec = DATASETS[dataset_name]
    train_steps: list[Any] = []
    if augmentation["random_crop"]:
        train_steps.append(
            transforms.RandomCrop(augmentation["crop_size"], padding=augmentation["padding"])
        )
    if augmentation["horizontal_flip"]:
        train_steps.append(transforms.RandomHorizontalFlip())
    train_steps.append(transforms.ToTensor())

    common_erasing = {
        "probability": erasing["probability"],
        "min_area": erasing["min_area"],
        "max_area": erasing["max_area"],
        "min_aspect": erasing["min_aspect"],
        "trials": erasing["trials"],
    }
    if erasing["mode"] == "paper_random":
        train_steps.append(RandomErasing(mode="paper_random", **common_erasing))
    train_steps.append(transforms.Normalize(dataset_spec["mean"], dataset_spec["std"]))
    if erasing["mode"] == "author_constant":
        train_steps.append(
            RandomErasing(
                mode="author_constant",
                channel_values=erasing["channel_values"],
                **common_erasing,
            )
        )
    if erasing["mode"] not in {"off", "paper_random", "author_constant"}:
        raise ValueError(f"unsupported erasing mode: {erasing['mode']}")

    test_steps = [
        transforms.ToTensor(),
        transforms.Normalize(dataset_spec["mean"], dataset_spec["std"]),
    ]
    return transforms.Compose(train_steps), transforms.Compose(test_steps)


def build_loaders(
    config: dict[str, Any], seed: int, smoke: bool
) -> tuple[DataLoader, DataLoader]:
    training = config["training"]
    generator = torch.Generator().manual_seed(seed)
    train_transform, test_transform = build_transforms(config)
    dataset_name = config["dataset"]["name"]
    if dataset_name not in DATASETS:
        raise ValueError(f"unsupported dataset: {dataset_name}")
    dataset_spec = DATASETS[dataset_name]
    if smoke:
        train_dataset = datasets.FakeData(
            size=64,
            image_size=(
                dataset_spec["input_channels"],
                dataset_spec["image_size"],
                dataset_spec["image_size"],
            ),
            num_classes=dataset_spec["num_classes"],
            transform=train_transform,
            random_offset=seed,
        )
        test_dataset = datasets.FakeData(
            size=64,
            image_size=(
                dataset_spec["input_channels"],
                dataset_spec["image_size"],
                dataset_spec["image_size"],
            ),
            num_classes=dataset_spec["num_classes"],
            transform=test_transform,
            random_offset=seed + 10_000,
        )
        return (
            DataLoader(train_dataset, batch_size=16, shuffle=True, generator=generator),
            DataLoader(test_dataset, batch_size=16, shuffle=False),
        )

    root = config["dataset"]["root"]
    dataset_loader = dataset_spec["loader"]
    train_dataset = dataset_loader(
        root=root,
        train=True,
        download=config["dataset"]["download"],
        transform=train_transform,
    )
    test_dataset = dataset_loader(
        root=root,
        train=False,
        download=config["dataset"]["download"],
        transform=test_transform,
    )
    return (
        DataLoader(
            train_dataset,
            batch_size=training["train_batch_size"],
            shuffle=True,
            num_workers=training["workers"],
            pin_memory=True,
            worker_init_fn=seed_worker,
            generator=generator,
            persistent_workers=training["workers"] > 0,
        ),
        DataLoader(
            test_dataset,
            batch_size=training["test_batch_size"],
            shuffle=False,
            num_workers=training["workers"],
            pin_memory=True,
            worker_init_fn=seed_worker,
            persistent_workers=training["workers"] > 0,
        ),
    )


def run_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    optimizer: torch.optim.Optimizer | None,
) -> tuple[float, float]:
    training = optimizer is not None
    model.train(training)
    loss_sum = 0.0
    correct = 0
    sample_count = 0
    context = torch.enable_grad() if training else torch.inference_mode()
    with context:
        for inputs, targets in loader:
            inputs = inputs.to(device, non_blocking=True)
            targets = targets.to(device, non_blocking=True)
            if optimizer is not None:
                optimizer.zero_grad(set_to_none=True)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            if optimizer is not None:
                loss.backward()
                optimizer.step()
            batch_size = targets.size(0)
            loss_sum += loss.item() * batch_size
            correct += (outputs.argmax(dim=1) == targets).sum().item()
            sample_count += batch_size
    return loss_sum / sample_count, 100.0 * correct / sample_count


def environment_record(device: torch.device) -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "torchvision": __import__("torchvision").__version__,
        "device": str(device),
        "gpu": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
        "cuda_runtime": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
    }


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    deterministic = config["runtime"]["deterministic"]
    seed_everything(args.seed, deterministic)
    device = select_device(args.device)
    train_loader, test_loader = build_loaders(config, args.seed, args.smoke)

    dataset_name = config["dataset"]["name"]
    if dataset_name not in DATASETS:
        raise ValueError(f"unsupported dataset: {dataset_name}")
    dataset_spec = DATASETS[dataset_name]
    model = CifarResNet(
        depth=config["model"]["depth"],
        num_classes=dataset_spec["num_classes"],
        input_channels=dataset_spec["input_channels"],
        image_size=dataset_spec["image_size"],
    ).to(device)
    criterion = nn.CrossEntropyLoss()
    training = config["training"]
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=training["learning_rate"],
        momentum=training["momentum"],
        weight_decay=training["weight_decay"],
    )
    scheduler = torch.optim.lr_scheduler.MultiStepLR(
        optimizer,
        milestones=training["milestones"],
        gamma=training["gamma"],
    )

    run_name = f"{config['experiment']['name']}_seed{args.seed}"
    if args.smoke:
        run_name += "_smoke"
    run_dir = Path(config["runtime"]["output_root"]) / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    metadata = {
        "config_path": str(args.config),
        "config": config,
        "seed": args.seed,
        "smoke": args.smoke,
        "environment": environment_record(device),
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    epochs = 1 if args.smoke else training["epochs"]
    best_accuracy = 0.0
    final_accuracy = 0.0
    started = time.time()
    with (run_dir / "metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=("epoch", "learning_rate", "train_loss", "train_accuracy", "test_loss", "test_accuracy"),
        )
        writer.writeheader()
        for epoch in range(epochs):
            learning_rate = optimizer.param_groups[0]["lr"]
            train_loss, train_accuracy = run_epoch(
                model, train_loader, criterion, device, optimizer
            )
            test_loss, test_accuracy = run_epoch(
                model, test_loader, criterion, device, optimizer=None
            )
            scheduler.step()
            writer.writerow(
                {
                    "epoch": epoch + 1,
                    "learning_rate": learning_rate,
                    "train_loss": train_loss,
                    "train_accuracy": train_accuracy,
                    "test_loss": test_loss,
                    "test_accuracy": test_accuracy,
                }
            )
            stream.flush()
            if test_accuracy > best_accuracy:
                best_accuracy = test_accuracy
                torch.save(model.state_dict(), run_dir / "best.pt")
            final_accuracy = test_accuracy
            print(
                f"epoch={epoch + 1}/{epochs} lr={learning_rate:.5f} "
                f"train_acc={train_accuracy:.2f} test_acc={test_accuracy:.2f}",
                flush=True,
            )

    summary = {
        "best_accuracy": best_accuracy,
        "best_error_rate": 100.0 - best_accuracy,
        "final_accuracy": final_accuracy,
        "final_error_rate": 100.0 - final_accuracy,
        "elapsed_seconds": time.time() - started,
        "is_paper_result": False,
        "note": "Smoke results are structural checks only." if args.smoke else "New reproduction result; compare against paper target separately.",
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
