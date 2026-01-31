#ifndef DOMINO_CORE_PROCESS_GUARD_H
#define DOMINO_CORE_PROCESS_GUARD_H

#ifdef __cplusplus
extern "C" {
#endif

void dom_process_guard_enter(const char *process_name);
void dom_process_guard_exit(void);
int dom_process_guard_is_active(void);
void dom_process_guard_note_mutation(const char *file, int line);
unsigned int dom_process_guard_violation_count(void);
unsigned int dom_process_guard_mutation_count(void);
void dom_process_guard_reset(void);

#if !defined(DOM_PROCESS_GUARD_ENABLED)
#  if !defined(NDEBUG)
#    define DOM_PROCESS_GUARD_ENABLED 1
#  else
#    define DOM_PROCESS_GUARD_ENABLED 0
#  endif
#endif

#if DOM_PROCESS_GUARD_ENABLED
#  define DOM_PROCESS_GUARD_MUTATION() dom_process_guard_note_mutation(__FILE__, __LINE__)
#else
#  define DOM_PROCESS_GUARD_MUTATION() ((void)0)
#endif

#ifdef __cplusplus
}
#endif

#endif
