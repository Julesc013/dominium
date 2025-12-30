#include "dss_txn_internal.h"

#include <cstdlib>
#include <cstring>

dss_bool dss_txn_failpoint_after_commit_step(dss_u32 step_id) {
    const char *env = std::getenv("DSK_FAILPOINT");
    const char *prefix = "mid_commit_step_";
    size_t i = 0u;
    if (!env || !env[0]) {
        return DSS_FALSE;
    }
    while (prefix[i]) {
        if (env[i] != prefix[i]) {
            return DSS_FALSE;
        }
        ++i;
    }
    {
        const char *num = env + i;
        if (!num[0]) {
            return DSS_FALSE;
        }
        dss_u32 val = 0u;
        while (*num) {
            char c = *num++;
            if (c < '0' || c > '9') {
                return DSS_FALSE;
            }
            val = (val * 10u) + (dss_u32)(c - '0');
        }
        return (val == step_id) ? DSS_TRUE : DSS_FALSE;
    }
}
