# Karate Bunnies

A playable browser fighting game with a twenty-fight campaign, original bunny artwork, selectable fur and gi colors, touch and keyboard controls, and real two-player matchmaking on the included server.

## Run

From this directory with Node.js 22 or later:

    node server.mjs

Open http://127.0.0.1:8787. The server has no third-party dependencies. PORT changes its port; HOST changes the bind address. To play across devices on a trusted local network, set HOST to 0.0.0.0 and use the computer's LAN address on the phone. The preview URL on localhost only works on the computer running the server.

This repository contains the standalone Karate Bunnies game.

## Build

    node build.mjs

The dist directory contains the static game and artwork. All twenty campaign fights, settings, and customization work on a static host. Online VS requires the Node server and same-origin /api routes. For the full game deploy this source directory as a Node service; start server.mjs. GitHub stores the source; running a public game URL requires a separate hosting deployment.

## Play

The animated title screen contains Fight / Story, VS Search, and Settings. All menus, overlays, controls, and results stay inside the same game container; the host page provides no required game controls. Fight / Story opens arena selection, followed by fighter selection and customization. Confirming the fighter randomizes and reveals the solo opponent; Start Fight then enters the arena. Win a bout to unlock the next arena; won stages can be replayed. The twenty-fight journey starts with two coaches in a rabbit-hole dojo, passes through gardens, village venues, and mountain tournaments, and ends with 2,400 spectators in the Ultimate Bunny Arena. All twenty locations have distinct paintings. Progress, appearance, and settings save in local browser storage.

On fighter selection, combine white, cream, gray, or tan fur with coral, mint, lavender, sky blue, purple, pink, or black gi. The headband matches the gi; the belt stays black and the paws remain bare. Appearance is cosmetic.

Move with A/D or left/right arrows. Tap J or the Attack button for punch, punch, kick, spinning kick. Hold K or Guard to block. For directional kicks, hold Attack, choose one direction with the four-way pad or WASD/arrows, then release Attack:

- Down: low kick.
- Up: high head kick; a clean hit launches the opponent.
- Forward: front chest kick; a clean hit knocks back.
- Back: spinning kick.

Forward/back are relative to the opponent. While Attack is held, directions select a move instead of moving the bunny. Direction selection is retained until release. Guard, interrupted holds, and focus loss cancel queued holds. Basic movement is horizontal; up/down do not jump. Escape pauses solo; settings and loss of focus cannot pause online matches.

A/G can abbreviate action labels; they are not implied key bindings. The current keyboard bindings are identified separately in Settings and under the desktop action buttons.

## Online VS

Open the game in two browser sessions, choose VS Search, select and confirm a fighter, then enter VS Search from the fighter screen in both sessions. Matchmaking pairs real players, never AI stand-ins. Combat runs at a fixed 60 Hz on the server. Clients submit validated input commands and receive authoritative snapshots. Both players must accept a rematch. Canceling search removes the session; disconnects end the bout and a disconnect before the opening bow aborts it. No accounts or ranked ladder are included.

The server stores live queues and matches in memory. A restart ends online sessions; campaign saves remain in the browser. Production hosting needs a persistent running process and same-origin API routing. Cross-region latency, real iOS/Safari devices, and public-load behavior have not been verified.

## Verification

    node --test combat.test.mjs sprite-bounds.test.mjs audience-render.test.mjs
    node --test server.test.mjs
    node check-balance.mjs

The server integration test requires server.mjs to be running on port 8787 (or set KB_TEST_URL). It verifies pairing, independent appearance, authoritative launching kicks, and invalid-token rejection. Combat tests cover directional releases, captured facing, guarding, launches, knockback, combo order, canceled holds, simultaneous hits, time expiry, and sequential unlocks. The balance script verifies one deterministic policy can win every stage; it does not establish final human difficulty.

Browser QA used Chromium through Microsoft Edge at desktop and 390 by 844 mobile viewports, including real multi-touch event delivery, solo pause, stage-one victory and next-stage navigation, customization, and paired online sessions. Layout screenshots are internal QA outputs. A real phone and Safari pass remain to be done.

## Art and animation

Arena paintings were made with the built-in image generator using the approved bunny character sheet as the style reference. Five 2 by 2 sheets provide twenty distinct locations, stored as optimized WebP files; the campaign manifest selects a quadrant. All audiences are integrated into the arena paintings. Coaches sit on stools; fans occupy benches, steps, balconies, and spectator tiers. Contact shadows, rail occlusion, and distance scaling are authored in the artwork. No fighter sprites are stamped over the environment to represent spectators. Displayed stadium audience sizes are narrative attendance figures rather than individually counted painted characters. All audience counts increase from one stage to the next.

