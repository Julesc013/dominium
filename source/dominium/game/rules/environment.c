#include "dominium/environment.h"

dom_status dom_environment_create(const dom_environment_desc* desc,
                                  dom_environment_system** out_env)
{
    (void)desc;
    (void)out_env;
    return DOM_STATUS_UNSUPPORTED;
}

void dom_environment_destroy(dom_environment_system* env)
{
    (void)env;
}

dom_status dom_environment_tick(dom_environment_system* env,
                                uint32_t dt_millis)
{
    (void)env;
    (void)dt_millis;
    return DOM_STATUS_UNSUPPORTED;
}

dom_status dom_environment_sample_point(dom_environment_system* env,
                                        dom_surface_id surface,
                                        const WPosExact* pos,
                                        dom_environment_sample* out_sample,
                                        size_t out_sample_size)
{
    (void)env;
    (void)surface;
    (void)pos;
    if (out_sample && out_sample_size >= sizeof(dom_environment_sample)) {
        out_sample->struct_size      = (uint32_t)sizeof(dom_environment_sample);
        out_sample->struct_version   = 0;
        out_sample->temperature_mK   = 0;
        out_sample->pressure_mPa     = 0;
        out_sample->humidity_permille = 0;
        out_sample->wind_mm_s        = 0;
        out_sample->radiation_uSvph  = 0;
    }
    return DOM_STATUS_UNSUPPORTED;
}
