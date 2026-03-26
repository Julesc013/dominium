Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI
Replacement Target: XI-3 convergence planning

# XI-2 Final

- duplicate_clusters: `6065`
- scored_implementations: `24119`
- unique_candidates: `15896`

## Highest Scoring Canonical Candidates

- `verify_pack_set` -> `src/packs/compat/__init__.py` score=`79.05` confidence=`high` gap=`19.88`
- `REFUSAL_PACK_REGISTRY_MISSING` -> `src/packs/compat/__init__.py` score=`79.05` confidence=`high` gap=`24.65`
- `REFUSAL_SAVE_PACK_LOCK_MISMATCH` -> `src/lib/save/__init__.py` score=`79.05` confidence=`high` gap=`21.25`
- `DEFAULT_CONTRACT_BUNDLE_REF` -> `src/lib/save/__init__.py` score=`79.05` confidence=`high` gap=`16.49`
- `load_semantic_contract_registry` -> `tools/compatx/core/semantic_contract_validator.py` score=`84.05` confidence=`high` gap=`24.76`
- `mod_manifest_init` -> `game/include/dominium/mods/mod_manifest.h` score=`89.4` confidence=`high` gap=`25.1`
- `dom_data_schema_find` -> `engine/include/domino/io/data_validate.h` score=`85.95` confidence=`high` gap=`15.23`
- `dom_data_schema_register` -> `engine/include/domino/io/data_validate.h` score=`78.81` confidence=`high` gap=`16.49`
- `generate_explain_artifact` -> `src/meta/explain/__init__.py` score=`79.05` confidence=`high` gap=`21.4`
- `REFUSAL_PROVIDES_HASH_MISMATCH` -> `src/lib/provides/__init__.py` score=`79.05` confidence=`high` gap=`13.7`

## Modules Most Affected By Duplication

- `unknown.src.geo` clusters=`163` score_rows=`169` avg_score=`63.85`
- `unknown.src.mobility` clusters=`137` score_rows=`137` avg_score=`60.74`
- `unknown.src.logic` clusters=`131` score_rows=`131` avg_score=`61.27`
- `unknown.src.worldgen.earth` clusters=`130` score_rows=`231` avg_score=`58.74`
- `unknown.src.signals` clusters=`128` score_rows=`128` avg_score=`65.94`
- `unknown.src.system` clusters=`118` score_rows=`152` avg_score=`65.88`
- `unknown.src.process` clusters=`99` score_rows=`123` avg_score=`60.63`
- `unknown.src.signals.transport` clusters=`96` score_rows=`148` avg_score=`60.3`
- `unknown.src.control` clusters=`94` score_rows=`99` avg_score=`63.49`
- `unknown.src.lib.artifact` clusters=`89` score_rows=`163` avg_score=`64.13`
- `unknown.src.geo.worldgen` clusters=`82` score_rows=`140` avg_score=`63.85`
- `unknown.src.geo.overlay` clusters=`78` score_rows=`138` avg_score=`62.84`

## src/ Directories Most Likely To Contain Shadow Implementations

- `src/geo` candidates=`785` low_arch=`785` avg_score=`61.89`
- `src/logic` candidates=`763` low_arch=`763` avg_score=`59.13`
- `src/lib` candidates=`742` low_arch=`742` avg_score=`64.95`
- `src/mobility` candidates=`701` low_arch=`701` avg_score=`61.13`
- `src/worldgen` candidates=`697` low_arch=`697` avg_score=`57.84`
- `src/meta` candidates=`567` low_arch=`567` avg_score=`64.27`
- `src/system` candidates=`510` low_arch=`510` avg_score=`62.42`
- `src/signals` candidates=`485` low_arch=`485` avg_score=`60.24`
- `src/control` candidates=`483` low_arch=`483` avg_score=`62.22`
- `src/process` candidates=`391` low_arch=`391` avg_score=`62.46`
- `src/appshell` candidates=`231` low_arch=`231` avg_score=`63.03`
- `src/electric` candidates=`194` low_arch=`194` avg_score=`58.59`

