"""Thin re-export so cli.py can discover the subparser uniformly."""
from bitwatch.commands.alert_cmd import add_subparser  # noqa: F401
