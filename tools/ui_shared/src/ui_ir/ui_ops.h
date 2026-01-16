/*
FILE: source/domino/ui_ir/ui_ops.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir ops
RESPONSIBILITY: Deterministic ops.json parsing and scripted edits for UI IR.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher runtime.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Return codes with diagnostics; no printing.
DETERMINISM: Ops applied in file order; strict parsing and stable diagnostics.
*/
#ifndef DOMINO_UI_IR_OPS_H_INCLUDED
#define DOMINO_UI_IR_OPS_H_INCLUDED

#include <map>
#include <string>
#include <stddef.h>

#include "ui_ir_doc.h"
#include "ui_ir_diag.h"

typedef bool (*domui_ops_save_fn)(void* user_ctx, const domui_doc* doc, domui_diag* diag);

typedef struct domui_ops_apply_params {
    domui_ops_save_fn save_fn;
    void* save_user;

    domui_ops_apply_params()
        : save_fn(0),
          save_user(0)
    {
    }
} domui_ops_apply_params;

typedef struct domui_ops_result {
    std::map<std::string, domui_u32> created_ids;
    bool validation_failed;
    bool save_failed;
    bool final_validate;

    domui_ops_result()
        : created_ids(),
          validation_failed(false),
          save_failed(false),
          final_validate(true)
    {
    }
} domui_ops_result;

bool domui_ops_apply_json(domui_doc* doc,
                          const char* json_text,
                          size_t json_len,
                          const domui_ops_apply_params* params,
                          domui_ops_result* out_result,
                          domui_diag* out_diag);

#endif /* DOMINO_UI_IR_OPS_H_INCLUDED */
