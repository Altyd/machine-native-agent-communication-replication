#!/usr/bin/env python3
"""Summarize validation-battery exports for the paper."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"


BATTERIES = {
    "gpt-4o-mini original": DATA / "battery_gpt4o_mini.json",
    "gpt-5.4-mini replication": DATA / "battery_gpt54_mini.json",
}


def normalize_condition(condition: str) -> str:
    if condition in {"NUMERIC", "NUMERIC_V2"}:
        return "COMPRESSED-v2" if condition == "NUMERIC_V2" else "COMPRESSED-v1"
    if condition == "NATURAL_TERSE":
        return "NATURAL-TERSE"
    return condition


def flatten_runs(payload: dict) -> list[dict]:
    runs: list[dict] = []
    for suite, suite_runs in payload["results"].items():
        for run in suite_runs:
            item = dict(run)
            item["suite"] = suite
            item["paper_condition"] = normalize_condition(run["condition"])
            runs.append(item)
    return runs


def is_premature_natural_finalization(run: dict) -> bool:
    conversation = run.get("conversation") or []
    return (
        run.get("condition") == "NATURAL"
        and len(conversation) == 1
        and conversation[0].get("role") == "solver"
    )


def summarize(runs: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for run in runs:
        grouped[run["paper_condition"]].append(run)

    summary = {}
    for condition, items in sorted(grouped.items()):
        total = len(items)
        correct = sum(1 for item in items if item.get("correct"))
        tokens = sum(item.get("totalTokens", 0) for item in items) / total
        turns = sum(item.get("turns", 0) for item in items) / total
        summary[condition] = {
            "runs": total,
            "correct": correct,
            "accuracy": correct / total if total else 0.0,
            "avg_tokens": tokens,
            "avg_turns": turns,
        }
    return summary


def print_summary(title: str, summary: dict[str, dict]) -> None:
    print(f"\n## {title}")
    print("| Condition | Runs | Accuracy | Avg tokens | Avg turns |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for condition, row in summary.items():
        print(
            f"| {condition} | {row['runs']} | "
            f"{row['correct']}/{row['runs']} ({row['accuracy']:.1%}) | "
            f"{row['avg_tokens']:.2f} | {row['avg_turns']:.2f} |"
        )


def print_invalid_runs(runs: list[dict]) -> None:
    invalid = [run for run in runs if is_premature_natural_finalization(run)]
    if not invalid:
        return
    print("\n### Premature NATURAL Finalizations")
    print("| Suite | Run | Scenario | Expected | Correct | Tokens |")
    print("| --- | ---: | --- | --- | --- | ---: |")
    for run in invalid:
        print(
            f"| {run.get('suite')} | {run.get('runNum')} | "
            f"{run.get('scenarioId', '')} | {run.get('expectedAnswer', '')} | "
            f"{run.get('correct')} | {run.get('totalTokens', 0)} |"
        )


def print_suite_d_breakdown(runs: list[dict], title: str) -> None:
    suite_d = [run for run in runs if run.get("suite") == "D"]
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for run in suite_d:
        grouped[(run["paper_condition"], run.get("scenarioId", ""))].append(run)
    if not grouped:
        return
    print(f"\n### {title} Suite D By Scenario")
    print("| Condition | Scenario | Accuracy |")
    print("| --- | --- | ---: |")
    for (condition, scenario), items in sorted(grouped.items()):
        correct = sum(1 for item in items if item.get("correct"))
        print(f"| {condition} | {scenario} | {correct}/{len(items)} |")


def main() -> None:
    for title, path in BATTERIES.items():
        payload = json.loads(path.read_text())
        runs = flatten_runs(payload)
        print_summary(f"{title} raw aggregate", summarize(runs))
        print_invalid_runs(runs)

        adjusted = [
            run for run in runs
            if not is_premature_natural_finalization(run)
        ]
        print_summary(f"{title} adjusted aggregate", summarize(adjusted))
        print_suite_d_breakdown(adjusted, title)


if __name__ == "__main__":
    main()
