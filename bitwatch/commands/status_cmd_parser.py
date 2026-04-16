"""Thin shim so the CLI can import a consistent add_subparser symbol."""
from bitwatch.commands.status_cmd import add_subparser  # noqa: F401
