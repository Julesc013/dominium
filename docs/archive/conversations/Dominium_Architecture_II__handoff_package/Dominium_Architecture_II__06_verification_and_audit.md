# Verification and Audit — Dominium Architecture II

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
| --- | --- | --- | --- |
| Some early transcript content skipped. | medium | Marked apparent access as partial and preserved uncertainty. | Early rail/electrical details may be incomplete. |
| Actual repo files uninspected. | high | Added verification items and caveats. | On-disk files may differ. |
| Lua data vs JSON data docs tension. | high | Added QUESTION-04 and VERIFY-08. | Needs user/doc resolution. |
| Render API sketches conflict. | high | Added QUESTION-05 and TASK-34. | Must finalize before implementation. |
| External platform/toolchain claims stale. | high | Added verification queue for DX9, SDL2, Lua, CMake. | Requires external checks. |
| Licence legal validity unverified. | high | Marked legal review required. | Must not publish blindly. |
| Generated docs may not be applied. | high | Added TASK-01..04 and VERIFY-01. | Needs repo inspection. |
| Assistant suggestions could be mistaken for decisions. | medium | Decision register labels final-ish/tentative status. | Future aggregator must preserve labels. |
| Some artifacts huge/per-directory specs not fully reprinted. | medium | Ledger lists them; full report summarizes key contents. | May need original chat for exact file text. |

## 2. Final Reliability Assessment

- Completeness rating: 4/5
- Reliability rating: 4/5
- Aggregation readiness rating: 4/5
- Main remaining uncertainty sources:
  - Actual repo contents not inspected.
  - Some earlier transcript messages skipped.
  - External API/toolchain/legal facts need verification.
  - Lua-vs-JSON and render command API need resolution.

## 3. Manual Verification Checklist

- VERIFY-01: Actual repo file contents and whether V4 docs applied.
- VERIFY-02: Actual directory existence under /engine, /game, /data, etc.
- VERIFY-03: DX9.0c support on Windows 2000 SP4 through Windows 11+.
- VERIFY-04: SDL2 support for Windows 2000 target.
- VERIFY-05: Lua 5.4.4 portability to required compilers.
- VERIFY-06: Restrictive LICENCE.md legal enforceability.
- VERIFY-07: CMake minimum/toolchains and flags.
- VERIFY-08: JSON-vs-Lua data policy.
- VERIFY-09: Final DomDrawCmd/camera API.
- VERIFY-10: Current docs use LICENCE.md and SPEC_CORE.md names consistently.
- VERIFY-11: .gitignore behaviour.
- VERIFY-12: Third-party licence compliance for Lua/LZ4/etc.
- VERIFY-13: OpenGL/Vulkan/future platform support matrices.
- VERIFY-14: Win98 SE DX9/GL1 feasibility.
- VERIFY-15: Exact contents of docs/dev/dominium_new_*.txt.

## 4. Residual Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Spec drift across docs/dev files. | Codex implements contradictory architecture. | high | high | Run consistency pass; keep V4 docs canonical. | WORKSTREAM-01 | FACT |
| RISK-02 | Codex invents directories or files outside contract. | Repo sprawl and bad implementation. | medium | high | Prompt scope and DIRECTORY_CONTEXT. | WORKSTREAM-01, WORKSTREAM-22 | FACT |
| RISK-03 | Treating brainstorming as final decisions. | Wrong architecture enters spec. | medium | high | Use labels and user-statement priority. | WORKSTREAM-01 | FACT |
| RISK-04 | Platform/render boundaries blur. | OS/GPU APIs leak into sim/game. | medium | critical | Addendum, BUILDING V4, lint checks. | WORKSTREAM-14 | FACT |
| RISK-05 | Floats enter authoritative simulation through Lua/render/helpers. | Cross-platform desync. | medium | critical | API conversion, no sim floats, tests. | WORKSTREAM-02, WORKSTREAM-15 | FACT |
| RISK-06 | Lua sandbox escape or nondeterministic script behavior. | Security/desync. | medium | critical | Disable OS/native/debug and deterministic RNG. | WORKSTREAM-15 | FACT |
| RISK-07 | Surface/space/cross-surface sync overreach. | Sharding/orbit complexity, desync. | medium | high | Defer space/multiplayer; async only. | WORKSTREAM-12, WORKSTREAM-21 | FACT |
| RISK-08 | DX9/Win2000 target not feasible as assumed. | MVP platform failure. | medium | high | Verify SDK/runtime early. | WORKSTREAM-14 | UNCERTAIN / UNVERIFIED |
| RISK-09 | SDL2 or Lua version incompatible with old targets. | Build/tooling failures. | medium | medium-high | Verify and patch/version-pin. | WORKSTREAM-14, WORKSTREAM-15 | UNCERTAIN / UNVERIFIED |
| RISK-10 | Canonical hash/serializer includes unstable data or misses authoritative state. | False determinism results. | medium | high | Define serialization order and exclusions. | WORKSTREAM-16 | FACT |
| RISK-11 | MVP scope too broad. | Implementation stalls. | high | high | Minimal prototypes only; defer assets/multiplayer/space. | WORKSTREAM-18 | FACT |
| RISK-12 | Corridor/microgrid overlap ambiguity. | Invalid construction/pathing. | medium | medium-high | Ownership/portal rules. | WORKSTREAM-08 | FACT |
| RISK-13 | Network solver complexity creep. | MVP delay. | medium | medium | Simple power first, fluid/data thin. | WORKSTREAM-09 | INFERENCE |
| RISK-14 | Binary formats too underdefined for Codex. | Serializer guesses layouts. | medium | high | Finalize exact structs for MVP components. | WORKSTREAM-16 | FACT |
| RISK-15 | Sparse/full-size surface overdesign. | Memory/perf or slow implementation. | medium | medium | MVP flat sparse test area with full surface metadata. | WORKSTREAM-05 | INFERENCE |
| RISK-16 | .gitignore/build rules hide needed files. | Missing tracked build configs. | medium | medium | Audit git ignore. | WORKSTREAM-17 | INFERENCE |
| RISK-17 | Actual repo tree differs from generated specs. | Patches fail or create wrong files. | medium | medium | Inspect before applying. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| RISK-18 | Restrictive licence legally weak. | Legal exposure. | unclear | high | Legal review. | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| RISK-19 | Future cross-server trade/security underspecified. | Cheating/rollback/desync. | medium | high | Future security/net spec. | WORKSTREAM-21 | INFERENCE |

## 5. Recommended Re-Extraction Triggers

- If the actual repo files differ from the user-pasted tree.
- If V4 docs were not applied or were edited afterward.
- If another chat contains conflicting MVP/platform/data decisions.
- If legal/licence text changes.
- If Codex implementation discovers missing architecture decisions.
- If user clarifies Lua-vs-JSON or render command API.
