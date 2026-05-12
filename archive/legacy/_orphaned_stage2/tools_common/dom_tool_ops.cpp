/*
FILE: source/dominium/tools/common/dom_tool_ops.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/common/dom_tool_ops
RESPONSIBILITY: Implements `dom_tool_ops`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_tool_ops.h"

#include "dom_tool_io.h"
#include "dom_tool_validate.h"

extern "C" {
#include "domino/system/dsys.h"
}

namespace dom {
namespace tools {

bool load_tlv_file(const std::string &path,
                   std::vector<unsigned char> &out,
                   std::string *err) {
    return read_file(path, out, err);
}

bool save_tlv_file(const std::string &path,
                   const std::vector<unsigned char> &data,
                   std::string *err) {
    const unsigned char *ptr = data.empty() ? (const unsigned char *)0 : &data[0];
    return write_file(path, ptr, data.size(), err);
}

bool validate_tlv_against_schema(u32 schema_id,
                                 const std::vector<unsigned char> &payload,
                                 std::string *err) {
    return validate_schema_payload(schema_id, payload, err);
}

bool preview_entity(u32 schema_id, u32 entity_id, std::string *err) {
    (void)schema_id;
    (void)entity_id;
    if (err) *err = "preview_entity: TODO";
    return false;
}

bool preview_world_slice(int x, int y, int z, int radius, std::string *err) {
    (void)x; (void)y; (void)z; (void)radius;
    if (err) *err = "preview_world_slice: TODO";
    return false;
}

bool preview_process_flow(u32 process_id, std::string *err) {
    (void)process_id;
    if (err) *err = "preview_process_flow: TODO";
    return false;
}

bool open_in_engine_for_validation(const std::string &exe_path,
                                   const std::vector<std::string> &args,
                                   std::string *err) {
    std::vector<const char *> argv;
    size_t i;

    if (exe_path.empty()) {
        if (err) *err = "open_in_engine_for_validation: empty exe_path";
        return false;
    }

    argv.resize(args.size() + 2u, (const char *)0);
    argv[0] = exe_path.c_str();
    for (i = 0u; i < args.size(); ++i) {
        argv[i + 1u] = args[i].c_str();
    }
    argv[args.size() + 1u] = 0;

    {
        dsys_process_handle handle;
        const dsys_proc_result rc = dsys_proc_spawn(exe_path.c_str(), &argv[0], 1, &handle);
        if (rc != DSYS_PROC_OK) {
            if (err) *err = "open_in_engine_for_validation: spawn failed";
            return false;
        }
        {
            int exit_code = 0;
            const dsys_proc_result wrc = dsys_proc_wait(&handle, &exit_code);
            if (wrc != DSYS_PROC_OK) {
                if (err) *err = "open_in_engine_for_validation: wait failed";
                return false;
            }
            if (exit_code != 0) {
                if (err) *err = "open_in_engine_for_validation: process failed";
                return false;
            }
        }
    }

    return true;
}

} // namespace tools
} // namespace dom

