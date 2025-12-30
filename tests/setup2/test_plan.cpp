#include "dsk/dsk_contracts.h"
#include "dsk/dsk_digest.h"
#include "dsk/dsk_error.h"
#include "dsk/dsk_plan.h"
#include "dsk/dsk_splat_caps.h"
#include "dsk/dsk_tlv.h"
#include "dsk_resolve.h"

#include <algorithm>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <vector>

#ifndef SETUP2_TESTS_SOURCE_DIR
#define SETUP2_TESTS_SOURCE_DIR "."
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static void build_fixture_manifest(dsk_manifest_t *out_manifest, int legacy_linux_only) {
    dsk_manifest_clear(out_manifest);
    out_manifest->product_id = "dominium";
    out_manifest->version = "1.0.0";
    out_manifest->build_id = "dev";
    out_manifest->supported_targets.push_back("win32_nt5");
    out_manifest->supported_targets.push_back("linux_deb");

    {
        dsk_layout_template_t layout;
        layout.template_id = "root_base";
        layout.target_root = "primary";
        layout.path_prefix = "app";
        out_manifest->layout_templates.push_back(layout);
    }

    {
        dsk_manifest_component_t comp;
        comp.component_id = "base";
        comp.kind = "runtime";
        comp.default_selected = DSK_TRUE;
        {
            dsk_artifact_t art;
            art.artifact_id = "base_art";
            art.hash = "basehash";
            art.digest64 = 0x1111111111111111ULL;
            art.size = 100u;
            art.source_path = "base.dat";
            art.layout_template_id = "root_base";
            comp.artifacts.push_back(art);
        }
        out_manifest->components.push_back(comp);
    }

    {
        dsk_manifest_component_t comp;
        comp.component_id = "core";
        comp.kind = "product";
        comp.default_selected = DSK_TRUE;
        comp.deps.push_back("base");
        comp.conflicts.push_back("legacy");
        {
            dsk_artifact_t art;
            art.artifact_id = "core_art";
            art.hash = "corehash";
            art.digest64 = 0x2222222222222222ULL;
            art.size = 200u;
            art.source_path = "core.dat";
            art.layout_template_id = "root_base";
            comp.artifacts.push_back(art);
        }
        out_manifest->components.push_back(comp);
    }

    {
        dsk_manifest_component_t comp;
        comp.component_id = "legacy";
        comp.kind = "product";
        comp.default_selected = DSK_FALSE;
        if (legacy_linux_only) {
            comp.supported_targets.push_back("linux_deb");
        }
        {
            dsk_artifact_t art;
            art.artifact_id = "legacy_art";
            art.hash = "legacyhash";
            art.digest64 = 0x3333333333333333ULL;
            art.size = 300u;
            art.source_path = "legacy.dat";
            art.layout_template_id = "root_base";
            comp.artifacts.push_back(art);
        }
        out_manifest->components.push_back(comp);
    }
}

static void build_request_default(dsk_request_t *out_request) {
    dsk_request_clear(out_request);
    out_request->operation = DSK_OPERATION_INSTALL;
    out_request->install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    out_request->ui_mode = DSK_UI_MODE_CLI;
    out_request->policy_flags = DSK_POLICY_DETERMINISTIC;
    out_request->target_platform_triple = "win32_nt5";
}

static void build_request_custom(dsk_request_t *out_request) {
    dsk_request_clear(out_request);
    out_request->operation = DSK_OPERATION_INSTALL;
    out_request->install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    out_request->ui_mode = DSK_UI_MODE_CLI;
    out_request->policy_flags = DSK_POLICY_DETERMINISTIC;
    out_request->target_platform_triple = "win32_nt5";
    out_request->requested_components.push_back("legacy");
}

static dsk_status_t write_manifest_bytes(const dsk_manifest_t &manifest,
                                         std::vector<dsk_u8> &out) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st = dsk_manifest_write(&manifest, &buf);
    if (dsk_error_is_ok(st)) {
        out.assign(buf.data, buf.data + buf.size);
    }
    dsk_tlv_buffer_free(&buf);
    return st;
}

