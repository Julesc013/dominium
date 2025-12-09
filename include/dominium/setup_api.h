#ifndef DOMINIUM_SETUP_API_H_INCLUDED
#define DOMINIUM_SETUP_API_H_INCLUDED

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Forward declaration from domino/core.h */
typedef struct dom_core_t dom_core;

typedef enum {
    DOM_SETUP_SCOPE_PORTABLE = 0,
    DOM_SETUP_SCOPE_PER_USER,
    DOM_SETUP_SCOPE_ALL_USERS
} dom_setup_scope;

typedef enum {
    DOM_SETUP_ACTION_INSTALL = 0,
    DOM_SETUP_ACTION_REPAIR,
    DOM_SETUP_ACTION_UNINSTALL,
    DOM_SETUP_ACTION_VERIFY
} dom_setup_action;

typedef enum {
    DOM_SETUP_STATUS_OK = 0,
    DOM_SETUP_STATUS_ERROR,
    DOM_SETUP_STATUS_INVALID_ARGUMENT,
    DOM_SETUP_STATUS_IO_ERROR,
    DOM_SETUP_STATUS_PERMISSION_DENIED
} dom_setup_status;

typedef struct {
    uint32_t          struct_size;
    uint32_t          struct_version;
    const char       *product_id;       /* "dominium" */
    const char       *product_version;  /* "1.0.0" */
    const char       *build_id;         /* optional hash/branch */
    dom_setup_scope   scope;
    const char       *target_dir;       /* optional: override directory */
    int               quiet;            /* non-zero => minimal output */
    int               no_launcher;      /* optional flags */
    int               no_desktop_shortcuts;
} dom_setup_desc;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    dom_setup_action action;
    /* path to existing install (for repair/uninstall) */
    const char *existing_install_dir;
} dom_setup_command;

typedef struct {
    uint32_t struct_size;
    uint32_t struct_version;
    /* simple counters: bytes copied, files, etc. */
    uint64_t bytes_total;
    uint64_t bytes_done;
    uint32_t files_total;
    uint32_t files_done;
    const char *current_step;  /* e.g. "Copying game core" */
} dom_setup_progress;

typedef void (*dom_setup_progress_cb)(const dom_setup_progress *prog,
                                      void *user);

/* Lifecycle: attach/detach to Domino core (pkg/inst/filesystem) */
dom_setup_status dom_setup_create(dom_core              *core,
                                  const dom_setup_desc  *desc,
                                  void                 **out_ctx);

void             dom_setup_destroy(void *ctx);

/* Execute a setup action */
dom_setup_status dom_setup_execute(void                      *ctx,
                                   const dom_setup_command   *cmd,
                                   dom_setup_progress_cb      cb,
                                   void                      *cb_user);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_SETUP_API_H_INCLUDED */
