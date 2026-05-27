"""Build Phase 2 conversation reader pages."""

import sys

from conversation_corpus import main


if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "readers"]))