static dsk_status_t write_request_bytes(const dsk_request_t &request,
                                        std::vector<dsk_u8> &out) {
    dsk_tlv_buffer_t buf;
    dsk_status_t st = dsk_request_write(&request, &buf);
    if (dsk_error_is_ok(st)) {
        out.assign(buf.data, buf.data + buf.size);
    }
    dsk_tlv_buffer_free(&buf);
    return st;
}

static void build_caps(dsk_splat_caps_t *out_caps) {
    dsk_splat_caps_clear(out_caps);
    out_caps->supported_scopes = DSK_SPLAT_SCOPE_USER | DSK_SPLAT_SCOPE_SYSTEM | DSK_SPLAT_SCOPE_PORTABLE;
    out_caps->supported_ui_modes = DSK_SPLAT_UI_CLI;
    out_caps->supports_portable_ownership = DSK_TRUE;
    out_caps->default_root_convention = DSK_SPLAT_ROOT_CONVENTION_PORTABLE;
    out_caps->elevation_required = DSK_SPLAT_ELEVATION_NEVER;
    out_caps->rollback_semantics = DSK_SPLAT_ROLLBACK_NONE;
}

static dsk_status_t build_plan(const dsk_manifest_t &manifest,
                               const dsk_request_t &request,
                               dsk_plan_t *out_plan) {
    dsk_resolved_set_t resolved;
    std::vector<dsk_plan_refusal_t> refusals;
    dsk_splat_caps_t caps;
    dsk_u64 caps_digest;
    dsk_u64 manifest_digest;
    dsk_u64 request_digest;
    std::vector<dsk_u8> manifest_bytes;
    std::vector<dsk_u8> request_bytes;
    dsk_status_t st;

    st = dsk_resolve_components(manifest, request, request.target_platform_triple, &resolved, &refusals);
    if (!dsk_error_is_ok(st)) {
        return st;
    }

    build_caps(&caps);
    caps_digest = dsk_splat_caps_digest64(&caps);

    st = write_manifest_bytes(manifest, manifest_bytes);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    st = write_request_bytes(request, request_bytes);
    if (!dsk_error_is_ok(st)) {
        return st;
    }
    manifest_digest = dsk_digest64_bytes(&manifest_bytes[0], (dsk_u32)manifest_bytes.size());
    request_digest = dsk_digest64_bytes(&request_bytes[0], (dsk_u32)request_bytes.size());

    return dsk_plan_build(manifest,
                          request,
                          "splat_portable",
                          caps,
                          caps_digest,
                          resolved,
                          manifest_digest,
                          request_digest,
                          out_plan);
}

static int read_file_bytes(const std::string &path, std::vector<dsk_u8> &out) {
    std::ifstream in(path.c_str(), std::ios::binary);
    if (!in) {
        return 0;
    }
    in.seekg(0, std::ios::end);
    std::streamoff size = in.tellg();
    in.seekg(0, std::ios::beg);
    if (size <= 0) {
        return 0;
    }
    out.resize((size_t)size);
    in.read(reinterpret_cast<char *>(&out[0]), size);
    return in.good() || in.eof();
}

static int test_resolve_default_components(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_resolved_set_t resolved;
    dsk_status_t st;

    build_fixture_manifest(&manifest, 0);
    build_request_default(&request);

    st = dsk_resolve_components(manifest, request, request.target_platform_triple, &resolved, 0);
    if (!dsk_error_is_ok(st)) {
        return fail("resolve default failed");
    }
    if (resolved.components.size() != 2u) {
        return fail("unexpected default component count");
    }
    if (resolved.components[0].component_id != "base" ||
        resolved.components[1].component_id != "core") {
        return fail("unexpected default component ids");
    }
    return 0;
}

static int test_resolve_explicit_components(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_resolved_set_t resolved;
    dsk_status_t st;

    build_fixture_manifest(&manifest, 0);
    build_request_custom(&request);

    st = dsk_resolve_components(manifest, request, request.target_platform_triple, &resolved, 0);
    if (!dsk_error_is_ok(st)) {
        return fail("resolve explicit failed");
    }
    if (resolved.components.size() != 1u) {
        return fail("unexpected explicit component count");
    }
    if (resolved.components[0].component_id != "legacy") {
        return fail("unexpected explicit component id");
    }
    return 0;
}

