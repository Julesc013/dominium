# compat Authority Scan

## Status

- Scan type: `authority_scan`
- Findings: 849
- Moves/rewrites applied: `false`

## Markers Found

- `compat/capability_negotiation.py:1` capability
- `compat/capability_negotiation.py:15` canonical
- `compat/capability_negotiation.py:15` sha256
- `compat/capability_negotiation.py:18` capability
- `compat/capability_negotiation.py:21` contract
- `compat/capability_negotiation.py:23` capability
- `compat/capability_negotiation.py:25` refusal
- `compat/capability_negotiation.py:26` contract
- `compat/capability_negotiation.py:26` refusal
- `compat/capability_negotiation.py:27` refusal
- `compat/capability_negotiation.py:95` contract
- `compat/capability_negotiation.py:96` contract
- `compat/capability_negotiation.py:106` contract
- `compat/capability_negotiation.py:113` capability
- `compat/capability_negotiation.py:114` capability
- `compat/capability_negotiation.py:117` capability
- `compat/capability_negotiation.py:118` capability
- `compat/capability_negotiation.py:122` capability
- `compat/capability_negotiation.py:133` contract
- `compat/capability_negotiation.py:134` contract
- `compat/capability_negotiation.py:141` capability
- `compat/capability_negotiation.py:142` capability
- `compat/capability_negotiation.py:148` schema
- `compat/capability_negotiation.py:155` canonical
- `compat/capability_negotiation.py:155` sha256
- `compat/capability_negotiation.py:159` contract
- `compat/capability_negotiation.py:162` schema
- `compat/capability_negotiation.py:163` contract
- `compat/capability_negotiation.py:171` canonical
- `compat/capability_negotiation.py:171` sha256
- `compat/capability_negotiation.py:181` schema
- `compat/capability_negotiation.py:183` capability
- `compat/capability_negotiation.py:193` canonical
- `compat/capability_negotiation.py:193` sha256
- `compat/capability_negotiation.py:204` canonical
- `compat/capability_negotiation.py:204` sha256
- `compat/capability_negotiation.py:211` schema
- `compat/capability_negotiation.py:212` capability
- `compat/capability_negotiation.py:217` canonical
- `compat/capability_negotiation.py:217` sha256
- `compat/capability_negotiation.py:221` contract
- `compat/capability_negotiation.py:222` contract
- `compat/capability_negotiation.py:225` contract
- `compat/capability_negotiation.py:228` contract
- `compat/capability_negotiation.py:233` contract
- `compat/capability_negotiation.py:237` contract
- `compat/capability_negotiation.py:238` contract
- `compat/capability_negotiation.py:244` contract
- `compat/capability_negotiation.py:246` schema
- `compat/capability_negotiation.py:247` contract

## Highest-Risk Files

- `compat/__init__.py`
- `compat/capability_negotiation.py`
- `compat/data_format_loader.py`
- `compat/migration_lifecycle.py`
- `compat/descriptor/__init__.py`
- `compat/descriptor/descriptor_engine.py`
- `compat/handshake/__init__.py`
- `compat/handshake/handshake_engine.py`
- `compat/negotiation/__init__.py`
- `compat/negotiation/degrade_enforcer.py`
- `compat/negotiation/negotiation_engine.py`
- `compat/shims/__init__.py`
- `compat/shims/common.py`
- `compat/shims/flag_shims.py`
- `compat/shims/path_shims.py`
- `compat/shims/tool_shims.py`
- `compat/shims/validation_shims.py`

## Unknowns

- preserve_unknown entries: 4

## Future Validator Needs

Dedicated validators are required before moving any sensitive files from this root.
