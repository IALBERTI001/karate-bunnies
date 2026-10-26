# Browser game design preferences

Apply these user preferences to future game work in this workspace.

- The entire game is one self-contained game screen, suitable for embedding in any hosting page or browser.
- All navigation, settings, arena selection, fighter selection, customization, matchmaking, pause menus, and results belong inside that game screen. Do not build website navigation, external customization pages, or marketing-style UI around the game.
- Start with an animated title screen with the game menu overlaid on the scene.
- Solo flow: Fight or Story → Select arena → Select and customize fighter → confirm fighter → randomize/reveal opponent → Start Fight.
- Keep opponent randomization after player fighter selection. Online VS must find a real opponent, not disguise AI as another player.
- Use responsive in-game HUD and controls for phone, tablet, and desktop. The host page must not be needed to operate the game.
- Karate Bunnies uses the intended bunny sprites, colored gi with matching headbands, black belts, and bare paws. Keep every stage of the experience cute and alive.
- Round results should celebrate within the visible arena with integrated HUD actions; avoid website-style popup cards and blurred backdrops. Touch controls must retain usable hit areas independently of canvas scaling.
- Use one consistent illustrated game theme across every screen. Arena selection is a scene of destinations, fighter selection is a stage, and settings/matchmaking use integrated HUD treatment. Do not surround these screens with a large bordered, rounded, opaque or blurred panel; do not use website-style image cards.
- Spectators must be designed into the arena with correct perspective, physical seating or ground contact, occlusion, and matching light. Never scatter scaled-down fighter sprites over scenery, vegetation, railings, or empty air to simulate a crowd.
- Before returning game changes, perform a design review as well as functional checks. Visually inspect the changed screens and representative phone, tablet, and desktop layouts; assess composition, perspective, grounding, animation continuity, readable HUD, usable touch targets, combat feedback, and coherent navigation. Exercise a complete player flow, cancellation/pause/resume, and relevant failure states. Fix evident defects before delivery. A passing script or absence of console errors does not establish visual quality. Record known limitations honestly and do not claim physical-device validation from emulation.

- Game text must remain readable on phones: use at least 14 CSS pixels for visible text and generally 16 pixels for explanatory copy. Do not shrink labels to fit; reflow or allow scrolling inside the game. Check computed font sizes across every screen and visually inspect compact layouts before returning changes.
