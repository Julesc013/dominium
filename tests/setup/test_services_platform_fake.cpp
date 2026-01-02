#include "dss/dss_services.h"

#include <cstdio>
#include <cstring>
#include <string>

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static int test_platform_fake_triple(void) {
    dss_services_t services;
    dss_services_config_t cfg;
    std::string triple;
    dss_error_t st;

    dss_services_config_init(&cfg);
    cfg.platform_triple = "linux-test";
    dss_services_init_fake(&cfg, &services);

    st = services.platform.get_platform_triple(services.platform.ctx, &triple);
    dss_services_shutdown(&services);
    if (!dss_error_is_ok(st)) {
        return fail("get_platform_triple failed");
    }
    if (triple != "linux-test") {
        return fail("unexpected triple");
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        std::fprintf(stderr, "usage: test_services_platform_fake <test>\n");
        return 1;
    }
    if (std::strcmp(argv[1], "services_platform_fake") == 0) {
        return test_platform_fake_triple();
    }
    std::fprintf(stderr, "unknown test: %s\n", argv[1]);
    return 1;
}
