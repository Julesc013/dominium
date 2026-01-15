#include <cstdio>
#include <cstring>
#include <fstream>
#include <string>
#include <vector>

#include "dominium/core_err.h"
#include "dominium/core_tlv_schema.h"
#include "dominium/core_job.h"

#include "launcher_tlv_schema_registry.h"
#include "dsk/dsk_tlv_schema_registry.h"

#ifndef DOM_TLV_VECTORS_DIR
#define DOM_TLV_VECTORS_DIR "."
#endif

static int fail(const char* msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static bool read_file_bytes(const std::string& path, std::vector<unsigned char>& out) {
    std::ifstream in(path.c_str(), std::ios::binary);
    if (!in) {
        return false;
    }
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    in.seekg(0, std::ios::beg);
    if (size < 0) {
        return false;
    }
    out.resize((size_t)size);
    if (size > 0) {
        in.read(reinterpret_cast<char*>(&out[0]), size);
    }
    return in.good() || in.eof();
}

static u32 lcg_next(u32* state) {
    *state = (*state * 1664525u) + 1013904223u;
    return *state;
}

static int register_schemas(void) {
    core_tlv_schema_reset_registry();
    if (!dom::launcher_core::launcher_register_tlv_schemas()) {
        return 0;
    }
    if (!dsk_register_tlv_schemas()) {
        return 0;
    }
    if (!core_job_register_tlv_schemas()) {
        return 0;
    }
    return 1;
}

static int expect_invalid(u32 schema_id, const std::vector<unsigned char>& data) {
    u32 version = 0u;
    err_t err = core_tlv_schema_validate(schema_id,
                                         data.empty() ? (const unsigned char*)0 : &data[0],
                                         (u32)data.size(),
                                         &version);
    if (err_is_ok(&err)) {
        return 0;
    }
    return 1;
}

int main(void) {
    std::vector<unsigned char> inst;
    std::vector<unsigned char> state;
    std::vector<unsigned char> bad;
    u32 seed = 0xC0FFEEu;
    u32 i;

    if (!register_schemas()) {
        return fail("schema registry init failed");
    }

    if (!read_file_bytes(std::string(DOM_TLV_VECTORS_DIR) + "/instance_manifest/instance_v2_basic.tlv", inst)) {
        return fail("failed to read instance vector");
    }
    if (!read_file_bytes(std::string(DOM_TLV_VECTORS_DIR) + "/installed_state/installed_state_v1.tlv", state)) {
        return fail("failed to read installed_state vector");
    }

    if (inst.size() > 1u) {
        bad.assign(inst.begin(), inst.end() - 1u);
        if (!expect_invalid((u32)CORE_TLV_SCHEMA_LAUNCHER_INSTANCE_MANIFEST, bad)) {
            return fail("expected instance manifest truncation to fail");
        }
    }
    if (state.size() > 1u) {
        bad.assign(state.begin(), state.end() - 1u);
        if (!expect_invalid((u32)CORE_TLV_SCHEMA_SETUP_INSTALLED_STATE, bad)) {
            return fail("expected installed_state truncation to fail");
        }
    }
    if (inst.size() > 8u) {
        bad = inst;
        bad[4] = 0xFFu;
        bad[5] = 0xFFu;
        bad[6] = 0xFFu;
        bad[7] = 0x7Fu;
        (void)expect_invalid((u32)CORE_TLV_SCHEMA_LAUNCHER_INSTANCE_MANIFEST, bad);
    }

    for (i = 0u; i < 256u; ++i) {
        u32 len = (lcg_next(&seed) % 256u);
        bad.resize(len);
        for (u32 j = 0u; j < len; ++j) {
            bad[j] = (unsigned char)(lcg_next(&seed) & 0xFFu);
        }
        (void)core_tlv_schema_validate((u32)CORE_TLV_SCHEMA_LAUNCHER_INSTANCE_MANIFEST,
                                       bad.empty() ? (const unsigned char*)0 : &bad[0],
                                       (u32)bad.size(),
                                       &len);
        (void)core_tlv_schema_validate((u32)CORE_TLV_SCHEMA_SETUP_INSTALLED_STATE,
                                       bad.empty() ? (const unsigned char*)0 : &bad[0],
                                       (u32)bad.size(),
                                       &len);
    }

    return 0;
}
