# Reader Brief — Dominium Platform Support Planning

## What This Chat Was About

This chat was about platform support planning for Dominium. It started with broad questions about what systems and operating systems Dominium could support, then expanded into a large device-family inventory covering PlayStation, Xbox, Nintendo, PC handhelds, Android, Apple/iOS, Web, AR, VR, and cross-cutting graphics/runtime technologies. The most important user decision came near the end: Android, iOS, and Web will be primary top-tier support after PC.

The current working model is therefore: PC first; Android, iOS, and Web also Tier-0. PC implies Windows, macOS, and Linux planning, though exact minimums are not known. Android, iOS, and Web must not be treated as late ports. Consoles remain desired but should be treated as gated secondary targets unless elevated. Legacy consoles, old handhelds, retro OSes, and bare-metal/firmware targets should be treated as constrained/research/engine-only unless the user later makes them a priority.

The best continuation is to create a formal Platform Support Matrix and platform contracts. Do not rely on prior assistant claims or old citation IDs for current platform facts. Verify SDKs, stores, browser features, console rules, hardware status, and legal constraints from current official sources before implementation planning.

## Most Important Things to Know

- PC is the first primary platform family.
- Android is primary top-tier support after PC.
- iOS is primary top-tier support after PC.
- Web is primary top-tier support after PC.
- Mobile and Web should not be treated as late ports.
- Use a formal platform support matrix/platform contracts.
- Consoles are desired but gated/secondary unless elevated.
- Legacy consoles/retro OSes are constrained/research by default.
- “Domino” engine/core name is unconfirmed.
- All external platform facts require verification before future use.
- Do not bundle proprietary BIOS/firmware for legacy/emulated support.
- Closed console support must use official access for commercial/native support.
- PC handhelds map primarily to PC OS targets plus handheld QA/UX profiles.
- XR priority is unresolved; runtime-first OpenXR/WebXR was only an assistant proposal.
- Engine/toolchain choice is not established.
- Support must be defined by scope: full product, reduced build, engine-only, emulator-hosted, remote-play, unsupported.
- This package is chat-specific and not a whole-project summary.

## Active Plans or Workstreams

- WORKSTREAM-01: Overall Dominium platform support strategy and tier model — highest priority.
- WORKSTREAM-02: Tier-0 PC desktop operating system support — highest priority.
- WORKSTREAM-03: Tier-0 Android ecosystem support — highest priority.
- WORKSTREAM-04: Tier-0 iOS/iPadOS and Apple-family classification — highest priority.
- WORKSTREAM-05: Tier-0 Web/WASM/browser/PWA support — highest priority.
- WORKSTREAM-06: Closed console support strategy: PlayStation, Xbox, Nintendo — medium-high priority.
- WORKSTREAM-07: PC handheld support — high priority.
- WORKSTREAM-10: Cross-cutting architecture, backend, runtime, and compatibility strategy — highest priority.
- WORKSTREAM-11: Chat-specific handoff/report package — highest for current task priority.

## Decisions Already Made

- DECISION-01: PC is the first primary platform family for Dominium. (FACT; decided by explicit user wording).
- DECISION-02: Android is primary top-tier support after PC. (FACT; decided by explicit user statement).
- DECISION-03: iOS is primary top-tier support after PC. (FACT; decided by explicit user statement).
- DECISION-04: Web is primary top-tier support after PC. (FACT; decided by explicit user statement).
- DECISION-05: Mobile and Web should be treated as co-equal roots with PC, not late ports. (INFERENCE; inferred working decision based on explicit user priority and prior assistant framing).
- DECISION-06: Closed commercial consoles are secondary/gated support targets, not current Tier-0. (INFERENCE; assistant-proposed working classification; not explicitly accepted or rejected).
- DECISION-07: Legacy consoles and retro systems are constrained/research/engine-only targets by default, not full Dominium parity targets. (INFERENCE; assistant-proposed working classification).
- DECISION-08: PC handhelds should map primarily to PC OS targets rather than become separate base platform families. (INFERENCE; assistant-proposed working classification).
- DECISION-09: Web/WASM is both a universal fallback and a Tier-0 support target. (FACT / INFERENCE; decided/inferred from latest user priority).
- DECISION-10: Use platform contracts/support matrix rather than an undifferentiated “support everything” claim. (INFERENCE; assistant-proposed; strongly implied by scope).
- DECISION-11: Closed console support must use official platform-holder paths for commercial/native support. (UNCERTAIN / UNVERIFIED; assistant-proposed constraint requiring external verification).
- DECISION-12: Do not bundle proprietary BIOS/firmware or rely on firmware redistribution for legacy support. (INFERENCE; assistant-proposed legal/safety constraint).

