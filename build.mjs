import {mkdir,copyFile,cp,writeFile,readdir,rm} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';import path from 'node:path';
// Static upload package (CrazyGames and other hosts): game code, used assets only, and a dated build stamp shown in Settings.
const root=path.dirname(fileURLToPath(import.meta.url));const output=path.join(root,'dist');await rm(output,{recursive:true,force:true});await mkdir(output,{recursive:true});
for(const file of ['index.html','style.css','main.mjs','render.mjs','sprite-bounds.mjs','campaign.mjs','combat.mjs','numbers.mjs','story.mjs','lesson.mjs','sdk.mjs','music.mjs','wardrobe.mjs','gi-patterns.mjs'])await copyFile(path.join(root,file),path.join(output,file));
const UNUSED=new Set(['character-lineup.png','belt-mask-0.png','belt-mask-1.png','belt-mask-2.png','belt-mask-3.png']);
await cp(path.join(root,'assets'),path.join(output,'assets'),{recursive:true,filter:src=>!UNUSED.has(path.basename(src))&&!/^(belt-mask|parts-pass)-3d-/.test(path.basename(src))});
const stamp=new Date().toISOString().slice(0,16).replace('T',' ')+' UTC';
await writeFile(path.join(output,'version.mjs'),`export const BUILD = '${stamp}';\n`);
console.log(`Static build ${stamp} ready in dist (${(await readdir(path.join(output,'assets'))).length} assets). Online VS needs server.mjs and stays hidden.`);
