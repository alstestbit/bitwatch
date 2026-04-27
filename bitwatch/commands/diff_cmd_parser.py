"""Thin re-export so cli.py can import add_subparser uniformly.

This module acts as the parser entry point for the 'diff' subcommand,
delegating all argument registration to the core diff_cmd module.
"""
from bitwatch.commands.diff_cmd import add_subparser  # noqa: F401

__all__ = ["add_subparser"]
