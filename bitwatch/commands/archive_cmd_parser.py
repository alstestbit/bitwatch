"""Thin re-export so cli.py can discover the archive subcommand."""
from bitwatch.commands.archive_cmd import add_subparser  # noqa: F401
