// First-fight lesson QA (preview flag ?tutorial=v1). Requires server.mjs on 8787.
// Plays every step by keyboard on desktop and by touch on a phone; checks glows, progress dots, the held clock,
// that Mochi only attacks on the guard step, Skip, that it runs once, and the flag-off game.
const {chromium}=require('playwright');const assert=require('node:assert/strict');
const BASE=process.env.KB_TEST_URL||'http://127.0.0.1:8787';const OUT=process.env.KB_QA_OUT||__dirname;
const hooks=`\nglobalThis.__m=()=>({time:match.time,phase:match.phase,lesson:match.lesson?.mode??null,php:match.fighters[0].hp,ohp:match.fighters[1].hp,facing:match.fighters[0].facing,step:lesson?.step??null,cheering:!!lesson?.cheering,oppSwings:match.events.filter(e=>e.type==='swing'&&e.fighter===1).length});
globalThis.__close=()=>{const [a,b]=match.fighters;a.x=440;b.x=550;};`;
(async()=>{const b=await chromium.launch({headless:true,...(process.env.KB_BROWSER_CHANNEL?{channel:process.env.KB_BROWSER_CHANNEL}:{}),args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const errors=[],done=[];
 const open=async(url,opts={width:1100,height:820})=>{const p=await b.newPage({viewport:{width:opts.width,height:opts.height},hasTouch:!!opts.touch,isMobile:!!opts.touch});p.on('pageerror',e=>errors.push(e.message));
  await p.route('**/main.mjs',async r=>{const f=await r.fetch();await r.fulfill({response:f,body:(await f.text())+hooks});});await p.goto(url);return p;};
 const toFight=async p=>{await p.locator('#fight').click();await p.locator('[data-stage="1"]').click();await p.locator('#confirm-fighter').click();await p.locator('#begin').click();
  if(await p.locator('#story-skip').count())await p.locator('#story-skip').click();await p.waitForFunction(()=>__m().phase==='fight',null,{timeout:20000});};
 const waitStep=async(p,n)=>p.waitForFunction(n=>__m().step===n&&!__m().cheering,n,{timeout:15000});
 const glows=p=>p.locator('.tutorial-glow').evaluateAll(es=>es.map(e=>e.id||e.dataset.dir));
 // Keyboard helpers.
 const key={tap:async p=>{await p.keyboard.down('j');await p.waitForTimeout(40);await p.keyboard.up('j');},
  hold:async(p,k)=>{await p.keyboard.down('j');await p.waitForTimeout(60);await p.keyboard.down(k);await p.waitForTimeout(60);await p.keyboard.up('j');await p.keyboard.up(k);}};
 const untilStep=async(p,n,act,tries=12)=>{for(let i=0;i<tries;i++){if((await p.evaluate(()=>__m())).step>=n)return;await p.evaluate(()=>__close());await act();await p.waitForTimeout(700);}await waitStep(p,n);};

 // 1. Desktop, keyboard, full lesson.
 let p=await open(BASE+'/?tutorial=v1');await toFight(p);await p.locator('.lesson-card').waitFor();await waitStep(p,0);
 assert.match(await p.locator('.lesson-say').textContent(),/Tap Attack/);assert.deepEqual(await glows(p),['attack']);assert.match(await p.locator('.lesson-keys').textContent(),/J/);
 await p.screenshot({path:`${OUT}/qa-lesson-desktop-1.png`});
 const t0=(await p.evaluate(()=>__m())).time;
 await untilStep(p,1,()=>key.tap(p));await waitStep(p,1);
 await untilStep(p,2,async()=>{for(let k=0;k<4;k++){await key.tap(p);await p.waitForFunction(()=>!document.querySelector('.lesson-card')||true);await p.waitForTimeout(560);}});await waitStep(p,2);
 assert.deepEqual(await glows(p),['guard']);assert.equal((await p.evaluate(()=>__m())).oppSwings,0,'Mochi does not attack before the guard step');
 await p.evaluate(()=>__close());await p.keyboard.down('k');await p.waitForFunction(()=>__m().step>=3||__m().cheering,null,{timeout:20000});await p.keyboard.up('k');await waitStep(p,3);
 assert.ok((await p.evaluate(()=>__m())).oppSwings>=1,'Mochi jabs on the guard step');
 assert.deepEqual((await glows(p)).sort(),['attack','up']);await p.screenshot({path:`${OUT}/qa-lesson-desktop-high.png`});
 await untilStep(p,4,()=>key.hold(p,'w'));await waitStep(p,4);
 const fwd=(await p.evaluate(()=>__m())).facing>0?'right':'left';assert.deepEqual((await glows(p)).sort(),['attack',fwd].sort(),'forward glows toward Mochi');
 await untilStep(p,5,()=>key.hold(p,fwd==='right'?'ArrowRight':'ArrowLeft'));await waitStep(p,5);
 await untilStep(p,6,()=>key.hold(p,'s'));await waitStep(p,6);
 const sw=(await p.evaluate(()=>__m())).oppSwings;
 await untilStep(p,7,()=>key.hold(p,fwd==='right'?'ArrowLeft':'ArrowRight'));
 await p.waitForFunction(()=>/You know them all/.test(document.querySelector('.lesson-say')?.textContent||''),null,{timeout:8000});let m=await p.evaluate(()=>__m());assert.ok(t0-m.time<0.6,'clock held for the whole lesson: '+m.time);await p.screenshot({path:`${OUT}/qa-lesson-desktop-end.png`});
assert.ok(m.php>=35&&m.ohp>=35);assert.equal(m.oppSwings,sw,'Mochi stops jabbing after the guard step');
 await p.locator('.lesson-card').waitFor({state:'detached',timeout:6000});assert.equal((await glows(p)).length,0);
 await p.waitForFunction(()=>__m().time<45,null,{timeout:20000});done.push('desktop keyboard lesson');
 // Runs once: the next stage-1 fight has no lesson.
 await p.evaluate(()=>{});await p.keyboard.press('Escape');await p.locator('#leave-fight').click();await toFight(p);await p.waitForTimeout(800);assert.equal(await p.locator('.lesson-card').count(),0,'lesson runs once');done.push('runs once');await p.close();

 // 2. Phone, touch: card layout, glow on touch buttons, Skip.
 p=await open(BASE+'/?tutorial=v1',{width:390,height:844,touch:true});await toFight(p);await waitStep(p,0);
 assert.equal(await p.locator('.lesson-keys').isVisible(),false,'no key hints on touch screens');
 const tap=async()=>{const r=await p.locator('#attack').boundingBox();await p.touchscreen.tap(r.x+r.width/2,r.y+r.height/2);};
 await untilStep(p,1,tap);await waitStep(p,1);await p.screenshot({path:`${OUT}/qa-lesson-phone-chain.png`});
 const card=await p.locator('.lesson-card').boundingBox(),arena=await p.locator('#arena').boundingBox(),menu=await p.locator('#pause-fight').boundingBox(),skip=await p.locator('#lesson-skip').boundingBox();
 assert.ok(card.x>=0&&card.x+card.width<=390&&card.y>=menu.y+menu.height-1,'card sits below the arena header');assert.ok(card.y+card.height<arena.y+arena.height*0.75,'card stays above the bunnies');
 assert.ok(skip.height>=44);
 const fonts=await p.locator('.lesson-card *').evaluateAll(es=>es.filter(e=>e.textContent.trim()&&e.offsetParent).map(e=>parseFloat(getComputedStyle(e).fontSize)));assert.ok(fonts.every(f=>f>=14));
 await p.locator('#lesson-skip').click();assert.equal(await p.locator('.lesson-card').count(),0);assert.equal((await glows(p)).length,0);
 await p.waitForFunction(()=>__m().time<45&&__m().lesson===null,null,{timeout:20000});done.push('phone touch + skip');
 // Landscape phone layout.
 await p.close();p=await open(BASE+'/?tutorial=v1',{width:844,height:390,touch:true});await toFight(p);await waitStep(p,0);await p.waitForTimeout(600);
 const c2=await p.locator('.lesson-card').boundingBox(),dp=await p.locator('.dpad').boundingBox(),ab=await p.locator('.action-buttons').boundingBox();
 const overlap=(a,b)=>a.x<b.x+b.width&&a.x+a.width>b.x&&a.y<b.y+b.height&&a.y+a.height>b.y;assert.ok(!overlap(c2,dp)&&!overlap(c2,ab),'landscape card clear of controls');
 await p.screenshot({path:`${OUT}/qa-lesson-landscape.png`});done.push('landscape layout');await p.close();
 // 3. Not shown once stage 1 is won, or without the flag.
 p=await open(BASE+'/?tutorial=v1');await p.evaluate(()=>localStorage.setItem('kb-campaign-v1',JSON.stringify({cleared:[1]})));await p.reload();
 await p.locator('#fight').click();const tab=p.locator('[data-chapter="0"]');if(await tab.count())await tab.first().click();await p.locator('[data-stage="1"]').click();await p.locator('#confirm-fighter').click();await p.locator('#begin').click();
 if(await p.locator('#story-skip').count())await p.locator('#story-skip').click();await p.waitForFunction(()=>__m().phase==='fight',null,{timeout:20000});await p.waitForTimeout(600);
 assert.equal(await p.locator('.lesson-card').count(),0,'no lesson after stage 1 is won');await p.close();
 p=await open(BASE+'/?story=off');await toFight(p);await p.waitForTimeout(600);assert.equal(await p.locator('.lesson-card').count(),0,'no lesson without the flag');done.push('only when wanted');
 assert.deepEqual(errors,[]);console.log('Lesson QA passed:',done.join(' · '));await b.close();})().catch(e=>{console.error(e);process.exit(1);});
