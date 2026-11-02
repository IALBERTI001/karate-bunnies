// CrazyGames QA step 1 for Karate Bunnies: a scripted session on the built upload package (dist) with a stand-in SDK.
// Usage: serve dist (python3 -m http.server 8792 --bind 127.0.0.1 --directory dist), then
//   B=http://127.0.0.1:8792/ OUT=<dir> SIZES=821x462,910x512 node tools/qa/technical-gate.cjs
// Per window size: fresh first launch (welcome), training, main menu, settings, arenas, fighter, story scene, fight, pause,
// result; screenshots of each; page/console errors, HTTP >= 400, hosts contacted, SDK event log, bytes and time to the first
// gameplayStart (NOSHOT=settings,pause skips those screenshots on slow software-rendering machines; audits still run), text rendered under 10 px (CrazyGames floor) and under 14 px (our floor), and browser-default audits.
let playwright;try{playwright=require('playwright');}catch{playwright=require('/opt/npm-tools/node_modules/playwright');}
const fs=require('fs');const B=process.env.B||'http://127.0.0.1:8792/';const OUT=process.env.OUT||'qa-gate';fs.mkdirSync(OUT,{recursive:true});
const SIZES=(process.env.SIZES||'821x462,910x512,1080x607,1216x684,1280x720,1920x1080,800x450,390x844').split(',').map(s=>s.split('x').map(Number));
const fake=()=>{window.__sdklog=[];const st={};const push=e=>window.__sdklog.push(e);
 window.CrazyGames={SDK:{environment:'crazygames',init:async()=>{push('init');},game:{gameplayStart:()=>push('gameplayStart'),gameplayStop:()=>push('gameplayStop'),loadingStart:()=>push('loadingStart'),loadingStop:()=>push('loadingStop'),happytime:()=>push('happytime'),settings:{muteAudio:false,disableChat:false},addSettingsChangeListener:()=>{}},
  data:{getItem:k=>st[k]??null,setItem:(k,v)=>{st[k]=String(v);push('data:'+k);},removeItem:k=>{delete st[k];},clear:()=>{for(const k in st)delete st[k];}},
  ad:{requestAd:(t,cb)=>{push('ad:'+t);cb?.adStarted?.();setTimeout(()=>cb?.adError?.('none'),100);},hasAdblock:async()=>false}}};};
