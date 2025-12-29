#include "dss/dss_services.h"

#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

#if defined(_WIN32)
#include <direct.h>
#include <errno.h>
#else
#include <errno.h>
#include <sys/stat.h>
#endif

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static int make_dir_if_needed(const char *path) {
    if (!path || !path[0]) {
        return 0;
    }
#if defined(_WIN32)
    if (_mkdir(path) == 0) {
        return 1;
    }
#else
    if (mkdir(path, 0755) == 0) {
        return 1;
    }
#endif
    return (errno == EEXIST) ? 1 : 0;
}

static int ends_with(const std::string &value, const std::string &suffix) {
    if (suffix.size() > value.size()) {
        return 0;
    }
    return value.compare(value.size() - suffix.size(), suffix.size(), suffix) == 0;
}

static int test_rejects_escape(void) {
    const char *root = "setup2_fs_sandbox";
    dss_services_t services;
    dss_services_config_t cfg;
    std::vector<dss_u8> bytes;
    dss_error_t st;

    if (!make_dir_if_needed(root)) {
        return fail("failed to create sandbox root");
    }

    dss_services_config_init(&cfg);
    cfg.sandbox_root = root;
    dss_services_init_fake(&cfg, &services);

    st = services.fs.read_file_bytes(services.fs.ctx, "../escape.txt", &bytes);
    dss_services_shutdown(&services);

    if (st.code != DSS_CODE_SANDBOX_VIOLATION) {
        return fail("expected sandbox violation");
    }
    return 0;
}

static int test_atomic_write(void) {
    const char *root = "setup2_fs_sandbox";
    dss_services_t services;
    dss_services_config_t cfg;
    std::vector<dss_u8> out;
    const dss_u8 first[] = { 'a', 'b', 'c' };
    const dss_u8 second[] = { 'x', 'y', 'z', 'q' };
    dss_error_t st;

    if (!make_dir_if_needed(root)) {
        return fail("failed to create sandbox root");
    }

    dss_services_config_init(&cfg);
    cfg.sandbox_root = root;
    dss_services_init_fake(&cfg, &services);

    st = services.fs.write_file_bytes_atomic(services.fs.ctx, "state.bin", first, 3u);
    if (!dss_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail("atomic write failed");
    }
    st = services.fs.read_file_bytes(services.fs.ctx, "state.bin", &out);
    if (!dss_error_is_ok(st) || out.size() != 3u || std::memcmp(&out[0], first, 3u) != 0) {
        dss_services_shutdown(&services);
        return fail("readback mismatch");
    }

    st = services.fs.write_file_bytes_atomic(services.fs.ctx, "state.bin", second, 4u);
    if (!dss_error_is_ok(st)) {
        dss_services_shutdown(&services);
        return fail("second atomic write failed");
    }
    st = services.fs.read_file_bytes(services.fs.ctx, "state.bin", &out);
    if (!dss_error_is_ok(st) || out.size() != 4u || std::memcmp(&out[0], second, 4u) != 0) {
        dss_services_shutdown(&services);
        return fail("second readback mismatch");
    }

    dss_services_shutdown(&services);
    return 0;
}

static int test_canonicalize_stable(void) {
    const char *root = "setup2_fs_sandbox";
    dss_services_t services;
    dss_services_config_t cfg;
    std::string out;
    dss_error_t st;

    if (!make_dir_if_needed(root)) {
        return fail("failed to create sandbox root");
    }

    dss_services_config_init(&cfg);
    cfg.sandbox_root = root;
    dss_services_init_fake(&cfg, &services);

    st = services.fs.canonicalize_path(services.fs.ctx, "dir//sub/./file.txt", &out);
    dss_services_shutdown(&services);
    if (!dss_error_is_ok(st)) {
        return fail("canonicalize failed");
    }
    if (!ends_with(out, "dir/sub/file.txt")) {
        return fail("canonicalize mismatch");
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: test_services_fs_sandbox <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "services_fs_rejects_escape") == 0) {
        return test_rejects_escape();
    }
    if (std::strcmp(argv[1], "services_fs_atomic_write") == 0) {
        return test_atomic_write();
    }
    if (std::strcmp(argv[1], "services_fs_canonicalize") == 0) {
        return test_canonicalize_stable();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
