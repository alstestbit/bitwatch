"""Thin re-export so cli.py can discover the archive subcommand.

This module acts as the entry point for the 'archive' subcommand within
the CLI dispatch system. It re-exports `add_subparser` from the
implementation module so that the CLI loader only needs to import from
a consistent location pattern across all command packages.
"""
from bitwatch.commands.archive_cmd import add_subparser  # noqa: F401
