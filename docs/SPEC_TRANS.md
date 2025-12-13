# Transport Subsystem (Splines + Movers)

## Overview
- Engine-level logistics is expressed as **splines** (world geometry + profile) and **movers** (generic payloads moving along splines).
- The subsystem is domain-agnostic: it only understands splines, ports, movers, containers, vehicles, and fluid packets.

## Runtime Types
- `d_spline_node` (`trans/d_trans_spline.h`): world-space anchors in `q32_32` with optional normal/tangent fields (`q16_16`).
- `d_spline_instance` (`trans/d_trans_spline.h`): runtime spline instance with:
  - `id`, `profile_id`, `flags`
  - node range into a per-world node pool (`node_start_index`, `node_count`)
  - optional endpoint attachments (`endpoint_*_eid` + `endpoint_*_port_*`)
  - cached `length` in `q16_16`
- `d_mover` (`trans/d_trans_mover.h`): runtime mover with:
  - `kind`, `spline_id`, `param` in `[0,1]` (Q16.16)
  - `speed_param` (computed from profile + spline length), `size_param` (spacing hint)
  - `payload_id` / `payload_count` summary (item/container/vehicle/fluid id + units)

## Simulation Tick
- `d_trans_tick` advances movers via `d_trans_mover_tick`.
- Effective speed is derived from the spline profile (`base_speed`) and a simple grade factor (based on endpoint elevation delta vs spline length, clamped by `max_grade`).
- Endpoint behavior is generic:
  - If an item mover reaches an attached sink port, it attempts to deposit into the attached structure inventory (single-item inventory for now).
  - If a spline has an attached source port, the subsystem can spawn item movers by pulling from the source structure inventory.

## Serialization / Determinism
- Transport state is persisted via the subsystem serializer under `TAG_SUBSYS_DTRANS`:
  - spline records (id, profile, flags, endpoints, cached length, nodes)
  - mover records (id, kind, spline id, param, payload summary)
- `d_sim_hash_world` includes this serialized payload, making logistics state part of deterministic hashing.

