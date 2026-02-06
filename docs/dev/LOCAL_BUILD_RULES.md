Status: DERIVED
Last Reviewed: 2026-02-06
Supersedes: none
Superseded By: none

# Local Build Rules (BUILD-ID-0 Stage 2)

Local builds are non-distributable and must never allocate a GBN.
All local and CI builds must stamp a BII and report build_gbn=none.

Presets
- LOCAL (preset name: local)
  - fast dev build
  - minimal tests
  - gbn=none, bii stamped
- VERIFY (preset name: verify)
  - strict warnings-as-errors
  - determinism + schema + replay hash tests
  - gbn=none
- RELEASE-CHECK (preset name: release-check)
  - dry-run repox release
  - generates preview artifacts only
  - gbn=none

Commands
- Build: cmake --build --preset local
- Verify: ctest --preset verify --output-on-failure
- Release check: python scripts/repox/repox_release.py --kind beta --channel beta --dry-run --ctest-preset verify
