#ifndef DSU_EXE_ARCHIVE_H_INCLUDED
#define DSU_EXE_ARCHIVE_H_INCLUDED

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dsu_exe_archive_t dsu_exe_archive_t;

int dsu_exe_archive_open(const char *exe_path, dsu_exe_archive_t **out_archive);
void dsu_exe_archive_close(dsu_exe_archive_t *archive);
int dsu_exe_archive_extract(dsu_exe_archive_t *archive, const char *dest_root);
int dsu_exe_archive_validate_paths(dsu_exe_archive_t *archive);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DSU_EXE_ARCHIVE_H_INCLUDED */
