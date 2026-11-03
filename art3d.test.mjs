// The Blender puppet art set (?art=3d) must stay a drop-in for the painted sprites.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
const json=f=>JSON.parse(readFileSync(new URL('assets/'+f,import.meta.url)));

test('3d set has the same animations, speeds and order as the painted set',()=>{
  const base=json('animations.json'),set=json('animations-3d.json');
  assert.deepEqual(set.animations.map(a=>[a.name,a.fps,a.loop]),base.animations.map(a=>[a.name,a.fps,a.loop]));
  for(const a of set.animations){const at=set.atlases[a.atlas];assert.ok(at,a.name);assert.ok(a.startFrame+4<=at.columns*at.rows,a.name+' fits its atlas');}
});

test('3d set ships every sheet and mask the renderer loads',()=>{
  const set=json('animations-3d.json');
  set.atlases.forEach((a,i)=>{for(const f of [a.file,`belt-soft-3d-${i}.png`,`gi-parts-3d-${i}.png`])assert.ok(existsSync(new URL('assets/'+f,import.meta.url)),f);assert.equal(a.passes,true);});
  assert.equal(json('gi-anchors-3d.json').length,set.atlases.length);
  assert.ok(set.atlases.some(a=>a.turnaround),'shop turnaround');
});

test('fight sheets share one standing reference frame so fighters keep one size',()=>{
  const set=json('animations-3d.json');
  set.atlases.filter(a=>!a.turnaround).forEach((a,i)=>assert.ok(set.animations.every(n=>n.atlas!==i||n.startFrame>=1),'cell 0 is the reference pose'));
});
