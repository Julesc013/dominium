#include "domino/sys.h"
#include <stdio.h>

int main(void)
{
    domino_sys_context* ctx = NULL;
    domino_sys_desc desc;
    domino_sys_paths paths;
    domino_sys_platform_info info;
    unsigned long t0, t1;
    desc.profile_hint = DOMINO_SYS_PROFILE_AUTO;
    if (domino_sys_init(&desc, &ctx) != 0 || !ctx) {
        printf("sys init failed\n");
        return 1;
    }
    domino_sys_get_platform_info(ctx, &info);
    if (domino_sys_get_paths(ctx, &paths) != 0) {
        domino_sys_log(ctx, DOMINO_LOG_ERROR, "test_platform_probe", "paths unavailable");
        domino_sys_shutdown(ctx);
        return 1;
    }
    t0 = domino_sys_time_millis(ctx);
    domino_sys_sleep_millis(ctx, 10);
    t1 = domino_sys_time_millis(ctx);
    if (t1 < t0) {
        domino_sys_log(ctx, DOMINO_LOG_WARN, "test_platform_probe", "time did not advance");
    }
    domino_sys_log(ctx, DOMINO_LOG_INFO, "test_platform_probe", paths.install_root);
    domino_sys_shutdown(ctx);
    return 0;
}
