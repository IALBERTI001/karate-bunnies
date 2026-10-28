// First-fight lesson (preview: ?tutorial=v1). One move at a time; each step ticks off from a real move.
// say = [coach, line] (6 words or fewer). glow = controls to highlight: attack, guard, up, down,
// forward, back (forward/back resolve against the bunny's facing). mode = what Mochi does meanwhile.
export const LESSON = [
  { id: 'tap',   say: ['hazel',   'Tap Attack to punch!'],                 glow: ['attack'],            keys: 'Tap J',                       done: e => e.type === 'swing' && e.move === 'punch1' },
  { id: 'chain', say: ['bramble', 'Keep tapping: punch, punch, kick, spin!'], glow: ['attack'],         keys: 'Tap J four times',            done: e => e.type === 'swing' && e.move === 'spin' && e.chain },
  { id: 'guard', say: ['hazel',   'Hold Guard to block Mochi!'],           glow: ['guard'], mode: 'jab', keys: 'Hold K',                     done: e => e.type === 'block' && e.fighter === 0 },
  { id: 'high',  say: ['bramble', 'Hold Attack, press Up, let go!'],       glow: ['attack', 'up'],      keys: 'Hold J, press W, let go',     done: e => e.type === 'swing' && e.move === 'high' },
  { id: 'front', say: ['bramble', 'Hold Attack, press Forward, let go!'],  glow: ['attack', 'forward'], keys: 'Hold J, press toward Mochi',  done: e => e.type === 'swing' && e.move === 'front' },
  { id: 'low',   say: ['hazel',   'Hold Attack, press Down, let go!'],     glow: ['attack', 'down'],    keys: 'Hold J, press S, let go',     done: e => e.type === 'swing' && e.move === 'low' },
  { id: 'spin',  say: ['hazel',   'Hold Attack, press Back, let go!'],     glow: ['attack', 'back'],    keys: 'Hold J, press away from Mochi', done: e => e.type === 'swing' && e.move === 'spin' && !e.chain }
];
export const CHEERS = ['Yes!', 'Lovely!', 'Great job!', 'Perfect!', 'Wonderful!'];
export const LESSON_END = ['hazel', 'You’re ready, little one!'];

// Only the player's own swings and blocks count.
export function stepDone(step, e) { return !!step && (e.type !== 'swing' || e.fighter === 0) && step.done(e); }

export function glowTargets(step, facing = 1) {
  const fwd = facing > 0 ? 'right' : 'left', back = fwd === 'right' ? 'left' : 'right';
  return (step?.glow ?? []).map(g => g === 'attack' ? '#attack' : g === 'guard' ? '#guard'
    : `.dir[data-dir="${g === 'forward' ? fwd : g === 'back' ? back : g}"]`);
}
