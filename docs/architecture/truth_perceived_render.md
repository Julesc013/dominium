Status: DERIVED
Last Reviewed: 2026-02-15
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to canon v1.0.0 and enforced by `client/CMakeLists.txt` and `tools/xstack/repox/check.py`.

# Truth/Perceived/Render Boundary v1

## Purpose
Define hard architectural boundaries that prevent renderer epistemic leakage and keep authority in TruthModel + Observation Kernel layers.

## Layer Ownership
- TruthModel owner:
  - `engine/include/domino/truth_model_v1.h`
  - authoritative references only.
- PerceivedModel owner:
  - `client/observability/perceived_model_v1.h`
  - derived immutable snapshot only.
- RenderModel owner:
  - `client/presentation/render_model_v1.h`
  - presentation projection only.

## Allowed Dependencies
- Observation layer may read TruthModel and registries.
- Renderer may read PerceivedModel and RenderModel contracts.
- Renderer must not import TruthModel headers or symbols.
- UI host may read PerceivedModel and RenderModel contracts.
- UI host may emit Intents only through process-intent pipeline.

## Forbidden Dependencies
- `client/presentation/*` importing `domino/truth_model_v1.h`
- renderer logic directly reading authoritative simulation payloads
- renderer-owned law/authority decisions
- UI host direct mutation of TruthModel / UniverseState
- UI descriptor selectors referencing `truth_model.*`

## Enforcement Mechanisms
1. Build-time boundary:
   - `client/CMakeLists.txt` compiles presentation sources with `DOMINIUM_RENDERER_BOUNDARY=1`.
   - `engine/include/domino/truth_model_v1.h` hard-errors when included under renderer boundary macro.
   - CMake configure check refuses if presentation sources are missing the boundary macro.
2. Static boundary scan (STRICT/FULL):
   - `tools/xstack/repox/check.py` rule `repox.renderer_truth_import`
   - `tools/xstack/repox/check.py` rule `repox.renderer_truth_symbol`
   - triggered by `tools/xstack/run strict` and `tools/xstack/run full`.
3. Registry compile selector gate:
   - UI descriptor data bindings must use `source=perceived_model`.
   - selector syntax is validated at compile time.
   - selectors beginning with truth namespace are refused deterministically.

## Determinism Rules
- Observation derivation must be pure and deterministic.
- PerceivedModel hash uses canonical JSON serialization.
- RenderModel derivation hash uses PerceivedModel-only payload.
- UI action -> Intent mapping is deterministic for identical descriptor + selection + widget state.
- Gating outcomes (`available`/`unavailable`) are deterministic for identical law + authority + lens inputs.

## Example Flow
1. Build TruthModel from session artifacts and lockfile hashes.
2. Observation Kernel derives PerceivedModel.
3. Renderer adapter derives RenderModel from PerceivedModel hash.
4. UI host loads `ui.registry`, binds widgets to PerceivedModel selectors, and emits intents.
5. Process runtime executes/refuses intents; process/refusal logs surface back into PerceivedModel channels.
6. Run-meta records:
   - `session_spec_hash`
   - `pack_lock_hash`
   - registry hashes
   - `perceived_model_hash`
   - `render_model_hash`

## TODO
- Add compile-time target split for standalone renderer library in future refactor.
- Add generated dependency graph artifact proving no renderer->truth edge.
- Add per-file boundary annotations to IDE tooling.
- Add formal UI selector grammar contract and static checker artifact.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/architecture/truth_model.md`
- `docs/architecture/observation_kernel.md`
- `docs/architecture/lens_system.md`
- `docs/architecture/ui_registry.md`
- `docs/contracts/refusal_contract.md`
