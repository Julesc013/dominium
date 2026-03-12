Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Offline and Air-Gapped Operation (DEV-OPS-0)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


Scope: offline development, updates, and distribution.

Development (offline)
- Use pre-fetched dependencies or vendored archives.
- Configure CMake with:
  - DOM_DISALLOW_DOWNLOADS=ON
  - FETCHCONTENT_FULLY_DISCONNECTED=ON
  - FETCHCONTENT_UPDATES_DISCONNECTED=ON

Updates (offline)
- Use bundle files created by RepoX release tooling.
- Apply updates via Setup in offline mode.

LAN mirrors
- Host update feeds and bundles on a local mirror.
- Point launcher/setup to the mirror via config.

Rules
- No mandatory cloud dependency.
- All offline operations must be deterministic.
