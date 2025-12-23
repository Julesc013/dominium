/*
FILE: source/domino/ui_codegen/ui_codegen.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_codegen
RESPONSIBILITY: Deterministic codegen for UI action bindings + registry handling.
ALLOWED DEPENDENCIES: C++98 standard headers, UI IR headers.
FORBIDDEN DEPENDENCIES: UI backends, launcher.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Return codes with diagnostics; no printing.
DETERMINISM: Stable action ordering + deterministic file output.
*/
#ifndef DOMINO_UI_CODEGEN_H_INCLUDED
#define DOMINO_UI_CODEGEN_H_INCLUDED

#include <map>
#include <string>

#include "ui_ir_diag.h"
#include "ui_ir_types.h"

struct domui_action_registry {
    domui_u32 next_id;
    std::map<std::string, domui_u32> key_to_id;

    domui_action_registry();
};

struct domui_codegen_params {
    const char* input_tlv_path;
    const char* registry_path;
    const char* out_gen_dir;
    const char* out_user_dir;
    const char* doc_name_override;

    domui_codegen_params();
};

bool domui_action_registry_load(const char* path, domui_action_registry* out, domui_diag* diag);
bool domui_action_registry_save(const char* path, const domui_action_registry& reg, domui_diag* diag);

bool domui_codegen_run(const domui_codegen_params* params, domui_diag* diag);

#endif /* DOMINO_UI_CODEGEN_H_INCLUDED */
