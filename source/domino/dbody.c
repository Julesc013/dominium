#include "domino/dbody.h"
#include "domino/dorbit.h"

#include <string.h>

#define DBODY_MAX 64
#define DSITE_MAX 128

static Body g_bodies[DBODY_MAX];
static BodyId g_body_count = 0;

static SpaceSite g_sites[DSITE_MAX];
static SpaceSiteId g_site_count = 0;

BodyId dbody_register(const Body *def)
{
    Body copy;
    if (!def) return 0;
    if (g_body_count >= (BodyId)DBODY_MAX) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = g_body_count + 1;
    }
    g_bodies[g_body_count] = copy;
    g_body_count++;
    return copy.id;
}

const Body *dbody_get(BodyId id)
{
    if (id == 0) return 0;
    if (id > g_body_count) return 0;
    return &g_bodies[id - 1];
}

Q48_16 dbody_get_mu(BodyId id)
{
    const Body *b = dbody_get(id);
    if (!b) return 0;
    return b->mu;
}

bool dbody_get_space_pos(BodyId id, U64 t, SpacePos *out)
{
    const Body *b = dbody_get(id);
    if (!b || !out) return false;
    if (b->orbit.central == 0 || b->orbit.central == b->id) {
        out->x = 0;
        out->y = 0;
        out->z = 0;
        return true;
    }
    dorbit_to_space_pos(&b->orbit, t, out);
    return true;
}

void dbody_sun_direction(BodyId body, U64 t, Q16_16 out_dir3[3])
{
    /* Approximate: vector from body to its central body normalised by max component */
    const Body *b = dbody_get(body);
    SpacePos self_pos;
    SpacePos central_pos;
    Q48_16 dx = 0;
    Q48_16 dy = 0;
    Q48_16 dz = 0;
    Q48_16 ax = 0;
    Q48_16 ay = 0;
    Q48_16 az = 0;
    Q48_16 max_abs = 0;
    if (!out_dir3) return;
    out_dir3[0] = 0;
    out_dir3[1] = 0;
    out_dir3[2] = 0;
    if (!b) return;
    if (!dbody_get_space_pos(body, t, &self_pos)) return;
    if (!dbody_get_space_pos(b->orbit.central, t, &central_pos)) {
        /* If no central, assume sun along +X */
        out_dir3[0] = (Q16_16)(1 << 16);
        return;
    }
    dx = central_pos.x - self_pos.x;
    dy = central_pos.y - self_pos.y;
    dz = central_pos.z - self_pos.z;
    ax = (dx < 0) ? -dx : dx;
    ay = (dy < 0) ? -dy : dy;
    az = (dz < 0) ? -dz : dz;
    max_abs = ax;
    if (ay > max_abs) max_abs = ay;
    if (az > max_abs) max_abs = az;
    if (max_abs == 0) {
        out_dir3[0] = (Q16_16)(1 << 16);
        return;
    }
    out_dir3[0] = (Q16_16)(((I64)dx << 16) / max_abs);
    out_dir3[1] = (Q16_16)(((I64)dy << 16) / max_abs);
    out_dir3[2] = (Q16_16)(((I64)dz << 16) / max_abs);
}

Q16_16 dbody_solar_flux_at_body(BodyId body)
{
    /* Stub: TODO derive from star luminosity and distance */
    (void)body;
    return (Q16_16)(1 << 16);
}

SpaceSiteId dspace_site_register(const SpaceSite *def)
{
    SpaceSite copy;
    if (!def) return 0;
    if (g_site_count >= (SpaceSiteId)DSITE_MAX) return 0;
    copy = *def;
    if (copy.id == 0) {
        copy.id = g_site_count + 1;
    }
    g_sites[g_site_count] = copy;
    g_site_count++;
    return copy.id;
}

const SpaceSite *dspace_site_get(SpaceSiteId id)
{
    if (id == 0) return 0;
    if (id > g_site_count) return 0;
    return &g_sites[id - 1];
}

static void dspace_add_pos(const SpacePos *a, const SpacePos *b, SpacePos *out)
{
    if (!a || !b || !out) return;
    out->x = a->x + b->x;
    out->y = a->y + b->y;
    out->z = a->z + b->z;
}

bool dspace_site_pos(SpaceSiteId id, U64 t, SpacePos *out)
{
    const SpaceSite *s = dspace_site_get(id);
    SpacePos base;
    if (!s || !out) return false;
    base.x = 0;
    base.y = 0;
    base.z = 0;
    if (s->attached_body != 0) {
        dbody_get_space_pos(s->attached_body, t, &base);
    }
    if (s->orbit.central != 0) {
        dorbit_to_space_pos(&s->orbit, t, out);
        dspace_add_pos(out, &base, out);
        return true;
    }
    dspace_add_pos(&base, &s->offset, out);
    return true;
}
