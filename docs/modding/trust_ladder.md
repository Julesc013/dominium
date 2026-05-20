Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional

# Mod And Pack Trust Ladder

Dominium packs start from no extra authority. A pack can only do what its
descriptor, trust level, permissions, and validation evidence allow.

## Levels

`data_only`: data only. No code, network, filesystem, process, or native access.

`schema_validated`: data checked by schemas. Still no executable code.

`scriptless_rule_data_pack`: declarative rules/data. No arbitrary scripting.
Determinism impact must be declared.

`workbench_authored_module`: Workbench-authored descriptors and views. It may
call registered commands, not private tools.

`external_process_adapter`: talks to a separate process. It must declare the
protocol, permissions, security impact, and replay impact.

`trusted_native_provider`: native code inside a trusted build/release boundary.
It needs ABI, platform, capability, and conformance evidence.

`signed_native_provider`: future signed native provider policy. It is not active
runtime behavior in this task.

## What Is Forbidden By Default

- silent permission escalation;
- silent pack overlay overwrites;
- undeclared filesystem or network access;
- invisible external adapters;
- unreviewed native providers;
- nondeterministic replay behavior without explicit isolation or refusal.

Validation failures produce diagnostic and refusal codes so tools can explain
what happened and what recovery is allowed.
