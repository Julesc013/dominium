#ifndef DSS_TXN_INTERNAL_H
#define DSS_TXN_INTERNAL_H

#include "dss/dss_txn.h"

#ifdef __cplusplus
extern "C" {
#endif

dss_bool dss_txn_failpoint_after_commit_step(dss_u32 step_id);

#ifdef __cplusplus
}
#endif

#endif /* DSS_TXN_INTERNAL_H */
