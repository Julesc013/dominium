/*
FILE: source/dominium/game/runtime/dom_calendar.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/calendar
RESPONSIBILITY: Calendar registry and deterministic fixed-pattern render/parse helpers.
*/
#include "runtime/dom_calendar.h"

#include <stddef.h>
#include <string.h>
#include <vector>

namespace {

struct CalendarEntry {
    dom_calendar_def def;
};

static int find_calendar_index(const std::vector<CalendarEntry> &entries, dom_calendar_id id) {
    size_t i;
    for (i = 0u; i < entries.size(); ++i) {
        if (entries[i].def.id == id) {
            return (int)i;
        }
    }
    return -1;
}

static void insert_sorted(std::vector<CalendarEntry> &entries, const dom_calendar_def &def) {
    size_t i = 0u;
    CalendarEntry entry;
    entry.def = def;
    while (i < entries.size() && entries[i].def.id < def.id) {
        ++i;
    }
    entries.insert(entries.begin() + (std::vector<CalendarEntry>::difference_type)i, entry);
}

static void reset_date(dom_calendar_date *out_date) {
    if (!out_date) {
        return;
    }
    memset(out_date, 0, sizeof(*out_date));
    out_date->intercalary = DOM_CALENDAR_INTERCALARY_NONE;
    out_date->fields_present = 0u;
}

static int add_u64(u64 a, u64 b, u64 *out_val) {
    u64 max = (u64)~(u64)0;
    if (!out_val) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (a > (max - b)) {
        return DOM_CALENDAR_OVERFLOW;
    }
    *out_val = a + b;
    return DOM_CALENDAR_OK;
}

static int mul_u64(u64 a, u64 b, u64 *out_val) {
    u64 max = (u64)~(u64)0;
    if (!out_val) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (a != 0ull && b > (max / a)) {
        return DOM_CALENDAR_OVERFLOW;
    }
    *out_val = a * b;
    return DOM_CALENDAR_OK;
}

static d_bool is_leap_year(u64 year, dom_calendar_leap_rule rule) {
    switch (rule) {
        case DOM_CALENDAR_LEAP_GREGORIAN:
            if ((year % 400ull) == 0ull) {
                return D_TRUE;
            }
            if ((year % 100ull) == 0ull) {
                return D_FALSE;
            }
            return ((year % 4ull) == 0ull) ? D_TRUE : D_FALSE;
        case DOM_CALENDAR_LEAP_JULIAN:
            return ((year % 4ull) == 0ull) ? D_TRUE : D_FALSE;
        case DOM_CALENDAR_LEAP_NONE:
        default:
            return D_FALSE;
    }
}

static int year_to_days(const dom_calendar_fixed_pattern *fixed, u64 year, u64 *out_days) {
    u64 days_years = 0ull;
    u64 leap_count = 0ull;
    u64 leap_days = 0ull;
    int rc;

    if (!fixed || !out_days) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (fixed->year_days == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    rc = mul_u64(year, (u64)fixed->year_days, &days_years);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }

    switch (fixed->leap_rule) {
        case DOM_CALENDAR_LEAP_GREGORIAN:
            leap_count = (year / 4ull) - (year / 100ull) + (year / 400ull);
            break;
        case DOM_CALENDAR_LEAP_JULIAN:
            leap_count = (year / 4ull);
            break;
        case DOM_CALENDAR_LEAP_NONE:
        default:
            leap_count = 0ull;
            break;
    }

    rc = mul_u64(leap_count, (u64)fixed->intercalary_leap_days, &leap_days);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }
    return add_u64(days_years, leap_days, out_days);
}

