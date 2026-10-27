// Story scenes for the 20-stage campaign (preview: ?story=v1).
// Lines stay at 6 words or fewer; the blip voice carries the feeling.
export const MAX_WORDS = 6;

// pitch = base blip frequency in Hz (the approved "Blips" style from the voice sampler).
export const CAST = {
  bunny:   { name: 'Bunny',           color: '#c96b62', pitch: 620 },
  hazel:   { name: 'Coach Hazel',     color: '#5f8a52', pitch: 330 },
  bramble: { name: 'Coach Bramble',   color: '#b97a24', pitch: 250 },
  mochi:   { name: 'Mochi',           color: '#5f9a84', pitch: 540 },
  pip:     { name: 'Pip',             color: '#4f86b8', pitch: 700 },
  pebble:  { name: 'Pebble',          color: '#7d7480', pitch: 360 },
  clover:  { name: 'Clover',          color: '#7a55b0', pitch: 560 },
  dew:     { name: 'Dew',             color: '#6f7fb8', pitch: 600 },
  nibbles: { name: 'Nibbles',         color: '#c6603f', pitch: 420 },
  petal:   { name: 'Petal',           color: '#c75d95', pitch: 660 },
  luna:    { name: 'Luna',            color: '#4f7fb0', pitch: 500 },
  buttons: { name: 'Buttons',         color: '#7a55b0', pitch: 450 },
  poppy:   { name: 'Poppy',           color: '#4f8a5f', pitch: 640 },
  ripple:  { name: 'Ripple',          color: '#c0584f', pitch: 380 },
  jasmine: { name: 'Jasmine',         color: '#3d3a46', pitch: 520 },
  nimbus:  { name: 'Nimbus'       ,   color: '#4f7fb0', pitch: 220 },
  maple:   { name: 'Maple',           color: '#c75d95', pitch: 480 },
  snowdrop:{ name: 'Snowdrop',        color: '#7a55b0', pitch: 680 },
  sunny:   { name: 'Sunny',           color: '#4f8a5f', pitch: 580 },
  velvet:  { name: 'Velvet',          color: '#3d3a46', pitch: 340 },
  nova:    { name: 'Nova',            color: '#8a6fc0', pitch: 600 },
  ember:   { name: 'Ember',           color: '#d0553f', pitch: 470 },
  grand:   { name: 'Grandmaster Bun', color: '#6a4aa0', pitch: 190 }
};

