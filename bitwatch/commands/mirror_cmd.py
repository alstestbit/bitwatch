"""mirror command — manage and trigger target mirroring."""
from __future__ import annotations

import argparse
from pathlib import Path

from bitwatch import mirror as _mirror
from bitwatch.config import BitwatchConfig

_DEFAULT_MIRRORS = Path(".bitwatch_mirrors.json")


def add_subparser(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("mirror", help="manage file/directory mirroring")
    p.add_argument("action", choices=["list", "set", "remove", "run"])
    p.add_argument("--target", default=None, help="watch target name")
    p.add_argument("--dest", default=None, help="destination directory")
    p.add_argument("--mirrors-file", default=str(_DEFAULT_MIRRORS))
    p.add_argument("--config", default="bitwatch.json")
    p.set_defaults(func=run)


def run(args: argparse.Namespace) -> int:
    mpath = Path(args.mirrors_file)
    mirrors = _mirror.load_mirrors(mpath)

    if args.action == "list":
        if not mirrors:
            print("No mirrors configured.")
        else:
            for tgt, dest in mirrors.items():
                print(f"  {tgt} -> {dest}")
        return 0

    if args.action == "set":
        if not args.target or not args.dest:
            print("Error: --target and --dest required for set.")
            return 1
        mirrors[args.target] = args.dest
        _mirror.save_mirrors(mirrors, mpath)
        print(f"Mirror set: {args.target} -> {args.dest}")
        return 0

    if args.action == "remove":
        if not args.target:
            print("Error: --target required for remove.")
            return 1
        if args.target not in mirrors:
            print(f"No mirror for target '{args.target}'.")
            return 1
        del mirrors[args.target]
        _mirror.save_mirrors(mirrors, mpath)
        print(f"Mirror removed for '{args.target}'.")
        return 0

    if args.action == "run":
        cfg_path = Path(args.config)
        if not cfg_path.exists():
            print(f"Config not found: {cfg_path}")
            return 1
        cfg = BitwatchConfig.load(cfg_path)
        target_paths = {t.name: t.path for t in cfg.targets}
        ran = 0
        for tgt, dest in mirrors.items():
            src = target_paths.get(tgt)
            if src is None:
                print(f"Warning: target '{tgt}' not in config, skipping.")
                continue
            copied = _mirror.perform_mirror(src, dest)
            for c in copied:
                print(f"Mirrored: {c}")
            ran += len(copied)
        if ran == 0:
            print("Nothing mirrored.")
        return 0

    return 0
