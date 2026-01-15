@echo off
setlocal EnableExtensions EnableDelayedExpansion

REM ============================================================
REM Dominium: Finish structural refactor to canonical tree
REM - Moves / renames / merges / obsoletes
REM - No deletes; ambiguous items are quarantined to legacy/_orphaned
REM ============================================================

echo === Dominium finish_refactor_100 ===
echo Working dir: %CD%
echo.

REM ---------------------------
REM Helpers (inline)
REM ---------------------------
REM :mkd "path"  -> mkdir if missing
REM :mvdir "src" "dst" -> move dir if src exists; if dst exists, quarantine src into legacy/_orphaned
REM :mvcontents "src\*" "dst\" -> move contents when safe
REM :qdir "src" "reason" -> move into legacy/_orphaned\reason\...
REM ---------------------------

set "ORPH=legacy\_orphaned"
if not exist "legacy" mkdir "legacy"
if not exist "%ORPH%" mkdir "%ORPH%"

REM ---------------------------
REM Create canonical skeleton (idempotent)
REM ---------------------------
for %%D in (
  docs docs\architecture docs\specs docs\guides docs\history
  schema schema\world schema\save schema\net schema\mod schema\tool
  libs libs\base libs\base\include libs\base\include\dmn libs\base\modules
  libs\base\modules\tlv libs\base\modules\hash libs\base\modules\fixed libs\base\modules\math libs\base\modules\audit
  libs\fsmodel libs\fsmodel\include libs\fsmodel\modules
  libs\crypto libs\netproto
  engine engine\include engine\modules engine\render engine\tests
  engine\modules\core engine\modules\ecs engine\modules\sim engine\modules\world engine\modules\io engine\modules\sys
  engine\modules\sys\time engine\modules\sys\fs engine\modules\sys\thread engine\modules\sys\atomics
  engine\render\sw engine\render\gl engine\render\gl\core engine\render\gl\shaders
  engine\render\vulkan engine\render\d3d engine\render\d3d\d3d7 engine\render\d3d\d3d9 engine\render\d3d\d3d11 engine\render\d3d\d3d12
  engine\render\metal engine\render\null
  game game\core game\rules game\ai game\economy game\content game\mods game\ui game\tests
  game\content\worldgen game\content\factions game\content\tech game\content\scenarios
  client client\core client\core\session client\core\input client\core\net client\ui client\ui\menus client\ui\hud client\ui\overlays client\platform client\tests
  client\platform\win client\platform\win\win9x client\platform\win\winnt client\platform\linux client\platform\bsd client\platform\mac client\platform\mac\classic client\platform\mac\osx client\platform\wasm
  server server\core server\core\world server\core\auth server\core\net server\core\shard server\core\persist server\platform server\tools server\tests
  server\platform\win server\platform\win\winnt server\platform\linux server\platform\bsd server\platform\mac server\platform\mac\osx server\platform\container server\platform\baremetal
  launcher launcher\core launcher\core\discover launcher\core\profile launcher\core\invoke launcher\ui launcher\platform launcher\tests
  launcher\platform\win launcher\platform\win\win9x launcher\platform\win\winnt launcher\platform\linux launcher\platform\bsd launcher\platform\mac launcher\platform\mac\classic launcher\platform\mac\osx
  setup setup\core setup\core\fetch setup\core\verify setup\core\install setup\core\rollback setup\packages setup\packages\client setup\packages\server setup\packages\tools setup\ui setup\platform setup\tests
  setup\platform\win setup\platform\win\win9x setup\platform\win\winnt setup\platform\linux setup\platform\bsd setup\platform\mac setup\platform\mac\classic setup\platform\mac\osx
  tools tools\pack tools\inspect tools\migrate tools\verify tools\modkit tools\benchmark
  sdk sdk\include sdk\samples sdk\tools sdk\docs
  ci ci\build ci\test ci\verify ci\release
  dist labs
) do (
  if not exist "%%D" mkdir "%%D" >nul 2>nul
)

REM ---------------------------
REM 1) Fix .github location: move ci\.github -> .github
REM ---------------------------
if exist "ci\.github" (
  if not exist ".github" (
    move "ci\.github" ".github" >nul
    echo Moved: ci\.github -> .github
  ) else (
    REM If .github already exists, quarantine ci\.github
    call :qdir "ci\.github" "github_conflict"
  )
)

REM ---------------------------
REM 2) Flatten known double-nesting patterns
REM ---------------------------

REM game\tests\tests -> game\tests
if exist "game\tests\tests" (
  move "game\tests\tests\*" "game\tests\" >nul 2>nul
  echo Flattened: game\tests\tests -> game\tests
)

REM game\mods\mods -> game\mods
if exist "game\mods\mods" (
  move "game\mods\mods\*" "game\mods\" >nul 2>nul
  echo Flattened: game\mods\mods -> game\mods
)

REM tools\tools -> tools (merge by moving children)
if exist "tools\tools" (
  for /d %%X in ("tools\tools\*") do (
    set "NAME=%%~nxX"
    if exist "tools\!NAME!" (
      call :qdir "tools\!NAME!" "tools_conflict_!NAME!"
    )
    move "%%X" "tools\!NAME!" >nul
    echo Moved tool: tools\tools\!NAME! -> tools\!NAME!
  )
  for %%F in ("tools\tools\*") do (
    if exist "%%F" (
      move "%%F" "tools\" >nul 2>nul
      echo Moved file: %%~nxF -> tools\
    )
  )
)

REM ---------------------------
REM 3) Engine contamination cleanup (strict)
REM    Engine must not contain unrelated include/external or nested legacy trees.
REM ---------------------------

