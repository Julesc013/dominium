# net Draft Salvage Map

## Status: Draft / Not Approved

- Apply allowed: `false`
- Approval status: `not_approved`
- Entry count: 22

## Recommended Fates

- `adapt`: 17
- `preserve_unknown`: 5

## Candidate Future Target Locations

No target paths are approved. Future targets must be selected by an approved move plan.

## High-Risk Files

- `net/__init__.py`
- `net/anti_cheat/__init__.py`
- `net/anti_cheat/anti_cheat_engine.py`
- `net/policies/__init__.py`
- `net/policies/policy_lockstep.py`
- `net/policies/policy_server_authoritative.py`
- `net/policies/policy_srz_hybrid.py`
- `net/srz/__init__.py`
- `net/srz/routing.py`
- `net/srz/shard_coordinator.py`
- `net/testing/__init__.py`
- `net/testing/net_disorder_sim.py`
- `net/transport/__init__.py`
- `net/transport/interface.py`
- `net/transport/loopback.py`
- `net/transport/tcp_stub.py`
- `net/transport/udp_stub.py`

## preserve_unknown Files

- `net/anti_cheat`
- `net/policies`
- `net/srz`
- `net/testing`
- `net/transport`

## References Requiring Future Rewrite

- Raw references recorded: 1083

## Validators Required Before Any Move

- AIDE salvage-map check
- repo layout strict validator
- root allowlist strict validator
- distribution/component validators
- docs/build/UI/ABI checks as applicable

## Blockers Before Move

- No approved salvage map.
- No approved move map.
- No reference rewrite plan.
- No rollback evidence packet.
