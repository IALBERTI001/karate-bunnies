// Version the complete browser module graph so returning players do not mix releases.
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
const files=['index.html','style.css','main.mjs','render.mjs','sprite-bounds.mjs','campaign.mjs','combat.mjs','numbers.mjs','story.mjs','lesson.mjs','wardrobe.mjs','gi-patterns.mjs'];
const root=new URL('./',import.meta.url),sources=await Promise.all(files.map(f=>readFile(new URL(f,root),'utf8')));
const normalize=s=>s.replace(/\r\n/g,'\n').replace(/\?v=[a-f\d]{12}/g,'');
const version=createHash('sha256').update(sources.map((s,i)=>files[i]+'\n'+normalize(s)).join('\n')).digest('hex').slice(0,12);
let stale=false;
for(let i=0;i<files.length;i++){
 let next=sources[i];
 if(files[i].endsWith('.mjs'))next=next.replace(/(from\s+['"])(\.\/[^'"]+\.mjs)(?:\?v=[a-f\d]{12})?(['"])/g,(_,a,b,c)=>a+b+'?v='+version+c);
 if(files[i]==='index.html')next=next.replace(/(href="style\.css|src="main\.mjs)(?:\?v=[a-f\d]{12})?(")/g,(_,a,b)=>a+'?v='+version+b);
 if(next!==sources[i]){stale=true;if(!process.argv.includes('--check'))await writeFile(new URL(files[i],root),next);}
}
if(stale&&process.argv.includes('--check')){console.error('Browser asset versions are stale. Run node refresh-assets.mjs and commit the updated URLs.');process.exitCode=1;}
else console.log(`Browser asset release ${version} ${stale?'updated':'verified'}.`);
