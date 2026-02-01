Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Mod Ecosystem (MOD1)





Status: binding.


Scope: mod participation, pack rules, and save safety.





## Core rules


- Mods ARE packs and follow UPS rules.


- Mods never write files at runtime.


- Mods participate in saves via registered ops only.


- Mods can be removed safely.


- Missing mods -> explicit degraded/frozen modes.





## Save safety


- Mod state is isolated per mod_id.


- Unknown mod chunks are preserved across saves.


- Missing required mod data => frozen/inspect-only load.





## Compatibility


- Mods declare capabilities; content targets capabilities, not engine versions.


- Unknown fields in manifests and mod data must be preserved.


- No executable code in packs.





## See also


- `docs/architecture/MOD_ECOSYSTEM_RULES.md`


- `docs/architecture/PACK_FORMAT.md`