REM engine\external -> libs\base\modules\hash\xxhash (if exactly xxhash) else orphan
if exist "engine\external\xxhash" (
  if exist "libs\base\modules\hash\xxhash" call :qdir "libs\base\modules\hash\xxhash" "hash_xxhash_conflict"
  move "engine\external\xxhash" "libs\base\modules\hash\xxhash" >nul
  echo Moved: engine\external\xxhash -> libs\base\modules\hash\xxhash
) else (
  if exist "engine\external" call :qdir "engine\external" "engine_external_orphan"
)

REM engine\include\dominium (misplaced) -> game\include\dominium (create) else orphan
if exist "engine\include\dominium" (
  if not exist "game\include" mkdir "game\include" >nul 2>nul
  if exist "game\include\dominium" call :qdir "game\include\dominium" "game_include_dominium_conflict"
  move "engine\include\dominium" "game\include\dominium" >nul
  echo Moved: engine\include\dominium -> game\include\dominium
)

REM engine\include\dsu and engine\include\dui are not engine-ABI. Quarantine.
if exist "engine\include\dsu" call :qdir "engine\include\dsu" "misplaced_headers_dsu"
if exist "engine\include\dui" call :qdir "engine\include\dui" "misplaced_headers_dui"

REM engine\launcher_core_launcher and engine\setup_core_setup should never be under engine. Move to legacy root.
if exist "engine\launcher_core_launcher" (
  if exist "legacy\launcher_core_launcher" call :qdir "legacy\launcher_core_launcher" "legacy_launcher_core_conflict"
  move "engine\launcher_core_launcher" "legacy\launcher_core_launcher" >nul
  echo Moved: engine\launcher_core_launcher -> legacy\launcher_core_launcher
)
if exist "engine\setup_core_setup" (
  if exist "legacy\setup_core_setup" call :qdir "legacy\setup_core_setup" "legacy_setup_core_conflict"
  move "engine\setup_core_setup" "legacy\setup_core_setup" >nul
  echo Moved: engine\setup_core_setup -> legacy\setup_core_setup
)

REM ---------------------------
REM 4) Promote engine subsystems out of legacy snapshot if present
REM    (If you already promoted, this will be mostly no-ops)
REM ---------------------------

REM legacy\engine_modules_engine\engine\{subsystems} -> engine\modules\<subsystem>
if exist "legacy\engine_modules_engine\engine" (
  for %%S in (
    agent ai audio caps compat content decor dui econ env hydro input job launcher mod net policy replay res research sim state struct system trans tui ui ui_codegen ui_ir vehicle view world
  ) do (
    if exist "legacy\engine_modules_engine\engine\%%S" (
      if not exist "engine\modules\%%S" mkdir "engine\modules\%%S" >nul 2>nul
      move "legacy\engine_modules_engine\engine\%%S\*" "engine\modules\%%S\" >nul 2>nul
      echo Promoted: %%S -> engine\modules\%%S
    )
  )
)

REM IMPORTANT: engine must not keep launcher module
if exist "engine\modules\launcher" (
  call :qdir "engine\modules\launcher" "engine_has_launcher_module"
)

REM ---------------------------
REM 5) Move residual old monolith code out of legacy/source into products (coarse, safe)
REM    Anything ambiguous goes to legacy/_orphaned for later manual/Codex mapping.
REM ---------------------------

REM legacy\source\game -> game/_legacy_code (do not merge into game/core blindly)
if exist "legacy\source\game" (
  if not exist "legacy\_orphaned\legacy_source_game" mkdir "legacy\_orphaned\legacy_source_game" >nul 2>nul
  move "legacy\source\game" "legacy\_orphaned\legacy_source_game\game" >nul
  echo Quarantined: legacy\source\game
)

REM legacy\source\common -> legacy/_orphaned (shared monolith needs redesign)
if exist "legacy\source\common" (
  call :qdir "legacy\source\common" "legacy_source_common"
)

REM ---------------------------
REM 6) Cleanup obvious leftovers
REM ---------------------------

REM data/ is legacy staging; move under legacy if you want canonical tree to be clean.
REM If you still rely on it, comment these out.
if exist "data" (
  if not exist "legacy\data" (
    move "data" "legacy\data" >nul
    echo Moved: data -> legacy\data
  ) else (
    call :qdir "data" "data_conflict"
  )
)

REM temp.cmd belongs nowhere
if exist "temp.cmd" (
  call :qdir "temp.cmd" "temp_files"
)

echo.
echo === Done. Repo is now structurally canonical. ===
echo Anything not safely mappable was moved into: %ORPH%
echo Next step is code refactor (includes, CMake targets, API boundaries).
echo.
endlocal
exit /b 0

REM ------------------------------------------------------------
REM Subroutines
REM ------------------------------------------------------------
:qdir
REM %1=path %2=reason
set "SRC=%~1"
set "REASON=%~2"
if not exist "%SRC%" exit /b 0
if not exist "%ORPH%\%REASON%" mkdir "%ORPH%\%REASON%" >nul 2>nul
for %%Z in ("%SRC%") do set "BASE=%%~nxZ"
set "DST=%ORPH%\%REASON%\%BASE%"
REM ensure unique destination
set /a N=0
:qd_try
if exist "%DST%" (
  set /a N+=1
  set "DST=%ORPH%\%REASON%\%BASE%_%N%"
  goto qd_try
)
move "%SRC%" "%DST%" >nul
echo Quarantined: %SRC% -> %DST%
exit /b 0
