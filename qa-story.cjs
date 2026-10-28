// Story scenes QA (preview flag ?story=v1). Requires server.mjs on 8787.
// Checks: fixed story opponent, scene holds the fight clock and inputs, tap/keyboard/Attack advance,
// Skip, win and loss scenes over the arena, flag off = unchanged game, layout at four viewports.
const {chromium}=require('playwright');const assert=require('node:assert/strict');
const BASE=process.env.KB_TEST_URL||'http://127.0.0.1:8787';const OUT=process.env.KB_QA_OUT||__dirname;
const inject=async p=>p.route('**/main.mjs',async route=>{const r=await route.fetch();const source=await r.text();
 await route.fulfill({response:r,body:source+`\nglobalThis.__testResult=(res)=>{match.phase='done';match.result=res;match.fighters.forEach((f,i)=>{const lost=res==='player'?i===1:i===0;f.hp=lost?0:100;f.animation=lost?17:16;f.time=0;f.move=null;f.z=0;});finish();};globalThis.__clock=()=>match.time;globalThis.__phase=()=>match.phase;globalThis.__belt=()=>heroSkin().belt;globalThis.__anims=()=>match.fighters.map(f=>f.animation);`});});
const toFight=async(p,url,stageId=1)=>{await p.goto(url);if(stageId>1)await p.evaluate(n=>localStorage.setItem('kb-campaign-v1',JSON.stringify({cleared:[...Array(n-1).keys()].map(i=>i+1)})),stageId);if(stageId>1)await p.reload();
 await p.locator('#fight').click();const tab=p.locator(`[data-chapter="${Math.floor((stageId-1)/4)}"]`);if(await tab.count())await tab.first().click();
 await p.locator(`[data-stage="${stageId}"]`).click();await p.locator('#confirm-fighter').click();return (await p.locator('#opponent-choice').textContent()).trim();};
