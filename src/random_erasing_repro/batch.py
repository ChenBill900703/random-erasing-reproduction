from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONFIGS = (
    Path("configs/cifar10_resnet20_baseline.toml"),
    Path("configs/cifar10_resnet20_re_paper.toml"),
    Path("configs/cifar10_resnet20_re_author_code.toml"),
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--configs", type=Path, nargs="+", default=list(DEFAULT_CONFIGS))
    parser.add_argument(
        "--status-path",
        type=Path,
        default=None,
        help="Optional status JSON path; defaults to <output_root>/batch_status.json.",
    )
    return parser.parse_args()


def load_config(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        return tomllib.load(stream)


def write_status(path: Path, status: dict[str, Any]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(status, indent=2), encoding="utf-8")
    temporary.replace(path)


def completed_run_is_valid(run_dir: Path, experiment: str, seed: int) -> bool:
    metadata_path = run_dir / "metadata.json"
    summary_path = run_dir / "summary.json"
    metrics_path = run_dir / "metrics.csv"
    best_path = run_dir / "best.pt"
    if not all(path.exists() for path in (metadata_path, summary_path, metrics_path, best_path)):
        return False
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    return (
        metadata.get("seed") == seed
        and metadata.get("smoke") is False
        and metadata.get("config", {}).get("experiment", {}).get("name") == experiment
        and summary.get("is_paper_result") is False
    )


def main() -> None:
    args = parse_args()
    configs = [(path, load_config(path)) for path in args.configs]
    output_roots = {Path(config["runtime"]["output_root"]) for _, config in configs}
    if len(output_roots) != 1:
        raise ValueError("all configs must use the same output_root")
    output_root = output_roots.pop()
    output_root.mkdir(parents=True, exist_ok=True)
    status_path = args.status_path or output_root / "batch_status.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status: dict[str, Any] = {
        "state": "running",
        "started_at": utc_now(),
        "updated_at": utc_now(),
        "current": None,
        "completed": [],
        "skipped": [],
        "failed": None,
    }
    write_status(status_path, status)

    try:
        for config_path, config in configs:
            experiment = config["experiment"]["name"]
            for seed in config["experiment"]["seeds"]:
                run_dir = output_root / f"{experiment}_seed{seed}"
                item = {"experiment": experiment, "seed": seed}
                if completed_run_is_valid(run_dir, experiment, seed):
                    status["skipped"].append(item)
                    status["updated_at"] = utc_now()
                    write_status(status_path, status)
                    print(f"skip completed experiment={experiment} seed={seed}", flush=True)
                    continue

                status["current"] = {**item, "started_at": utc_now()}
                status["updated_at"] = utc_now()
                write_status(status_path, status)
                print(f"start experiment={experiment} seed={seed}", flush=True)
                subprocess.run(
                    [
                        sys.executable,
                        "-u",
                        "-m",
                        "random_erasing_repro.train",
                        "--config",
                        str(config_path),
                        "--seed",
                        str(seed),
                    ],
                    check=True,
                )
                if not completed_run_is_valid(run_dir, experiment, seed):
                    raise RuntimeError(f"run completed without valid artifacts: {run_dir}")
                status["completed"].append({**item, "finished_at": utc_now()})
                status["current"] = None
                status["updated_at"] = utc_now()
                write_status(status_path, status)

            subprocess.run(
                [
                    sys.executable,
                    "-u",
                    "-m",
                    "random_erasing_repro.summarize",
                    "--config",
                    str(config_path),
                ],
                check=True,
            )

        status["state"] = "completed"
        status["current"] = None
        status["finished_at"] = utc_now()
        status["updated_at"] = utc_now()
        write_status(status_path, status)
    except BaseException as error:
        status["state"] = "failed"
        status["failed"] = {
            "type": type(error).__name__,
            "message": str(error),
            "at": utc_now(),
        }
        status["updated_at"] = utc_now()
        write_status(status_path, status)
        raise


if __name__ == "__main__":
    main()