// Per stage: the opponent's cast key, lines before the fight, lines after a win.
export const SCRIPT = [
  { opp: 'mochi',   before: [['hazel', 'Paws up, little one. Breathe.'], ['bunny', 'Okay… I can do this!']],
                    win:    [['bunny', 'I did it! Friends, Mochi?'], ['mochi', 'Best friends! Again tomorrow?']] },
  { opp: 'pip',     before: [['pip', 'Heard you’re new. Show me!'], ['bunny', 'My knees are wobbly…']],
                    win:    [['pip', 'Wow, quick paws! Teach me?'], ['bunny', 'Let’s practice together!']] },
  { opp: 'pebble',  before: [['pebble', 'My guard never breaks.'], ['bramble', 'Kick low, little bunny!']],
                    win:    [['bunny', 'I found the gap!'], ['pebble', 'Clever! Come back soon.']] },
  { opp: 'clover',  before: [['bunny', 'Daylight! It’s so bright!'], ['clover', 'Ready for the big world?']],
                    win:    [['clover', 'You belong out here.'], ['bunny', 'Gardens, here I come!']] },
  { opp: 'dew',     before: [['dew', 'Morning! Mind the dewdrops.'], ['bunny', 'My first garden fight!']],
                    win:    [['ember', 'Lucky hop. You won’t last.'], ['bunny', 'Who was that?']] },
  { opp: 'nibbles', before: [['nibbles', 'Win, and carrots are yours!'], ['bunny', 'Carrots? Let’s go!']],
                    win:    [['nibbles', 'Fair and square. Enjoy!'], ['mochi', 'That’s my best friend!']] },
  { opp: 'petal',   before: [['petal', 'Even petals fall gracefully.'], ['bunny', 'I’ll be graceful too.']],
                    win:    [['petal', 'Your kindness shows. Friends?'], ['bunny', 'Always!']] },
  { opp: 'luna',    before: [['luna', 'Fireflies came to watch you.'], ['bunny', 'I’m not scared anymore.']],
                    win:    [['ember', 'Still here? Hmph. Village next.'], ['bunny', 'See you there, Ember!']] },
  { opp: 'buttons', before: [['buttons', 'The whole square knows you!'], ['bunny', 'The village came… for me?']],
                    win:    [['bunny', 'Thank you, everyone!'], ['buttons', 'Come visit the market!']] },
  { opp: 'poppy',   before: [['poppy', 'Festival champion? Not today!'], ['bunny', 'Let’s give them a show!']],
                    win:    [['poppy', 'Best festival ever!'], ['pip', 'We cheered the loudest!']] },
  { opp: 'ripple',  before: [['ripple', 'My kicks push like rivers.'], ['hazel', 'Guard, then strike back.']],
                    win:    [['bunny', 'I stood my ground!'], ['ripple', 'Steady as a willow.']] },
  { opp: 'jasmine', before: [['jasmine', 'Tea after? Fight first.'], ['bunny', 'Deal! Best of luck!']],
                    win:    [['jasmine', 'The mountains are calling you.'], ['ember', 'Mountains are no garden, bunny.']] },
  { opp: 'nimbus',  before: [['nimbus', 'Strength is calm, little one.'], ['bunny', 'I’ll stay calm. Promise.']],
                    win:    [['nimbus', 'You listened. Now you’re strong.'], ['bunny', 'Thank you, Master Nimbus!']] },
  { opp: 'maple',   before: [['maple', 'Leaves fall. So will you!'], ['bunny', 'Not today, Maple!']],
                    win:    [['maple', 'Okay, okay. You’re good!'], ['bunny', 'You were too!']] },
  { opp: 'snowdrop',before: [['snowdrop', 'Cold paws? Warm heart?'], ['bunny', 'My friends keep me warm.']],
                    win:    [['snowdrop', 'Your fire beat my frost.'], ['clover', 'Snowpaws champion! Woohoo!']] },
  { opp: 'sunny',   before: [['sunny', 'The whole city’s watching!'], ['bunny', 'Then let’s make them smile!']],
                    win:    [['sunny', 'The grand arenas await!'], ['bramble', 'We’re so proud of you.']] },
  { opp: 'velvet',  before: [['bunny', 'So big… deep breath.'], ['velvet', 'Your first grand arena. Bow!']],
                    win:    [['velvet', 'You earned this stage.'], ['mochi', 'From our dojo to here!']] },
  { opp: 'nova',    before: [['nova', 'Under the lights, we shine.'], ['bunny', 'Let’s both shine bright!']],
                    win:    [['nova', 'You shine brightest tonight.'], ['bunny', 'One more step…']] },
  { opp: 'ember',   before: [['ember', 'You actually made it here.'], ['bunny', 'Thanks to my friends.']],
                    win:    [['ember', 'You win. Friends… maybe?'], ['bunny', 'Friends, Ember. Always.']] },
  { opp: 'grand',   before: [['grand', 'Show me how far you came.'], ['bunny', 'All the way from the roots!']],
                    win:    [['grand', 'Champion. The crowd is yours.'], ['bunny', 'For everyone who believed in me!']] }
];

export const LOSS = [['hazel', 'Shake it off. Try again!'], ['bramble', 'Every champion falls sometimes.'], ['hazel', 'Breathe. You’ve got this.']];

export const wordCount = text => text.trim().split(/\s+/).filter(w => /[\p{L}\p{N}]/u.test(w)).length;

// moment: 'before' | 'win' | 'loss'. Returns [{key,name,color,pitch,text,side}] where side is
// 'player' (the hero), 'opponent' (the stage's fighter) or 'aside' (coach / friend off screen).
export function storyLines(stageId, moment, pick = Math.random) {
  const s = SCRIPT[stageId - 1];
  if (!s) return [];
  const raw = moment === 'loss' ? [LOSS[Math.floor(pick() * LOSS.length) % LOSS.length]] : (s[moment] ?? []);
  return raw.map(([key, text]) => ({ key, ...CAST[key], text, side: key === 'bunny' ? 'player' : key === s.opp ? 'opponent' : 'aside' }));
}

export const opponentName = stageId => CAST[SCRIPT[stageId - 1]?.opp]?.name;

// One blip per vowel group; a word ending in . ! ? … , adds a pause; a question rises at its end.
export const BLIP = { gap: 0.075, length: 0.06, pause: 0.18, gain: 0.09, multiplier: 1.6 };
export function blipSchedule(text, pitch) {
  const out = []; let t = 0;
  for (const word of text.toLowerCase().split(/\s+/).filter(Boolean)) {
    const groups = word.match(/[aeiouy]+/g) || (/[\p{L}\p{N}]/u.test(word) ? ['a'] : []);
    const end = /[.!?…,]$/.test(word), rise = /\?$/.test(word);
    groups.forEach((_, i) => {
      const last = i === groups.length - 1;
      out.push({ at: t, freq: pitch * BLIP.multiplier * (rise && last ? 1.35 : 1) });
      t += BLIP.gap + (last && end ? BLIP.pause : 0);
    });
  }
  return { blips: out, duration: t };
}
