#include "domino/core/process_guard.h"

#if DOM_PROCESS_GUARD_ENABLED
static int g_process_guard_depth = 0;
static unsigned int g_process_guard_violations = 0;
static unsigned int g_process_guard_mutations = 0;
#endif

void dom_process_guard_enter(const char *process_name)
{
#if DOM_PROCESS_GUARD_ENABLED
    (void)process_name;
    g_process_guard_depth += 1;
#else
    (void)process_name;
#endif
}

void dom_process_guard_exit(void)
{
#if DOM_PROCESS_GUARD_ENABLED
    if (g_process_guard_depth > 0) {
        g_process_guard_depth -= 1;
    }
#endif
}

int dom_process_guard_is_active(void)
{
#if DOM_PROCESS_GUARD_ENABLED
    return g_process_guard_depth > 0;
#else
    return 0;
#endif
}

void dom_process_guard_note_mutation(const char *file, int line)
{
#if DOM_PROCESS_GUARD_ENABLED
    (void)file;
    (void)line;
    g_process_guard_mutations += 1;
    if (g_process_guard_depth <= 0) {
        g_process_guard_violations += 1;
    }
#else
    (void)file;
    (void)line;
#endif
}

unsigned int dom_process_guard_violation_count(void)
{
#if DOM_PROCESS_GUARD_ENABLED
    return g_process_guard_violations;
#else
    return 0;
#endif
}

unsigned int dom_process_guard_mutation_count(void)
{
#if DOM_PROCESS_GUARD_ENABLED
    return g_process_guard_mutations;
#else
    return 0;
#endif
}

void dom_process_guard_reset(void)
{
#if DOM_PROCESS_GUARD_ENABLED
    g_process_guard_depth = 0;
    g_process_guard_violations = 0;
    g_process_guard_mutations = 0;
#endif
}
