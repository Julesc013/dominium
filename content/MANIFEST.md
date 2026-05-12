# Content Manifest

Status: PROVISIONAL
Phase: POST-CONVERGE-03

This manifest records the POST-CONVERGE-03 content-root review. No pack, profile, bundle, model, modding, data, or template files were moved into `content/` in this task.

| Previous Path | New Path | Action | Notes | Identity Preservation |
| --- | --- | --- | --- | --- |
| `data/` | not moved | left_for_review | Mixed registries, planning mirrors, authored data, generated evidence, baselines, runtime/release/XStack data, and `data/packs/` scoped authored pack material. | No data paths or IDs changed. |
| `packs/` | not moved | left_for_review | Active runtime pack substrate with `pack.json`, capability, trust, and compatibility sidecars. | Pack IDs and compatibility semantics unchanged. |
| `profiles/` | not moved | left_for_review | Contains `profiles/bundles/bundle.mvp_default.json`, which embeds profile bundle identity and path metadata. | Profile IDs, profile bundle ID, hashes, and rel-path metadata unchanged. |
| `bundles/` | not moved | left_for_review | Active bundle profile source referenced by XStack/control tooling and docs. | Bundle IDs unchanged. |
| `modding/` | not moved | left_for_review | Active Python mod policy engine imported by product/server and XStack tooling. | Mod policy IDs and trust/capability semantics unchanged. |
| `models/` | not moved | left_for_review | Active Python constitutive model engine imported by engine, game domains, meta, and tests. | Model IDs and model binding semantics unchanged. |
| `templates/` | not moved | left_for_review | Root templates are referenced by protected `specs/reality` and XStack/AIDE contract surfaces. | Template paths remain stable pending protected review. |

Future content moves must update this manifest and the layout exception ledger in the same task that moves files.
