"""Build Phase 1 conversation corpus inventory artifacts."""

import sys

from conversation_corpus import main


if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "inventory"]))
