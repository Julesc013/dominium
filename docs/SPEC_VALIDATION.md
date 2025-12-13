Validation Pipeline
-------------------
- Content validation runs after all packs/mods load and before world creation. The pass enforces non-empty UTF-8 names, non-zero IDs, and basic referential integrity (materials on items, deposits -> materials). Failures abort session initialization.
- Subsystem validators exist for RES/ENV/BUILD/TRANS/STRUCT/VEH/JOB and run after world creation, before simulation. They are pure functions of world state and are expected to be deterministic.
- Save verification re-loads the freshly written world into a temporary instance and compares world hashes; mismatches are reported immediately to avoid silent corruption.
- Launcher hooks are expected to expose a “Verify Instance” action that loads the configured packs/mods, runs content validation, and exercises subsystem validators against an empty worldgen.
- Reserved engine internals must not be overridden by packs/mods; IDs must stay within the content contract and schema versions must match the engine’s registered schemas.
