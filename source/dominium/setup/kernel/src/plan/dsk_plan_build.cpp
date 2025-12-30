#include "dsk/dsk_plan.h"

#include <algorithm>

static const dsk_manifest_component_t *dsk_find_component(const dsk_manifest_t &manifest,
                                                          const std::string &id) {
    size_t i;
    for (i = 0u; i < manifest.components.size(); ++i) {
        if (manifest.components[i].component_id == id) {
            return &manifest.components[i];
        }
    }
    return 0;
}

static const dsk_layout_template_t *dsk_find_layout_template(const dsk_manifest_t &manifest,
                                                              const std::string &id) {
    size_t i;
    for (i = 0u; i < manifest.layout_templates.size(); ++i) {
        if (manifest.layout_templates[i].template_id == id) {
            return &manifest.layout_templates[i];
        }
    }
    return 0;
}

static std::string dsk_root_convention_token(dsk_u16 convention) {
    switch (convention) {
    case DSK_SPLAT_ROOT_CONVENTION_PORTABLE:
        return "root:portable";
    case DSK_SPLAT_ROOT_CONVENTION_WINDOWS_PROGRAM_FILES:
        return "root:windows_program_files";
    case DSK_SPLAT_ROOT_CONVENTION_LINUX_PREFIX:
        return "root:linux_prefix";
    case DSK_SPLAT_ROOT_CONVENTION_MACOS_APPLICATIONS:
        return "root:macos_applications";
    case DSK_SPLAT_ROOT_CONVENTION_STEAM_LIBRARY:
        return "root:steam_library";
    default:
        return "root:unknown";
    }
}

static std::string dsk_join_rel_path(const std::string &a, const std::string &b) {
    if (a.empty()) {
        return b;
    }
    if (b.empty()) {
        return a;
    }
    if (a[a.size() - 1u] == '/') {
        return a + b;
    }
    return a + "/" + b;
}

static dsk_u16 dsk_select_ownership(const dsk_request_t &request,
                                    const dsk_splat_caps_t &caps) {
    if (request.ownership_preference != DSK_OWNERSHIP_ANY) {
        return request.ownership_preference;
    }
    if (caps.supports_pkg_ownership) {
        return DSK_OWNERSHIP_PKG;
    }
    if (caps.supports_portable_ownership) {
        return DSK_OWNERSHIP_PORTABLE;
    }
    return DSK_OWNERSHIP_ANY;
}

static dsk_u32 dsk_root_index_for(const std::string &root_token,
                                  const std::vector<std::string> &roots) {
    size_t i;
    if (root_token.empty()) {
        return 0u;
    }
    if (root_token == "primary") {
        return 0u;
    }
    for (i = 0u; i < roots.size(); ++i) {
        if (roots[i] == root_token) {
            return (dsk_u32)i;
        }
    }
    return 0u;
}

struct dsk_file_op_build_t {
    std::string root_key;
    std::string component_id;
    std::string artifact_id;
    dsk_u16 op_kind;
    std::string target_path;
    dsk_plan_file_op_t op;
};

struct dsk_step_build_t {
    std::string root_key;
    std::string component_id;
    std::string artifact_id;
    dsk_u16 step_kind;
    std::string target_path;
    dsk_plan_step_t step;
};

static bool dsk_file_op_build_less(const dsk_file_op_build_t &a,
                                   const dsk_file_op_build_t &b) {
    if (a.root_key != b.root_key) {
        return a.root_key < b.root_key;
    }
    if (a.component_id != b.component_id) {
        return a.component_id < b.component_id;
    }
    if (a.artifact_id != b.artifact_id) {
        return a.artifact_id < b.artifact_id;
    }
    if (a.op_kind != b.op_kind) {
        return a.op_kind < b.op_kind;
    }
    return a.target_path < b.target_path;
}

static bool dsk_step_build_less(const dsk_step_build_t &a,
                                const dsk_step_build_t &b) {
    if (a.root_key != b.root_key) {
        return a.root_key < b.root_key;
    }
    if (a.component_id != b.component_id) {
        return a.component_id < b.component_id;
    }
    if (a.artifact_id != b.artifact_id) {
        return a.artifact_id < b.artifact_id;
    }
    if (a.step_kind != b.step_kind) {
        return a.step_kind < b.step_kind;
    }
    return a.target_path < b.target_path;
}

