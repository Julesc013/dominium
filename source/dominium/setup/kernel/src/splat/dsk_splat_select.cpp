#include "dsk/dsk_contracts.h"
#include "dsk/dsk_splat.h"

#include <algorithm>

static std::string dsk_to_lower(const std::string &s) {
    std::string out = s;
    size_t i;
    for (i = 0u; i < out.size(); ++i) {
        char c = out[i];
        if (c >= 'A' && c <= 'Z') {
            out[i] = (char)(c - 'A' + 'a');
        }
    }
    return out;
}

static int dsk_contains_token(const std::string &haystack, const char *token) {
    std::string h = dsk_to_lower(haystack);
    std::string t = dsk_to_lower(token ? token : "");
    if (t.empty()) {
        return 0;
    }
    return h.find(t) != std::string::npos;
}

static int dsk_manifest_allows_platform(const dsk_manifest_t &manifest,
                                        const std::string &platform) {
    size_t i;
    if (manifest.platform_targets.empty()) {
        return 1;
    }
    for (i = 0u; i < manifest.platform_targets.size(); ++i) {
        std::string target = dsk_to_lower(manifest.platform_targets[i]);
        if (target == "*" || target == "any") {
            return 1;
        }
        if (dsk_to_lower(platform) == target) {
            return 1;
        }
    }
    return 0;
}

static std::string dsk_pick_splat_for_platform(const std::string &platform) {
    if (dsk_contains_token(platform, "steam")) {
        return "splat_steam";
    }
    if (dsk_contains_token(platform, "win")) {
        return "splat_win32_nt5";
    }
    if (dsk_contains_token(platform, "mac")) {
        return "splat_macos_pkg";
    }
    if (dsk_contains_token(platform, "linux") && dsk_contains_token(platform, "rpm")) {
        return "splat_linux_rpm";
    }
    if (dsk_contains_token(platform, "linux") && dsk_contains_token(platform, "deb")) {
        return "splat_linux_deb";
    }
    if (dsk_contains_token(platform, "linux")) {
        return "splat_linux_deb";
    }
    return "splat_portable";
}

static void dsk_build_candidates(dsk_splat_selection_t *out_selection) {
    std::vector<dsk_splat_info_t> list;
    size_t i;
    dsk_splat_registry_list(list);
    out_selection->candidates.clear();
    for (i = 0u; i < list.size(); ++i) {
        out_selection->candidates.push_back(list[i].id);
    }
}

dsk_status_t dsk_splat_select(const dsk_manifest_t &manifest,
                              const dsk_request_t &request,
                              dsk_splat_selection_t *out_selection) {
    size_t i;
    if (!out_selection) {
        return dsk_error_make(DSK_DOMAIN_KERNEL, DSK_CODE_INVALID_ARGS, DSK_SUBCODE_NONE, 0u);
    }
    out_selection->chosen.clear();
    out_selection->rejections.clear();
    dsk_build_candidates(out_selection);

    if (!request.requested_splat.empty()) {
        if (!dsk_splat_registry_contains(request.requested_splat)) {
            return dsk_error_make(DSK_DOMAIN_KERNEL,
                                  DSK_CODE_VALIDATION_ERROR,
                                  DSK_SUBCODE_SPLAT_NOT_FOUND,
                                  DSK_ERROR_FLAG_USER_ACTIONABLE);
        }
        out_selection->chosen = request.requested_splat;
        for (i = 0u; i < out_selection->candidates.size(); ++i) {
            if (out_selection->candidates[i] == out_selection->chosen) {
                continue;
            }
            dsk_splat_rejection_t rej;
            rej.id = out_selection->candidates[i];
            rej.code = DSK_SPLAT_REJECT_NOT_REQUESTED;
            out_selection->rejections.push_back(rej);
        }
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }

    if (request.platform_triple.empty() ||
        !dsk_manifest_allows_platform(manifest, request.platform_triple)) {
        out_selection->chosen = "splat_portable";
        for (i = 0u; i < out_selection->candidates.size(); ++i) {
            if (out_selection->candidates[i] == out_selection->chosen) {
                continue;
            }
            dsk_splat_rejection_t rej;
            rej.id = out_selection->candidates[i];
            rej.code = DSK_SPLAT_REJECT_MANIFEST_MISMATCH;
            out_selection->rejections.push_back(rej);
        }
        return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
    }

    out_selection->chosen = dsk_pick_splat_for_platform(request.platform_triple);
    if (!dsk_splat_registry_contains(out_selection->chosen)) {
        out_selection->chosen = "splat_portable";
    }
    for (i = 0u; i < out_selection->candidates.size(); ++i) {
        if (out_selection->candidates[i] == out_selection->chosen) {
            continue;
        }
        dsk_splat_rejection_t rej;
        rej.id = out_selection->candidates[i];
        rej.code = DSK_SPLAT_REJECT_PLATFORM_MISMATCH;
        out_selection->rejections.push_back(rej);
    }

    return dsk_error_make(DSK_DOMAIN_NONE, DSK_CODE_OK, DSK_SUBCODE_NONE, 0u);
}
