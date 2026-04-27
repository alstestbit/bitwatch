"""Thin shim so cli.py can discover the anomaly sub-command parser."""

from bitwatch.commands.anomaly_cmd import add_subparser

__all__ = ["add_subparser"]
