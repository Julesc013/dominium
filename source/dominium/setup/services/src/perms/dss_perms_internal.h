#ifndef DSS_PERMS_INTERNAL_H
#define DSS_PERMS_INTERNAL_H

#include "dss/dss_perms.h"

#ifdef __cplusplus
#include <string>

struct dss_perms_context_t {
    std::string user_install_root;
    std::string user_data_root;
    std::string system_install_root;
    std::string system_data_root;
};

#endif

#endif /* DSS_PERMS_INTERNAL_H */
