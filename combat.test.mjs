import test from 'node:test';import assert from 'node:assert/strict';
import {createMatch,input,step,MOVES} from './combat.mjs';import {STAGES,loadProgress,clearStage,validSkin} from './campaign.mjs';
function ready(){const m=createMatch();m.phase='fight';m.fighters[0].x=440;m.fighters[1].x=550;return m;}
function run(m,t){for(let i=0;i<Math.ceil(t*60);i++)step(m,1/60,{ai:false});}
function attack(m,key,index=0){input(m,index,{type:'attackDown'});if(key)input(m,index,{type:'direction',key,value:true});input(m,index,{type:'attackUp'});if(key)input(m,index,{type:'direction',key,value:false});}
for(const [key,name]of [['down','low'],['up','high'],['right','front'],['left','spin']])test(`Hold Attack plus ${key} produces ${name} and only fires on release`,()=>{const m=ready();input(m,0,{type:'attackDown'});input(m,0,{type:'direction',key,value:true});run(m,.1);assert.equal(m.fighters[0].move,null);input(m,0,{type:'attackUp'});assert.equal(m.fighters[0].move,name);});
 test('Forward/back use the captured facing on either side',()=>{const m=ready();m.fighters[0].x=600;m.fighters[1].x=450;m.fighters[0].facing=-1;attack(m,'left');assert.equal(m.fighters[0].move,'front');});
 test('High kick launches then landing protection prevents air loops',()=>{const m=ready();attack(m,'up');run(m,.4);assert.ok(m.fighters[1].z>0);assert.ok(m.fighters[1].hp<100);run(m,.9);assert.equal(m.fighters[1].z,0);assert.ok(m.fighters[1].invuln>0);});
 test('Front kick knocks back more than a punch',()=>{const a=ready(),b=ready();attack(a,'right');attack(b);run(a,.4);run(b,.4);assert.ok(a.fighters[1].x-b.fighters[1].x>60);});
 test('Guard blocks launch and damage',()=>{const m=ready();input(m,1,{type:'direction',key:'guard',value:true});run(m,.05);attack(m,'up');run(m,.5);assert.equal(m.fighters[1].hp,100);assert.equal(m.fighters[1].z,0);assert.ok(m.events.some(e=>e.type==='block'));});
 test('Tap combo advances punch punch kick spin; holding does not auto-fire',()=>{const m=ready();m.fighters[1].x=850;for(const move of ['punch1','punch2','kick','spin']){attack(m);assert.equal(m.fighters[0].move,move);const v=MOVES[move];run(m,v.startup+v.active+v.recovery+.03);}input(m,0,{type:'attackDown'});run(m,2);assert.equal(m.fighters[0].move,null);});
 test('Interrupted holds and reset do not release a stored attack',()=>{const m=ready();input(m,0,{type:'attackDown'});input(m,0,{type:'direction',key:'up',value:true});input(m,0,{type:'reset'});input(m,0,{type:'attackUp'});assert.equal(m.fighters[0].move,null);});
 test('Time expiry and equal health produce a draw',()=>{const m=ready();m.time=.01;run(m,.1);assert.equal(m.phase,'done');assert.equal(m.result,'draw');});
 test('Simultaneous attacks resolve as a trade',()=>{const m=ready();attack(m,null,0);attack(m,null,1);run(m,.2);assert.equal(m.fighters[0].hp,93);assert.equal(m.fighters[1].hp,93);});
 test('Campaign has twenty unique arenas and a strictly increasing audience',()=>{assert.equal(STAGES.length,20);assert.equal(new Set(STAGES.map(s=>s.art+'/'+s.panel)).size,20);assert.equal(STAGES[0].fans,2);assert.equal(STAGES[19].name,'The Great Bunny Bowl');for(let i=1;i<20;i++)assert.ok(STAGES[i].fans>STAGES[i-1].fans);});
 test('Progress only unlocks the next fight and cannot skip stages',()=>{let p=loadProgress(null);assert.equal(p.unlocked,1);p=clearStage(p,20);assert.equal(p.unlocked,1);for(let n=1;n<=20;n++)p=clearStage(p,n);assert.equal(p.unlocked,20);assert.equal(p.cleared.length,20);assert.deepEqual(loadProgress({cleared:[1,1,2,20,-1,'3']}),{cleared:[1,2],unlocked:3});assert.deepEqual(loadProgress('garbage'),{cleared:[],unlocked:1});});
 test('Invalid saved customizations fall back safely',()=>{assert.deepEqual(validSkin({fur:'unknown',gi:'unknown'}),{fur:'White',gi:'Coral'});assert.deepEqual(validSkin({fur:'Gray',gi:'Black'}),{fur:'Gray',gi:'Black'});});

