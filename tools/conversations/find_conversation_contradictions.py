"""Build Phase 3 conversation contradiction and promotion reports."""

import sys

from conversation_corpus import main


if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "audit"]))
