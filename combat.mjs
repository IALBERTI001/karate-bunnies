export const WIDTH=1000, ROUND_TIME=45;
export const MOVES={
 punch1:{animation:4,damage:7,reach:155,startup:.12,active:.12,recovery:.17,push:14},
 punch2:{animation:5,damage:8,reach:160,startup:.14,active:.12,recovery:.18,push:16},
 kick:{animation:6,damage:10,reach:185,startup:.18,active:.14,recovery:.23,push:24},
 spin:{animation:7,damage:13,reach:200,startup:.25,active:.14,recovery:.32,push:35},
 low:{animation:8,damage:9,reach:170,startup:.16,active:.14,recovery:.24,push:18},
 high:{animation:9,damage:12,reach:172,startup:.26,active:.13,recovery:.34,push:20,launch:true},
 front:{animation:10,damage:11,reach:193,startup:.22,active:.14,recovery:.30,push:115}
};
const clamp=(n,a,b)=>Math.max(a,Math.min(b,n));
export function fighter(x,facing){return {x,facing,hp:100,action:'idle',animation:0,time:0,stun:0,invuln:0,z:0,vz:0,combo:0,comboUntil:0,move:null,hit:false,hold:false,holdFacing:facing,selection:null,heldTime:0,guard:false,input:{left:false,right:false,up:false,down:false,guard:false}};}
export function createMatch({stage=1,online=false}={}){return {fighters:[fighter(350,1),fighter(650,-1)],stage,online,time:ROUND_TIME,clock:0,phase:'intro',intro:1.8,result:null,events:[],eventId:0,ai:{wait:.75,guard:0,seed:stage*123+17}};}
export function pushEvent(m,type,data={}){m.events.push({id:++m.eventId,type,...data});if(m.events.length>24)m.events.shift();}
function canAct(f){return f.hp>0&&f.stun<=0&&f.z<=0&&!f.move;}
function selectedDirection(f){const i=f.input;if(i.up&&!i.down&&!i.left&&!i.right)return 'high';if(i.down&&!i.up&&!i.left&&!i.right)return 'low';if(i.left!==i.right&&!i.up&&!i.down){const dir=i.right?1:-1;return dir===f.holdFacing?'front':'spin';}return null;}
export function input(m,index,event){const f=m.fighters[index];if(!f||m.phase!=='fight')return;const {type,key,value}=event;
 if(type==='reset'){f.input={left:false,right:false,up:false,down:false,guard:false};f.hold=false;f.selection=null;f.guard=false;return;}
 if(type==='direction'&&['left','right','up','down','guard'].includes(key)){f.input[key]=!!value;if(key==='guard'&&value){f.hold=false;f.selection=null;}if(f.hold){const d=selectedDirection(f);if(d)f.selection=d;}return;}
 if(type==='attackDown'&&canAct(f)&&!f.input.guard&&!f.hold){f.hold=true;f.holdFacing=f.facing;f.selection=null;f.heldTime=0;const d=selectedDirection(f);if(d)f.selection=d;return;}
 if(type==='attackCancel'){f.hold=false;f.selection=null;return;}
 if(type==='attackUp'&&f.hold){const selected=f.selection;f.hold=false;f.selection=null;if(!canAct(f)||f.input.guard)return;let move=selected;if(!move){if(m.clock>f.comboUntil)f.combo=0;move=['punch1','punch2','kick','spin'][f.combo];f.combo=(f.combo+1)%4;f.comboUntil=m.clock+1.05;}else{f.combo=0;f.comboUntil=0;}f.chained=!selected;startMove(f,move);pushEvent(m,'swing',{fighter:index,move});}
}
function startMove(f,name){f.move=name;f.action='attack';f.animation=MOVES[name].animation;f.time=0;f.hit=false;f.guard=false;}
function random(m){m.ai.seed=(Math.imul(m.ai.seed,1664525)+1013904223)>>>0;return m.ai.seed/4294967296;}
export function updateAI(m,dt){if(m.phase!=='fight')return;const f=m.fighters[1],p=m.fighters[0],d=clamp((m.stage-1)/19,0,1);m.ai.wait-=dt;m.ai.guard-=dt;if(!canAct(f))return;
 if(m.ai.guard>0){input(m,1,{type:'direction',key:'guard',value:true});return;}
 if(m.ai.wait>0)return;
 f.input.guard=false;f.input.left=false;f.input.right=false;
 const gap=Math.abs(f.x-p.x);if(gap>148){f.input[p.x<f.x?'left':'right']=true;m.ai.wait=.10;return;}
 const r=random(m);if(p.move&&r<.28+d*.25){m.ai.guard=.18+random(m)*.25;m.ai.wait=.2;return;}
 if(r<.15){f.input[p.x<f.x?'right':'left']=true;m.ai.wait=.15;return;}
 const choice=random(m);if(choice<.25+d*.2){const special=['low','high','front','spin'][Math.floor(random(m)*4)];f.hold=true;f.selection=special;input(m,1,{type:'attackUp'});}else{input(m,1,{type:'attackDown'});input(m,1,{type:'attackUp'});}
 m.ai.wait=.35+(1-d)*.5+random(m)*.4;
}
export function step(m,dt,{ai=true}={}){dt=clamp(dt,0,.05);if(m.phase==='done'){for(const f of m.fighters)f.time+=dt;return;}m.clock+=dt;
 if(m.phase==='intro'){for(const f of m.fighters)f.time+=dt;m.intro=Math.max(0,m.intro-dt);if(m.intro===0){m.phase='fight';for(const f of m.fighters){f.animation=0;f.time=0;}pushEvent(m,'start');}return;}
 if(ai)updateAI(m,dt);m.time=Math.max(0,m.time-dt);
 for(const f of m.fighters){f.time+=dt;f.invuln=Math.max(0,f.invuln-dt);f.stun=Math.max(0,f.stun-dt);if(f.hold)f.heldTime+=dt;
  if(f.z>0||f.vz>0){f.z+=f.vz*dt;f.vz-=920*dt;f.animation=13;f.action='airborne';if(f.z<=0){f.z=0;f.vz=0;f.stun=.25;f.invuln=Math.max(f.invuln,.5);f.animation=14;f.time=0;f.action='landing';pushEvent(m,'land',{x:f.x});}continue;}
  if(f.move){const mv=MOVES[f.move];if(f.time>=mv.startup+mv.active+mv.recovery){f.move=null;f.action='idle';f.time=0;}continue;}
  if(f.stun>0)continue;
  const wasGuard=f.guard;f.guard=!!f.input.guard&&!f.hold;
  if(wasGuard&&!f.guard){f.stun=.09;f.animation=3;continue;}
  if(f.guard){f.action='guard';f.animation=3;continue;}
  const direction=Number(f.input.right)-Number(f.input.left);if(direction&&!f.hold){f.x=clamp(f.x+direction*230*dt,90,910);f.action='walk';f.animation=direction===f.facing?1:2;}else{f.action=f.hold?'hold':'idle';f.animation=0;}
 }
 const [a,b]=m.fighters;const gap=b.x-a.x;if(Math.abs(gap)<140){const sign=gap>=0?1:-1,mid=(a.x+b.x)/2;a.x=clamp(mid-70*sign,90,910);b.x=clamp(mid+70*sign,90,910);}
 for(let i=0;i<2;i++){const f=m.fighters[i],o=m.fighters[1-i];if(!f.move&&!f.hold)f.facing=o.x>=f.x?1:-1;}
 // Collect contacts before resolving them so simultaneous clean hits can trade.
 const contacts=[];for(let i=0;i<2;i++){const f=m.fighters[i],o=m.fighters[1-i],mv=MOVES[f.move];if(mv&&!f.hit&&f.time>=mv.startup&&f.time<=mv.startup+mv.active&&o.invuln<=0&&o.z<10&&Math.abs(f.x-o.x)<=mv.reach&&(o.x-f.x)*f.facing>0){f.hit=true;contacts.push({i,mv});}}
 for(const {i,mv} of contacts){const f=m.fighters[i],o=m.fighters[1-i];if(o.guard&&o.facing===-f.facing){o.x=clamp(o.x+f.facing*12,90,910);pushEvent(m,'block',{fighter:1-i,x:o.x});}else{o.hp=Math.max(0,o.hp-mv.damage);o.x=clamp(o.x+f.facing*mv.push,90,910);o.move=null;o.hold=false;o.selection=null;o.guard=false;o.combo=0;o.invuln=.50;o.stun=.46;o.time=0;o.animation=mv.push>50?12:11;o.action='hit';if(mv.launch){o.vz=410;o.z=1;o.stun=.5;o.animation=13;}pushEvent(m,'hit',{fighter:1-i,x:o.x,damage:mv.damage,launch:!!mv.launch,move:f.move,chain:!!f.chained&&f.move==='spin'});}}
 if(a.hp<=0||b.hp<=0||m.time<=0){m.phase='done';m.result=a.hp===b.hp?'draw':a.hp>b.hp?'player':'opponent';for(let i=0;i<2;i++){const f=m.fighters[i];f.move=null;f.hold=false;f.z=0;f.animation=m.result==='draw'?15:((m.result==='player')===(i===0)?16:17);f.time=0;}pushEvent(m,'finish',{result:m.result});}
}
