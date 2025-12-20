/*
FILE: source/dominium/setup/core/include/dsu/dsu_report.h
MODULE: Dominium Setup
PURPOSE: Deterministic forensics/reporting over installed state + audit logs (Plan S-5).
*/
#ifndef DSU_REPORT_H_INCLUDED
#define DSU_REPORT_H_INCLUDED

#include "dsu_ctx.h"
#include "dsu_log.h"
#include "dsu_state.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dsu_report_format_t {
    DSU_REPORT_FORMAT_JSON = 0,
    DSU_REPORT_FORMAT_TEXT = 1
} dsu_report_format_t;

typedef struct dsu_report_verify_summary_t {
    dsu_u32 struct_size;
    dsu_u32 struct_version;

    dsu_u32 checked;
    dsu_u32 ok;
    dsu_u32 missing;
    dsu_u32 modified;
    dsu_u32 extra;
    dsu_u32 errors;
} dsu_report_verify_summary_t;

DSU_API void dsu_report_verify_summary_init(dsu_report_verify_summary_t *s);

/* Frees memory returned by the report generators. */
DSU_API void dsu_report_free(dsu_ctx_t *ctx, void *p);

DSU_API dsu_status_t dsu_report_list_installed(dsu_ctx_t *ctx,
                                              const dsu_state_t *state,
                                              dsu_report_format_t format,
                                              char **out_report);

DSU_API dsu_status_t dsu_report_touched_paths(dsu_ctx_t *ctx,
                                             const dsu_state_t *state,
                                             dsu_report_format_t format,
                                             char **out_report);

DSU_API dsu_status_t dsu_report_uninstall_preview(dsu_ctx_t *ctx,
                                                 const dsu_state_t *state,
                                                 const char *const *components,
                                                 dsu_u32 component_count,
                                                 dsu_report_format_t format,
                                                 char **out_report);

DSU_API dsu_status_t dsu_report_verify(dsu_ctx_t *ctx,
                                      const dsu_state_t *state,
                                      dsu_report_format_t format,
                                      char **out_report,
                                      dsu_report_verify_summary_t *out_summary);

DSU_API dsu_status_t dsu_report_corruption_assessment(dsu_ctx_t *ctx,
                                                     const dsu_state_t *state,
                                                     const dsu_log_t *audit_log,
                                                     dsu_report_format_t format,
                                                     char **out_report);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_REPORT_H_INCLUDED */

