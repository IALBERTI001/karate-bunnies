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

## Story scenes pass (2026-10-27, preview flag)

- Visually inspected pre-fight, win and loss scenes at 390×844, 1280×800, 768×1024 and 844×390. First placement inside the arena hid both bunnies on phones and was clipped in phone landscape; moved the dialogue into the bottom HUD band and re-inspected. "A friendly bow." no longer shows behind a scene.
- qa-story.cjs passed; existing result, carrot, theme and typography scripts pass with the flag off. Blip voice confirmed scheduled through the effects channel in Chromium; not listened to on a device.
- Found, not fixed (approved layout): in phone landscape (844×390) the controls band covers the fighters below the shoulders during normal fights.

## Belts and landscape pass (2026-10-27)

- Phone landscape: control band no longer hides the fighters (approved fix). Inspected at three landscape sizes; story bubble in landscape now floats over the floor and touches the fighters' feet only.
- Belt masks inspected on every pose in all three atlases after three rounds of fixes (side-view belts missed, a hidden-belt frame missed, outline specks). Belt colours inspected on six fur/gi combinations; first shading was too dark (white read grey) and was brightened.
- Brown belt on a black gi is the lowest-contrast combination; readable but quiet.

## Celebrations pass (2026-10-27, ?fx=v1)

- Inspected launch, knockback, chain and KO captures on desktop and a phone with Reduced motion. Pops sit above the opponent and stay inside the arena.
- Feel is not established: hit-stop length, word frequency and slow-mo duration need a human playtest on a real phone.

## Round 3 (2026-10-27): defaults, red belt, lesson, on-screen buttons

- Story, belts and celebrations on by default after approval. Red belt inspected on four gi colours.
- Lesson inspected at phone, phone landscape and desktop. First phone placement covered the arena title and Pause; the card is now placed from the header layout and centred between title and Pause when there is room.
- Found and fixed a regression from round 1: a story CSS edit had added gap:12px to the global button rule (arena cards 24px taller).
- On-screen buttons: PC fight inspected with buttons hidden; the first version made the arena jump when dialogue started, so dialogue now floats over the floor in that mode.
- Test-machine limits: software rendering in the test browser slows timed taps and screenshots of the pause blur on the larger hidden-buttons arena; the lesson, effects and typography scripts run with buttons shown, and qa-buttons covers hidden mode. Measured 56–60 fps in both modes at 1239×869.

## Open quality gates

- Physical Android/iPhone/tablet input, Safari rendering, browser chrome and safe-area behavior, and mobile audio interruptions need device validation.
- Sustained performance, memory use, thermal behavior, network latency/loss, and load need measured budgets and profiling.
- Four poses per action and first-pass synthesized audio remain art/audio polish limitations. Human playtesting must judge anticipation, contact timing, recovery clarity, sound appeal, and fatigue.
- Full human campaign progression and difficulty curve have not been validated. Automated combat correctness does not establish fun or fairness.
- Failure-state coverage is incomplete: reconnect, long search cancellation, restricted storage, and graphics-context loss deserve a dedicated pass before release.

Use these open gates to guide subsequent work. Resolve or clearly report material limitations; do not silently label the game production ready.

## Gi shop sample (2026-10-30)

- Added an open-scene fitting room inside the game, linked from the title and fighter selection. Six cloth previews and an animated bunny share the existing environment and gold/wood palette. Five prints cost 10 carrots; Raiders Football costs 100. Plain colors remain free.
- Inspected the actual local build at desktop, 390×844, 320×568, 768×1024, and 844×390. Phone and short-landscape shop content intentionally scrolls inside the game. At 320 pixels the catalog reflows to two columns; text measurements found no shop/header text below 14 CSS pixels and no page horizontal overflow. Tablet grid spacing was tightened after inspection.
- Verified insufficient-funds controls on a fresh wallet, a 10-carrot purchase (150→140), Raiders purchase (140→40), disabled repeat purchase, free switching to an owned outfit, switching back to plain, reload persistence, and return from wardrobe to the selected arena's fighter setup. Seed credits were only disposable localhost QA data; the game does not grant store-test currency.
- Exercised title→arena→fighter→confirm/reveal→story→combat→pause/resume→defeat→main menu wearing Raiders. Outfit and headband stayed on the bunny; fur, bare paws and the white rank belt remained visible. The prints use the existing per-pixel gi material mask, without replacing sprites. The small football crest is a sample fan design and is less readable at combat scale than in the shop swatch.
- 56 unit tests passed, static build passed, and the server pairing/authoritative-combat test passed with a Raiders design in player appearance. Storage-failure unit tests cover canonical-save refusal and a failed legacy mirror. Browser checks used the in-app desktop browser and emulated viewport sizes; no physical mobile device, mobile touch hardware or Safari validation is claimed.
- Existing release quality gates above still apply. Inventory and carrots remain browser-local, rather than an account-backed economy.

## Glitter cuties expansion (2026-10-30)

- Added Strawberry Sugar, Cloud Cuddle, Honey Hug, Lavender Lullaby, Rainbow Ribbon and Fairy Floss. Individually drawn berry, cloud/rainbow, teddy, sleepy moon, bow and fairy-wing prints include pearly flecks, small hearts and four-point glints. All twelve shop outfits now cost 10 carrots, superseding the initial Raiders price.
- Added two six-outfit collection selectors to preserve a browsable rack. Visually inspected all six on the animated bunny, plus the shop at desktop, 390×844 phone and 768×1024 tablet. Phone shop scrolling stays inside the game; measured shop text remained at least 14 CSS pixels with no horizontal page overflow.
- Soft cloth highlights are masked to gi material and applied before the belt mask. Eight cached phases limit shimmer variation within the existing bounded cache. Reduced Motion freezes the shimmer in menus and combat; two separated captures of the still fitting-room bunny matched byte for byte. Glitter does not introduce a screen-wide particle effect.
- Verified a new Strawberry Sugar purchase deducted exactly 10 (40→30), preserved existing ownership, and appeared in fighter selection, story and a playable fight. Exercised attack and pause/resume wearing the new print. A fresh zero-wallet preview also correctly disabled purchasing. No physical mobile or Safari validation is claimed.
- 58 unit tests and static build passed. Multiplayer integration passed with Raiders and Fairy Floss appearances. New tests cover all twelve prices, six glitter flags, bounded/reduced-motion phases, finite motif painting and balanced canvas state. Existing device/performance/release gates remain open.