static int test_resolve_dependency_closure(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_resolved_set_t resolved;
    dsk_status_t st;

    build_fixture_manifest(&manifest, 0);
    build_request_default(&request);
    request.requested_components.clear();
    request.requested_components.push_back("core");

    st = dsk_resolve_components(manifest, request, request.target_platform_triple, &resolved, 0);
    if (!dsk_error_is_ok(st)) {
        return fail("resolve dependency closure failed");
    }
    if (resolved.components.size() != 2u) {
        return fail("unexpected dependency closure count");
    }
    if (resolved.components[0].component_id != "base" ||
        resolved.components[1].component_id != "core") {
        return fail("unexpected dependency closure ids");
    }
    return 0;
}

static int test_resolve_conflict_refusal(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_resolved_set_t resolved;
    std::vector<dsk_plan_refusal_t> refusals;
    dsk_status_t st;

    build_fixture_manifest(&manifest, 0);
    build_request_default(&request);
    request.requested_components.clear();
    request.requested_components.push_back("core");
    request.requested_components.push_back("legacy");

    st = dsk_resolve_components(manifest, request, request.target_platform_triple, &resolved, &refusals);
    if (dsk_error_is_ok(st)) {
        return fail("expected conflict refusal");
    }
    if (st.subcode != DSK_SUBCODE_EXPLICIT_CONFLICT) {
        return fail("unexpected conflict subcode");
    }
    if (refusals.empty() || refusals[0].code != DSK_PLAN_REFUSAL_EXPLICIT_CONFLICT) {
        return fail("missing conflict refusal");
    }
    return 0;
}

static int test_resolve_platform_incompat_refusal(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_resolved_set_t resolved;
    std::vector<dsk_plan_refusal_t> refusals;
    dsk_status_t st;

    build_fixture_manifest(&manifest, 1);
    build_request_default(&request);
    request.requested_components.clear();
    request.requested_components.push_back("legacy");

    st = dsk_resolve_components(manifest, request, request.target_platform_triple, &resolved, &refusals);
    if (dsk_error_is_ok(st)) {
        return fail("expected platform incompat refusal");
    }
    if (st.subcode != DSK_SUBCODE_PLATFORM_INCOMPATIBLE) {
        return fail("unexpected platform incompat subcode");
    }
    if (refusals.empty() || refusals[0].code != DSK_PLAN_REFUSAL_PLATFORM_INCOMPATIBLE) {
        return fail("missing platform incompat refusal");
    }
    return 0;
}

static int test_plan_byte_identical_repeat(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_plan_t plan;
    dsk_tlv_buffer_t a;
    dsk_tlv_buffer_t b;
    dsk_status_t st;

    build_fixture_manifest(&manifest, 0);
    build_request_default(&request);

    st = build_plan(manifest, request, &plan);
    if (!dsk_error_is_ok(st)) {
        return fail("plan build failed");
    }

    st = dsk_plan_write(&plan, &a);
    if (!dsk_error_is_ok(st)) {
        return fail("plan write A failed");
    }
    st = dsk_plan_write(&plan, &b);
    if (!dsk_error_is_ok(st)) {
        dsk_tlv_buffer_free(&a);
        return fail("plan write B failed");
    }

    if (a.size != b.size || std::memcmp(a.data, b.data, a.size) != 0) {
        dsk_tlv_buffer_free(&a);
        dsk_tlv_buffer_free(&b);
        return fail("plan bytes not identical");
    }
    dsk_tlv_buffer_free(&a);
    dsk_tlv_buffer_free(&b);
    return 0;
}

static int test_plan_digest_stable(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_plan_t plan;
    dsk_plan_t parsed;
    dsk_tlv_buffer_t buf;
    dsk_status_t st;
    dsk_u64 digest;

    build_fixture_manifest(&manifest, 0);
    build_request_default(&request);

    st = build_plan(manifest, request, &plan);
    if (!dsk_error_is_ok(st)) {
        return fail("plan build failed");
    }
    st = dsk_plan_write(&plan, &buf);
    if (!dsk_error_is_ok(st)) {
        return fail("plan write failed");
    }
    st = dsk_plan_parse(buf.data, buf.size, &parsed);
    if (!dsk_error_is_ok(st)) {
        dsk_tlv_buffer_free(&buf);
        return fail("plan parse failed");
    }
    digest = dsk_plan_payload_digest(&parsed);
    dsk_tlv_buffer_free(&buf);
    if (digest != parsed.plan_digest64) {
        return fail("plan digest mismatch");
    }
    return 0;
}

