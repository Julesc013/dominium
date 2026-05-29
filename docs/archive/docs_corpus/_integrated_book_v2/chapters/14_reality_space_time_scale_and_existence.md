## 14. Reality, Space, Time, Scale, and Existence

The world model treats reality, existence, space, time, and scale as governed simulation concerns rather than renderer conveniences.

**Why this chapter matters.** Canon supplies the general law: deterministic process, event-driven advancement, provenance, and truth/perception separation. Conversation evidence adds scale concerns, visitability, temporal resilience, 2038 awareness, and layered representation.

> [!CURRENT_TRUTH] Current repo truth comes first in this chapter. Archive and conversation evidence is used to explain design intent, recurring concerns, and review candidates without promoting it.

### Integrated Evidence

The current repo-backed evidence emphasizes: Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular (EVC-00705).
The archive and conversation corpus add: Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular (EVC-00705). The key technical conclusion was that the world cannot be treated as a normal game-engine level full of live actors. The world must be a deterministic simulation and data system first. Domino should store the true universe as seeds, rules, fields, sparse (EVC-00274). The chat concluded that Dominium's requirements exceed what UE5, UE6, Domino, or any single commercial engine can provide out of the box. The game should be architected as a custom deterministic simulation and persistent world backend, with Unreal as a (EVC-00605). Major game-system design also emerged: deterministic fixed-point numeric policy, integer item storage, world origin at center/sea level, sparse 3D surface grid, Keplerian on-rails space, seamless surface/space transitions via reference frames and sim (EVC-00165).
The downstream implication is that: The practical purpose is simple: a future reader should be able to open this one file and quickly understand the substance of the conversation without needing to reread the whole transcript. It is not a replacement for the structured package; it is the (EVC-00265).

### Decisions Already Visible

- **Decision:** The key technical conclusion was that the world cannot be treated as a normal game-engine level full of live actors. The world must be a deterministic simulation and data system first. Domino should store the true universe as seeds, rules, fields, sparse... _Evidence:_ `EVC-00274` from `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md`. _Status:_ conversation advisory evidence.
- **Decision:** The chat concluded that Dominium's requirements exceed what UE5, UE6, Domino, or any single commercial engine can provide out of the box. The game should be architected as a custom deterministic simulation and persistent world backend, with Unreal as a... _Evidence:_ `EVC-00605` from `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__09_in_chat_reader.md`. _Status:_ conversation advisory evidence.

### Specifications and Requirements

- **Specification:** Major game-system design also emerged: deterministic fixed-point numeric policy, integer item storage, world origin at center/sea level, sparse 3D surface grid, Keplerian on-rails space, seamless surface/space transitions via reference frames and sim... _Evidence:_ `EVC-00165` from `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Specification:** 1. Domino should probably be the deterministic simulation/data core. 2. Unreal should not be assumed to own the authoritative universe. 3. Planets should be science-bounded procedural outputs, not arbitrary slider toys. 4. Designer painting should be an... _Evidence:_ `EVC-00242` from `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Specification:** What is Domino exactly? Should Unreal be first frontend? Which language/math stack should DominiumSim use? What terrain model is best? How exact must collapsed simulation be? What first MMO scale target is realistic? _Evidence:_ `EVC-00601` from `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__06_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Specification:** The chat began with the user pasting what they called the latest README. That README already had a strong direction: deterministic C89 engine core, C++98 higher layers, fixed-point math, bit-identical simulation across platforms, sparse planetary-scale... _Evidence:_ `EVC-00971` from `docs/archive/conversations/_reader/by_chat/readme_ports_determinism.md`. _Status:_ conversation advisory evidence.

### Constraints, Prohibitions, and Prerequisites

- **Prerequisite:** Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular... _Evidence:_ `EVC-00705` from `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`. _Status:_ conversation advisory evidence.
- **Constraint:** The mothership solves several design problems at once. It explains why players have a HUD, blueprints, recipes, construction guidance, and advanced technical knowledge. Players do not need to reinvent CPUs, railway gauges, smelting, computing, or... _Evidence:_ `EVC-00269` from `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md`. _Status:_ conversation advisory evidence.
- **Constraint:** The main outcome is not that Dominium needs a conceptual rewrite. The outcome is that Dominium's existing model is directionally correct, but needs boundary hardening: audit all DSYS backend timers, freeze ACT units and serialization semantics, prevent... _Evidence:_ `EVC-00560` from `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md`. _Status:_ conversation advisory evidence.
- **Constraint:** CP/M-80/86 is tooling/limited frontends only, not complete world simulation. _Evidence:_ `EVC-01387` from `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__05_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Prerequisite:** This is a recommendation, not a user-confirmed decision. It requires current verification and prototype tests before being formalised. _Evidence:_ `EVC-00235` from `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md`. _Status:_ conversation advisory evidence.
- **Prerequisite:** **The first real milestone should be small.** Prove spawn, survey, build, mine, refine, fabricate, and create a new spawn point before scaling to planets, cities, and MMO systems. _Evidence:_ `EVC-00272` from `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md`. _Status:_ conversation advisory evidence.
- **Prerequisite:** Before reading the rest of this report, remember this: this chat's central contribution is not one isolated feature. It is a whole design philosophy for Dominium's world engine. The game should be deterministic, fixed-point, sparse, modular... _Evidence:_ `EVC-01051` from `docs/archive/conversations/_reader/by_chat/world_architecture.md`. _Status:_ conversation advisory evidence.

