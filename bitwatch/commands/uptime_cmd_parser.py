"""Thin re-export so cli.py can discover the uptime subcommand uniformly."""

from bitwatch.commands.uptime_cmd import add_subparser  # noqa: F401
