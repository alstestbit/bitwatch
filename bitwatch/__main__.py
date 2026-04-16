"""Allow running bitwatch as a module: python -m bitwatch."""

import sys

from bitwatch.cli import main

if __name__ == "__main__":
    sys.exit(main())