The intended bunny atlases contain eighteen actions at four poses per action. Whole-atlas connected-component bounds preserve ears crossing nominal grid boundaries, and per-pose masks exclude neighboring fragments. A padded replacement atlas repairs the idle and forward-walk ear tips; a runtime material-color shader separates gi and headband from fur. This is a first animation pass: registration, pose continuity, material-mask quality, final combat balance, and timing deserve further art and human playtesting before a public release. The build uses these bunny sprites throughout; no placeholder fighters are substituted.

## Persistent game presentation rule

The workspace AGENTS.md records the user preference for future games: everything happens within the game screen. No external website navigation or separate customization pages. Use an animated title menu, in-game arena selection, in-game fighter customization, opponent reveal after confirmation, and an explicit Start Fight action.

## In arena results and touch measurements

Round results retain the visible arena and bunny celebration/recovery poses. The result heading overlays the arena; next-arena, replay, and menu actions occupy the bottom HUD. No popup card or backdrop blur is used for results. Pause and settings use a transparent in-game overlay rather than a website card.

Touch controls use pixel sizes independent of canvas scaling. Each phone direction target is 48 by 48 CSS pixels, increasing to 56 by 56 on tablets. Attack and Guard range from 64 to 88 pixels in the measured default layouts; the larger-control setting raises action sizes to 68 through 100 pixels. The movement pad supports sliding a held thumb between directions, a neutral center, pointer cancellation, and simultaneous Attack/Guard touches.

qa-touch-layouts.cjs measured 320 by 568, 360 by 640, 390 by 844, 430 by 932, 768 by 1024, 1024 by 768, and 844 by 390. Normal and larger controls fit without overlap or document scrolling in all seven. Multi-touch hold, Up-to-Down thumb slide, and release were exercised at 320, 390, and 768 widths through Chromium CDP touch events. touch-layout-results.json contains the measured bounds. These are emulated browser tests, not real iOS, Android, or tablet hardware results.

qa-result-ui.cjs injects a controlled result into its test browser only, to verify victory presentation, absence of a dialog, result-button bounds at 320 pixels, and next-stage navigation. It does not add a cheat API to the production game. qa-playthrough.cjs exercises a normal playable fight to a result.

## Unified scene presentation

Arena selection presents four gold-framed destination markers directly over the chapter environment, connected by a path. There is no opaque, rounded, bordered, blurred container or cream image-card list. The backdrop changes with the selected chapter. Fighter selection stages the bunnies directly in the environment, with gi selection and fight actions in the bottom HUD. Settings and matchmaking use the same open-scene presentation. Title buttons, fight HUD, results, settings controls, and start cues share the warm wood, gold, and moss-green palette. qa-theme.cjs verifies scene wrappers are transparent and unbordered and captures the garden chapter at the reported 1126 by 790 viewport.

## Spectator placement correction

The procedural drawCrowd layer has been removed completely. Only the two combatants use independently rendered bunny sprites. Four revised 2 by 2 audience atlases cover the first sixteen arenas; the final four use the existing stadium audience painting. The scene remains empty in front for combat. Audience attendance labels are narrative campaign figures rather than a literal count of painted characters.

Background geometry and fighters share a uniform world-camera transform. Portrait view must not enlarge the background audience independently of the fighters. Camera fitting leaves a full silhouette margin for both fighters, including near arena boundaries. Audience-render tests verify that no extra sprite actors are introduced and that both fighters fit the phone camera.

Prompt provenance for the audience edits is recorded in audience-art-prompts.json. Browser scene captures and qa-audiences.cjs cover underground, garden, village, tournament, and championship settings in desktop and phone layouts.

Five portrait atlases extend all twenty environments upward with painted ceilings, canopy, or sky. They preserve the arena floor and audience perspective without stretching the landscape artwork or filling the screen with a blurred duplicate. The renderer uses measured panel boundaries to keep adjacent paintings out of view. Portrait edit prompts are recorded in portrait-art-prompts.json.

## Result readability and arena framing

Results use a single Victory, Defeat, Draw, or Champion label on a solid dark full-width arena banner. Narrative eyebrow and explanatory result copy have been removed. The arena canvas fits the available viewport aspect ratio; the background uses the painting’s full horizontal overscan so edge camera movement does not reveal empty strips. Portrait and landscape still share uniform world scaling. qa-result-framing.cjs exercises the bright village arena with both fighters at the left boundary, plus 320-pixel result actions.

## Typography baseline

Visible game text uses a 14 CSS pixel minimum; explanatory copy is generally 16 pixels. Compact arena and settings screens can scroll within the game instead of shrinking text. qa-typography.cjs checks nine screens at five viewports (320×568 through desktop and phone landscape), records computed-size violations in typography-audit.json, and verifies no host-page overflow. This checks font size, not a guarantee of physical-device readability. Internal menu scrolling is intentional; older scripts that require every menu action to remain in the initial viewport need that expectation updated.

