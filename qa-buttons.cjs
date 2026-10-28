// On-screen buttons setting QA. Requires server.mjs on 8787.
// Auto hides the buttons on a PC and shows them on a touch screen; the bottom band still appears for
// story dialogue and results; Settings can force Show or Hide; the lesson's last card mentions the setting on a PC.
const {chromium}=require('playwright');const assert=require('node:assert/strict');
const BASE=process.env.KB_TEST_URL||'http://127.0.0.1:8787';const OUT=process.env.KB_QA_OUT||__dirname;
const hooks=`\nglobalThis.__win=()=>{match.phase='done';match.result='player';match.fighters.forEach((f,i)=>{f.hp=i?0:100;f.animation=i?17:16;f.time=0;f.move=null;f.z=0;});finish();};globalThis.__phase=()=>match?.phase;globalThis.__toEnd=()=>{for(let i=0;i<7;i++)nextLessonStep();};`;
(async()=>{const b=await chromium.launch({headless:true,...(process.env.KB_BROWSER_CHANNEL?{channel:process.env.KB_BROWSER_CHANNEL}:{}),args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const errors=[],done=[];
 const open=async(url,o={width:1280,height:800})=>{const p=await b.newPage({viewport:{width:o.width,height:o.height},hasTouch:!!o.touch,isMobile:!!o.touch});p.on('pageerror',e=>errors.push(e.message));
  await p.route('**/main.mjs',async r=>{const f=await r.fetch();await r.fulfill({response:f,body:(await f.text())+hooks});});await p.goto(url);return p;};
 const begin=async p=>{await p.locator('#fight').click();await p.locator('[data-stage="1"]').click();await p.locator('#confirm-fighter').click();await p.locator('#begin').click();};
 const shown=p=>p.locator('#attack').isVisible();
 // 1. PC, Auto: story band shows, buttons hidden during the fight, result buttons shown.
 let p=await open(BASE+'/');await begin(p);await p.locator('.story-bubble').waitFor();
 assert.ok(await p.locator('.story-bubble').isVisible(),'dialogue band still appears');assert.equal(await shown(p),false,'buttons stay hidden behind the dialogue');
 await p.screenshot({path:`${OUT}/qa-buttons-pc-story.png`});await p.locator('#story-skip').click();await p.waitForFunction(()=>__phase()==='fight',null,{timeout:20000});
 assert.equal(await shown(p),false,'Auto hides buttons on a PC');assert.equal(await p.locator('.fight-controls').isVisible(),false,'no empty band');
 const arena=await p.locator('#arena').boundingBox();assert.ok(arena.y+arena.height>720,'arena fills the freed space');
 await p.screenshot({path:`${OUT}/qa-buttons-pc-fight.png`});
 await p.evaluate(()=>__win());await p.locator('#story-skip').click();assert.ok(await p.locator('#next-fight').isVisible(),'result buttons shown');done.push('PC auto');
 // 2. Settings: Always show, then Hide, from the in-fight pause menu.
 await p.locator('#retry').click();if(await p.locator('#story-skip').count())await p.locator('#story-skip').click();await p.waitForFunction(()=>__phase()==='fight',null,{timeout:20000});
 await p.keyboard.press('Escape');await p.locator('#fight-settings').click();assert.equal(await p.locator('#buttons').inputValue(),'auto');
 await p.screenshot({path:`${OUT}/qa-buttons-settings.png`});
 await p.locator('#buttons').selectOption('show');await p.locator('#resume').click();assert.equal(await shown(p),true,'Always show');
 await p.screenshot({path:`${OUT}/qa-buttons-pc-show.png`});
 await p.reload();assert.equal(await p.evaluate(()=>JSON.parse(localStorage.getItem('kb-settings-v1')).buttons),'show','setting is saved');
 await p.evaluate(()=>{const s=JSON.parse(localStorage.getItem('kb-settings-v1'));s.buttons='hide';localStorage.setItem('kb-settings-v1',JSON.stringify(s));});await p.close();done.push('settings show/hide');
 // 3. Phone, Auto: buttons shown; Hide works on touch too.
 p=await open(BASE+'/',{width:390,height:844,touch:true});await begin(p);await p.locator('#story-skip').click();await p.waitForFunction(()=>__phase()==='fight',null,{timeout:20000});
 assert.equal(await shown(p),true,'Auto shows buttons on a touch screen');await p.close();
 p=await open(BASE+'/',{width:390,height:844,touch:true});await p.evaluate(()=>localStorage.setItem('kb-settings-v1',JSON.stringify({music:.25,effects:.5,reduced:false,shake:true,large:false,buttons:'hide'})));await p.reload();
 await begin(p);await p.locator('#story-skip').click();await p.waitForFunction(()=>__phase()==='fight',null,{timeout:20000});assert.equal(await shown(p),false,'Hide works on a phone');
 await p.screenshot({path:`${OUT}/qa-buttons-phone-hide.png`});await p.close();done.push('phone auto + hide');
 // 4. Lesson on a PC: keys shown, last card mentions the setting.
 p=await open(BASE+'/?tutorial=v1');await begin(p);await p.locator('#story-skip').click();await p.locator('.lesson-card').waitFor();
 assert.ok(await p.locator('.lesson-keys').isVisible(),'keys shown when buttons are hidden');
 await p.evaluate(()=>__toEnd());await p.waitForFunction(()=>/Tip: Settings/.test(document.querySelector('.lesson-keys')?.textContent||''),null,{timeout:5000});
 await p.screenshot({path:`${OUT}/qa-buttons-lesson-tip.png`});done.push('lesson tip');await p.close();
 assert.deepEqual(errors,[]);console.log('Buttons QA passed:',done.join(' · '));await b.close();})().catch(e=>{console.error(e);process.exit(1);});
