// Dojo theme: a gentle 16-bar loop (about 38 s at 100 BPM) made in code, so it stays tiny and works offline.
// Lead melody on a soft triangle, warm chord pads, a round bass; C major pentatonic so it stays cute and calm.
export const BPM = 100, BEAT = 60 / BPM, BAR = BEAT * 4, BARS = 16;
const N = n => 440 * 2 ** ((n - 69) / 12); // MIDI note -> Hz
// Chords per bar (MIDI roots and triads): C Am F G | C Em F G | Am F C G | F G C C
const CHORDS = [[48,[60,64,67]],[45,[57,60,64]],[41,[57,60,65]],[43,[55,59,62]],
                [48,[60,64,67]],[40,[55,59,64]],[41,[57,60,65]],[43,[55,59,62]],
                [45,[57,60,64]],[41,[57,60,65]],[48,[55,60,64]],[43,[55,59,62]],
                [41,[57,60,65]],[43,[55,59,62]],[48,[60,64,67]],[48,[60,64,67]]];
// Melody: [bar, beat, MIDI note, length in beats]; rests are simply gaps.
const MELODY = [
  [0,0,72,1],[0,1,74,.5],[0,1.5,76,1.5],[0,3,79,1],
  [1,0,76,1],[1,1,74,1],[1,2,72,2],
  [2,0,69,1],[2,1,72,1],[2,2,74,1],[2,3,76,1],
  [3,0,74,3],
  [4,0,79,1],[4,1,76,.5],[4,1.5,74,.5],[4,2,76,2],
  [5,0,79,1],[5,1,81,1],[5,2,79,2],
  [6,0,77,1],[6,1,76,1],[6,2,74,1],[6,3,72,1],
  [7,0,74,2],[7,2,67,2],
  [8,0,69,1],[8,1,72,1],[8,2,76,1.5],[8,3.5,74,.5],
  [9,0,72,1],[9,1,69,1],[9,2,72,2],
  [10,0,76,1],[10,1,79,1],[10,2,81,1],[10,3,79,1],
  [11,0,76,2],[11,2,74,2],
  [12,0,72,1],[12,1,74,1],[12,2,76,1],[12,3,77,1],
  [13,0,79,1.5],[13,1.5,76,.5],[13,2,74,2],
  [14,0,76,1],[14,1,74,1],[14,2,72,1],[14,3,67,1],
  [15,0,72,3]
];
/** Every note in one loop: {t (s from loop start), f (Hz), d (s), v (0..1), kind: 'lead'|'pad'|'bass'}. */
export function musicScore() {
  const out = [];
  for (const [bar, beat, n, len] of MELODY) out.push({ t: bar * BAR + beat * BEAT, f: N(n), d: len * BEAT * .92, v: .55, kind: 'lead' });
  CHORDS.forEach(([root, triad], bar) => {
    for (const n of triad) out.push({ t: bar * BAR, f: N(n), d: BAR * .98, v: .16, kind: 'pad' });
    out.push({ t: bar * BAR, f: N(root), d: BEAT * 1.6, v: .5, kind: 'bass' });
    out.push({ t: bar * BAR + 2 * BEAT, f: N(root + 7), d: BEAT * 1.4, v: .38, kind: 'bass' });
  });
  return out.sort((a, b) => a.t - b.t);
}
export const LOOP = BARS * BAR;

/** Schedules the loop a little ahead of time on an AudioContext; returns {stop}. */
export function startMusic(ctx, destination, { lookahead = 0.6, tick = 200, isPaused = () => false } = {}) {
  const score = musicScore();
  let loopStart = ctx.currentTime + 0.1, idx = 0, stopped = false;
  const voice = (ev, at) => {
    const o = ctx.createOscillator(), g = ctx.createGain();
    o.type = ev.kind === 'lead' ? 'triangle' : 'sine'; o.frequency.setValueAtTime(ev.f, at);
    const peak = ev.v, attack = ev.kind === 'pad' ? 0.25 : 0.02, end = at + ev.d;
    g.gain.setValueAtTime(0.0001, at); g.gain.exponentialRampToValueAtTime(peak, at + attack);
    g.gain.setValueAtTime(peak, Math.max(at + attack, end - (ev.kind === 'pad' ? 0.4 : 0.12)));
    g.gain.exponentialRampToValueAtTime(0.0001, end);
    o.connect(g); g.connect(destination); o.start(at); o.stop(end + 0.05);
  };
  const timer = setInterval(() => {
    if (stopped) return;
    if (isPaused()) { loopStart = ctx.currentTime + 0.1; idx = 0; return; } // restart cleanly after a pause
    const horizon = ctx.currentTime + lookahead;
    while (true) {
      if (idx >= score.length) { idx = 0; loopStart += LOOP; }
      const ev = score[idx], at = loopStart + ev.t;
      if (at > horizon) break;
      if (at >= ctx.currentTime - 0.05) voice(ev, at);
      idx++;
    }
  }, tick);
  return { stop() { stopped = true; clearInterval(timer); } };
}
