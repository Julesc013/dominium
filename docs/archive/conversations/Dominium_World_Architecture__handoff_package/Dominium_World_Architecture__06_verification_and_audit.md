# Verification and Audit — Dominium World Architecture

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
|---|---|---|---|
| Signed Q16.16 local X/Y contradiction | Critical | Added explicit correction: use unsigned local fixed or centered signed scheme. | User should confirm preferred representation. |
| Signed Q4.12 chunk-local contradiction | Critical | Added explicit correction: use unsigned UQ4.12. | Implementation prompt must be updated. |
| Region bit-width inconsistency | Critical | Corrected decomposition: Region-in-Segment is 8 bits. | Existing prompt may still contain old text. |
| C89 incompatibility in previous prompt | Critical | Added portability warning and verification tasks. | Exact compiler strategy still unknown. |
| Saved rotations ambiguity | High | Marked saved rotations as 8-bit per user statement. | Exceptions for vehicles require user confirmation. |
| Artifact tracking incomplete for current package | Medium | Added ARTIFACT-16 through ARTIFACT-23 for files created now. | Counts should be manually checked. |
| Assistant suggestions may appear as decisions | Medium | Added labels and source hierarchy. | Aggregator must preserve labels. |
| Solver details vague | Medium | Open questions and tasks added. | Requires future design/prototype. |
| Repo state unknown | High | Added critical repo inspection task. | Cannot be resolved in this chat. |
| Project-level context boundary | Low | Marked source scope as THIS CHAT ONLY; noted project name caveat. | Future aggregator should track provenance. |

## 2. Final Reliability Assessment

- Completeness rating: 4/5.
- Reliability rating: 4/5.
- Aggregation readiness rating: 4/5.
- Main uncertainty sources:
  - Actual repository/build system/toolchain unknown.
  - Strict C89 plus 64-bit requirement unresolved.
  - Several solver formulas and grid resolutions unresolved.
  - Some architecture items are assistant inferences, not direct user decisions.

## 3. Manual Verification Checklist

- Confirm unsigned fixed-point correction.
- Confirm C89 portability approach.
- Confirm saved rotations remain 8-bit.
- Confirm Region bit decomposition in any future spec/prompt.
- Inspect actual repo before code generation.
- Check generated ZIP includes all seven requested files.
- Review YAML parse validity.
- Verify that no assistant recommendation has been promoted to FACT without basis.

## 4. Residual Risk Register

