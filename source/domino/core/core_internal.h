#ifndef DOMINO_CORE_INTERNAL_H
#define DOMINO_CORE_INTERNAL_H

#include <stddef.h>
#include <stdint.h>
#include "domino/core.h"
#include "domino/pkg.h"
#include "domino/inst.h"
#include "domino/event.h"
#include "domino/view.h"
#include "domino/model_table.h"
#include "domino/model_tree.h"
#include "domino/sim.h"
#include "domino/canvas.h"

#define DOM_MAX_PACKAGES 32
#define DOM_MAX_INSTANCES 16
#define DOM_MAX_EVENT_SUBS 32
#define DOM_MAX_VIEWS 16
#define DOM_MAX_TABLE_MODELS 8
#define DOM_MAX_TREE_MODELS 8

typedef struct dom_event_subscription {
    dom_event_kind   kind;
    dom_event_handler handler;
    void*            user;
} dom_event_subscription;

typedef struct dom_instance_record {
    dom_instance_info info;
    dom_sim_state     sim;
} dom_instance_record;

struct dom_core_t {
    uint32_t api_version;
    uint64_t tick_counter;

    dom_package_info packages[DOM_MAX_PACKAGES];
    uint32_t         package_count;
    dom_package_id   next_package_id;

    dom_instance_record instances[DOM_MAX_INSTANCES];
    uint32_t            instance_count;
    dom_instance_id     next_instance_id;

    const char* table_models[DOM_MAX_TABLE_MODELS];
    uint32_t    table_model_count;
    const char* tree_models[DOM_MAX_TREE_MODELS];
    uint32_t    tree_model_count;

    dom_view_desc views[DOM_MAX_VIEWS];
    uint32_t      view_count;

    dom_event_subscription subs[DOM_MAX_EVENT_SUBS];
    uint32_t               sub_count;
};

#endif /* DOMINO_CORE_INTERNAL_H */
