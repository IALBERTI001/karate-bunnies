// Training QA. Requires server.mjs on 8787.
// First launch opens the welcome title with Start training; training plays every lesson step (keyboard on desktop,
// touch on a phone) with glows, dots, a held clock, and Mochi jabbing only on the guard step; the end card's
// Go to main menu reaches the title; later launches start at the title; Skip; Replay training from Settings;
// stage 1 has no lesson; ?tutorial=off skips training.
const {chromium}=require('playwright');const assert=require('node:assert/strict');
const BASE=process.env.KB_TEST_URL||'http://127.0.0.1:8787';const OUT=process.env.KB_QA_OUT||__dirname;
const hooks=`\nglobalThis.__m=()=>({time:match?.time,phase:match?.phase,mode:modeState.mode,lesson:match?.lesson?.mode??null,php:match?.fighters[0].hp,ohp:match?.fighters[1].hp,facing:match?.fighters[0].facing,step:lesson?.step??null,cheering:!!lesson?.cheering,oppSwings:match?match.events.filter(e=>e.type==='swing'&&e.fighter===1).length:0,log:match?match.events.map(e=>e.type+':'+(e.fighter??'')+':'+(e.move??'')).join(' '):'',carrots,cleared:progress.cleared.length,view});
globalThis.__close=()=>{const [a,b]=match.fighters;a.x=440;b.x=550;};`;
(async()=>{const b=await chromium.launch({headless:true,...(process.env.KB_BROWSER_CHANNEL?{channel:process.env.KB_BROWSER_CHANNEL}:{}),args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const errors=[],done=[];
 const open=async(url,opts={width:1100,height:820})=>{const ctx=await b.newContext({viewport:{width:opts.width,height:opts.height},hasTouch:!!opts.touch,isMobile:!!opts.touch});const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
  await p.route('**/main.mjs',async r=>{const f=await r.fetch();await r.fulfill({response:f,body:(await f.text())+hooks});});
  // Buttons shown: software rendering in the test browser is too slow for timed taps on the larger hidden-buttons arena (qa-buttons.cjs covers that mode).
  await p.addInitScript(()=>{try{if(!localStorage.getItem('kb-settings-v1'))localStorage.setItem('kb-settings-v1',JSON.stringify({music:.25,effects:.5,reduced:false,shake:true,large:false,buttons:'show'}));}catch{}});await p.goto(url);return p;};
 const train=async p=>{await p.locator('#start-training').click();await p.waitForFunction(()=>__m().phase==='fight'&&__m().step===0,null,{timeout:30000});};
 const waitStep=async(p,n)=>p.waitForFunction(n=>__m().step===n&&!__m().cheering,n,{timeout:15000});
 const glows=p=>p.locator('.tutorial-glow').evaluateAll(es=>es.map(e=>e.id||e.dataset.dir));
 const key={tap:async p=>{await p.keyboard.down('j');await p.waitForTimeout(40);await p.keyboard.up('j');},
  hold:async(p,k)=>{await p.keyboard.down('j');await p.waitForTimeout(60);await p.keyboard.down(k);await p.waitForTimeout(60);await p.keyboard.up('j');await p.keyboard.up(k);}};
 const untilStep=async(p,n,act,tries=12)=>{for(let i=0;i<tries;i++){if((await p.evaluate(()=>__m())).step>=n)return;await p.evaluate(()=>__close());await act();await p.waitForTimeout(700);}await waitStep(p,n);};

 // 1. Desktop first launch: welcome title, full training by keyboard, end card, main menu.
 let p=await open(BASE+'/');await p.locator('#start-training').waitFor();
 assert.equal(await p.locator('#fight').count(),0,'first launch shows training, not the full menu');assert.ok(await p.locator('#skip-training').isVisible());
 await p.screenshot({path:`${OUT}/qa-training-welcome-desktop.png`});
 await train(p);assert.equal(await p.locator('.arena-title small').textContent(),'TRAINING');assert.equal(await p.locator('.story-scene').count(),0,'no story lines in training');
 assert.match(await p.locator('.lesson-say').textContent(),/Tap Attack/);assert.deepEqual(await glows(p),['attack']);assert.match(await p.locator('.lesson-keys').textContent(),/J/);
 const t0=(await p.evaluate(()=>__m())).time;
 await untilStep(p,1,()=>key.tap(p));await waitStep(p,1);{const mm=await p.evaluate(()=>__m());assert.equal(mm.oppSwings,0,'Mochi does not attack before the guard step: '+mm.log);}
 await untilStep(p,2,async()=>{for(let k=0;k<4;k++){await key.tap(p);await p.waitForTimeout(560);}});await waitStep(p,2);
 assert.deepEqual(await glows(p),['guard']);
 await p.evaluate(()=>__close());await p.keyboard.down('k');await p.waitForFunction(()=>__m().step>=3||__m().cheering,null,{timeout:20000});await p.keyboard.up('k');await waitStep(p,3);
 assert.ok((await p.evaluate(()=>__m())).oppSwings>=1,'Mochi jabs on the guard step');
 assert.deepEqual((await glows(p)).sort(),['attack','up']);
 await untilStep(p,4,()=>key.hold(p,'w'));await waitStep(p,4);
 const fwd=(await p.evaluate(()=>__m())).facing>0?'right':'left';assert.deepEqual((await glows(p)).sort(),['attack',fwd].sort(),'forward glows toward Mochi');
 await untilStep(p,5,()=>key.hold(p,fwd==='right'?'ArrowRight':'ArrowLeft'));await waitStep(p,5);
 await untilStep(p,6,()=>key.hold(p,'s'));await waitStep(p,6);
 await untilStep(p,7,()=>key.hold(p,fwd==='right'?'ArrowLeft':'ArrowRight'));
 await p.locator('#lesson-menu').waitFor({timeout:8000});let m=await p.evaluate(()=>__m());
 assert.match(await p.locator('.lesson-say').textContent(),/ready, little one/);assert.ok(t0-m.time<0.6,'clock held: '+m.time);assert.ok(m.php>=35&&m.ohp>=35);
 await p.waitForTimeout(1500);m=await p.evaluate(()=>__m());assert.ok(t0-m.time<0.6,'practice bout does not start after the lesson');assert.ok(await p.locator('#lesson-menu').isVisible(),'end card waits for the player');
 await p.screenshot({path:`${OUT}/qa-training-end-desktop.png`});
 await p.locator('#lesson-menu').click();await p.locator('#fight').waitFor();m=await p.evaluate(()=>__m());
 assert.equal(m.view,'home');assert.equal(m.carrots,0,'training pays no carrots');assert.equal(m.cleared,0,'training is not a campaign win');done.push('first launch → training → main menu');
 // Later launches start at the main menu; stage 1 has no lesson.
 await p.reload();await p.locator('#fight').waitFor();assert.equal(await p.locator('#start-training').count(),0,'second launch starts at the menu');
 await p.locator('#fight').click();await p.locator('[data-stage="1"]').click();await p.locator('#confirm-fighter').click();await p.locator('#begin').click();
 if(await p.locator('#story-skip').count())await p.locator('#story-skip').click();await p.waitForFunction(()=>__m().phase==='fight',null,{timeout:30000});await p.waitForTimeout(600);
 assert.equal(await p.locator('.lesson-card').count(),0,'no lesson in stage 1');done.push('runs once');
 // Replay training from Settings.
 await p.keyboard.press('Escape');await p.locator('#leave-fight').click();await p.locator('#open-settings').click();await p.locator('#replay-training').click();
 await p.waitForFunction(()=>__m().mode==='training'&&__m().step===0,null,{timeout:30000});done.push('replay from Settings');await p.close();

 // 2. Phone first launch: touch taps, card layout, Skip goes to the menu.
 p=await open(BASE+'/',{width:390,height:844,touch:true});await p.locator('#start-training').waitFor();await p.screenshot({path:`${OUT}/qa-training-welcome-phone.png`});
 await train(p);assert.equal(await p.locator('.lesson-keys').isVisible(),false,'no key hints on touch screens');
 const tap=async()=>{const r=await p.locator('#attack').boundingBox();await p.touchscreen.tap(r.x+r.width/2,r.y+r.height/2);};
 await untilStep(p,1,tap);await waitStep(p,1);
 const card=await p.locator('.lesson-card').boundingBox(),arena=await p.locator('#arena').boundingBox(),menu=await p.locator('#pause-fight').boundingBox(),skip=await p.locator('#lesson-skip').boundingBox();
 assert.ok(card.x>=0&&card.x+card.width<=390&&card.y>=menu.y+menu.height-1,'card sits below the arena header');assert.ok(card.y+card.height<arena.y+arena.height*0.75,'card stays above the bunnies');assert.ok(skip.height>=44);
 const fonts=await p.locator('.lesson-card *').evaluateAll(es=>es.filter(e=>e.textContent.trim()&&e.offsetParent).map(e=>parseFloat(getComputedStyle(e).fontSize)));assert.ok(fonts.every(f=>f>=14));
 await p.locator('#lesson-skip').click();await p.locator('#fight').waitFor();assert.equal((await p.evaluate(()=>__m())).view,'home','Skip goes to the main menu');
 await p.reload();await p.locator('#fight').waitFor();assert.equal(await p.locator('#start-training').count(),0,'skipped training does not return');done.push('phone touch + skip');await p.close();
 // 3. Phone landscape card layout; Skip to main menu on the welcome screen.
 p=await open(BASE+'/',{width:844,height:390,touch:true});await train(p);await p.waitForTimeout(600);
 const c2=await p.locator('.lesson-card').boundingBox(),dp=await p.locator('.dpad').boundingBox(),ab=await p.locator('.action-buttons').boundingBox();
 const overlap=(a,c)=>a.x<c.x+c.width&&a.x+a.width>c.x&&a.y<c.y+c.height&&a.y+a.height>c.y;assert.ok(!overlap(c2,dp)&&!overlap(c2,ab),'landscape card clear of controls');
 await p.screenshot({path:`${OUT}/qa-training-landscape.png`});await p.close();
 p=await open(BASE+'/');await p.locator('#skip-training').click();await p.locator('#fight').waitFor();await p.reload();await p.locator('#fight').waitFor();done.push('landscape + skip to menu');await p.close();
 // 4. Players with campaign progress, and ?tutorial=off, start at the menu; ?tutorial=v1 forces training.
 p=await open(BASE+'/');await p.evaluate(()=>{localStorage.setItem('kb-campaign-v1',JSON.stringify({cleared:[1]}));});await p.reload();await p.locator('#fight').waitFor();await p.close();
 p=await open(BASE+'/?tutorial=off');await p.locator('#fight').waitFor();await p.close();
 p=await open(BASE+'/?tutorial=v1');await p.evaluate(()=>localStorage.setItem('kb-lesson-v1','true'));await p.reload();await p.locator('#start-training').waitFor();await p.close();done.push('who sees training');
 assert.deepEqual(errors,[]);console.log('Training QA passed:',done.join(' · '));await b.close();})().catch(e=>{console.error(e);process.exit(1);});
