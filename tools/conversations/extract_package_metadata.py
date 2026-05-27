"""Alias for Phase 1 package metadata extraction."""

import sys

from conversation_corpus import main


if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "inventory"]))
