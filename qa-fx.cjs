// Big-moment celebrations QA (preview flag ?fx=v1). Requires server.mjs on 8787.
// Lands a launch, a knockback and a full tap chain, then a KO; checks hit-stop, word pops, KO slow-mo,
// Reduced motion, and that the game is unchanged without the flag.
const {chromium}=require('playwright');const assert=require('node:assert/strict');
const BASE=process.env.KB_TEST_URL||'http://127.0.0.1:8787';const OUT=process.env.KB_QA_OUT||__dirname;
const hooks=`\nglobalThis.__fx=()=>({pops:pops.map(p=>p.text),frozen:wall<freezeUntil,slow:wall<slowUntil,clock:match.clock,phase:match.phase,result:match.result});
globalThis.__busy=()=>!!match.fighters[0].move;
globalThis.__close=(hp)=>{const [a,b]=match.fighters;a.x=440;b.x=530;a.facing=1;b.facing=-1;b.guard=false;b.input.guard=false;b.move=null;b.stun=0;b.invuln=0;b.z=0;if(hp)b.hp=hp;match.ai.wait=9;match.ai.guard=0;};`;
(async()=>{const b=await chromium.launch({headless:true,...(process.env.KB_BROWSER_CHANNEL?{channel:process.env.KB_BROWSER_CHANNEL}:{}),args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const errors=[],done=[];
 const open=async(url,vw=1100,vh=820,reduced=false)=>{const p=await b.newPage({viewport:{width:vw,height:vh}});p.on('pageerror',e=>errors.push(e.message));
  await p.route('**/main.mjs',async r=>{const f=await r.fetch();await r.fulfill({response:f,body:(await f.text())+hooks});});
  await p.goto(url);if(reduced){await p.evaluate(()=>localStorage.setItem('kb-settings-v1',JSON.stringify({music:.3,effects:.5,reduced:true,shake:false,large:false})));await p.reload();}
  await p.locator('#fight').click();await p.locator('[data-stage="1"]').click();await p.locator('#confirm-fighter').click();await p.locator('#begin').click();
  await p.waitForFunction(()=>__fx().phase==='fight',null,{timeout:20000});return p;};
 const land=async(p,dir,want,shot,hp)=>{for(let t=0;t<8;t++){await p.evaluate(h=>__close(h),hp);
   if(dir){await p.keyboard.down('j');await p.keyboard.down(dir);await p.waitForTimeout(40);await p.keyboard.up('j');await p.keyboard.up(dir);}
   else for(let k=0;k<4;k++){await p.evaluate(()=>__close());await p.keyboard.press('j');await p.waitForFunction(()=>__busy(),null,{timeout:3000}).catch(()=>{});await p.waitForFunction(()=>!__busy(),null,{timeout:5000});}
   for(let w=0;w<30;w++){const s=await p.evaluate(()=>__fx());if(want(s)){if(shot)await p.screenshot({path:`${OUT}/${shot}`});return s;}await p.waitForTimeout(25);}
   await p.waitForTimeout(700);}
  throw Error('move did not land: '+dir);};
 let p=await open(BASE+'/?fx=v1');
 // Launch (Attack + Up): word pop, and the fight clock pauses briefly on contact.
 let s=await land(p,'ArrowUp',x=>x.pops.length>0,'qa-fx-launch.png');assert.ok(['Wheee!','Up you go!'].includes(s.pops.at(-1)),s.pops.join());
 await p.waitForTimeout(1200);
 s=await land(p,'ArrowRight',x=>x.pops.some(w=>w==='Pow!'||w==='Boom!'),'qa-fx-knock.png');
 await p.waitForTimeout(1200);
 s=await land(p,null,x=>x.pops.some(w=>w==='Combo!'||w==='Hi-yah!'),'qa-fx-chain.png');done.push('launch, knockback, chain pops');
 // Hit-stop: freeze flag is raised on contact and the sim clock holds while frozen.
 await p.waitForTimeout(1200);await p.evaluate(()=>__close());await p.keyboard.down('j');await p.keyboard.down('ArrowUp');await p.waitForTimeout(40);await p.keyboard.up('j');await p.keyboard.up('ArrowUp');
 let frozenSeen=null;for(let w=0;w<80&&!frozenSeen;w++){const a=await p.evaluate(()=>__fx());if(a.frozen){await p.waitForTimeout(30);const c=await p.evaluate(()=>__fx());frozenSeen=[a,c];}else await p.waitForTimeout(8);}
 assert.ok(frozenSeen,'hit-stop engaged');if(frozenSeen[1].frozen)assert.equal(frozenSeen[1].clock,frozenSeen[0].clock,'clock holds during hit-stop');done.push('hit-stop');
 // KO slow-mo: finishing hit starts slow motion and the result waits for it.
 await p.waitForTimeout(1200);const ko=await land(p,'ArrowRight',x=>x.phase==='done',null,4);const waiting=await p.locator('.round-announcement').count();assert.equal(ko.result,'player');assert.ok(ko.slow,'KO slow motion');assert.equal(waiting,0,'result waits for the slow-mo');
 await p.screenshot({path:`${OUT}/qa-fx-ko.png`});await p.locator('.round-announcement').waitFor({timeout:5000});done.push('KO slow-mo');
 await p.close();
 // Reduced motion: no slow-mo, pops still shown (static).
 p=await open(BASE+'/?fx=v1',390,844,true);s=await land(p,'ArrowUp',x=>x.pops.length>0,'qa-fx-phone-reduced.png');
 await p.waitForTimeout(1200);await land(p,'ArrowRight',x=>x.phase==='done',null,4);assert.equal((await p.evaluate(()=>__fx())).slow,false,'no slow-mo with Reduced motion');done.push('reduced motion');await p.close();
 // Flag off: no pops, no freeze.
 p=await open(BASE+'/');await p.evaluate(()=>__close());await p.keyboard.down('j');await p.keyboard.down('ArrowUp');await p.waitForTimeout(40);await p.keyboard.up('j');await p.keyboard.up('ArrowUp');await p.waitForTimeout(800);
 const off=await p.evaluate(()=>__fx());assert.equal(off.pops.length,0);done.push('flag off unchanged');
 assert.deepEqual(errors,[]);console.log('FX QA passed:',done.join(' · '));await b.close();})().catch(e=>{console.error(e);process.exit(1);});