static int year_from_day_index(const dom_calendar_fixed_pattern *fixed,
                               u64 day_index,
                               u64 *out_year,
                               u64 *out_day_of_year,
                               d_bool *out_leap) {
    u64 low;
    u64 high;
    if (!fixed || !out_year || !out_day_of_year || !out_leap) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (fixed->year_days == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    low = 0ull;
    high = (day_index / (u64)fixed->year_days) + 2ull;

    while (low <= high) {
        u64 mid = low + ((high - low) / 2ull);
        u64 days_mid = 0ull;
        u64 days_next = 0ull;
        int rc = year_to_days(fixed, mid, &days_mid);
        if (rc != DOM_CALENDAR_OK) {
            return rc;
        }
        rc = year_to_days(fixed, mid + 1ull, &days_next);
        if (rc != DOM_CALENDAR_OK) {
            return rc;
        }
        if (days_mid <= day_index && day_index < days_next) {
            *out_year = mid;
            *out_day_of_year = day_index - days_mid;
            *out_leap = is_leap_year(mid, fixed->leap_rule);
            return DOM_CALENDAR_OK;
        }
        if (day_index < days_mid) {
            if (mid == 0ull) {
                break;
            }
            high = mid - 1ull;
        } else {
            low = mid + 1ull;
        }
    }
    return DOM_CALENDAR_ERR;
}

static int map_day_to_month(const dom_calendar_fixed_pattern *fixed,
                            u64 day_of_year,
                            d_bool leap,
                            dom_calendar_date *out_date) {
    u64 intercalary_total;
    u64 month_days_total = 0ull;
    u64 day;
    u32 i;
    if (!fixed || !out_date) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (!fixed->month_lengths || fixed->month_count == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    intercalary_total = (u64)fixed->intercalary_base_days;
    if (leap == D_TRUE) {
        intercalary_total += (u64)fixed->intercalary_leap_days;
    }

    for (i = 0u; i < fixed->month_count; ++i) {
        month_days_total += (u64)fixed->month_lengths[i];
    }

    if (fixed->intercalary_after_month == 0u) {
        if (day_of_year >= month_days_total) {
            u64 intercalary_index = day_of_year - month_days_total;
            if (intercalary_index >= intercalary_total) {
                return DOM_CALENDAR_INVALID_ARGUMENT;
            }
            out_date->intercalary = (intercalary_index < fixed->intercalary_base_days)
                                        ? DOM_CALENDAR_INTERCALARY_YEAR_DAY
                                        : DOM_CALENDAR_INTERCALARY_LEAP_DAY;
            out_date->fields_present |= DOM_CALENDAR_FIELD_INTERCALARY;
            return DOM_CALENDAR_OK;
        }
    } else if (fixed->intercalary_after_month > fixed->month_count) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    day = day_of_year;
    for (i = 0u; i < fixed->month_count; ++i) {
        u32 month_index = i + 1u;
        u32 month_len = fixed->month_lengths[i];
        if (fixed->intercalary_after_month == month_index) {
            if (day < (u64)month_len) {
                out_date->month = month_index;
                out_date->day = (u32)(day + 1ull);
                out_date->fields_present |= DOM_CALENDAR_FIELD_MONTH | DOM_CALENDAR_FIELD_DAY;
                return DOM_CALENDAR_OK;
            }
            if (day < (u64)month_len + intercalary_total) {
                u64 intercalary_index = day - (u64)month_len;
                out_date->intercalary = (intercalary_index < fixed->intercalary_base_days)
                                            ? DOM_CALENDAR_INTERCALARY_YEAR_DAY
                                            : DOM_CALENDAR_INTERCALARY_LEAP_DAY;
                out_date->fields_present |= DOM_CALENDAR_FIELD_INTERCALARY;
                return DOM_CALENDAR_OK;
            }
            day -= intercalary_total;
        }
        if (day < (u64)month_len) {
            out_date->month = month_index;
            out_date->day = (u32)(day + 1ull);
            out_date->fields_present |= DOM_CALENDAR_FIELD_MONTH | DOM_CALENDAR_FIELD_DAY;
            return DOM_CALENDAR_OK;
        }
        day -= (u64)month_len;
    }

    return DOM_CALENDAR_INVALID_ARGUMENT;
}

static int month_day_to_doy(const dom_calendar_fixed_pattern *fixed,
                            u32 month,
                            u32 day,
                            d_bool leap,
                            u64 *out_doy) {
    u64 intercalary_total;
    u64 doy = 0ull;
    u32 i;
    if (!fixed || !out_doy) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (!fixed->month_lengths || fixed->month_count == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (month == 0u || month > fixed->month_count) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    intercalary_total = (u64)fixed->intercalary_base_days;
    if (leap == D_TRUE) {
        intercalary_total += (u64)fixed->intercalary_leap_days;
    }

    for (i = 1u; i < month; ++i) {
        doy += (u64)fixed->month_lengths[i - 1u];
        if (fixed->intercalary_after_month == i && intercalary_total > 0ull) {
            doy += intercalary_total;
        }
    }

    if (day == 0u || day > fixed->month_lengths[month - 1u]) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    doy += (u64)(day - 1u);
    *out_doy = doy;
    return DOM_CALENDAR_OK;
}

static int render_fixed_pattern(const dom_calendar_def *def,
                                u64 day_index,
                                u64 seconds_in_day,
                                u32 subsecond_ticks,
                                dom_calendar_date *out_date) {
    u64 year = 0ull;
    u64 day_of_year = 0ull;
    d_bool leap = D_FALSE;
    int rc;
    i64 year_display;

    if (!def || !out_date) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (def->day_seconds == 0ull) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    rc = year_from_day_index(&def->u.fixed, day_index, &year, &day_of_year, &leap);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }

    year_display = (i64)year + (i64)def->year_offset;
    if (year_display < 0) {
        return DOM_CALENDAR_BACKWARDS;
    }

    out_date->year = (u64)year_display;
    out_date->day_of_year = day_of_year;
    out_date->fields_present |= DOM_CALENDAR_FIELD_YEAR | DOM_CALENDAR_FIELD_DAY_OF_YEAR;

    if (def->u.fixed.week_length > 0u) {
        out_date->weekday = (u32)(day_of_year % (u64)def->u.fixed.week_length);
        out_date->week_of_year = (u32)(day_of_year / (u64)def->u.fixed.week_length);
        out_date->fields_present |= DOM_CALENDAR_FIELD_WEEKDAY | DOM_CALENDAR_FIELD_WEEK_OF_YEAR;
    }

    rc = map_day_to_month(&def->u.fixed, day_of_year, leap, out_date);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }

    if (seconds_in_day >= def->day_seconds) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    out_date->hour = (u32)(seconds_in_day / 3600ull);
    out_date->minute = (u32)((seconds_in_day / 60ull) % 60ull);
    out_date->second = (u32)(seconds_in_day % 60ull);
    out_date->subsecond_ticks = subsecond_ticks;
    out_date->fields_present |= DOM_CALENDAR_FIELD_TIME | DOM_CALENDAR_FIELD_SUBSECOND;
    return DOM_CALENDAR_OK;
}

} // namespace