static int test_plan_validate_rejects_corrupt_header(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_plan_t plan;
    dsk_tlv_buffer_t buf;
    dsk_status_t st;

    build_fixture_manifest(&manifest, 0);
    build_request_default(&request);

    st = build_plan(manifest, request, &plan);
    if (!dsk_error_is_ok(st)) {
        return fail("plan build failed");
    }
    st = dsk_plan_write(&plan, &buf);
    if (!dsk_error_is_ok(st)) {
        return fail("plan write failed");
    }
    if (buf.size > 16u) {
        buf.data[16] ^= 0xFFu;
    }
    st = dsk_plan_parse(buf.data, buf.size, &plan);
    dsk_tlv_buffer_free(&buf);
    if (dsk_error_is_ok(st)) {
        return fail("expected corrupt header failure");
    }
    if (st.subcode != DSK_SUBCODE_TLV_BAD_CRC) {
        return fail("unexpected corrupt header subcode");
    }
    return 0;
}

static int test_plan_lists_canonically_sorted(void) {
    dsk_plan_t plan;
    dsk_plan_t parsed;
    dsk_tlv_buffer_t buf;
    dsk_status_t st;

    dsk_plan_clear(&plan);
    plan.product_id = "dominium";
    plan.product_version = "1.0.0";
    plan.selected_splat_id = "splat_portable";
    plan.selected_splat_caps_digest64 = 0xAAAABBBBCCCCDDDDULL;
    plan.operation = DSK_OPERATION_INSTALL;
    plan.install_scope = DSK_INSTALL_SCOPE_SYSTEM;
    plan.install_roots.push_back("root:b");
    plan.install_roots.push_back("root:a");
    plan.manifest_digest64 = 0x1111111111111111ULL;
    plan.request_digest64 = 0x2222222222222222ULL;
    plan.resolved_set_digest64 = 0x3333333333333333ULL;

    {
        dsk_resolved_component_t a;
        dsk_resolved_component_t b;
        a.component_id = "core";
        a.component_version = "1.0.0";
        a.kind = "product";
        a.source = DSK_PLAN_COMPONENT_SOURCE_DEFAULT;
        b.component_id = "base";
        b.component_version = "1.0.0";
        b.kind = "runtime";
        b.source = DSK_PLAN_COMPONENT_SOURCE_DEFAULT;
        plan.resolved_components.push_back(a);
        plan.resolved_components.push_back(b);
    }
    {
        dsk_plan_step_t step_a;
        dsk_plan_step_t step_b;
        step_a.step_id = 2u;
        step_a.step_kind = DSK_PLAN_STEP_STAGE_ARTIFACT;
        step_b.step_id = 1u;
        step_b.step_kind = DSK_PLAN_STEP_VERIFY_HASHES;
        plan.ordered_steps.push_back(step_a);
        plan.ordered_steps.push_back(step_b);
    }
    {
        dsk_plan_file_op_t op_a;
        dsk_plan_file_op_t op_b;
        op_a.op_kind = DSK_PLAN_FILE_OP_COPY;
        op_a.to_path = "z.dat";
        op_b.op_kind = DSK_PLAN_FILE_OP_COPY;
        op_b.to_path = "a.dat";
        plan.file_ops.push_back(op_a);
        plan.file_ops.push_back(op_b);
    }

    plan.plan_digest64 = dsk_plan_payload_digest(&plan);
    st = dsk_plan_write(&plan, &buf);
    if (!dsk_error_is_ok(st)) {
        return fail("plan write failed");
    }
    st = dsk_plan_parse(buf.data, buf.size, &parsed);
    dsk_tlv_buffer_free(&buf);
    if (!dsk_error_is_ok(st)) {
        return fail("plan parse failed");
    }
    if (parsed.install_roots[0] != "root:a") {
        return fail("install_roots not sorted");
    }
    if (parsed.resolved_components[0].component_id != "base") {
        return fail("resolved_components not sorted");
    }
    if (parsed.ordered_steps[0].step_id != 1u) {
        return fail("ordered_steps not sorted");
    }
    if (parsed.file_ops[0].to_path != "a.dat") {
        return fail("file_ops not sorted");
    }
    return 0;
}

