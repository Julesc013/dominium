#include <stdio.h>

#include "job/d_job.h"

int d_job_validate(const d_world *w) {
    u32 i;
    u32 count;
    (void)w;

    count = d_content_job_template_count();
    for (i = 0u; i < count; ++i) {
        const d_proto_job_template *t = d_content_get_job_template_by_index(i);
        if (!t) {
            continue;
        }
        if (t->purpose < (u16)D_JOB_PURPOSE_OPERATE_PROCESS || t->purpose > (u16)D_JOB_PURPOSE_BUILD_STRUCTURE) {
            fprintf(stderr, "job validate: invalid purpose in template %u\n", (unsigned)t->id);
            return -1;
        }
        if (t->process_id != 0u && !d_content_get_process(t->process_id)) {
            fprintf(stderr, "job validate: template %u references missing process %u\n",
                    (unsigned)t->id, (unsigned)t->process_id);
            return -1;
        }
        if (t->structure_id != 0u && !d_content_get_structure(t->structure_id)) {
            fprintf(stderr, "job validate: template %u references missing structure %u\n",
                    (unsigned)t->id, (unsigned)t->structure_id);
            return -1;
        }
        if (t->spline_profile_id != 0u && !d_content_get_spline_profile(t->spline_profile_id)) {
            fprintf(stderr, "job validate: template %u references missing spline profile %u\n",
                    (unsigned)t->id, (unsigned)t->spline_profile_id);
            return -1;
        }
    }
    return 0;
}
