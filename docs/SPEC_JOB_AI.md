Jobs/AI subsystem (stub)
-----------------------
- Job templates are identified by `d_job_template_id` (see `d_job_proto.h`); runtime jobs use `d_job_instance` (id, template_id, flags, subject/target entity ids, target position, params TLV).
- Minimal planner stub: `d_job_tick` currently no-ops but iterates all jobs for a world.
- Jobs are created/destroyed with `d_job_create` / `d_job_destroy`; registry is per-world using a fixed table.
- Chunk-level persistence is empty for now; instance-level persistence under `TAG_SUBSYS_DJOB` stores count + job records (ids, template, flags, entities, target coords, params blob).
- Model registration is not defined yet; hooks remain stubs for future planners.
- Launcher/setup do not synthesize jobs; they only ensure the job template schemas in packs/mods align with the running core/suite version during compatibility checks.
