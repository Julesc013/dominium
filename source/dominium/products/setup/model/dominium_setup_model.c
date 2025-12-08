#include "dominium_setup_model.h"
#include "dominium/product_manifest.h"
#include "domino/sys.h"

#include <string.h>

static void dom_join(char* dst, size_t cap,
                     const char* a, const char* b)
{
    size_t i = 0;
    size_t j = 0;
    if (!dst || cap == 0) return;
    if (!a) a = "";
    if (!b) b = "";
    while (a[i] != '\0' && i + 1 < cap) {
        dst[i] = a[i];
        ++i;
    }
    if (i > 0 && i + 1 < cap) {
        char c = dst[i - 1];
        if (c != '/' && c != '\\') {
            dst[i++] = '/';
        }
    }
    while (b[j] != '\0' && i + 1 < cap) {
        dst[i++] = b[j++];
    }
    dst[i] = '\0';
}

int dominium_setup_list_installed(dominium_installed_product* out,
                                  unsigned int max_count,
                                  unsigned int* out_count)
{
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    domino_sys_paths paths;
    domino_sys_dir_iter* product_it;
    char product_name[260];
    int is_dir = 0;
    unsigned int count = 0;

    if (out_count) *out_count = 0;

    sdesc.profile_hint = DOMINO_SYS_PROFILE_FULL;
    if (domino_sys_init(&sdesc, &sys) != 0) {
        return -1;
    }
    domino_sys_get_paths(sys, &paths);

    product_it = domino_sys_dir_open(sys, paths.program_root);
    if (!product_it) {
        domino_sys_shutdown(sys);
        return 0;
    }

    while (domino_sys_dir_next(sys, product_it, product_name, sizeof(product_name), &is_dir)) {
        domino_sys_dir_iter* ver_it;
        char product_path[260];
        char version_name[260];
        if (!is_dir || product_name[0] == '.') continue;
        dom_join(product_path, sizeof(product_path), paths.program_root, product_name);
        ver_it = domino_sys_dir_open(sys, product_path);
        if (!ver_it) continue;
        while (domino_sys_dir_next(sys, ver_it, version_name, sizeof(version_name), &is_dir)) {
            char manifest_path[260];
            dominium_product_desc desc;
            if (!is_dir || version_name[0] == '.') continue;
            dom_join(manifest_path, sizeof(manifest_path), product_path, version_name);
            dom_join(manifest_path, sizeof(manifest_path), manifest_path, "product.toml");
            if (dominium_product_load(manifest_path, &desc) == 0) {
                if (out && count < max_count) {
                    strncpy(out[count].id, desc.id, sizeof(out[count].id) - 1);
                    out[count].id[sizeof(out[count].id) - 1] = '\0';
                    out[count].version = desc.version;
                    out[count].content_api = desc.content_api;
                }
                ++count;
            }
        }
        domino_sys_dir_close(sys, ver_it);
    }
    domino_sys_dir_close(sys, product_it);
    domino_sys_shutdown(sys);
    if (out_count) *out_count = count;
    return 0;
}
