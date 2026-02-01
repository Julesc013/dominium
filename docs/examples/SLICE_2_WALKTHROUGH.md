Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# SLICE-2 Walkthrough (CLI)

This walkthrough demonstrates delegation, authority enforcement, shared
infrastructure, and deterministic failure with zero packs installed.

1) Create a world and a small logistics network:

```
client "batch new-world template=builtin.minimal_system seed=11 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; network-create id=1 type=logistics; network-node network=1 id=100 capacity=1 stored=0 min=1; network-node network=1 id=200 capacity=1 stored=0 min=1; network-edge network=1 id=300 a=100 b=200 capacity=1 loss=0"
```

2) Add two agents:
   - Agent 1 has logistics capability and knowledge of the network endpoints.
   - Agent 2 can survey and act as delegator.

```
client "batch new-world template=builtin.minimal_system seed=11 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; network-create id=1 type=logistics; network-node network=1 id=100 capacity=1 stored=0 min=1; network-node network=1 id=200 capacity=1 stored=0 min=1; network-edge network=1 id=300 a=100 b=200 capacity=1 loss=0; agent-add id=1 caps=logistics resource=100 dest=200; agent-add id=2 caps=survey"
```

3) Create goals and delegate the stabilize goal to agent 1:

```
client "batch new-world template=builtin.minimal_system seed=11 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; network-create id=1 type=logistics; network-node network=1 id=100 capacity=1 stored=0 min=1; network-node network=1 id=200 capacity=1 stored=0 min=1; network-edge network=1 id=300 a=100 b=200 capacity=1 loss=0; agent-add id=1 caps=logistics resource=100 dest=200; agent-add id=2 caps=survey; goal-add agent=1 type=stabilize; goal-add agent=2 type=survey; delegate delegator=2 delegatee=1 goal=1"
```

Expected: `delegation=ok`.

4) Simulate once; authority is still missing, so the plan is refused:

```
client "batch new-world template=builtin.minimal_system seed=11 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; network-create id=1 type=logistics; network-node network=1 id=100 capacity=1 stored=0 min=1; network-node network=1 id=200 capacity=1 stored=0 min=1; network-edge network=1 id=300 a=100 b=200 capacity=1 loss=0; agent-add id=1 caps=logistics resource=100 dest=200; agent-add id=2 caps=survey; goal-add agent=1 type=stabilize; goal-add agent=2 type=survey; delegate delegator=2 delegatee=1 goal=1; simulate; events"
```

Expected: `event=client.agent.plan ... reason=insufficient_authority`.

5) Grant authority and simulate again:

```
client "batch new-world template=builtin.minimal_system seed=11 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; network-create id=1 type=logistics; network-node network=1 id=100 capacity=1 stored=0 min=1; network-node network=1 id=200 capacity=1 stored=0 min=1; network-edge network=1 id=300 a=100 b=200 capacity=1 loss=0; agent-add id=1 caps=logistics resource=100 dest=200; agent-add id=2 caps=survey; goal-add agent=1 type=stabilize; goal-add agent=2 type=survey; delegate delegator=2 delegatee=1 goal=1; authority-grant granter=2 grantee=1 authority=infra; simulate; events"
```

Expected: `event=client.agent.command` entries for both agents.

6) Infrastructure bottleneck failure is deterministic:

The network nodes have `min=1` and `stored=0`, so the tick emits
`event=client.network.fail ... reason=threshold`. This is deterministic and
auditable via `events`.

7) Save and replay:

```
client "batch new-world template=builtin.minimal_system seed=11 policy.authority=policy.authority.shell policy.mode=policy.mode.nav.free; network-create id=1 type=logistics; network-node network=1 id=100 capacity=1 stored=0 min=1; network-node network=1 id=200 capacity=1 stored=0 min=1; network-edge network=1 id=300 a=100 b=200 capacity=1 loss=0; agent-add id=1 caps=logistics resource=100 dest=200; agent-add id=2 caps=survey; goal-add agent=1 type=stabilize; goal-add agent=2 type=survey; delegate delegator=2 delegatee=1 goal=1; authority-grant granter=2 grantee=1 authority=infra; simulate; save path=data/saves/slice2.save"
client "batch inspect-replay path=data/saves/slice2.save; events"
```

Expected: replay contains `event=client.network.fail` entries.

Notes:
- All identifiers are generic; no world assumptions are implied.
- Delegation and authority are enforced via deterministic refusal codes.