Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none

# PKG Implementation Report

## Scope

This report captures the current `dompkg` packaging pipeline state for `winnt/x86_64` on this repository head.

## Validation Commands

- `python scripts/ci/check_repox_rules.py --repo-root .`
- `cmake --build out/build/vs2026/verify --config Debug --target domino_engine dominium_game`
- `cmake --build out/build/vs2026/verify --config Debug --target testx_all`
- `dist/sys/winnt/x64/bin/tools/tool_ui_bind.exe --repo-root . --check`
- `cmake --build out/build/vs2026/verify --config Debug --target pkg_pack_all`
- `cmake --build out/build/vs2026/verify --config Debug --target pkg_index_all`
- `cmake --build out/build/vs2026/verify --config Debug --target pkg_verify_all`
- `cmake --build out/build/vs2026/verify --config Debug --target dist_build_manifest`

## Output Locations

- Packages: `dist/pkg/winnt/x86_64/pkgs`
- Package index: `dist/pkg/winnt/x86_64/index/pkg_index.json`
- Build manifest: `dist/meta/winnt/x86_64/build_manifest.json`

## Produced Packages (pkg_id -> content_hash)

- `org.dominium.core.runtime_cfg` -> `19fc20ecd889eb5d37e8027a597547c3123fc98fa548986d3c5c0c7d390d2498`
- `org.dominium.core.engine` -> `899c251278103cff79ab8ed581414ee677a4ac1f69e30925d42d8ab8a6096cbf`
- `org.dominium.core.game` -> `1f2b98f3dfc3af0b434b8120df97f1ec4a9ce4928d64b294345ebe8c0497b4d6`
- `org.dominium.core.client` -> `ad3abb979b2365434086877b00be14e8a03f18fd829620f9c9d00fd0b52a88e7`
- `org.dominium.core.server` -> `2baf89dcafa8ea678e5c87e17fb184b21909bdfd059972a216d347ba582998e3`
- `org.dominium.core.launcher` -> `2ee5ea46d84214138588eb8a2f6600257c638e806a5717dafbd589bf10761515`
- `org.dominium.core.setup` -> `8d4665da63a520563dca99af81ec8e42882537a40e750a23ae2857b424acf482`
- `org.dominium.rend.soft` -> `6448ec176ed2b9a57733447e48f9e12461b01ab914a174ff68bd0322a27b68e3`
- `org.dominium.rend.null` -> `48acf5fb306b323241f8d7f90d44c87aa2e62d12e3fae4b15615db9e8e2a117d`
- `org.dominium.tools.ui` -> `86d66323307dfa9f3ad9ea227c48d8cb1876412f8cb5dd6377b533ba2aeee8d5`
- `org.dominium.tools.pack` -> `321763f77289b74f4f16ed9e172a405023a53962fdcbc8eb639f0b382050bae0`
- `org.dominium.res.common` -> `e47c5c420aa142d8e53db2ef1b434c0738eff5982fd1b9df4257abd020ae7f6b`
- `org.dominium.locale.en_US` -> `60044095c23805429ccb17837cbbc9d43e85835fda855b2a0cbf82c0a0adc688`
- `org.dominium.res.packs.base` -> `85f91af1d7ed9948d0bcc71abbf20b331e7bcf12f2e1c508b9490d188a278dac`
- `org.dominium.docs.user` -> `9b0f3bb4444bd114b219a038bca024d496b3de8ed3fef840dd93586e2f83df1d`
- `org.dominium.sym.client` -> `4bc7b49b23c1935e7d4f38b77abf13035bb7dbac9a91631664ab7976e974e4cf`
- `org.dominium.sym.server` -> `c3a68c365e8d93409d5ed74e6e54c5edebcdb2a7e2430810e34f9bc320cb0b76`
- `org.dominium.sym.launcher` -> `703eaf4502b601ebea54c213c0236a5e8b128ead5a324ebd036b85521bda8498`
- `org.dominium.sym.setup` -> `95f4b8093e9546e73995c51f04631fb54f420416852654a9385b4f10d1d4ae39`

## Install Projection Determinism Status

- Setup smoke (`setup_install_smoke`) passes deterministically.
- Full deterministic install/rollback coverage remains enforced by `setup_install_tests` in `testx_all`.

## Policy and Contract Locations

- Package format/manifest contracts: `docs/distribution/PKG_FORMAT.md`, `docs/distribution/PKG_MANIFEST.md`
- Dist tree contract: `docs/distribution/DIST_TREE_CONTRACT.md`
- Install/rollback contract: `docs/distribution/PKG_INSTALL_AND_ROLLBACK.md`
- CI pipeline contract: `docs/ci/DIST_PKG_PIPELINE.md`
- RepoX rulesets: `repo/repox/rulesets`

## Offline Install and Steam Mapping

- Offline cache and transfer procedure: `docs/distribution/OFFLINE_AND_STEAM_MAPPING.md`
- Depot/transport mapping is treated as packaging transport over canonical `dompkg` payloads.
