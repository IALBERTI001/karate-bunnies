// Renders every gi on the bunny in several poses: node tools/qa/gi-sheet.cjs out.png [query]
const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:1200,height:900}});
p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>m.type()==='error'&&console.log('CONSOLE',m.text()));
await p.goto('http://127.0.0.1:8787/qa-gi-sheet.html?'+(process.argv[3]||''));await p.waitForFunction(()=>document.title==='done',null,{timeout:120000});
await p.locator('#c').screenshot({path:process.argv[2]});await b.close();})();
