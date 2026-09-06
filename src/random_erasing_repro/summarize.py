from __future__ import annotations

import argparse
import json
import statistics
import tomllib
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def stats(values: list[float]) -> dict[str, Any]:
    return {
        "values": values,
        "mean": statistics.mean(values),
        "population_std": statistics.pstdev(values),
        "sample_std": statistics.stdev(values) if len(values) > 1 else None,
    }


def main() -> None:
    args = parse_args()
    with args.config.open("rb") as stream:
        config = tomllib.load(stream)

    experiment = config["experiment"]
    output_root = Path(config["runtime"]["output_root"])
    summaries = []
    for seed in experiment["seeds"]:
        suffix = "_smoke" if args.smoke else ""
        path = output_root / f"{experiment['name']}_seed{seed}{suffix}" / "summary.json"
        if not path.exists():
            raise FileNotFoundError(f"missing run summary: {path}")
        summaries.append(json.loads(path.read_text(encoding="utf-8")))

    aggregate = {
        "experiment": experiment["name"],
        "seeds": experiment["seeds"],
        "smoke": args.smoke,
        "is_paper_result": False,
        "best_error_rate": stats([row["best_error_rate"] for row in summaries]),
        "final_error_rate": stats([row["final_error_rate"] for row in summaries]),
        "note": (
            "Smoke aggregates are structural checks only."
            if args.smoke
            else "New reproduction aggregate; paper does not state best-vs-final or std convention."
        ),
    }
    output = output_root / f"{experiment['name']}_aggregate{'_smoke' if args.smoke else ''}.json"
    output.write_text(json.dumps(aggregate, indent=2), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))


if __name__ == "__main__":
    main()

