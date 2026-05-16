# AIDE-MOVE-02-REFINE Candidates

## Status

- Task ID: AIDE-MOVE-02-REFINE
- Candidate found: no
- Apply allowed: false
- Approval status: not_approved

## Candidate Table

| Candidate | Root | Type | Accepted? | Risk | References | Target | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ide/manifests/**` | `ide` | machine-readable projection metadata | no | medium | high | none | Deferred by prior gates; manifest/schema material is not docs-only. |
| `performance/*.py` | `performance` | Python tooling | no | medium | 116 | none | Active Python helpers with product/client imports and tooling references. |
| `validation/*.py` | `validation` | Python validation tooling | no | medium | 1998 | none | Active validation modules and broad XStack references. |
| `governance/*.py` | `governance` | Python policy/governance tooling | no | medium | 1399 | none | Policy/governance helper code, not docs-only evidence. |
| `meta/**` | `meta` | Python policy/governance tooling | no | unknown | 1345 | none | Broad, Python-heavy, policy-sensitive, and high-reference. |
| `templates/adapter_template.md` | `templates` | template scaffold | no | medium | 5 exact refs | none | Human-readable, but classified as convert/template_scaffold and referenced by XStack contract/audit/generated evidence. |
| `templates/domain_contract_template.md` | `templates` | template scaffold | no | medium | 1 exact ref | none | Human-readable, but referenced by protected specs/reality template material. |
| `data/**/*.md` / `data/**/*.txt` | `data` | content/package docs | no | high | unknown | none | Identity-sensitive content and package material. |
| `packs/README.md` / `bundles/README.md` | `packs`, `bundles` | package identity docs | no | high | unknown | none | Pack/bundle identity-sensitive. |
| `specs/reality/*.md` / `updates/README.md` | `specs`, `updates` | authority docs | no | protected | unknown | none | Authority/spec/update-sensitive. |
| `libs/**/CMakeLists.txt` | `libs` | build input | no | protected | unknown | none | ABI/build/CMake-sensitive. |

## Recommendation

Do not run `AIDE-MOVE-02-PLAN-R2` yet. No candidate survived the refinement filter.

Recommended next task: `POST-CONVERGE-10F - Unit Annotation and RepoX Rule Remediation`.
