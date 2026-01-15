/*
FILE: source/domino/ui_ir/ui_caps.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / ui_ir caps
RESPONSIBILITY: Backend/tier capability declarations for UI IR validation.
ALLOWED DEPENDENCIES: C++98 standard headers only.
FORBIDDEN DEPENDENCIES: UI backends, launcher runtime.
THREADING MODEL: Caller-managed; no internal synchronization.
ERROR MODEL: Return null/false on lookup failures; no printing.
DETERMINISM: Ordered registration; deterministic lookups.
*/
#ifndef DOMINO_UI_IR_CAPS_H_INCLUDED
#define DOMINO_UI_IR_CAPS_H_INCLUDED

#include <vector>

#include "ui_ir_types.h"
#include "ui_ir_string.h"

typedef domui_string domui_backend_id;
typedef domui_string domui_tier_id;
typedef domui_string domui_cap_feature;

typedef struct domui_feature_entry {
    domui_cap_feature key;
    int emulated;
} domui_feature_entry;

typedef struct domui_cap_limit {
    domui_string key;
    int value;
} domui_cap_limit;

typedef struct domui_widget_cap {
    domui_widget_type type;
    domui_string_list props;
    domui_string_list events;
} domui_widget_cap;

typedef struct domui_tier_caps {
    domui_tier_id tier_id;
    std::vector<domui_widget_cap> widgets;
    std::vector<domui_feature_entry> features;
    std::vector<domui_cap_limit> limits;
} domui_tier_caps;

typedef struct domui_backend_caps {
    domui_backend_id backend_id;
    domui_string_list tiers;
    std::vector<domui_tier_caps> tier_caps;
} domui_backend_caps;

typedef struct domui_target_set {
    domui_string_list backends;
    domui_string_list tiers;
} domui_target_set;

void domui_register_backend_caps(const domui_backend_caps& caps);
const domui_backend_caps* domui_get_backend_caps(const domui_backend_id& backend_id);
const domui_backend_caps* domui_get_backend_caps_cstr(const char* backend_id);
const domui_tier_caps* domui_get_tier_caps(const domui_backend_caps* backend, const domui_tier_id& tier_id);
const domui_tier_caps* domui_find_tier_caps(const domui_tier_id& tier_id, const domui_backend_caps** out_backend);
int domui_backend_tier_index(const domui_backend_caps* backend, const domui_tier_id& tier_id);
const domui_tier_caps* domui_get_highest_tier_caps(const domui_backend_caps* backend);

const domui_widget_cap* domui_find_widget_cap(const domui_tier_caps* tier, domui_widget_type type);
bool domui_tier_supports_widget(const domui_tier_caps* tier, domui_widget_type type);
bool domui_tier_supports_prop(const domui_tier_caps* tier, domui_widget_type type, const domui_string& prop_key);
bool domui_tier_supports_event(const domui_tier_caps* tier, domui_widget_type type, const domui_string& event_name);

const domui_feature_entry* domui_tier_find_feature(const domui_tier_caps* tier, const domui_cap_feature& feature_key);
bool domui_tier_has_feature(const domui_tier_caps* tier, const domui_cap_feature& feature_key);
bool domui_tier_limit_value(const domui_tier_caps* tier, const domui_string& limit_key, int* out_value);

void domui_register_default_backend_caps(void);

#endif /* DOMINO_UI_IR_CAPS_H_INCLUDED */
