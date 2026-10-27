import {mkdir,copyFile,cp,writeFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';import path from 'node:path';
const root=path.dirname(fileURLToPath(import.meta.url));const output=path.join(root,'dist');await mkdir(output,{recursive:true});
for(const file of ['index.html','style.css','main.mjs','render.mjs','sprite-bounds.mjs','campaign.mjs','combat.mjs','numbers.mjs','story.mjs','lesson.mjs'])await copyFile(path.join(root,file),path.join(output,file));
await cp(path.join(root,'assets'),path.join(output,'assets'),{recursive:true});
await writeFile(path.join(output,'BUILD.txt'),'Karate Bunnies static campaign build. Online matchmaking requires the included Node server from the source project.\n');
console.log('Static build ready in karate-bunnies/dist. Full campaign works on a static host; online VS requires server.mjs.');
