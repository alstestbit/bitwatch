"""Thin registration shim so snapshot_cmd integrates with the main CLI."""

from __future__ import annotations

# Re-export for uniform command discovery used by cli.py
from bitwatch.commands.snapshot_cmd import add_subparser, run

__all__ = ["add_subparser", "run"]
