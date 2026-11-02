// CrazyGames QA step 2: a brand-new player (cleared storage) at 1280x720 (or W/H), about 2 s of thinking per action.
// Logs timestamps for load, first action, first hit, first word pop, lesson end, first story fight hit, plus the
// number of words on screen in each captured frame. Usage: B=<url> OUT=<dir> node tools/qa/new-player-run.cjs
let playwright;try{playwright=require('playwright');}catch{playwright=require('/opt/npm-tools/node_modules/playwright');}
const fs=require('fs');const B=process.env.B||'http://127.0.0.1:8792/';const OUT=process.env.OUT||'qa-new-player';fs.mkdirSync(OUT,{recursive:true});
const W=+process.env.W||1280,H=+process.env.H||720,THINK=+process.env.THINK||2000;
const hooks=`\nglobalThis.__np={events:[],state:()=>({phase:match?.phase,step:lesson?.step??null,mode:modeState.mode,view,ohp:match?.fighters?.[1]?.hp,pops:pops.length})};
(()=>{const o=fxHit;fxHit=function(e){__np.events.push({t:performance.now(),type:'hit',move:e.move,fighter:e.fighter});return o.apply(this,arguments);};})();`;
const words=()=>{let n=0;const seen=[];for(const el of document.querySelectorAll('#app *')){const own=[...el.childNodes].filter(c=>c.nodeType===3).map(c=>c.textContent).join(' ').trim();if(!own)continue;const r=el.getBoundingClientRect();if(r.width<2||r.height<2||r.bottom<0||r.top>innerHeight)continue;const s=getComputedStyle(el);if(s.visibility==='hidden'||s.display==='none'||+s.opacity===0)continue;const w=own.split(/\s+/).filter(x=>/[A-Za-z0-9]/.test(x));n+=w.length;seen.push(own.slice(0,40));}return {n,seen};};
(async()=>{const b=await playwright.chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required']});
 const p=await b.newPage({viewport:{width:W,height:H}});p.setDefaultTimeout(90000);const log=[];const t0=Date.now();const T=()=>((Date.now()-t0)/1000).toFixed(1);
 await p.route('**/main.mjs*',async r=>{const f=await r.fetch();await r.fulfill({response:f,body:(await f.text())+hooks});});
 const frame=async(name,note='')=>{const w=await p.evaluate(words);await p.screenshot({path:`${OUT}/${String(log.length).padStart(2,'0')}-${name}.png`});log.push({t:+T(),name,words:w.n,note,text:w.seen.slice(0,12)});};
 const think=()=>p.waitForTimeout(THINK);
 const st=()=>p.evaluate(()=>__np.state());
 await p.goto(B);await p.locator('#start-training,#fight').first().waitFor();await frame('load');
 await think();await p.locator('#start-training').click();const tAction=T();
 await p.waitForFunction(()=>__np.state().step===0,null,{timeout:60000});await frame('lesson-step-1');
 // Step 1: tap attack until the step ticks; note the first hit.
 const key=async(k,hold)=>{await p.keyboard.down('j');if(hold){await p.waitForTimeout(80);await p.keyboard.down(hold);await p.waitForTimeout(80);}else await p.waitForTimeout(60);await p.keyboard.up('j');if(hold)await p.keyboard.up(hold);};
 const until=async(n,act)=>{for(let i=0;i<10;i++){if((await st()).step>=n)return true;await act();await p.waitForTimeout(800);}return (await st()).step>=n;};
 await think();await key();await p.waitForTimeout(400);await frame('first-tap');
 await until(1,()=>key());await think();
 await until(2,async()=>{for(let k=0;k<4;k++){await key();await p.waitForTimeout(550);}});await frame('chain');
 await think();await p.keyboard.down('k');await p.waitForFunction(()=>__np.state().step>=3,null,{timeout:30000}).catch(()=>{});await p.keyboard.up('k');
 await think();await until(4,()=>key(0,'w'));await p.waitForTimeout(200);await frame('high-kick');
 await think();await until(5,()=>key(0,'ArrowRight'));await think();await until(6,()=>key(0,'s'));await think();await until(7,()=>key(0,'ArrowLeft'));
 await p.locator('#lesson-menu').waitFor({timeout:30000}).catch(()=>{});await frame('lesson-end');
 await think();if(await p.locator('#lesson-menu').count())await p.locator('#lesson-menu').click();await p.locator('#fight').waitFor();await frame('main-menu');
 await think();await p.locator('#fight').click();await frame('arenas');await think();await p.locator('[data-stage="1"]').click();await frame('fighter');await think();await p.locator('#confirm-fighter').click();await think();await p.locator('#begin').click();
 await p.locator('.story-bubble').waitFor();await p.waitForTimeout(800);await frame('story-before');await think();
 while(await p.locator('.story-scene').count()){await p.keyboard.press('Enter');await p.waitForTimeout(900);}
 await p.waitForFunction(()=>__np.state().phase==='fight',null,{timeout:60000});await frame('stage1-fight');
 for(let i=0;i<12&&(await st()).phase==='fight';i++){await key();await p.waitForTimeout(450);}await frame('stage1-mid');
 const ev=await p.evaluate(()=>__np.events.map(e=>({t:e.t,type:e.type,move:e.move,fighter:e.fighter})));const nav0=await p.evaluate(()=>performance.timeOrigin);
 const firstHit=ev.find(e=>e.fighter===1);console.log(JSON.stringify({firstAction:tAction,firstPlayerHitSecFromLoad:firstHit?+((firstHit.t)/1000).toFixed(1):null,playerHits:ev.filter(e=>e.fighter===1).length,frames:log},null,1));await b.close();})().catch(e=>{console.error(e);process.exit(1);});