dsk_status_t dsk_plan_build(const dsk_manifest_t &manifest,
                            const dsk_request_t &request,
                            const std::string &selected_splat_id,
                            const dsk_splat_caps_t &splat_caps,
                            dsk_u64 splat_caps_digest64,
                            const dsk_resolved_set_t &resolved,
                            dsk_u64 manifest_digest64,
                            dsk_u64 request_digest64,
                            dsk_plan_t *out_plan) {
    size_t i;
    std::vector<dsk_file_op_build_t> file_ops;
    std::vector<dsk_step_build_t> steps;
    std::vector<std::string> roots;
    dsk_u16 ownership;

    if (!out_plan) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }

    dsk_plan_clear(out_plan);
    out_plan->product_id = manifest.product_id;
    out_plan->product_version = manifest.version;
    out_plan->selected_splat_id = selected_splat_id;
    out_plan->selected_splat_caps_digest64 = splat_caps_digest64;
    out_plan->operation = request.operation;
    out_plan->install_scope = request.install_scope;
    out_plan->manifest_digest64 = manifest_digest64;
    out_plan->request_digest64 = request_digest64;
    out_plan->resolved_set_digest64 = resolved.digest64;
    out_plan->resolved_components = resolved.components;

    if (!request.preferred_install_root.empty()) {
        out_plan->install_roots.push_back(request.preferred_install_root);
    } else {
        out_plan->install_roots.push_back(dsk_root_convention_token(splat_caps.default_root_convention));
    }
    roots = out_plan->install_roots;
    ownership = dsk_select_ownership(request, splat_caps);

    for (i = 0u; i < resolved.components.size(); ++i) {
        const dsk_resolved_component_t &res = resolved.components[i];
        const dsk_manifest_component_t *comp = dsk_find_component(manifest, res.component_id);
        size_t j;
        if (!comp) {
            return dsk_error_make(DSK_DOMAIN_KERNEL,
                                  DSK_CODE_VALIDATION_ERROR,
                                  DSK_SUBCODE_INVALID_FIELD,
                                  DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        for (j = 0u; j < comp->artifacts.size(); ++j) {
            const dsk_artifact_t &art = comp->artifacts[j];
            const dsk_layout_template_t *layout = dsk_find_layout_template(manifest,
                                                                           art.layout_template_id);
            std::string target_path;
            std::string root_key;
            dsk_u32 root_id;

            if (!layout) {
                return dsk_error_make(DSK_DOMAIN_KERNEL,
                                      DSK_CODE_VALIDATION_ERROR,
                                      DSK_SUBCODE_INVALID_FIELD,
                                      DSK_ERROR_FLAG_USER_ACTIONABLE);
            }

            target_path = dsk_join_rel_path(layout->path_prefix, art.source_path);
            root_id = dsk_root_index_for(layout->target_root, roots);
            root_key = (root_id < roots.size()) ? roots[root_id] : roots[0];

            {
                dsk_file_op_build_t op_build;
                op_build.root_key = root_key;
                op_build.component_id = res.component_id;
                op_build.artifact_id = art.artifact_id;
                op_build.op_kind = DSK_PLAN_FILE_OP_COPY;
                op_build.target_path = target_path;
                op_build.op.op_kind = DSK_PLAN_FILE_OP_COPY;
                op_build.op.from_path = art.source_path;
                op_build.op.to_path = target_path;
                op_build.op.ownership = ownership;
                op_build.op.digest64 = art.digest64;
                op_build.op.size = art.size;
                file_ops.push_back(op_build);
            }

            {
                dsk_step_build_t step_build;
                step_build.root_key = root_key;
                step_build.component_id = res.component_id;
                step_build.artifact_id = art.artifact_id;
                step_build.step_kind = DSK_PLAN_STEP_STAGE_ARTIFACT;
                step_build.target_path = target_path;
                step_build.step.step_id = 0u;
                step_build.step.step_kind = DSK_PLAN_STEP_STAGE_ARTIFACT;
                step_build.step.component_id = res.component_id;
                step_build.step.artifact_id = art.artifact_id;
                step_build.step.target_root_id = root_id;
                steps.push_back(step_build);
            }
            {
                dsk_step_build_t step_build;
                step_build.root_key = root_key;
                step_build.component_id = res.component_id;
                step_build.artifact_id = art.artifact_id;
                step_build.step_kind = DSK_PLAN_STEP_VERIFY_HASHES;
                step_build.target_path = target_path;
                step_build.step.step_id = 0u;
                step_build.step.step_kind = DSK_PLAN_STEP_VERIFY_HASHES;
                step_build.step.component_id = res.component_id;
                step_build.step.artifact_id = art.artifact_id;
                step_build.step.target_root_id = root_id;
                steps.push_back(step_build);
            }
        }
    }

    std::sort(file_ops.begin(), file_ops.end(), dsk_file_op_build_less);
    for (i = 0u; i < file_ops.size(); ++i) {
        out_plan->file_ops.push_back(file_ops[i].op);
    }

    std::sort(steps.begin(), steps.end(), dsk_step_build_less);
    for (i = 0u; i < steps.size(); ++i) {
        out_plan->ordered_steps.push_back(steps[i].step);
    }

    {
        dsk_plan_step_t step;
        step.step_id = 0u;
        step.step_kind = DSK_PLAN_STEP_COMMIT_SWAP;
        step.target_root_id = 0u;
        out_plan->ordered_steps.push_back(step);
    }
    {
        dsk_plan_step_t step;
        step.step_id = 0u;
        step.step_kind = DSK_PLAN_STEP_REGISTER_ACTIONS;
        step.target_root_id = 0u;
        out_plan->ordered_steps.push_back(step);
    }
    {
        dsk_plan_step_t step;
        step.step_id = 0u;
        step.step_kind = DSK_PLAN_STEP_WRITE_STATE;
        step.target_root_id = 0u;
        out_plan->ordered_steps.push_back(step);
    }
    {
        dsk_plan_step_t step;
        step.step_id = 0u;
        step.step_kind = DSK_PLAN_STEP_WRITE_AUDIT;
        step.target_root_id = 0u;
        out_plan->ordered_steps.push_back(step);
    }

    for (i = 0u; i < out_plan->ordered_steps.size(); ++i) {
        out_plan->ordered_steps[i].step_id = (dsk_u32)(i + 1u);
    }

    out_plan->plan_digest64 = dsk_plan_payload_digest(out_plan);
    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
