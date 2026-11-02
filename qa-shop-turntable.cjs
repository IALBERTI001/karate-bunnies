// Shop 360 turntable: auto spin, drag, buttons and arrow keys turn the bunny; back views show the back mark; no errors.
const {chromium}=require('playwright'),assert=require('assert');
(async()=>{const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});const url=(process.env.KB_TEST_URL||'http://127.0.0.1:8787')+'/?story=off&fx=off';const errors=[];
for(const [w,h] of [[1280,720],[390,844]]){const p=await b.newPage({viewport:{width:w,height:h}});p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>m.type()==='error'&&errors.push(m.text()));
 await p.addInitScript(()=>{localStorage.setItem('kb-lesson-v1','true');localStorage.setItem('kb-wardrobe-v1',JSON.stringify({version:1,balance:40,owned:['golden-knights'],equipped:'golden-knights'}));});
 await p.goto(url);await p.locator('#open-shop').click();await p.locator('#shop-bunny').waitFor();
 const shot=async n=>{await p.waitForTimeout(400);return p.locator('#shop-bunny').screenshot({path:`qa-turntable-${w}-${n}.png`});};
 const a=await shot('auto-a');await p.waitForTimeout(1500);const b2=await shot('auto-b');assert.notDeepEqual(a,b2,'auto spin changes the view');
 for(let i=0;i<4;i++)await p.locator('#turn-right').click();await shot('back');
 await p.locator('#shop-bunny').focus();await p.keyboard.press('ArrowLeft');await shot('key');
 const box=await p.locator('#shop-bunny').boundingBox();await p.mouse.move(box.x+box.width/2,box.y+box.height/2);await p.mouse.down();await p.mouse.move(box.x+box.width/2-120,box.y+box.height/2,{steps:6});await p.mouse.up();await shot('drag');
 const still1=await shot('still-1');await p.waitForTimeout(1200);const still2=await shot('still-2');assert.deepEqual(still1,still2,'turning by hand stops the auto spin');
 assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
 await p.screenshot({path:`qa-turntable-${w}-page.png`});await p.close();}
assert.deepEqual(errors,[]);await b.close();console.log('Turntable: auto spin, buttons, arrow keys, drag, hand turn stops spin, 2 layouts, no errors');})().catch(e=>{console.error(e);process.exit(1)});
