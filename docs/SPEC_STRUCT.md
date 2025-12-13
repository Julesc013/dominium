# Structures / Machines (STRUCT)

The structure subsystem stores placed structure instances and provides generic hooks for other subsystems (ENV/HYDRO/RES) without embedding game-specific semantics.

## 1. Instances
- `d_struct_instance` stores id, proto id, transform, chunk id, flags, optional entity link, inventory summary, and an opaque TLV `state` blob.
- Chunk persistence uses `TAG_SUBSYS_DSTRUCT`: count + instance records.

## 2. Prototypes
- Prototypes come from the content layer (`d_proto_structure`) and include TLV blobs:
  - `layout`: generic layout + attachments
  - `io`: generic port definitions
  - `processes`: process list

## 3. ENV Volume Integration
- On spawn, STRUCT may create interior environmental volumes from `proto->layout`:
  - `D_TLV_ENV_VOLUME`: local AABB in Q16.16 (min/max for x/y/z)
  - `D_TLV_ENV_EDGE`: connects local volumes (`A`,`B`), where `B=0` couples to exterior; includes `GAS_K` and `HEAT_K`
- Created volumes are added to the ENV volume graph with `owner_struct_eid = struct_instance_id` and removed on destroy.

## 4. Optional Hydrology Flags
- `D_TLV_ENV_HYDRO_FLAGS` (u32) in `proto->layout` may mark generic hydro interactions (watertight/floodable/drains).

