#ifndef DSS_TXN_H
#define DSS_TXN_H

#include "dss_archive.h"
#include "dss_error.h"
#include "dss_fs.h"
#include "dsk/dsk_plan.h"
#include "dsk/dsk_tlv.h"

#ifdef __cplusplus
#include <string>
#include <vector>

/* Transaction journal tags (0x7000 range). */
#define DSS_TLV_TAG_TXN_PLAN_DIGEST64 0x7001u
#define DSS_TLV_TAG_TXN_STAGE_ROOT 0x7002u
#define DSS_TLV_TAG_TXN_STEPS 0x7003u

#define DSS_TLV_TAG_TXN_STEP_ENTRY 0x7010u
#define DSS_TLV_TAG_TXN_STEP_ID 0x7011u
#define DSS_TLV_TAG_TXN_STEP_KIND 0x7012u
#define DSS_TLV_TAG_TXN_STEP_SRC 0x7013u
#define DSS_TLV_TAG_TXN_STEP_DST 0x7014u
#define DSS_TLV_TAG_TXN_STEP_ROLLBACK_KIND 0x7015u
#define DSS_TLV_TAG_TXN_STEP_ROLLBACK_SRC 0x7016u
#define DSS_TLV_TAG_TXN_STEP_ROLLBACK_DST 0x7017u

/* Transaction step kinds. */
#define DSS_TXN_STEP_MKDIR 1u
#define DSS_TXN_STEP_COPY_FILE 2u
#define DSS_TXN_STEP_EXTRACT_ARCHIVE 3u
#define DSS_TXN_STEP_ATOMIC_RENAME 4u
#define DSS_TXN_STEP_DIR_SWAP 5u
#define DSS_TXN_STEP_DELETE_FILE 6u
#define DSS_TXN_STEP_REMOVE_DIR 7u

struct dss_txn_step_t {
    dss_u32 step_id;
    dss_u16 op_kind;
    std::string src_path;
    std::string dst_path;
    dss_u16 rollback_kind;
    std::string rollback_src;
    std::string rollback_dst;
};

struct dss_txn_journal_t {
    dss_u64 plan_digest64;
    std::string stage_root;
    std::vector<dss_txn_step_t> steps;
};

DSS_API void dss_txn_journal_clear(dss_txn_journal_t *journal);
DSS_API dss_error_t dss_txn_journal_parse(const dss_u8 *data,
                                          dss_u32 size,
                                          dss_txn_journal_t *out_journal);
DSS_API dss_error_t dss_txn_journal_write(const dss_txn_journal_t *journal,
                                          dsk_tlv_buffer_t *out_buf);

DSS_API dss_error_t dss_txn_build(const dsk_plan_t *plan,
                                  const std::vector<std::string> &install_roots,
                                  const std::string &stage_root,
                                  dss_bool supports_atomic_swap,
                                  dss_txn_journal_t *out_journal);

DSS_API dss_error_t dss_txn_execute(const dss_fs_api_t *fs,
                                    const dss_archive_api_t *archive,
                                    const dss_txn_journal_t *journal,
                                    dss_u32 start_step,
                                    dss_u32 *out_last_step);

DSS_API dss_error_t dss_txn_execute_step(const dss_fs_api_t *fs,
                                         const dss_archive_api_t *archive,
                                         const dss_txn_step_t *step);

DSS_API dss_error_t dss_txn_rollback(const dss_fs_api_t *fs,
                                     const dss_txn_journal_t *journal,
                                     dss_u32 last_completed_step);

#endif /* __cplusplus */

#endif /* DSS_TXN_H */
