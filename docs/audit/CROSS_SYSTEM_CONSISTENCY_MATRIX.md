Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Bound to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Cross-System Consistency Matrix

Legend:
- `ALLOWED`: System owns/executes this responsibility.
- `FORBIDDEN`: Responsibility is disallowed for this system.
- `READ-ONLY`: System may consume data but must not mutate authoritative state.
- `DERIVED-ONLY`: System may produce derived/run-meta artifacts only.
- `NOT-APPLICABLE`: Responsibility does not apply.

## Matrix

| System | State mutation authority | Artifact generation | Registry consumption | Schema validation | Capability enforcement | Determinism enforcement | Refusal emission | Packaging interaction | Versioning/BII stamping | Logging/run-meta | Derived artifact production |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Engine | ALLOWED | DERIVED-ONLY | READ-ONLY | FORBIDDEN | READ-ONLY | ALLOWED | ALLOWED | FORBIDDEN | FORBIDDEN | ALLOWED | DERIVED-ONLY |
| Game | ALLOWED | DERIVED-ONLY | READ-ONLY | FORBIDDEN | READ-ONLY | ALLOWED | ALLOWED | FORBIDDEN | FORBIDDEN | ALLOWED | DERIVED-ONLY |
| Client | FORBIDDEN | DERIVED-ONLY | READ-ONLY | READ-ONLY | READ-ONLY | READ-ONLY | ALLOWED | FORBIDDEN | FORBIDDEN | ALLOWED | DERIVED-ONLY |
| Server | ALLOWED | DERIVED-ONLY | READ-ONLY | READ-ONLY | ALLOWED | ALLOWED | ALLOWED | FORBIDDEN | FORBIDDEN | ALLOWED | DERIVED-ONLY |
| Launcher | FORBIDDEN | DERIVED-ONLY | READ-ONLY | READ-ONLY | READ-ONLY | READ-ONLY | ALLOWED | READ-ONLY | READ-ONLY | ALLOWED | DERIVED-ONLY |
| Setup | FORBIDDEN | ALLOWED | READ-ONLY | ALLOWED | FORBIDDEN | ALLOWED | ALLOWED | ALLOWED | READ-ONLY | ALLOWED | ALLOWED |
| Tools | FORBIDDEN | ALLOWED | READ-ONLY | ALLOWED | FORBIDDEN | ALLOWED | ALLOWED | READ-ONLY | READ-ONLY | ALLOWED | ALLOWED |
| Packs | FORBIDDEN | FORBIDDEN | NOT-APPLICABLE | NOT-APPLICABLE | FORBIDDEN | FORBIDDEN | NOT-APPLICABLE | READ-ONLY | READ-ONLY | NOT-APPLICABLE | FORBIDDEN |
| Schemas | FORBIDDEN | FORBIDDEN | NOT-APPLICABLE | NOT-APPLICABLE | NOT-APPLICABLE | READ-ONLY | NOT-APPLICABLE | NOT-APPLICABLE | ALLOWED | NOT-APPLICABLE | FORBIDDEN |
| Registries | FORBIDDEN | DERIVED-ONLY | NOT-APPLICABLE | READ-ONLY | NOT-APPLICABLE | READ-ONLY | ALLOWED | READ-ONLY | READ-ONLY | DERIVED-ONLY | ALLOWED |
| UI IR | FORBIDDEN | DERIVED-ONLY | READ-ONLY | READ-ONLY | READ-ONLY | READ-ONLY | ALLOWED | FORBIDDEN | FORBIDDEN | ALLOWED | DERIVED-ONLY |
| Worldgen | ALLOWED | ALLOWED | READ-ONLY | ALLOWED | READ-ONLY | ALLOWED | ALLOWED | FORBIDDEN | READ-ONLY | ALLOWED | ALLOWED |
| SRZ | ALLOWED | DERIVED-ONLY | READ-ONLY | READ-ONLY | READ-ONLY | ALLOWED | ALLOWED | FORBIDDEN | FORBIDDEN | ALLOWED | DERIVED-ONLY |
| XStack (RepoX/TestX/AuditX/PerformX/CompatX/SecureX) | FORBIDDEN | ALLOWED | READ-ONLY | ALLOWED | READ-ONLY | ALLOWED | ALLOWED | READ-ONLY | READ-ONLY | ALLOWED | ALLOWED |

## Invariants

- Process-only mutation is restricted to Engine/Game/Server/Worldgen/SRZ commit pathways.
- Renderer/UI surfaces are read-only over PerceivedModel and emit intents only.
- Pack directories remain data-only and never execute code.
- Setup/Tools own deterministic artifact derivation and packaging assembly.
- XStack is governance/verification and must not author runtime mutation.

## Cross-References

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/truth_perceived_render.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/deterministic_packaging.md`
- `docs/testing/xstack_profiles.md`