const hooks=`\nglobalThis.__qa={win:()=>{match.phase='done';match.result='player';match.fighters.forEach((f,i)=>{f.hp=i?0:100;f.animation=i?17:16;f.time=0;f.move=null;f.z=0;});finish();},phase:()=>match?.phase,view:()=>view};`;
const textAudit=()=>{const tiny=[],small=[];for(const el of document.querySelectorAll('#app *')){if(![...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))continue;const r=el.getBoundingClientRect();if(r.width<2||r.height<2||r.bottom<0||r.top>innerHeight)continue;const s=getComputedStyle(el);if(s.visibility==='hidden'||+s.opacity===0||s.display==='none')continue;let scale=1;for(let p=el;p;p=p.parentElement){const t=getComputedStyle(p).transform;if(t&&t!=='none'){const m=t.match(/matrix\(([^,]+)/);if(m)scale*=+m[1];}}const px=parseFloat(s.fontSize)*scale;const txt=el.textContent.trim().slice(0,30);if(px<10)tiny.push(px.toFixed(1)+' '+txt);else if(px<14)small.push(px.toFixed(1)+' '+txt);}
 const overflow=document.documentElement.scrollWidth>innerWidth+1||document.documentElement.scrollHeight>innerHeight+1;return {tiny,small,overflow};};
const defaultsAudit=()=>{const out=[];if(document.querySelector('[title]'))out.push('title tooltips: '+[...document.querySelectorAll('[title]')].length);
 for(const el of document.querySelectorAll('input,select')){const s=getComputedStyle(el);if((el.type==='range'||el.type==='checkbox'||el.tagName==='SELECT')&&s.appearance!=='none'&&s.webkitAppearance!=='none')out.push('native '+(el.type||el.tagName)+' #'+el.id);}
 const b=getComputedStyle(document.body);if(b.userSelect!=='none'&&b.webkitUserSelect!=='none')out.push('body text selectable');
 if(document.querySelector('.fullscreen,[aria-label*="ullscreen"]'))out.push('custom fullscreen button');return out;};
(async()=>{const browser=await playwright.chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--autoplay-policy=no-user-gesture-required']});
 const report=[];const hosts=new Set();
 for(const [w,h] of SIZES){const mobile=w<h||w<=800;const ctx=await browser.newContext({viewport:{width:w,height:h},hasTouch:mobile,isMobile:mobile&&w<h});await ctx.addInitScript(fake);
  const pg=await ctx.newPage();pg.setDefaultTimeout(90000);const issues=[];let bytes=0,bytesAtStart=null;const t0=Date.now();let tStart=null;
  pg.on('pageerror',e=>issues.push('JS '+e.message));pg.on('console',m=>{if(m.type()==='error')issues.push('console '+m.text().slice(0,140));});
  pg.on('request',r=>hosts.add(new URL(r.url()).host));pg.on('response',async r=>{if(r.status()>=400)issues.push(`HTTP ${r.status()} ${r.url()}`);try{const l=+(r.headers()['content-length']||0)||(await r.body()).length;bytes+=l;}catch{}});
  await pg.route('**/main.mjs*',async r=>{const f=await r.fetch();await r.fulfill({response:f,body:(await f.text())+hooks});});
  const noShot=(process.env.NOSHOT||'').split(',');const shot=async name=>{await pg.waitForTimeout(500);if(!noShot.some(n=>n&&name.includes(n)))await pg.screenshot({path:`${OUT}/${w}x${h}-${name}.png`,timeout:90000});const t=await pg.evaluate(textAudit);if(t.tiny.length)issues.push(`${name}: text under 10px: ${t.tiny.slice(0,5).join(' | ')}`);if(t.small.length)issues.push(`${name}: text under 14px: ${t.small.slice(0,5).join(' | ')}`);if(t.overflow)issues.push(`${name}: page scrolls`);const d=await pg.evaluate(defaultsAudit);if(d.length)issues.push(`${name}: ${d.join('; ')}`);};
  await pg.goto(B);await pg.locator('#start-training,#fight').first().waitFor();const firstScreen=await pg.locator('#start-training').count()?'welcome':'menu';await shot('1-first-screen');
  if(firstScreen==='welcome'){await pg.locator('#start-training').click();await pg.waitForFunction(()=>__qa.phase()==='fight',null,{timeout:90000});tStart=Date.now()-t0;bytesAtStart=bytes;await pg.waitForTimeout(1200);await shot('2-training');await pg.locator('#lesson-skip').click();}
  await pg.locator('#fight').waitFor();await shot('3-menu');
  await pg.locator('#open-settings').click();await shot('4-settings');await pg.locator('[data-back]').first().click();
  await pg.locator('#fight').click();await shot('5-arenas');await pg.locator('[data-stage="1"]').click();await pg.locator('#confirm-fighter').click();await shot('6-fighter');
  await pg.locator('#begin').click();await pg.locator('.story-bubble').waitFor();await pg.waitForTimeout(1200);await shot('7-story');await pg.locator('#story-skip').click();
  await pg.waitForFunction(()=>__qa.phase()==='fight',null,{timeout:90000});await pg.waitForTimeout(800);await shot('8-fight');
  await pg.locator('#pause-fight').click();await shot('9-pause');await pg.locator('#resume').click();
  await pg.evaluate(()=>__qa.win());await pg.locator('.story-bubble').waitFor();await pg.waitForTimeout(900);await shot('10-win');await pg.locator('#story-skip').click();await shot('11-result');
  const sharp=await pg.evaluate(()=>{const c=document.querySelector('#arena');return c?{backing:[c.width,c.height],css:[Math.round(c.clientWidth*devicePixelRatio),Math.round(c.clientHeight*devicePixelRatio)]}:null;});
  if(sharp&&Math.abs(sharp.backing[0]-sharp.css[0])>2)issues.push(`arena canvas drawn at ${sharp.backing[0]}px wide, shown at ${sharp.css[0]}px (stretched ${(sharp.css[0]/sharp.backing[0]).toFixed(2)}x)`);
  const log=await pg.evaluate(()=>window.__sdklog.join(' '));
  report.push({size:`${w}x${h}`,firstScreen,tStartMs:tStart,mbToStart:bytesAtStart&&+(bytesAtStart/1e6).toFixed(1),mbTotal:+(bytes/1e6).toFixed(1),sdk:log,issues});await ctx.close();}
 console.log(JSON.stringify({report,hosts:[...hosts]},null,1));await browser.close();})().catch(e=>{console.error(e);process.exit(1);});
