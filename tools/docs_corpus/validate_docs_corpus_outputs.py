"""Validate generated docs-corpus outputs."""

from __future__ import annotations

import sys

from docs_corpus import main


if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "validate"]))
