Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Tools Overview (TOOLS-1)





Purpose: Provide read-only, deterministic tooling for authoring, inspection, and debugging of data-first content.





All tools are CLI-first. TUI/GUI shells must invoke these tools with identical arguments and surface identical results.





## Validation


- `tools/pack/pack_validate.py`


  - Validates pack manifests, namespace rules, unit annotations, and cross-pack capability references.


  - Example:


    - `python tools/pack/pack_validate.py --pack-root data/packs/org.dominium.core.units --format json`


- `tools/fab/fab_validate.py`


  - Validates FAB-0 data (materials, parts, assemblies, processes, standards).


  - Supports optional `--pack-root` (or pack-derived inputs) to enforce maturity labels.


  - Example:


    - `python tools/fab/fab_validate.py --input data/packs/org.dominium.core.parts.basic/data/fab_pack.json --pack-root data/packs/org.dominium.core.parts.basic --format json`





## Inspection


- `tools/pack/capability_inspect.py`


  - Reports provided/required capabilities, transitive closure, conflicts/overlaps, and baseline compatibility.


  - Example:


    - `python tools/pack/capability_inspect.py --pack-id org.dominium.core.units --pack-id org.dominium.worldgen.minimal --format json`


- `tools/coverage/coverage_inspect.py`


  - Reports coverage ladder status (C-A..C-H) and maturity breakdown.


  - Example:


    - `python tools/coverage/coverage_inspect.py --pack-id org.dominium.core.ecology.basic --format json`


- `tools/fab/fab_inspect.py`


  - Aggregates assembly properties and interface compatibility checks.





## Refusal Debugging


- `tools/inspect/refusal_explain.py`


  - Explains refusal payloads and validation failures with schema paths and data-side fixes.


  - Example:


    - `python tools/inspect/refusal_explain.py --input tmp/fab_validate.json --data data/packs/org.dominium.core.parts.basic/data/fab_pack.json --format json`





## Diff & Comparison
- `tools/fab/fab_diff.py`
  - Diffs two FAB packs and reports compatibility impact.
  - Example:
    - `python tools/fab/fab_diff.py --left data/packs/org.dominium.core.parts.basic --right data/packs/org.dominium.core.parts.extended --format json`
- `tools/playtest/replay_diff.py`
  - Diffs two replays and reports event/refusal divergence.

## Bugreporting
- `tools/bugreport/bugreport_cli.py`
  - Creates and inspects reproducible bugreport bundles with replay context.
  - Example:
    - `python tools/bugreport/bugreport_cli.py create --replay-bundle tmp/replay_bundle --install-manifest tmp/install.manifest.json --instance-manifest tmp/instance.manifest.json --runtime-descriptor tmp/runtime.descriptor.json --compat-report tmp/compat_report.json --ops-log tmp/ops.log --out tmp/bugreport_bundle`



## Determinism & Safety


- Tools are read-only and must never mutate simulation state.


- JSON output is deterministic (sorted keys and stable ordering).


- Any refusal codes surfaced by tools must match `docs/architecture/REFUSAL_SEMANTICS.md`.
