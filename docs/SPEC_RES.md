Resource subsystem (stub in Prompt 3)
-------------------------------------
- Channel descriptors (`dres_channel_desc`) identify resource channels, model family/id, and flags.
- Each chunk stores `dres_channel_cell` entries (desc + `values[]` and `deltas[]` arrays). The stub creates one channel with model_id 1.
- Sampling returns `dres_sample` structures (channel id/family/model plus resolved `value[]`).
- Models use `dres_model_vtable` (`init_chunk`, `compute_base`, `apply_delta`, `tick`) and register through `dres_register_model` (family `D_MODEL_FAMILY_RES`). A dummy model (id 1) is pre-registered.
- Worldgen provider `res_default` (id 1) calls `dres_init_chunk` when a chunk is created.
- Serialization stores chunk cells under TLV tag `TAG_SUBSYS_DRES` (count + desc + values + deltas). Instance-level data is empty for now.
- Dominium launcher/setup never bypass this API; resource data rides inside pack TLVs selected by `dom_packset`, keeping compatibility checks straightforward when products validate suite/core versions.