(async()=>{const b=await chromium.launch({headless:true,...(process.env.KB_BROWSER_CHANNEL?{channel:process.env.KB_BROWSER_CHANNEL}:{}),args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required']});
 const errors=[];const results=[];
 // 1. Full flow on a phone.
 let p=await b.newPage({viewport:{width:390,height:844},hasTouch:true,isMobile:true});p.setDefaultTimeout(90000);p.setDefaultNavigationTimeout(90000);await p.addInitScript(()=>{try{if(!localStorage.getItem('kb-lesson-v1'))localStorage.setItem('kb-lesson-v1','true');}catch{}});p.on('pageerror',e=>errors.push(e.message));await inject(p);
 assert.equal(await toFight(p,BASE+'/'),'Mochi','story mode reveals the stage character');
 await p.locator('#begin').click();await p.locator('.story-bubble').waitFor();
 assert.equal((await p.locator('.story-name').textContent()).trim(),'Coach Hazel');
 const c0=await p.evaluate(()=>__clock());await p.waitForTimeout(2500);
 assert.equal(await p.evaluate(()=>__clock()),c0,'clock holds during the scene');assert.equal(await p.evaluate(()=>__phase()),'intro','bow waits for the scene');
 await p.locator('#attack').dispatchEvent('pointerdown',{pointerId:1,isPrimary:true});await p.waitForTimeout(50);await p.locator('#attack').dispatchEvent('pointerup',{pointerId:1,isPrimary:true});
 await p.waitForTimeout(900);assert.equal((await p.locator('.story-name').textContent()).trim(),'Bunny','Attack advances the scene');
 await p.screenshot({path:OUT+'/qa-story-phone-before.png'});
 await p.locator('.story-bubble').click();await p.waitForTimeout(100);if(await p.locator('.story-bubble').count())await p.locator('.story-bubble').click();
 await p.waitForTimeout(200);assert.equal(await p.locator('.story-scene').count(),0,'scene ends after the last line');
 await p.waitForFunction(()=>__phase()==='fight',null,{timeout:20000});await p.waitForFunction(()=>__clock()<45,null,{timeout:20000});
 await p.evaluate(()=>__testResult('player'));await p.locator('.story-bubble').waitFor();await p.waitForTimeout(1200);
 assert.equal((await p.locator('.story-name').textContent()).trim(),'Bunny');assert.ok(await p.locator('.round-announcement').isVisible(),'VICTORY banner shows during the win scene');
 assert.equal(await p.locator('.modal-shade').count(),0);await p.screenshot({path:OUT+'/qa-story-phone-win.png'});
 const skip=await p.locator('#story-skip').boundingBox();assert.ok(skip.height>=48&&skip.width>=48,'Skip is a full touch target');
 const bubble=await p.locator('.story-bubble').boundingBox();assert.ok(bubble.x>=0&&bubble.x+bubble.width<=390);
 const fonts=await p.locator('.story-scene *').evaluateAll(es=>es.filter(e=>e.textContent.trim()&&getComputedStyle(e).visibility!=='hidden').map(e=>parseFloat(getComputedStyle(e).fontSize)));assert.ok(fonts.every(f=>f>=14),'text 14px or larger');
 await p.locator('#story-skip').click();assert.equal(await p.locator('.story-scene').count(),0,'Skip ends the scene');assert.ok(await p.locator('#next-fight').isVisible(),'result actions return after the scene');
 results.push('phone flow');
 // 2. Keyboard, Skip before the fight, loss scene on desktop.
 await p.close();p=await b.newPage({viewport:{width:1280,height:800}});p.setDefaultTimeout(90000);p.setDefaultNavigationTimeout(90000);await p.addInitScript(()=>{try{if(!localStorage.getItem('kb-lesson-v1'))localStorage.setItem('kb-lesson-v1','true');}catch{}});p.on('pageerror',e=>errors.push(e.message));await inject(p);
 await toFight(p,BASE+'/');await p.locator('#begin').click();await p.locator('.story-bubble').waitFor();await p.screenshot({path:OUT+'/qa-story-desktop-before.png'});
 await p.keyboard.press('Enter');await p.waitForTimeout(80);await p.keyboard.press('Enter');await p.waitForTimeout(900);assert.equal((await p.locator('.story-name').textContent()).trim(),'Bunny','Enter advances');
 await p.keyboard.press('Escape');assert.ok(await p.locator('#resume').isVisible(),'pause still works during a scene');await p.locator('#resume').click();
 const held=await p.evaluate(()=>__clock());await p.waitForTimeout(800);assert.equal(await p.evaluate(()=>__clock()),held,'resume from pause keeps the scene holding');
 await p.locator('#story-skip').click();await p.waitForFunction(()=>__phase()==='fight',null,{timeout:20000});
 await p.evaluate(()=>__testResult('opponent'));await p.locator('.story-bubble').waitFor();await p.waitForTimeout(1500);
 assert.match((await p.locator('.story-name').textContent()).trim(),/^Coach /);assert.deepEqual(await p.evaluate(()=>__anims()),[15,15],'both bunnies bow after a loss');await p.screenshot({path:OUT+'/qa-story-desktop-loss.png'});results.push('keyboard, pause, skip, loss');
 // 3. Tablet and phone landscape layouts, final stage.
 for(const [w,h,name] of [[768,1024,'tablet'],[844,390,'landscape']]){await p.setViewportSize({width:w,height:h});
  await toFight(p,BASE+'/',20);await p.locator('#begin').click();await p.locator('.story-bubble').waitFor();await p.waitForTimeout(900);
  const box=await p.locator('.story-bubble').boundingBox(),sk=await p.locator('#story-skip').boundingBox(),menu=await p.locator('#pause-fight').boundingBox();
  assert.ok(box.x>=0&&box.x+box.width<=w&&box.y>=0&&box.y+box.height<=h,`${name}: bubble on screen`);const arena=await p.locator('#arena').boundingBox();assert.ok(box.y>=arena.y+arena.height*0.6,`${name}: bubble stays in the bottom band`);
  assert.ok(!(sk.x<menu.x+menu.width&&sk.x+sk.width>menu.x&&sk.y<menu.y+menu.height&&sk.y+sk.height>menu.y),`${name}: Skip clear of Pause`);
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await p.screenshot({path:OUT+`/qa-story-${name}-stage20.png`});}
 results.push('tablet + landscape layout');
 // 4. Belt award: winning stage 4 earns the yellow belt; it changes on the coach's line, not before.
 await p.setViewportSize({width:390,height:844});await toFight(p,BASE+'/',4);
 assert.match(await p.locator('.fighter-start small').textContent(),/^White belt/);await p.locator('#begin').click();await p.locator('#story-skip').click();
 await p.waitForFunction(()=>__phase()==='fight',null,{timeout:20000});assert.equal(await p.evaluate(()=>__belt()),'White');
 await p.evaluate(()=>__testResult('player'));await p.locator('.story-bubble').waitFor();
 assert.equal(await p.evaluate(()=>__belt()),'White','old belt shows during the win lines');
 for(let i=0;i<6&&!(await p.locator('.story-name').textContent()).startsWith('Coach');i++){await p.locator('.story-bubble').click();await p.waitForTimeout(120);}
 await p.waitForTimeout(900);assert.equal((await p.locator('.story-name').textContent()).trim(),'Coach Hazel');assert.equal(await p.evaluate(()=>__belt()),'Yellow','belt changes on the award line');
 await p.screenshot({path:OUT+'/qa-story-belt-award.png'});await p.locator('#story-skip').click();
 await toFight(p,BASE+'/',5);assert.match(await p.locator('.fighter-start small').textContent(),/^Yellow belt/);
 // Skip still awards the belt.
 await p.evaluate(()=>localStorage.setItem('kb-campaign-v1',JSON.stringify({cleared:[1,2,3,4,5,6,7]})));await toFight(p,BASE+'/',8);await p.locator('#begin').click();await p.locator('#story-skip').click();
 await p.waitForFunction(()=>__phase()==='fight',null,{timeout:20000});await p.evaluate(()=>__testResult('player'));await p.locator('#story-skip').waitFor();await p.locator('#story-skip').click();
 assert.equal(await p.evaluate(()=>__belt()),'Green','Skip still awards the belt');results.push('belt award');
 // 5. Flag off: approved game unchanged.
 await p.setViewportSize({width:1280,height:800});const names=new Set();for(let i=0;i<6;i++)names.add(await toFight(p,BASE+'/?story=off'));
 await p.locator('#begin').click();await p.waitForTimeout(400);assert.equal(await p.locator('.story-scene').count(),0,'no scenes without the flag');
 assert.ok(names.size>1,'opponent stays randomized without the flag');assert.equal(await p.evaluate(()=>__belt()),undefined,'no belt change without the flag');results.push('flag off unchanged');
 assert.deepEqual(errors,[]);console.log('Story QA passed:',results.join(' · '));await b.close();})().catch(e=>{console.error(e);process.exit(1);});