test('A clean punch keeps the full hit reaction visible and prevents an immediate action',()=>{const m=ready();attack(m);run(m,.14);const target=m.fighters[1];assert.equal(target.action,'hit');assert.equal(target.animation,11);input(m,1,{type:'attackDown'});input(m,1,{type:'attackUp'});assert.equal(target.move,null);run(m,.32);assert.equal(target.action,'hit');assert.equal(target.animation,11);assert.ok(target.time>=.3);run(m,.18);assert.equal(target.action,'idle');assert.equal(target.animation,0);});

test('Grounded fighter bodies keep enough space to avoid drawing over one another',()=>{const m=ready();run(m,.02);assert.ok(Math.abs(m.fighters[1].x-m.fighters[0].x)>=140);attack(m);run(m,.2);assert.ok(m.fighters[1].hp<100);});

test('hit events name the move and mark a spin that finishes the tap chain', () => {
  const chain = ready(); const seen = [];
  for (let k = 0; k < 4; k++) { attack(chain, null); run(chain, 0.75); chain.fighters[1].x = 550; chain.fighters[0].x = 440; }
  for (const e of chain.events) if (e.type === 'hit') seen.push([e.move, e.chain]);
  assert.ok(seen.some(([m, c]) => m === 'spin' && c === true), JSON.stringify(seen));
  const direct = ready(); attack(direct, 'left'); run(direct, 0.8);
  const hit = direct.events.find(e => e.type === 'hit');
  assert.equal(hit?.move, 'spin'); assert.equal(hit.chain, false);
});

test('lesson mode: clock holds, nobody can be knocked out, partner only punches when asked', () => {
  const m = ready(); m.lesson = { mode: 'idle' }; m.stage = 1;
  for (let k = 0; k < 30; k++) { attack(m, 'right'); run(m, 0.7); m.fighters[0].x = 440; m.fighters[1].x = 550; }
  assert.equal(m.time, 45); assert.equal(m.phase, 'fight'); assert.ok(m.fighters[1].hp >= 35);
  assert.equal(m.events.filter(e => e.type === 'swing' && e.fighter === 1).length, 0, 'idle partner never attacks');
  const j = ready(); j.lesson = { mode: 'jab' }; step(j, 1/60);
  for (let i = 0; i < 60 * 5; i++) step(j, 1/60);
  const jabs = j.events.filter(e => e.type === 'swing' && e.fighter === 1);
  assert.ok(jabs.length >= 2 && jabs.every(e => e.move === 'punch1'), JSON.stringify(jabs));
  assert.ok(j.fighters[0].hp >= 35);
  j.lesson = null; for (let i = 0; i < 60; i++) step(j, 1/60); assert.ok(j.time < 45, 'clock runs after the lesson');
});

test('swing events say whether the move came from the tap chain', () => {
  const m = ready(); attack(m, null); const tap = m.events.find(e => e.type === 'swing');
  assert.equal(tap.chain, true); run(m, 0.8); attack(m, 'up');
  assert.equal(m.events.filter(e => e.type === 'swing').at(-1).chain, false);
});
