# Karate Bunnies design review

Reviewed 2026-10-25. This is a record of evidence and remaining work, not a claim of release readiness.

## Delivery standard

Every change needs both functional verification and visual inspection of its affected screens. Review composition, cute character appeal, consistent materials and typography, perspective, floor contact, silhouettes, readable action feedback, and continuity between screens. Review motion in context; a sprite sheet alone does not prove animation quality. Do not return visibly broken work simply because tests pass.

Keep the complete experience inside the game. Exercise title → arena → customization → opponent reveal → fight → result, plus back navigation, settings, pause/resume, input cancellation, save behavior, and relevant network failure states. Check portrait, landscape, tablet, desktop, and embedded-host constraints. Never confuse emulated input with physical-device testing.

## This pass

- Visually inspected arena selection, fighter selection, fight result on phone, and the 72-pose contact sheet. Complete ears and poses remain visible. Added contact shadows to fighter previews and inspected the resulting selection screen.
- Arena, fighter, settings, and matchmaking theme checks passed: scene wrappers remain transparent, without website card containers. Desktop screenshots refreshed after the preview change.
- Complete playable fight reached a defeat result. The recovery pose, result heading, retry, and arena-selection actions stayed inside the game. This run did not establish campaign difficulty or a full human campaign victory.
- Embedded-host flow and pause containment passed at 320×568, 844×390, and the script's embedded host configuration.
- Layout measurements passed at 320×568, 360×640, 390×844, 430×932, 768×1024, 1024×768, and 844×390. No measured control overlap or page scrolling. Direction targets are 48–56 CSS pixels; default action targets are 64–88 pixels.
- Two-finger hold, Up-to-Down thumb slide, and release passed at 320, 390, and 768 widths. An initial run failed its fixed-delay hint assertion under concurrent browser load; a separate rerun passed. Replaced fixed delays with waits for game state and hint updates, then reran the full seven-size script successfully. This does not prove all timing or hardware cases.
- 32 automated tests passed across combat, sprite bounds, audience/camera rendering, and authoritative online pairing. Coverage includes special releases, guard, launches, interruption, simultaneous hits, sequential unlocks, silhouette margins, and token rejection.
- Prior audience correction includes visual inspection of the revised environment atlases and representative desktop/phone scenes. Fans are in the environment painting, with no miniature fighter crowd layer.

## Open quality gates

- Physical Android/iPhone/tablet input, Safari rendering, browser chrome and safe-area behavior, and mobile audio interruptions need device validation.
- Sustained performance, memory use, thermal behavior, network latency/loss, and load need measured budgets and profiling.
- Four poses per action and first-pass synthesized audio remain art/audio polish limitations. Human playtesting must judge anticipation, contact timing, recovery clarity, sound appeal, and fatigue.
- Full human campaign progression and difficulty curve have not been validated. Automated combat correctness does not establish fun or fairness.
- Failure-state coverage is incomplete: reconnect, long search cancellation, restricted storage, and graphics-context loss deserve a dedicated pass before release.

Use these open gates to guide subsequent work. Resolve or clearly report material limitations; do not silently label the game production ready.
