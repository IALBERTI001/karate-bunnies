// Training lesson (first launch and Replay training). One move at a time; each step ticks off from a real move.
// say = [coach, line] (6 words or fewer) for touch buttons; kbd = the same line naming keyboard keys. glow = controls to highlight: attack, guard, up, down,
// forward, back (forward/back resolve against the bunny's facing). mode = what Mochi does meanwhile.
export const LESSON = [
  { id: 'tap', kbd: 'Press J to punch!',   say: ['hazel',   'Tap Attack to punch!'],                 glow: ['attack'],            keys: 'Tap J',                       done: e => e.type === 'swing' && e.move === 'punch1' },
  { id: 'chain', kbd: 'Keep pressing J: punch, kick, spin!', say: ['bramble', 'Keep tapping: punch, punch, kick, spin!'], glow: ['attack'],         keys: 'Tap J four times',            done: e => e.type === 'swing' && e.move === 'spin' && e.chain },
  { id: 'guard', kbd: 'Hold K to block Mochi!', say: ['hazel',   'Hold Guard to block Mochi!'],           glow: ['guard'], mode: 'jab', keys: 'Hold K',                     done: e => e.type === 'block' && e.fighter === 0 },
  { id: 'high', kbd: 'Hold J, press W, let go!',  say: ['bramble', 'Hold Attack, press Up, let go!'],       glow: ['attack', 'up'],      keys: 'Hold J, press W, let go',     done: e => e.type === 'swing' && e.move === 'high' },
  { id: 'front', kbd: 'Hold J, press toward Mochi, let go!', say: ['bramble', 'Hold Attack, press Forward, let go!'],  glow: ['attack', 'forward'], keys: 'Hold J, press toward Mochi',  done: e => e.type === 'swing' && e.move === 'front' },
  { id: 'low', kbd: 'Hold J, press S, let go!',   say: ['hazel',   'Hold Attack, press Down, let go!'],     glow: ['attack', 'down'],    keys: 'Hold J, press S, let go',     done: e => e.type === 'swing' && e.move === 'low' },
  { id: 'spin', kbd: 'Hold J, press away, let go!',  say: ['hazel',   'Hold Attack, press Back, let go!'],     glow: ['attack', 'back'],    keys: 'Hold J, press away from Mochi', done: e => e.type === 'swing' && e.move === 'spin' && !e.chain }
];
export const CHEERS = ['Yes!', 'Lovely!', 'Great job!', 'Perfect!', 'Wonderful!'];
export const LESSON_END = ['hazel', 'You’re ready, little one!'];
// Last beat: a real knockout. Mochi's health floor is lifted and one more hit wins.
export const LESSON_KO = { say: ['bramble', 'Now knock Mochi down!'], kbd: 'Finish it: press J!', tap: 'Finish it: tap Attack!' };
export const LESSON_REWARD = 3; // carrots, once, for finishing training

// Only the player's own swings and blocks count.
export function stepDone(step, e) { return !!step && (e.type !== 'swing' || e.fighter === 0) && step.done(e); }

export function glowTargets(step, facing = 1) {
  const fwd = facing > 0 ? 'right' : 'left', back = fwd === 'right' ? 'left' : 'right';
  return (step?.glow ?? []).map(g => g === 'attack' ? '#attack' : g === 'guard' ? '#guard'
    : `.dir[data-dir="${g === 'forward' ? fwd : g === 'back' ? back : g}"]`);
}
