Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Pack Format (UPS1)





Status: binding.


Scope: UPS pack structure, manifest format, and safety rules.





## Pack structure


```


data/packs/<pack_id>/
├── pack.toml (preferred) or pack.manifest (legacy)
├── data/ (preferred) or content/ (legacy)
├── schema/


├── ui/


└── docs/


```





Rules:


- `pack.toml` is REQUIRED for new packs; legacy packs MAY use `pack.manifest`.
- No executable code inside packs.


- No hardcoded paths.


- No implicit load-order dependencies.


- Everything namespaced (reverse-DNS).





## Manifest schema


The canonical manifest schema is:


- `schema/pack_manifest.schema`





Required fields (stable):


- pack_id


- pack_version


- pack_format_version


- provides[]


- depends[]


- requires_engine


- extensions{}





Unknown fields MUST be preserved.





## Format notes


- `pack.toml` is the runtime manifest format.
- `pack_manifest.json` is a schema-mapped representation for tooling/source control.
- Conversion between formats MUST preserve unknown fields.
- `content/` is a legacy alias for `data/` and must be migrated over time.



## Safety


- Packs MUST be loadable without reading pack contents.


- Capabilities are resolved by identifier only; file paths are never used.


- No pack may embed executable logic.





## See also


- `docs/architecture/MOD_ECOSYSTEM_RULES.md`


- `docs/architecture/LOCKFILES.md`


- `schema/pack_manifest.schema`
