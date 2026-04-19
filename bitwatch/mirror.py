"""Mirror: track which targets are being mirrored to a backup path."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List

_DEFAULT = Path(".bitwatch_mirrors.json")


def load_mirrors(path: Path = _DEFAULT) -> Dict[str, str]:
    """Return {target: dest} mapping."""
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def save_mirrors(mirrors: Dict[str, str], path: Path = _DEFAULT) -> None:
    path.write_text(json.dumps(mirrors, indent=2))


def mirror_path(target: str, mirrors: Dict[str, str]) -> str | None:
    """Return the destination for *target*, or None."""
    return mirrors.get(target)


def perform_mirror(src: str, dest: str) -> List[str]:
    """Copy *src* into *dest*, returning list of copied paths."""
    src_p = Path(src)
    dest_p = Path(dest)
    copied: List[str] = []
    if not src_p.exists():
        return copied
    if src_p.is_file():
        dest_p.mkdir(parents=True, exist_ok=True)
        out = dest_p / src_p.name
        shutil.copy2(src_p, out)
        copied.append(str(out))
    elif src_p.is_dir():
        out_dir = dest_p / src_p.name
        if out_dir.exists():
            shutil.rmtree(out_dir)
        shutil.copytree(src_p, out_dir)
        copied.append(str(out_dir))
    return copied
