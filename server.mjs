import http from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {randomBytes,randomUUID,timingSafeEqual} from 'node:crypto';
import {createMatch,input,step} from './combat.mjs';
import {validSkin} from './campaign.mjs';
const root=path.dirname(fileURLToPath(import.meta.url)),port=Number(process.env.PORT)||8787,host=process.env.HOST||'127.0.0.1';
const sessions=new Map(),rooms=new Map();
const mime={'.html':'text/html; charset=utf-8','.mjs':'text/javascript; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.png':'image/png','.webp':'image/webp','.svg':'image/svg+xml'};
const json=(res,status,value)=>{res.writeHead(status,{'Content-Type':'application/json','Cache-Control':'no-store'});res.end(JSON.stringify(value));};
async function body(req){let raw='';for await(const part of req){raw+=part;if(raw.length>16384)throw Object.assign(Error('Request too large'),{status:413});}try{return JSON.parse(raw||'{}');}catch{throw Object.assign(Error('Invalid request'),{status:400});}}
function auth(data){const s=sessions.get(data.id);if(!s||typeof data.token!=='string'||data.token.length!==s.token.length||!timingSafeEqual(Buffer.from(data.token),Buffer.from(s.token)))throw Object.assign(Error('Session expired. Search again.'),{status:401});s.lastSeen=performance.now();return s;}
function leave(s){if(s.room){const r=rooms.get(s.room);if(r){r.left.add(s.id);if(r.match.phase==='intro')r.aborted=true;else if(r.match.phase==='fight'){r.match.phase='done';r.match.result=r.ids.indexOf(s.id)===0?'opponent':'player';r.reason='disconnect';}}}sessions.delete(s.id);}
const server=http.createServer(async(req,res)=>{res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','same-origin');res.setHeader('Permissions-Policy','camera=(), microphone=(), geolocation=()');
 try{const url=new URL(req.url,'http://localhost');
 if(url.pathname.startsWith('/api/')){if(req.method!=='POST')return json(res,405,{error:'Use POST'});if(req.headers.origin){const origin=new URL(req.headers.origin);if(origin.host!==req.headers.host)return json(res,403,{error:'Origin not allowed'});}const data=await body(req);
  if(url.pathname==='/api/queue'){
   if(sessions.size>=200)return json(res,503,{error:'The matchmaking dojo is full. Please try again.'});const now=performance.now(),id=randomUUID(),token=randomBytes(24).toString('hex');const s={id,token,skin:validSkin(data.skin),lastSeen:now,created:now,room:null,lastSeq:0,rateTime:now,events:0};sessions.set(id,s);
   const peer=[...sessions.values()].find(p=>p.id!==id&&!p.room&&now-p.lastSeen<12000);
   if(peer){const rid=randomUUID(),stage=17;const r={id:rid,ids:[peer.id,id],skins:[peer.skin,s.skin],match:createMatch({stage,online:true}),left:new Set(),rematch:new Set(),stage,aborted:false,created:now};for(const f of r.match.fighters)f.animation=15;rooms.set(rid,r);peer.room=rid;s.room=rid;}
   return json(res,200,{id,token});
  }
  const s=auth(data);
  if(url.pathname==='/api/leave'){leave(s);return json(res,200,{ok:true});}
  const room=rooms.get(s.room);
  if(url.pathname==='/api/rematch'){if(!room||room.match.phase!=='done'||room.left.size)return json(res,409,{error:'Opponent unavailable'});room.rematch.add(s.id);if(room.rematch.size===2){room.match=createMatch({stage:room.stage,online:true});for(const f of room.match.fighters)f.animation=15;room.rematch.clear();room.created=performance.now();}return json(res,200,{ok:true});}
  if(url.pathname==='/api/poll'){
   if(!room)return json(res,200,{status:'waiting'});
   if(room.aborted)return json(res,200,{status:'opponent-left'});
   const index=room.ids.indexOf(s.id),now=performance.now();if(now-s.rateTime>1000){s.rateTime=now;s.events=0;}
   for(const c of (Array.isArray(data.commands)?data.commands:[]).slice(0,64)){if(!c||typeof c!=='object'||!Number.isSafeInteger(c.seq)||c.seq<=s.lastSeq)continue;s.lastSeq=c.seq;if(++s.events>100)continue;if(!['direction','attackDown','attackUp','attackCancel','reset'].includes(c.type))continue;input(room.match,index,c);}
   return json(res,200,{status:'matched',match:room.match,index,stage:room.stage,skins:room.skins,opponentLeft:room.left.size>0,rematchWaiting:room.rematch.size>0&&!room.rematch.has(s.id),reason:room.reason});
  }
  return json(res,404,{error:'Unknown action'});
 }
 if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);res.end();return;}
 const requested=decodeURIComponent(url.pathname==='/'?'/index.html':url.pathname),target=path.resolve(root,'.'+requested);if(!target.startsWith(root+path.sep)||!mime[path.extname(target)]||['server.mjs','combat.test.mjs','build.mjs','prepare-assets.cjs','qa.cjs'].includes(path.basename(target))){res.writeHead(404);res.end();return;}
 const info=await stat(target);if(!info.isFile()){res.writeHead(404);res.end();return;}res.writeHead(200,{'Content-Type':mime[path.extname(target)],'Cache-Control':path.extname(target)==='.webp'||path.extname(target)==='.png'?'public, max-age=3600':'no-cache'});res.end(req.method==='HEAD'?undefined:await readFile(target));
 }catch(e){if(!res.headersSent){if(e.code==='ENOENT'||e.code==='ENOTDIR'){res.writeHead(404);res.end();}else json(res,e.status||500,{error:e.status?e.message:'The dojo had a hiccup. Please retry.'});}else res.end();}
});
let previous=performance.now(),acc=0;
setInterval(()=>{const now=performance.now();acc+=Math.min(.1,(now-previous)/1000);previous=now;while(acc>=1/60){for(const r of rooms.values())if(!r.aborted)step(r.match,1/60,{ai:false});acc-=1/60;}for(const s of sessions.values())if(now-s.lastSeen>15000)leave(s);for(const [id,r]of rooms)if(r.left.size===2||now-r.created>300000)rooms.delete(id);},1000/60).unref();
server.listen(port,host,()=>console.log(`Karate Bunnies is ready at http://${host}:${port}`));
