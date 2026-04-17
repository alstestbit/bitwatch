"""Thin re-export so cli.py can discover replay via a uniform pattern."""
from bitwatch.commands.replay_cmd import add_subparser, run

__all__ = ["add_subparser", "run"]