### Contradictions, Risks, and Open Ends

- **Unresolved Question:** The main unresolved work is converting this concept into a formal spec and vertical slice. The best proposed first slice is: one planet region, one mothership, one robot body, one ore deposit, one power source, one cut/fill tool, one blueprint system... _Evidence:_ `EVC-00240` from `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md`. _Status:_ conversation advisory evidence.
- **Unresolved Question:** The unresolved detail is the exact representation: voxel chunks, signed-distance functions, heightfields, material fields, climate grids, graph overlays, or hybrid systems. _Evidence:_ `EVC-00271` from `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md`. _Status:_ conversation advisory evidence.
- **Unresolved Question:** The third unresolved issue is the exact time-scale mapping for Gregorian January 1, 2000 AD. The user specified the civil date, but not the exact technical instant. This affects deterministic world start. _Evidence:_ `EVC-00764` from `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`. _Status:_ conversation advisory evidence.
- **Change Of Direction:** The user then provided a long design monologue that changed the centre of gravity. The game became not only a technical engine challenge but a specific fiction and gameplay loop. The user described a procedurally generated star system or "galaxy" with as... _Evidence:_ `EVC-00234` from `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md`. _Status:_ conversation advisory evidence.
- **Change Of Direction:** The user then asked for the most compatible framework for cross-platform software intended to compile and run across past, present, and future target machines and operating systems. The answer shifted from arithmetic to architecture: durable code should... _Evidence:_ `EVC-00559` from `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md`. _Status:_ conversation advisory evidence.
- **Change Of Direction:** The user then asked for the most compatible framework for cross-platform software intended to compile and run across past, present, and future target machines and operating systems. The answer shifted from arithmetic to architecture: durable code should... _Evidence:_ `EVC-01012` from `docs/archive/conversations/_reader/by_chat/timekeeping_and_2038_resilience.md`. _Status:_ conversation advisory evidence.

### Second- and Third-Order Effects

- **Design Goal:** The practical purpose is simple: a future reader should be able to open this one file and quickly understand the substance of the conversation without needing to reread the whole transcript. It is not a replacement for the structured package; it is the... _Evidence:_ `EVC-00265` from `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md`. _Status:_ conversation advisory evidence.

### Implications for Next Work

Domain promotion should avoid treating speculative world-scale ambition as implemented gameplay.

Any later task that wants to move a claim from this chapter into live authority needs source IDs, target paths, authority compatibility, queue compatibility, and validation evidence. This chapter is therefore a review map, not a permission slip.

### Source Trail

- `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`
- `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md`
- `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__09_in_chat_reader.md`
- `docs/archive/conversations/Dominium_Architecture_IV/Dominium_Architecture_IV__05_reader_brief.md`
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__06_reader_brief.md`
- `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__06_reader_brief.md`
- `docs/archive/conversations/_reader/by_chat/readme_ports_determinism.md`
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__10_accompanying_human_readable_detailed_summary_report.md`
- `docs/archive/conversations/Timekeeping_and_2038_Resilience/Dominium_Timekeeping_and_2038_Resilience__01_human_readable_report.md`
- `docs/archive/conversations/readme_ports_determinism/dominium_readme_ports_determinism__05_reader_brief.md`
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__01_human_readable_report.md`
- `docs/archive/conversations/_reader/by_chat/world_architecture.md`
- `docs/archive/conversations/_reader/by_chat/chronology_celestial_systems.md`
- `docs/archive/conversations/_reader/by_chat/timekeeping_and_2038_resilience.md`
- `docs/archive/conversations/Dominium_Complete_Conversation/deterministic_solar_system_handoff_file/Dominium_Deterministic_Solar_System_Architecture__09_in_chat_reader.md`
- `docs/architecture/time_model.md`
- `docs/archive/audit/GR3_SCALE_METRICS.md`
- `docs/archive/audit/POWER_NETWORK_BASELINE.md`
