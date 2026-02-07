/*
CIV1 stub refusal tests.
*/
#include "dominium/rules/city/city_services_stub.h"
#include "dominium/rules/logistics/routing_stub.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int test_city_services_refusal(void)
{
    city_service_state state;
    civ1_refusal_code refusal = CIV1_REFUSAL_NONE;

    state.water_ok = 1u;
    state.power_ok = 1u;
    state.waste_ok = 1u;

    EXPECT(city_services_available_ex(&state, &refusal) == 0,
           "city services should refuse");
    EXPECT(refusal == CIV1_REFUSAL_NOT_IMPLEMENTED, "city services refusal mismatch");
    EXPECT(city_services_available(&state) == 0, "city services should be unavailable");
    return 0;
}

static int test_logistics_route_refusal(void)
{
    logistics_route_params params;
    dom_act_time_t duration = 99u;
    u32 cost = 77u;
    civ1_refusal_code refusal = CIV1_REFUSAL_NONE;

    params.distance_units = 100u;
    params.weight_class = 1u;
    params.base_speed = 2u;
    params.base_cost = 3u;

    EXPECT(logistics_route_estimate_ex(&params, &duration, &cost, &refusal) != 0,
           "routing should refuse");
    EXPECT(refusal == CIV1_REFUSAL_NOT_IMPLEMENTED, "routing refusal mismatch");
    EXPECT(duration == 0u, "routing duration should be zeroed");
    EXPECT(cost == 0u, "routing cost should be zeroed");
    return 0;
}

int main(void)
{
    if (test_city_services_refusal() != 0) return 1;
    if (test_logistics_route_refusal() != 0) return 1;
    return 0;
}
