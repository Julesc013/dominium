Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen offline update simulation baseline for v0.0.0-mock distribution gating.

# Update Simulation Run

- result: `complete`
- platform_tag: `win64`
- deterministic_fingerprint: `2fd12a8ad0891b69597b5dfb412ca226adcb4d4bf6735ae4aac6c14100a3f00c`
- baseline_present: `False`
- baseline_matches: `False`

## Scenario Results

- baseline install: result=`complete`, plan=`49e343eb9f3e3361abb64927a7982a5c3c3e0573eafe2524741080c4542c6d32`, component_set_hash=`114a18fddbfdaf539b4ded185b7daa3dbd9bae7ada58715c5a98f2327656693c`
- latest-compatible upgrade: result=`complete`, plan=`426094261cb20830fd54f0da9a94d74439c65abf3d2ffde37975d4d10f9e92fd`, client=`0.0.1`
- yanked exclusion: result=`complete`, skipped_yanked_count=`1`, selected_yanked=`none`
- strict trust: result=`complete`, refusal_code=`refusal.trust.signature_missing`
- rollback: result=`complete`, restored_component_set_hash=`114a18fddbfdaf539b4ded185b7daa3dbd9bae7ada58715c5a98f2327656693c`
