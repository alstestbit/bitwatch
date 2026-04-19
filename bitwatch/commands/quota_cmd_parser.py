"""Thin re-export so cli.py can discover the quota subparser."""
from bitwatch.commands.quota_cmd import add_subparser  # noqa: F401