## Carrot rewards

Each new fight victory pays one carrot, including campaign replays and online wins. Losses and draws pay none. The result guard prevents repeated finish processing from paying twice. The local balance is saved separately from campaign unlocks in kb-carrots-v1 and shown on the title, arena selection, and victory result. Rewards start with wins after this feature is installed; historical replay wins cannot be reconstructed. This is a browser-local reward balance, not an account-backed economy. qa-carrots.cjs verifies win/replay payouts, duplicate suppression, loss/draw behavior, persistence, and menu display.

## Clone and optional browser checks

    git clone https://github.com/IALBERTI001/karate-bunnies.git
    cd karate-bunnies
    node server.mjs

This is a private repository. Authenticate with an authorized GitHub account to clone it. Runtime and core tests need no dependency installation.

For browser and image-analysis tools, install development dependencies with `npm install`, then install the test browser with `npx playwright install chromium`. Keep the game server running in another terminal and run `node qa-typography.cjs` or `node qa-carrots.cjs`. To use an installed Microsoft Edge instead, set `KB_BROWSER_CHANNEL=msedge` in your shell. Browser captures are ignored by Git. Original art reprocessing scripts require `KB_ART_SOURCE_DIR`; all finished runtime assets are already included.

Campaign progress, customization, settings, and carrots are saved per browser. Pushing the code to GitHub does not synchronize those saves between devices. Online rooms are held in server memory.

## Story scenes preview (`?story=v1`)

Open http://127.0.0.1:8787/?story=v1 to preview the story campaign. Without the flag the approved game is unchanged.

- Before each fight, 2 short lines play in a dialogue box that takes over the bottom HUD band, so the arena and both bunnies stay visible. The fight clock, the bow and all inputs wait until the scene ends.
- After a win, 2 lines play while the VICTORY banner shows; after a loss, one encouraging coach line. Result actions return when the scene ends.
- Tap anywhere in the band, press Attack, Enter, Space or J to continue; Skip ends the scene. Pause still works during a scene.
- Every line is 6 words or fewer (enforced by story.test.mjs). Each character speaks in the approved "Blips" voice at their own pitch, played through the Sound effects volume. Reduced motion shows text at once.
- Story mode reveals the stage's own character (Mochi, Pip … Grandmaster Bun) after fighter confirmation instead of a random opponent. This changes approved behaviour and stays behind the flag until approved.

Script and cast live in story.mjs. `node qa-story.cjs` (server running) covers the flow, the held clock, Attack/Enter/tap/Skip, pause during a scene, win and loss scenes, layouts at 390×844, 768×1024, 844×390 and 1280×800, and the flag-off game.

### Belts (story preview)

In story mode the hero's belt shows her rank: White to start, Yellow after stage 4, Green after 8, Brown after 12, and the original Black belt after winning stage 20. The belt changes on the coach's award line after the winning fight (Skip still awards it), with sparkles and a chime. Opponents and online VS keep black belts. Fighter selection names the current belt.

Belts are recoloured with per-atlas masks in assets/belt-mask-<n>.png, built by `node prepare-belt-masks.mjs [--preview <dir>]` (needs the sharp dev dependency) from belt-mask.mjs. The mask finds dark regions bordered by the gi (thick bands, or very dark patches partly hidden by a limb) and keeps a 1px outline, so eyes and outlines are untouched. All 72 poses were inspected in the preview.

## Phone landscape fix

At short landscape sizes the themed control band had been painted solid over the arena and hid the fighters below the shoulders. The band is now transparent there, as the landscape layout intended; the d-pad and buttons keep their solid faces. Inspected at 667×375, 844×390 and 932×430; qa-touch-layouts.cjs passes.

## Big-moment celebrations preview (`?fx=v1`)

Open http://127.0.0.1:8787/?fx=v1 (combine with `&story=v1`). Solo fights only; online VS is unchanged.

- Hit-stop: the fight freezes for 0.05 s on a hit and 0.11 s on a launch, knockback or chain finisher (halved with Reduced motion).
- Word pops above the opponent when your bunny lands a launch (Wheee! / Up you go!), a front-kick knockback (Pow! / Boom!) or a spin that finishes the tap chain (Combo! / Hi-yah!), at most one every 0.8 s, with a two-note chime. They are drawn on the arena canvas at 24 CSS pixels or larger and hold still with Reduced motion.
- KO slow motion: a winning knockout plays at 35% speed for 0.9 s before the result (off with Reduced motion).

Hit events now include `move` and `chain` so effects can tell moves apart. `node qa-fx.cjs` (server running) lands each move in a real browser fight and checks the pops, hit-stop, KO slow-mo, Reduced motion and the flag-off game.
