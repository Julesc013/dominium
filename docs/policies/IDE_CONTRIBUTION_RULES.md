Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# IDE Contribution Rules (REPOX)

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






Status: binding.


Scope: IDE projections and contribution hygiene.





## Core rules


- IDE project files MUST NOT be committed outside `/ide/**` or documented packaging inputs.


- Generated IDE outputs are disposable; regenerate instead of editing.


- Core logic is not edited through legacy IDE projects.


- UI shell work stays within UI shell directories and stable C ABI boundaries.





## Projection workflow


- Use `scripts/ide_gen.bat` or `scripts/ide_gen.sh`.


- Commit templates and deterministic file lists only.


- Never commit generated outputs under `/ide/**` unless explicitly required and documented.





## Forbidden patterns


- `.sln`, `.vcxproj`, `.vcproj`, `.dsp`, `.dsw`, `.xcodeproj`, `.pbxproj`, `.mcp` outside `/ide/**`.


- IDE state directories (e.g., `.vs`, `.xcuserdata`) inside source trees.


- Silent IDE toolchain upgrades.





## Exceptions


Grandfathered packaging inputs must be listed in:


- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`





## Cross-references


- `docs/architecture/REPO_OWNERSHIP_AND_PROJECTIONS.md`


- `docs/architecture/GENERATED_CODE_POLICY.md`
