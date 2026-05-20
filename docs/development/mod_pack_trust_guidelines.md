Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Mod Pack Trust Guidelines

Use these rules when adding or reviewing mod/pack descriptors.

## Define A Pack

Choose the lowest trust level that works:

- use `data_only` for authored data with no side effects;
- use `schema_validated` when schema proof is required;
- use `scriptless_rule_data_pack` for declarative rules and data;
- use `workbench_authored_module` for Workbench-authored module descriptors;
- use `external_process_adapter` only when an external process is visible and
  declared;
- use `trusted_native_provider` only inside a trusted build/release boundary;
- do not use `signed_native_provider` for active behavior yet.

Declare `mod_id`, `mod_kind`, `trust_level`, `permissions`, `capabilities`,
`determinism_impact`, `security_impact`, diagnostics, refusals, evidence, and
compatibility range. IDs are dotted identifiers, not paths.

## Request Permissions

Every permission must be listed in `permissions` and explained in
`declared_permissions`. Do not rely on a capability, module ID, provider ID, or
folder name to imply authority.

Data-only packs should normally request only `read_pack_data`.

## Avoid Silent Overlays

If a pack overlays another payload, declare the target, conflict, and policy.
Use refusal unless the replacement or merge is intentional and evidence-backed.
Never use silent overwrite.

## Determinism

Declare `classification`, `replay_policy`, and `authoritative_state_impact`.
Adapters or providers that may be nondeterministic must be refused or isolated
from authoritative replay paths.

## External And Native Boundaries

External adapters must declare IPC/protocol identity, process access, network
access, filesystem access, security impact, and determinism impact.

Native providers require trusted/signed native provider policy, ABI surface,
capability declarations, provider conformance evidence, and review. This task
does not enable dynamic native plugin loading.

## Validation

Run:

```text
python tools/validators/package/check_mod_pack_trust.py --repo-root . --strict
```

Inventory mode is descriptive and does not migrate existing pack manifests:

```text
python tools/validators/package/check_mod_pack_trust.py --repo-root . --inventory
```