## Pending Tasks

- TASK-01: Create a formal Platform Support Matrix for Dominium.
- TASK-02: Define Tier-0 platform contracts.
- TASK-03: Define PC OS baselines.
- TASK-04: Define Android minimum API, ABI, graphics, and subdevice scope.
- TASK-05: Define iOS/iPadOS minimum OS/device baseline and Apple-family classification.
- TASK-06: Define Web/WASM/browser/PWA baseline.
- TASK-07: Create PC handheld profile.
- TASK-08: Define console Tier-1 strategy.
- TASK-09: Define legacy/retro target policy.
- TASK-10: Decide XR priority and runtime strategy.
- TASK-11: Choose or confirm engine/toolchain strategy.
- TASK-12: Confirm or retire the “Domino” engine/core name.

## Open Questions

- QUESTION-01: What exact target families are Tier-0 besides PC, Android, iOS, and Web?
- QUESTION-02: What minimum Android API level and ABI set will be supported?
- QUESTION-03: What minimum iOS/iPadOS version and device generations will be supported?
- QUESTION-04: What is the Web/browser baseline?
- QUESTION-05: Is WebGPU required, preferred, or optional, and is WebGL fallback mandatory?
- QUESTION-06: Which Windows versions and CPU architectures are supported?
- QUESTION-07: Which macOS versions and Mac architectures are supported?
- QUESTION-08: What Linux baseline is required?
- QUESTION-09: Are Android TV / Google TV first-class Tier-0 targets or secondary Android subtargets?
- QUESTION-10: Are tvOS, watchOS, and visionOS in scope, and at what tier?
- QUESTION-11: What engine/toolchain will Dominium use?
- QUESTION-12: Is “Domino” the real name for the engine/core layer?
- QUESTION-13: Is Steam Deck a named Tier-0 subtarget?
- QUESTION-14: Which current console generations are commercial targets?

## Files / Artifacts / Prompts to Preserve

- ARTIFACT-07: User comprehensive hardware/software target inventory.
- ARTIFACT-09: User’s decisive Android/iOS/Web top-tier statement.
- ARTIFACT-11: Previous Context Transfer Packet.
- ARTIFACT-13: This final generated report package.
- ARTIFACT-14: Prior citation IDs are non-portable and should not be relied on.

## What to Verify Before Acting

- VERIFY-01: Current official commercial console developer access requirements for PlayStation, Xbox, and Nintendo.
- VERIFY-02: Current PlayStation hardware/platform support status, including PS4/PS5/PS5 variants and PlayStation Portal role.
- VERIFY-03: Current Xbox One/Series development and compatibility model.
- VERIFY-04: Current Nintendo Switch/successor developer support and platform facts.
- VERIFY-05: Current Android SDK/NDK, Google Play target API, ABI, Android TV/Go/Automotive requirements.
- VERIFY-06: Current Apple SDK, App Store, iOS/iPadOS/macOS/tvOS/watchOS/visionOS submission and support requirements.
- VERIFY-07: Current WebGPU browser support and limitations.
- VERIFY-08: Current WebAssembly features needed for Dominium, including SIMD, threads, memory limits, filesystem/storage patterns.
- VERIFY-09: Steam Deck/SteamOS current developer guidance, Steam Deck Verified requirements, and Linux runtime assumptions.
- VERIFY-10: Feasibility of listed Apple devices: iPod Touch, Apple TV, Apple Watch, Vision Pro, Intel Mac, Apple Silicon Mac.
- VERIFY-11: Android TV, Google TV, Android Automotive, Chromebook Android compatibility, and vendor ROM constraints.
- VERIFY-12: Current OpenXR, WebXR, ARKit, ARCore, SteamVR, Meta, PlayStation VR, Windows Mixed Reality, and Pico runtime status.

## Best Next Step

Create the formal Platform Support Matrix. Start with Tier-0 PC, Android, iOS/iPadOS, and Web; then classify PC handhelds, consoles, XR, and legacy systems below that hierarchy unless the user explicitly changes priority.
