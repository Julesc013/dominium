#ifndef DOMINO_CORE_H_INCLUDED
#define DOMINO_CORE_H_INCLUDED

#include <stddef.h>
#include <stddef.h>
#include <stdint.h>
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_status {
    DOM_STATUS_OK = 0,
    DOM_STATUS_ERROR = -1,
    DOM_STATUS_INVALID_ARGUMENT = -2,
    DOM_STATUS_UNSUPPORTED = -3,
    DOM_STATUS_NOT_FOUND = -4
} dom_status;

typedef struct dom_core_t dom_core;

typedef struct dom_core_desc {
    uint32_t api_version;
} dom_core_desc;

typedef uint32_t dom_cmd_id;
typedef uint32_t dom_query_id;

typedef struct dom_cmd {
    dom_cmd_id  id;
    const void* data;
    size_t      size;
} dom_cmd;

typedef struct dom_query {
    dom_query_id id;
    const void*  in;
    size_t       in_size;
    void*        out;
    size_t       out_size;
} dom_query;

#define DOM_CMD_NOP 0u

#define DOM_QUERY_CORE_INFO 0u

typedef struct dom_core_info {
    uint32_t struct_size;
    uint32_t struct_version;
    uint32_t api_version;
    uint32_t package_count;
    uint32_t instance_count;
    uint64_t ticks;
} dom_core_info;

dom_core* dom_core_create(const dom_core_desc* desc);
void      dom_core_destroy(dom_core* core);
bool      dom_core_execute(dom_core* core, const dom_cmd* cmd);
bool      dom_core_query(dom_core* core, dom_query* q);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_CORE_H_INCLUDED */
