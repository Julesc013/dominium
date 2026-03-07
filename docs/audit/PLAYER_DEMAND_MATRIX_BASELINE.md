# Player Demand Matrix Baseline

Status: BASELINE (META-GENRE-0)  
Date: 2026-03-07  
Scope: canonical player-demand mapping, machine registry, enforcement hooks, and gap reporting.

## 1) Summary Stats

- total_demands: `120`
- cluster_count: `10`
- coverage_histogram:
  - present: `30`
  - partial: `30`
  - planned: `30`
  - unknown: `30`
- per-cluster counts:
  - cities_infrastructure: `12`
  - crafting_engineering_realism: `12`
  - cyber_automation_hacking: `12`
  - factory_automation: `12`
  - military_defense_sabotage: `12`
  - sandbox_creative_magic_alt_physics: `12`
  - science_research_invention: `12`
  - space_engineering: `12`
  - survival_primitive_tech: `12`
  - transport_logistics: `12`

## 2) Top 20 Pipe-Dream Demands

- `city.blackout_restoration_plan`: Blackout Restoration Plan (cities_infrastructure)
- `city.bridge_load_management`: Bridge Load Management (cities_infrastructure)
- `city.district_heating_grid`: District Heating Grid (cities_infrastructure)
- `city.earthquake_retrofit_program`: Earthquake Retrofit Program (cities_infrastructure)
- `city.heatwave_cooling_strategy`: Heatwave Cooling Strategy (cities_infrastructure)
- `city.hospital_backup_power`: Hospital Backup Power (cities_infrastructure)
- `city.smart_meter_rollout`: Smart Meter Rollout (cities_infrastructure)
- `city.stormwater_overflow_control`: Stormwater Overflow Control (cities_infrastructure)
- `city.transit_signal_priority`: Transit Signal Priority (cities_infrastructure)
- `city.waste_sorting_ecology`: Waste Sorting Ecology (cities_infrastructure)
- `city.water_main_leak_response`: Water Main Leak Response (cities_infrastructure)
- `city.zoning_pollution_tradeoff`: Zoning Pollution Tradeoff (cities_infrastructure)
- `engr.bearing_failure_forensics`: Bearing Failure Forensics (crafting_engineering_realism)
- `engr.cleanroom_contamination_control`: Cleanroom Contamination Control (crafting_engineering_realism)
- `engr.diesel_engine_rebuild`: Diesel Engine Rebuild (crafting_engineering_realism)
- `engr.field_overhaul_campaign`: Field Overhaul Campaign (crafting_engineering_realism)
- `engr.heat_treat_recipe_lock`: Heat Treat Recipe Lock (crafting_engineering_realism)
- `engr.metrology_lab_flow`: Metrology Lab Flow (crafting_engineering_realism)
- `engr.milling_jig_calibration`: Milling Jig Calibration (crafting_engineering_realism)
- `engr.precision_lathe_alignment`: Precision Lathe Alignment (crafting_engineering_realism)

## 3) Top 20 Biggest Gaps

- `space.asteroid_mining_caravan`: status=`unknown` next_series=`ADV-0`
- `space.cryogenic_orbit_transfer`: status=`unknown` next_series=`ADV-0`
- `space.space_elevator_maintenance`: status=`unknown` next_series=`ADV-0`
- `sand.alternate_law_challenge`: status=`unknown` next_series=`ALT-PHYS-0`
- `sand.chaos_to_order_masterpiece`: status=`unknown` next_series=`ALT-PHYS-0`
- `sand.impossible_bridge_choreography`: status=`unknown` next_series=`ALT-PHYS-0`
- `city.hospital_backup_power`: status=`unknown` next_series=`CIV-0`
- `city.smart_meter_rollout`: status=`unknown` next_series=`CIV-0`
- `city.stormwater_overflow_control`: status=`unknown` next_series=`CIV-0`
- `fact.automated_rework_loop`: status=`unknown` next_series=`LOGIC-0`
- `fact.deadlock_free_signaling`: status=`unknown` next_series=`LOGIC-0`
- `fact.rapid_changeover`: status=`unknown` next_series=`LOGIC-0`
- `mil.battlefield_repair_pipeline`: status=`unknown` next_series=`MIL-0`
- `mil.blackout_psyops_counter`: status=`unknown` next_series=`MIL-0`
- `mil.radar_network_resilience`: status=`unknown` next_series=`MIL-0`
- `trans.harbor_tide_window_ops`: status=`unknown` next_series=`MOB-10`
- `trans.jit_factory_supply`: status=`unknown` next_series=`MOB-10`
- `trans.mega_convoy_security`: status=`unknown` next_series=`MOB-10`
- `surv.charcoal_pit_control`: status=`unknown` next_series=`PROC-10`
- `surv.rope_bridge_field_fix`: status=`unknown` next_series=`PROC-10`

## 4) Enforcement Behavior

- RepoX invariant: `INV-CHANGE-MUST-REFERENCE-DEMAND`
- AuditX analyzer: `OrphanFeatureSmell` (`E300_ORPHAN_FEATURE_SMELL`)
- FAST profile: warning semantics (non-blocking)
- STRICT/FULL profiles: blocking semantics via RepoX severity escalation

## 5) Gate Snapshot

- RepoX STRICT: `refusal` (repository-global pre-existing blockers unrelated to META-GENRE-0 remain)
  - command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
- AuditX STRICT: `pass`
  - command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
- TestX subset (META-GENRE-0): `pass`
  - command: `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_player_demand_matrix_schema_valid,test_demand_ids_unique_and_stable_format,test_referenced_ids_exist_or_marked_TBD_with_series,test_minimum_demand_count_met,test_each_cluster_has_min_entries,test_each_demand_has_action_family_mapping,test_each_demand_has_tier_and_explain_fields`
- Gap report tool: `pass`
  - command: `python tools/meta/tool_generate_demand_gap_report.py --repo-root .`
- Topology map update: `pass`
  - command: `python tools/governance/tool_topology_generate.py --repo-root .`

## 6) Readiness

- Canonical matrix defined with 120 demand entries across required 10 genre clusters.
- RWAM linkage enforced via `rwam_affordances` per demand.
- Explain-contract linkage enforced via matrix tests and registry checks.
- XStack demand-mapping hooks are in place for future feature series planning.
