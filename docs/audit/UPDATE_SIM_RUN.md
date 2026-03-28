Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen offline update simulation baseline for v0.0.0-mock distribution gating.

# Update Simulation Run

- result: `complete`
- platform_tag: `win64`
- deterministic_fingerprint: `ce80e21684ed3d7309fd6381b3e19d9c7f3d371eb341ed82d31d46c13c105d5e`
- baseline_present: `True`
- baseline_matches: `True`

## Scenario Results

- baseline install: result=`complete`, plan=`687022fe92ef135f9fb25632ffc5d55c7bbb1459eb4f97eaf61ee19875a27643`, component_set_hash=`7cc6df93ec4119111602263c8f8ad6dfe5d6115a63abb10b15f5dfa773d83e76`
- latest-compatible upgrade: result=`complete`, plan=`80888ede6c7659c925ec02f4fe1c57592ddc849b14a40e72f28f789c3d9b8af5`, client=`0.0.1`
- yanked exclusion: result=`complete`, skipped_yanked_count=`1`, selected_yanked=`none`
- strict trust: result=`complete`, refusal_code=`refusal.trust.signature_missing`
- rollback: result=`complete`, restored_component_set_hash=`7cc6df93ec4119111602263c8f8ad6dfe5d6115a63abb10b15f5dfa773d83e76`
