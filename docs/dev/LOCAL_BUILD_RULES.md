Status: DERIVED
Last Reviewed: 2026-02-06
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Local Build Rules (BUILD-ID-0 Stage 2)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


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

Host equivalents
- Linux daily-use presets: `linux-gcc-dev` and `linux-verify`
- macOS daily-use presets: `macos-dev` and `macos-verify`
- Set `DOMINIUM_ADVANCED_PRESETS=1` to expose non-default toolchains and legacy/IDE projection presets.

Commands
- Build: cmake --build --preset local
- Verify: ctest --preset verify --output-on-failure
- Release check: python scripts/repox/repox_release.py --kind beta --channel beta --dry-run --ctest-preset verify
