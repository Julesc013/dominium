Dominium DOS Installer Layout

Expected directory layout (zip/floppy or staging dir):

  INSTALL.EXE
  MANIFESTS\dominium_legacy.dsumanifest
  PAYLOADS\payload.dsuarch
  DOCS\

INSTALL.EXE reads the manifest from MANIFESTS and payloads from PAYLOADS.
If using make_sfx, the payload archive is appended to INSTALL.EXE
with a DSUX footer (see make_sfx.bat/make_sfx.sh).
