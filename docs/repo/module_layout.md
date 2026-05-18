Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none
Stability: provisional
Task: NAME-00
Machine-Readable Source: `contracts/repo/naming.contract.toml`

# Module Layout

The module layout follows ownership slots, not generic source buckets.

## Target Grammar

```text
engine/
  include/
  kernel/
  determinism/
  identity/
  time/
  math/
  memory/
  order/
  schedule/
  event/
  state/
  execution/
  replay/
  proof/
  diagnostics/

game/
  authority/
  law/
  rule/
  process/
  world/
  scenario/
  domain/

runtime/
  shell/
  capability/
  component/
  platform/
  render/
  ui/
  input/
  audio/
  network/
  storage/
  ipc/
  diagnostics/
  supervisor/
  package/
  profile/
  instance/
  save/
  replay/
  update/

contracts/
  abi/
  architecture/
  build/
  capability/
  command/
  compatibility/
  component/
  diagnostics/
  distribution/
  domain/
  event/
  governance/
  identity/
  install/
  lock/
  manifest/
  package/
  policy/
  product/
  profile/
  projection/
  protocol/
  registry/
  release/
  repo/
  replay/
  safety/
  schema/
  security/
  service/
  stability/
  update/
  version/
  view/

content/
  assets/
  bundles/
  defaults/
  domains/
  examples/
  fixtures/
  locale/
  packs/
  profiles/
  templates/
  themes/
```

This is a target naming grammar. It is not an apply map.

## Ownership Rules

- `engine/` owns deterministic substrate, not game meaning or platform behavior.
- `game/` owns game law, process semantics, and domain implementation, not runtime adapters or product shell behavior.
- `runtime/` owns host services and adapters, not simulation truth.
- `apps/` owns thin product entrypoints and composition only.
- `contracts/` owns machine-readable law and identity definitions.
- `content/` owns authored payloads and data, not executable truth mutation.
- `tools/` owns validators, generators, migration helpers, and developer tooling.
- `docs/` explains; it does not override machine-readable law.

## Future MOVE-BULK Use

Future B-G refinement should use these slots as target grammar:

- templates/models/modding: `content/templates`, `content/assets`, `content/themes`, `docs/modding`, or `contracts/package` by file role.
- content identity: `content/packs`, `content/profiles`, `content/bundles`, `content/domains`, `contracts/package`, `contracts/profile`, or `release` after identity proof.
- authority and policy: `contracts/*`, `release/*`, `tools/*`, or `docs/*` according to whether the file is machine law, release control, tool behavior, or explanation.
- active tools: `tools/validators`, `tools/audit`, `tools/migration`, `tools/performance`, or preserved root exceptions until import/shim proof exists.
- runtime/core/net: `engine`, `game`, `runtime`, or `contracts` only after deterministic/runtime/build ownership proof.
- lib/libs: `engine`, `runtime`, `external`, `contracts/abi`, or `tools/build` only after ABI/build proof.

If a file has unclear identity, ABI, runtime, policy, or release meaning, it stays deferred.

The current MOVE-SCRIPT-00 dry run gives the next refinement gate its starting set: 1,593 route candidates, 172 skipped/deferred files, and 0 target collisions across 1,765 tracked files under the 23 former bad roots. Those candidates are not approved moves until a later gate and apply prompt authorize exact subsets.