| ID | Risk | Consequence | Likelihood | Severity | Mitigation | Workstreams | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Signed Q16.16 local X/Y bug | Cannot represent [0,65536); overflow/seams/corruption | medium | critical | Use unsigned UQ16.16 or centred signed scheme | WORKSTREAM-01, WORKSTREAM-11 | FACT |
| RISK-02 | Signed Q4.12 save-local bug | Cannot represent full 16m chunk range | medium | critical | Use unsigned UQ4.12 | WORKSTREAM-02, WORKSTREAM-11 | FACT |
| RISK-03 | Region bit-width inconsistency | Wrong directory/file address decomposition | medium | high | Correct Region-in-Segment to 8 bits | WORKSTREAM-01, WORKSTREAM-03 | FACT |
| RISK-04 | C89 incompatibility in implementation prompt | Code may fail target constraints | high | high | Use C89-style portability layer; avoid C99 constructs | WORKSTREAM-02, WORKSTREAM-11 | FACT |
| RISK-05 | 64-bit IDs in strict C89 unresolved | Portability failure or undefined type choices | medium | high | Document compiler extension/typedef strategy | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-06 | Saving caches as authoritative state | Reload divergences and bloated saves | medium | high | Only save deltas/dynamic state; mark caches disposable | WORKSTREAM-03, WORKSTREAM-04 | INFERENCE |
| RISK-07 | Too many files or poor save locality | Poor IO performance | medium | medium | Use Region files containing many chunks; sparse directories | WORKSTREAM-03 | INFERENCE |
| RISK-08 | Content/mod ID mismatch | World loads with wrong materials/recipes | medium | high | Strict content.lock and migrations | WORKSTREAM-03, WORKSTREAM-09 | INFERENCE |
| RISK-09 | Chunk streaming changes simulation | Non-deterministic gameplay and seams | medium | critical | Chunks are caches only; global/topological state | WORKSTREAM-04 | FACT |
| RISK-10 | Boundary crossing special cases introduce bugs | Performance spikes or state discontinuities | medium | high | O(1) wrap and streaming-independent systems | WORKSTREAM-04 | INFERENCE |
| RISK-11 | Terrain mesh seams | Visible cracks/collision gaps at chunk/region edges | medium | high | Sample φ at global coordinates with boundary overlap | WORKSTREAM-05 | INFERENCE |
| RISK-12 | Material/media queries become overcoupled | Hard to mod/extend systems | medium | medium | Use registries and WorldServices | WORKSTREAM-05, WORKSTREAM-09 | INFERENCE |
| RISK-13 | Fluid/weather scope explosion | Core becomes unbuildable multiphysics engine | medium | high | Use compartments/graphs/coarse grids; defer full physics | WORKSTREAM-06 | INFERENCE |
| RISK-14 | Fixed-point fluid solver instability | Bad pressures/flows/flooding | medium | high | Pick simple clamped formulas and tests | WORKSTREAM-06, WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| RISK-15 | Rupture model creates nondeterministic topology changes | Different clients diverge | low/medium | high | Threshold deterministic events; stable ordering | WORKSTREAM-07 | INFERENCE |
| RISK-16 | Oil/gas mixture complexity overwhelms v1 | Implementation delay | medium | medium | Start with simple species mass vectors | WORKSTREAM-07 | INFERENCE |
| RISK-17 | Network solvers become too realistic/slow | Performance and complexity loss | medium | medium | Use graph simplifications; no full EM | WORKSTREAM-08 | INFERENCE |
| RISK-18 | Lua nondeterminism | Cross-machine divergence | medium | high | Sandbox and deterministic APIs | WORKSTREAM-09 | INFERENCE |
| RISK-19 | Mod schemas hardcoded or unstable | Mod ecosystem breaks saves | medium | medium | Versioned manifests and registries | WORKSTREAM-09 | INFERENCE |
| RISK-20 | Repo architecture assumptions wrong | Codex overwrites/misplaces files | medium | high | Inspect repo before changes | WORKSTREAM-10, WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| RISK-21 | Launcher/tools duplicate file parsers | Format drift and bugs | medium | medium | Tools link engine IO | WORKSTREAM-10 | INFERENCE |
| RISK-22 | Previous Codex prompt used without audit | Implementation bakes in known design bugs | medium | critical | Repair prompt first | WORKSTREAM-11 | FACT |
| RISK-23 | No deterministic test harness | Bugs discovered late | medium | high | Add save/load/hash/seam tests early | WORKSTREAM-12 | INFERENCE |
| RISK-24 | Threading breaks determinism | Race/order-dependent state | medium | high | Single-thread sim; async only for pure caches initially | WORKSTREAM-12 | INFERENCE |
| RISK-25 | Report over-compression loses design details | Future assistant repeats questions/mistakes | low | medium | Use full package + registers | WORKSTREAM-13 | FACT |
| RISK-26 | Assistant suggestions mistaken as user decisions | Spec book becomes overconfident | medium | medium | Use labels and source hierarchy | WORKSTREAM-13 | FACT |

## 5. Recommended Re-Extraction Triggers

Re-extract or manually review this chat if:
- The original prior Codex prompt is about to be used directly.
- Another chat contradicts precision/world-size/core-language decisions.
- User changes C89/no-float constraints.
- Repo inspection reveals existing structures that conflict with proposed layout.
- A future aggregator cannot distinguish FACT vs INFERENCE for a major item.