## Continuous shop browsing (2026-10-30)

- Replaced the two collection selectors with one scrolling rack containing all twelve outfits, following user preference. Taller desktop/tablet layouts keep the fitting-room preview beside the rack; selecting an outfit preserves the rack's scroll position there. Compact layouts keep normal internal page scrolling.
- Verified all twelve buttons exist together, scrolled to the final rows and selected Lavender Lullaby with the preview still visible, and inspected the phone layout at 390×844 with no horizontal page overflow. Static build and syntax/diff checks passed. Purchases and outfit rendering were unchanged.

## Category dropdown (2026-10-30)

- Added a compact, labelled native Category dropdown above the scrolling rack: All gis (default), Glitter cuties, Original favorites. It replaces category buttons without removing the full scrolling browse experience. Changing categories keeps a valid preview and retains the filter through selecting/equipping an outfit; reopening the shop starts with All gis.
- Browser checks confirmed 12→6→6→12 items across the choices. Inspected desktop and 390×844 phone; the select is 44 CSS pixels high with no page horizontal overflow. Static build, syntax and diff checks passed. Prices, inventory and rendering were unchanged.

- Theme refinement: dropdown labels are All Gi, Glitter Collection, Sports Collection and Original Favorites. Collection membership is explicit in each catalog entry, so future themes can be added without changing the filter logic. Raiders is in Sports, the six glitter designs in Glitter, and the five other originals in Original Favorites. Catalog filtering tests and build passed; presentation uses the same inspected native dropdown.

## Las Vegas sports expansion (2026-10-30)

- Sports now has eleven regional team outfits: Golden Knights, Silver Knights, Aces, Aviators, Vegas-bound Athletics, UNLV Runnin’ Rebels, Lights FC, Knight Hawks, Desert Dogs, Thrill and the existing Raiders. Ten new outfits bring the full shop to 22, all priced at 10 carrots. Golden Knights is first in the Sports rack, with gold cloth, charcoal bands, red piping, hockey sticks and knight-visored fan crests.
- Added original vector jersey prints for hockey, basketball, baseball, football, soccer, lacrosse and volleyball. Sports masks retain the same bare paws, fur and rank belts. Inspected all Sports swatches plus Golden/Silver Knights, Aces, Aviators and Athletics on the actual bunny. Verified the eleven-item filter on desktop, 390×844 phone and 768×1024 tablet; phone measurements found no horizontal page overflow or text below 14 CSS pixels. Native dropdown and scrolling behavior remain unchanged.
- 61 unit tests, static build and authoritative multiplayer test passed. Coverage buys/saves/re-equips all eleven Sports outfits and verifies Golden Knights/Aces appearances survive matchmaking. Existing inventory IDs and saves are preserved. README records official team references and the Athletics' planned 2028 ballpark; no fictional Las Vegas NBA team is introduced. This is a curated major regional/college set, not an exhaustive amateur/school-team directory.
- No new physical-device, Safari, sustained-performance or human campaign-difficulty validation is claimed. New sports prints use the previously exercised purchase, story, combat and result flow; the browser preview checks did not fund or change the user's current wallet.

## Customize Bunny and Owned (2026-10-30)

- Renamed the title-menu entry, fighter-selection entry and fitting-room heading to Customize Bunny. Added Owned to the Category dropdown; it receives the purchased ID list and excludes unowned designs. An empty wardrobe shows a plain bunny, a clear message and Browse all gis, with no purchase button in the empty view.
- Verified a populated six-outfit Owned view against the existing local wardrobe, and an isolated empty wardrobe on localhost without changing the user's saved purchases. Browse all gis restored all 22 designs. Inspected desktop and a confirmed 390×844 viewport: heading reflows, category select fits, and no horizontal page overflow. No physical-device validation is claimed.
- 62 unit tests and static build passed, including empty/malformed ownership lists and purchased-only filtering. Existing purchases and currency remain unchanged by browsing.

- Deployment follow-up: a live-browser verification found cached unversioned modules still showing Gi Shop after Pages completed deployment. Added content-derived release query strings to the entry script, stylesheet and complete browser import graph. `refresh-assets.mjs --check` now runs in the test command to catch stale release URLs before publishing. The release helper normalizes line endings for consistent Windows/Linux hashes. All 62 unit tests and static build pass with the versioned imports.

## Halloween collection — 2026-10-31

Integrated six Halloween gi into the latest Customize Bunny shop, preserving existing original, sports, glitter, Owned filtering, ten-carrot pricing, lesson, story, and rank-belt behavior. An initial implementation based on an old local checkout was retained on codex/halloween-initial and was not pushed; final work extends current origin/main instead. Used the existing material-masked cloth-print renderer. Reviewed all six shop previews and the eighteen-action contact sheet, plus phone shop views. Fixed the shop heading clipping on small portrait screens. Browser checks verify purchase/equip/reload, retention of existing owned items, insufficient funds and storage-failure behavior, responsive containment, font sizes, and 1728 fur/outfit/frame renders. Earlier wardrobe/balance tests remain in place. No physical hardware validation is claimed.
