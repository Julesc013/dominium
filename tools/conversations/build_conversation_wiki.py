"""Build Phase 4 conversation wiki surfaces."""

import sys

from conversation_corpus import main


if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "wiki"]))
