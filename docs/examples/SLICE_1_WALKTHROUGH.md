Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# SLICE-1 Walkthrough (CLI)

This walkthrough uses the CLI shell to demonstrate survey, action, failure,
and replay inspection with zero packs installed. All values are generic.

1) Create a world with authority enabled:

```
client "new-world template=builtin.minimal_system seed=7 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free"
```

2) Set local fields and inspect subjective knowledge (unknown before survey):

```
client "batch new-world template=builtin.minimal_system seed=7 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; field-set field=support_capacity value=2; field-set field=surface_gradient value=1; field-set field=local_moisture value=2; field-set field=accessibility_cost value=0; fields"
```

Expected: field lines include `subjective=unknown` and `known=0`.

3) Survey the local area:

```
client "batch new-world template=builtin.minimal_system seed=7 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; field-set field=support_capacity value=2; field-set field=surface_gradient value=1; field-set field=local_moisture value=2; field-set field=accessibility_cost value=0; survey; fields"
```

Expected: survey succeeds; field lines show `known=1` and subjective values.

4) Collect material (success after survey):

```
client "batch new-world template=builtin.minimal_system seed=7 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; field-set field=support_capacity value=2; field-set field=surface_gradient value=1; field-set field=local_moisture value=2; field-set field=accessibility_cost value=0; survey; collect"
```

Expected: `process=ok process=collect_local_material`.

5) Trigger deterministic failure (insufficient support):

```
client "batch new-world template=builtin.minimal_system seed=7 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; field-set field=support_capacity value=0.5; field-set field=surface_gradient value=1; field-set field=local_moisture value=2; field-set field=accessibility_cost value=0; survey; assemble"
```

Expected: `process=failed ... reason=capacity`.

6) Save and inspect replay:

```
client "batch new-world template=builtin.minimal_system seed=7 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; field-set field=support_capacity value=0.5; field-set field=surface_gradient value=1; field-set field=local_moisture value=2; field-set field=accessibility_cost value=0; survey; assemble; save path=data/saves/world.save"
client "batch inspect-replay path=data/saves/world.save; events"
```

Expected: replay events include `client.process` with `result=failed` and `reason=capacity`.

Notes:
- `field-set` is a test-only convenience for SLICE-1.
- Values are unitless and generic; no world assumptions are implied.