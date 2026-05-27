"""Generate reconciliation and promotion-triage surfaces for the conversation corpus."""

import sys

from conversation_corpus import main


if __name__ == "__main__":
    raise SystemExit(main([*sys.argv[1:], "reconciliation"]))