static int test_plan_golden_default(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_plan_t plan;
    dsk_tlv_buffer_t buf;
    std::vector<dsk_u8> golden;
    dsk_status_t st;
    std::string path = std::string(SETUP2_TESTS_SOURCE_DIR) + "/golden/plan_default.tlv";

    build_fixture_manifest(&manifest, 0);
    build_request_default(&request);

    st = build_plan(manifest, request, &plan);
    if (!dsk_error_is_ok(st)) {
        return fail("plan build failed");
    }
    st = dsk_plan_write(&plan, &buf);
    if (!dsk_error_is_ok(st)) {
        return fail("plan write failed");
    }
    if (!read_file_bytes(path, golden)) {
        dsk_tlv_buffer_free(&buf);
        return fail("failed to read golden default plan");
    }
    if (buf.size != golden.size() ||
        std::memcmp(buf.data, &golden[0], buf.size) != 0) {
        dsk_tlv_buffer_free(&buf);
        return fail("golden default plan mismatch");
    }
    dsk_tlv_buffer_free(&buf);
    return 0;
}

static int test_plan_golden_custom(void) {
    dsk_manifest_t manifest;
    dsk_request_t request;
    dsk_plan_t plan;
    dsk_tlv_buffer_t buf;
    std::vector<dsk_u8> golden;
    dsk_status_t st;
    std::string path = std::string(SETUP2_TESTS_SOURCE_DIR) + "/golden/plan_custom.tlv";

    build_fixture_manifest(&manifest, 0);
    build_request_custom(&request);

    st = build_plan(manifest, request, &plan);
    if (!dsk_error_is_ok(st)) {
        return fail("plan build failed");
    }
    st = dsk_plan_write(&plan, &buf);
    if (!dsk_error_is_ok(st)) {
        return fail("plan write failed");
    }
    if (!read_file_bytes(path, golden)) {
        dsk_tlv_buffer_free(&buf);
        return fail("failed to read golden custom plan");
    }
    if (buf.size != golden.size() ||
        std::memcmp(buf.data, &golden[0], buf.size) != 0) {
        dsk_tlv_buffer_free(&buf);
        return fail("golden custom plan mismatch");
    }
    dsk_tlv_buffer_free(&buf);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: setup2_plan_tests <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "resolve_default_components") == 0) {
        return test_resolve_default_components();
    }
    if (std::strcmp(argv[1], "resolve_explicit_components") == 0) {
        return test_resolve_explicit_components();
    }
    if (std::strcmp(argv[1], "resolve_dependency_closure") == 0) {
        return test_resolve_dependency_closure();
    }
    if (std::strcmp(argv[1], "resolve_conflict_refusal") == 0) {
        return test_resolve_conflict_refusal();
    }
    if (std::strcmp(argv[1], "resolve_platform_incompat_refusal") == 0) {
        return test_resolve_platform_incompat_refusal();
    }
    if (std::strcmp(argv[1], "plan_byte_identical_repeat") == 0) {
        return test_plan_byte_identical_repeat();
    }
    if (std::strcmp(argv[1], "plan_digest_stable") == 0) {
        return test_plan_digest_stable();
    }
    if (std::strcmp(argv[1], "plan_validate_rejects_corrupt_header") == 0) {
        return test_plan_validate_rejects_corrupt_header();
    }
    if (std::strcmp(argv[1], "plan_lists_canonically_sorted") == 0) {
        return test_plan_lists_canonically_sorted();
    }
    if (std::strcmp(argv[1], "plan_golden_default") == 0) {
        return test_plan_golden_default();
    }
    if (std::strcmp(argv[1], "plan_golden_custom") == 0) {
        return test_plan_golden_custom();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