struct dom_calendar_registry {
    std::vector<CalendarEntry> entries;
};

dom_calendar_registry *dom_calendar_registry_create(void) {
    return new dom_calendar_registry();
}

void dom_calendar_registry_destroy(dom_calendar_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_calendar_registry_register(dom_calendar_registry *registry,
                                   const dom_calendar_def *def) {
    if (!registry || !def) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (def->id == 0ull) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (find_calendar_index(registry->entries, def->id) >= 0) {
        return DOM_CALENDAR_DUPLICATE_ID;
    }
    insert_sorted(registry->entries, *def);
    return DOM_CALENDAR_OK;
}

int dom_calendar_registry_get(const dom_calendar_registry *registry,
                              dom_calendar_id id,
                              dom_calendar_def *out_def) {
    int idx;
    if (!registry || !out_def) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    idx = find_calendar_index(registry->entries, id);
    if (idx < 0) {
        return DOM_CALENDAR_NOT_FOUND;
    }
    *out_def = registry->entries[(size_t)idx].def;
    return DOM_CALENDAR_OK;
}

int dom_calendar_registry_register_builtin(dom_calendar_registry *registry) {
    if (!registry) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    return DOM_CALENDAR_OK;
}

int dom_calendar_render(const dom_calendar_registry *registry,
                        dom_calendar_id id,
                        dom_time_frame_id frame,
                        dom_tick tick,
                        dom_ups ups,
                        d_bool calendar_known,
                        dom_calendar_date *out_date) {
    dom_calendar_def def;
    u64 seconds;
    u32 subsecond_ticks;
    dom_act_time_t act;
    dom_act_time_t frame_act;
    int rc;

    if (!registry || !out_date) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    reset_date(out_date);
    if (calendar_known == D_FALSE) {
        return DOM_CALENDAR_UNKNOWN;
    }
    if (ups == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    rc = dom_calendar_registry_get(registry, id, &def);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }
    if (def.day_seconds == 0ull) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (def.day_seconds > (u64)DOM_TIME_ACT_MAX) {
        return DOM_CALENDAR_OVERFLOW;
    }

    seconds = (u64)(tick / (dom_tick)ups);
    subsecond_ticks = (u32)(tick % (dom_tick)ups);
    if (seconds > (u64)DOM_TIME_ACT_MAX) {
        return DOM_CALENDAR_OVERFLOW;
    }
    act = (dom_act_time_t)seconds;
    rc = dom_time_frame_convert(frame, act, &frame_act);
    if (rc != DOM_TIME_OK) {
        return (rc == DOM_TIME_OVERFLOW) ? DOM_CALENDAR_OVERFLOW : DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (frame_act < 0) {
        return DOM_CALENDAR_BACKWARDS;
    }

    switch (def.kind) {
        case DOM_CALENDAR_KIND_FIXED_PATTERN:
            return render_fixed_pattern(&def,
                                        (u64)(frame_act / (dom_act_time_t)def.day_seconds),
                                        (u64)(frame_act % (dom_act_time_t)def.day_seconds),
                                        subsecond_ticks,
                                        out_date);
        default:
            return DOM_CALENDAR_NOT_IMPLEMENTED;
    }
}

int dom_calendar_parse(const dom_calendar_registry *registry,
                       dom_calendar_id id,
                       const dom_calendar_date *date,
                       dom_time_frame_id frame,
                       dom_act_time_t *out_act,
                       u32 *out_subsecond_ticks) {
    dom_calendar_def def;
    d_bool leap;
    u64 year_base;
    i64 year_base_i;
    u64 day_of_year;
    u64 days_before_year;
    u64 year_length;
    u64 total_days;
    u64 seconds_in_day = 0ull;
    u64 total_seconds = 0ull;
    int rc;

    if (!registry || !date || !out_act) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (frame != DOM_TIME_FRAME_ACT) {
        return DOM_CALENDAR_NOT_IMPLEMENTED;
    }
    if (date->fields_present == 0u) {
        return DOM_CALENDAR_UNKNOWN;
    }

    rc = dom_calendar_registry_get(registry, id, &def);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }
    if (def.kind != DOM_CALENDAR_KIND_FIXED_PATTERN) {
        return DOM_CALENDAR_NOT_IMPLEMENTED;
    }
    if (def.day_seconds == 0ull) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    if ((date->fields_present & DOM_CALENDAR_FIELD_YEAR) == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    year_base_i = (i64)date->year - (i64)def.year_offset;
    if (year_base_i < 0) {
        return DOM_CALENDAR_BACKWARDS;
    }
    year_base = (u64)year_base_i;
    leap = is_leap_year(year_base, def.u.fixed.leap_rule);

    if ((date->fields_present & DOM_CALENDAR_FIELD_DAY_OF_YEAR) != 0u) {
        day_of_year = date->day_of_year;
    } else if ((date->fields_present & DOM_CALENDAR_FIELD_MONTH) != 0u &&
               (date->fields_present & DOM_CALENDAR_FIELD_DAY) != 0u) {
        rc = month_day_to_doy(&def.u.fixed, date->month, date->day, leap, &day_of_year);
        if (rc != DOM_CALENDAR_OK) {
            return rc;
        }
    } else {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    year_length = (u64)def.u.fixed.year_days;
    if (leap == D_TRUE) {
        year_length += (u64)def.u.fixed.intercalary_leap_days;
    }
    if (day_of_year >= year_length) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    rc = year_to_days(&def.u.fixed, year_base, &days_before_year);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }
    rc = add_u64(days_before_year, day_of_year, &total_days);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }
    if ((date->fields_present & DOM_CALENDAR_FIELD_TIME) != 0u) {
        seconds_in_day = ((u64)date->hour * 3600ull) +
                         ((u64)date->minute * 60ull) +
                         (u64)date->second;
    }
    if (seconds_in_day >= def.day_seconds) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    rc = mul_u64(total_days, def.day_seconds, &total_seconds);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }
    rc = add_u64(total_seconds, seconds_in_day, &total_seconds);
    if (rc != DOM_CALENDAR_OK) {
        return rc;
    }
    if (total_seconds > (u64)DOM_TIME_ACT_MAX) {
        return DOM_CALENDAR_OVERFLOW;
    }
    *out_act = (dom_act_time_t)total_seconds;
    if (out_subsecond_ticks) {
        if ((date->fields_present & DOM_CALENDAR_FIELD_SUBSECOND) != 0u) {
            *out_subsecond_ticks = date->subsecond_ticks;
        } else {
            *out_subsecond_ticks = 0u;
        }
    }
    return DOM_CALENDAR_OK;
}
