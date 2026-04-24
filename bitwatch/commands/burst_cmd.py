"""CLI command: burst — detect rapid event clusters."""

from __future__ import annotations

import argparse
from pathlib import Path

from bitwatch.history import load_history
from bitwatch import burst as burst_lib

_DEFAULT_CONFIG = Path(".bitwatch_burst.json")


def add_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("burst", help="Detect rapid clusters of file-change events")
    p.add_argument("--history", default=None, help="Path to history file")
    p.add_argument("--window", type=int, default=60, help="Time window in seconds (default: 60)")
    p.add_argument("--threshold", type=int, default=5, help="Minimum events to trigger burst (default: 5)")
    p.add_argument("--target", default=None, help="Check a specific target only")
    p.add_argument("--config", default=str(_DEFAULT_CONFIG), help="Burst config file")
    p.add_argument("--set-window", type=int, default=None, dest="set_window", help="Persist window setting")
    p.add_argument("--set-threshold", type=int, default=None, dest="set_threshold", help="Persist threshold setting")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    cfg_path = Path(args.config)
    cfg = burst_lib.load_config(cfg_path)

    if args.set_window is not None:
        cfg["window"] = args.set_window
        burst_lib.save_config(cfg, cfg_path)
        print(f"Burst window set to {args.set_window}s")
        return 0

    if args.set_threshold is not None:
        cfg["threshold"] = args.set_threshold
        burst_lib.save_config(cfg, cfg_path)
        print(f"Burst threshold set to {args.set_threshold}")
        return 0

    window = args.window if args.window != 60 else int(cfg.get("window", args.window))
    threshold = args.threshold if args.threshold != 5 else int(cfg.get("threshold", args.threshold))

    history_path = Path(args.history) if args.history else None
    history = load_history(history_path)

    if not history:
        print("No history found.")
        return 0

    if args.target:
        in_burst = burst_lib.detect_burst(history, args.target, window, threshold)
        if in_burst:
            count = sum(
                1 for e in history if e.get("target") == args.target
            )
            print(f"BURST detected for '{args.target}': {count} events in last {window}s")
        else:
            print(f"No burst detected for '{args.target}'.")
        return 0

    summary = burst_lib.burst_summary(history, window, threshold)
    if not summary:
        print(f"No bursts detected (window={window}s, threshold={threshold}).")
        return 0

    print(f"Bursts detected (window={window}s, threshold={threshold}):")
    for target, count in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {target}: {count} events")
    return 0
