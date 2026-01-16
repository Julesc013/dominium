/*
FILE: include/dominium/provider_os_integration.h
MODULE: Dominium
PURPOSE: OS integration provider ABI (shortcuts, associations, open folder).
*/
#ifndef DOMINIUM_PROVIDER_OS_INTEGRATION_H
#define DOMINIUM_PROVIDER_OS_INTEGRATION_H

#include "domino/abi.h"
#include "domino/core/types.h"
#include "dom_contracts/core_err.h"
#include "dom_contracts/provider_base.h"

#ifdef __cplusplus
extern "C" {
#endif

#define PROVIDER_IID_OS_INTEGRATION_V1 ((dom_iid)0x504F5331u) /* 'POS1' */

typedef struct provider_os_shortcut_desc_v1 {
    u32 struct_size;
    u32 struct_version;
    const char* app_id;
    const char* target_path;
    const char* args;
    const char* icon_path;
} provider_os_shortcut_desc_v1;

typedef struct provider_os_file_assoc_desc_v1 {
    u32 struct_size;
    u32 struct_version;
    const char* extension;
    const char* app_id;
    const char* description;
} provider_os_file_assoc_desc_v1;

typedef struct provider_os_integration_v1 {
    DOM_ABI_HEADER;
    dom_query_interface_fn query_interface;
    const char* (*provider_id)(void);

    dom_abi_result (*create_shortcut)(const provider_os_shortcut_desc_v1* desc,
                                      err_t* out_err);
    dom_abi_result (*remove_shortcut)(const char* app_id,
                                      err_t* out_err);
    dom_abi_result (*register_file_assoc)(const provider_os_file_assoc_desc_v1* desc,
                                          err_t* out_err);
    dom_abi_result (*unregister_file_assoc)(const char* extension,
                                            const char* app_id,
                                            err_t* out_err);
    dom_abi_result (*open_folder)(const char* path_rel,
                                  u32 is_instance_relative,
                                  err_t* out_err);
} provider_os_integration_v1;

const provider_os_integration_v1* provider_os_integration_null_v1(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PROVIDER_OS_INTEGRATION_H */
