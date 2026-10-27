import {extractSpriteFrames,spritePlacement} from './sprite-bounds.mjs';
import {FURS,COLORS,BELTS} from './campaign.mjs';
const rgb=hex=>hex.match(/[a-f\d]{2}/gi).map(v=>parseInt(v,16)/255);
const image=async src=>{const i=new Image();i.src=src;await i.decode();return i;};
export class SpriteBank {
 async load(){
  this.manifest=await fetch('assets/animations.json').then(r=>r.json());this.images=await Promise.all(this.manifest.atlases.map(a=>image('assets/'+a.file)));this.beltImages=await Promise.all(this.manifest.atlases.map((a,i)=>image('assets/belt-mask-'+i+'.png').catch(()=>null)));this.cache=new Map();this.rects=[];this.masks=[];
  this.manifest.atlases.forEach((a,ai)=>{const im=this.images[ai],c=document.createElement('canvas');c.width=im.width;c.height=im.height;const cx=c.getContext('2d',{willReadFrequently:true});cx.drawImage(im,0,0);const data=cx.getImageData(0,0,c.width,c.height).data,tw=im.width/a.columns,th=im.height/a.rows,rects=[];
   const {frames,mask}=extractSpriteFrames(im.width,im.height,data,a.columns,a.rows);
   if(frames.some(r=>!r))throw Error('Sprite atlas has an unidentified pose: '+a.file);
   this.rects.push(frames);this.masks.push(mask);
  });
  const surface=this.surface=document.createElement('canvas');surface.width=surface.height=240;
  const gl=this.gl=surface.getContext('webgl',{alpha:true,premultipliedAlpha:false,preserveDrawingBuffer:true});
  if(!gl)throw Error('Your browser needs WebGL for the customizable bunny sprites.');
  const vs='attribute vec2 position;varying vec2 uv;void main(){uv=position*.5+.5;gl_Position=vec4(position.x,-position.y,0.,1.);}';
  const fs='precision mediump float;uniform sampler2D atlas;uniform sampler2D maskTex;uniform float maskId;uniform vec4 rect;uniform vec3 gi;uniform vec3 fur;uniform sampler2D beltTex;uniform vec3 belt;uniform float beltOn;varying vec2 uv;void main(){vec2 sampleUV=rect.xy+uv*rect.zw;if(abs(texture2D(maskTex,sampleUV).r-maskId)>.001)discard;vec4 c=texture2D(atlas,sampleUV);float hi=max(c.r,max(c.g,c.b));float lo=min(c.r,min(c.g,c.b));float green=smoothstep(.025,.13,c.g-max(c.r,c.b));float saturation=(hi-lo)/max(hi,.001);float pink=smoothstep(.12,.24,c.r-c.g)*smoothstep(.08,.18,c.r-c.b);float neutral=(1.-smoothstep(.42,.60,saturation))*(1.-pink);float light=smoothstep(.18,.48,hi);c.rgb=mix(c.rgb,fur*hi,neutral*light*(1.-green));c.rgb=mix(c.rgb,gi*(.35+.8*c.g),green);if(beltOn>.5){float m=smoothstep(.15,.85,texture2D(beltTex,sampleUV).r),t=smoothstep(0.,.36,hi);c.rgb=mix(c.rgb,min(belt*(.84+.3*t),vec3(1.)),m);}gl_FragColor=c;}';
  const compile=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;};
  const p=gl.createProgram();gl.attachShader(p,compile(gl.VERTEX_SHADER,vs));gl.attachShader(p,compile(gl.FRAGMENT_SHADER,fs));gl.linkProgram(p);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(p));gl.useProgram(p);const b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,-1,1,1,-1,1,1]),gl.STATIC_DRAW);const pos=gl.getAttribLocation(p,'position');gl.enableVertexAttribArray(pos);gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);
  this.textures=this.images.map(im=>{const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);for(const [key,v]of [[gl.TEXTURE_MIN_FILTER,gl.LINEAR],[gl.TEXTURE_MAG_FILTER,gl.LINEAR],[gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE],[gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE]])gl.texParameteri(gl.TEXTURE_2D,key,v);return t;});
  gl.uniform1i(gl.getUniformLocation(p,'atlas'),0);gl.uniform1i(gl.getUniformLocation(p,'maskTex'),1);this.maskTextures=this.images.map((im,i)=>{const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,im.width,im.height,0,gl.RGBA,gl.UNSIGNED_BYTE,this.masks[i]);for(const [key,value]of [[gl.TEXTURE_MIN_FILTER,gl.NEAREST],[gl.TEXTURE_MAG_FILTER,gl.NEAREST],[gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE],[gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE]])gl.texParameteri(gl.TEXTURE_2D,key,value);return t;});gl.uniform1i(gl.getUniformLocation(p,'beltTex'),2);this.beltTextures=this.beltImages.map(im=>{if(!im)return null;const t=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,t);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,im);for(const [key,value]of [[gl.TEXTURE_MIN_FILTER,gl.LINEAR],[gl.TEXTURE_MAG_FILTER,gl.LINEAR],[gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE],[gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE]])gl.texParameteri(gl.TEXTURE_2D,key,value);return t;});this.u=Object.fromEntries(['rect','gi','fur','maskId','belt','beltOn'].map(k=>[k,gl.getUniformLocation(p,k)]));return this;
 }
 frame(animation,frame,skin){
  const beltColor=skin.belt&&BELTS[skin.belt],key=[animation,frame,skin.fur,skin.gi,beltColor||''].join('/');if(this.cache.has(key))return this.cache.get(key);
  const a=this.manifest.animations[animation],ai=a.atlas,slot=a.startFrame+Math.min(3,frame),r=this.rects[ai][slot],im=this.images[ai],gl=this.gl;
  gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.activeTexture(gl.TEXTURE2);gl.bindTexture(gl.TEXTURE_2D,this.beltTextures[ai]||null);gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,this.maskTextures[ai]);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,this.textures[ai]);gl.uniform1f(this.u.maskId,(slot+1)/255);gl.uniform4f(this.u.rect,r.x/im.width,r.y/im.height,r.w/im.width,r.h/im.height);gl.uniform3fv(this.u.gi,rgb(COLORS[skin.gi]));gl.uniform3fv(this.u.fur,rgb(FURS[skin.fur]));gl.uniform1f(this.u.beltOn,beltColor&&this.beltTextures[ai]?1:0);if(beltColor)gl.uniform3fv(this.u.belt,rgb(beltColor));gl.drawArrays(gl.TRIANGLES,0,6);
  const c=document.createElement('canvas');c.width=240;c.height=240;c.getContext('2d').drawImage(this.surface,0,0);const result={image:c,rect:r};
  if(this.cache.size>400)this.cache.delete(this.cache.keys().next().value);this.cache.set(key,result);return result;
 }
 draw(ctx,x,y,size,animation,time,skin,facing=1,{once=false}={}){
  const a=this.manifest.animations[animation],index=once?Math.min(3,Math.floor(time*a.fps)):Math.floor(time*a.fps)%4,{image,rect:r}=this.frame(animation,index,skin);
  const reference=this.rects[a.atlas][0],placement=spritePlacement(r,reference,size);
  ctx.save();ctx.translate(x,y);ctx.scale(facing,1);ctx.drawImage(image,placement.x,placement.y,placement.width,placement.height);ctx.restore();
 }
}
export class ArenaArt {
 async load(){const names=['burrows','gardens','village','tournaments','championships'];[this.images,this.portraits]=await Promise.all([Promise.all(names.map(async k=>[k,await image('assets/'+k+(k==='championships'?'':'-audience')+'.webp')])).then(Object.fromEntries),Promise.all(names.map(async k=>[k,await image('assets/'+k+'-portrait.webp')])).then(Object.fromEntries)]);return this;}
 draw(ctx,stage,w,h){const im=this.images[stage.art],sw=im.width/2,sh=im.height/2,sx=stage.panel%2*sw,sy=Math.floor(stage.panel/2)*sh,worldWidth=sw*590/sh;ctx.drawImage(im,sx,sy,sw,sh,(1000-worldWidth)/2,0,worldWidth,590);}
 portrait(ctx,stage){const im=this.portraits[stage.art],r=portraitRegion(im.width,im.height,stage.art,stage.panel);const fullWidth=im.width/2,worldWidth=fullWidth*1000/r.w;ctx.drawImage(im,(stage.panel%2)*fullWidth,r.y,fullWidth,r.h,(1000-worldWidth)/2,590-r.worldHeight,worldWidth,r.worldHeight);}
 thumbnail(stage){const c=document.createElement('canvas');c.width=320;c.height=180;const ctx=c.getContext('2d');ctx.scale(c.width/1000,c.height/590);this.draw(ctx,stage,1000,590);return c.toDataURL('image/jpeg',.85);}
}
export function star(ctx,x,y,r,color,rotation=0){ctx.save();ctx.translate(x,y);ctx.rotate(rotation);ctx.fillStyle=color;ctx.beginPath();for(let i=0;i<8;i++){const a=i*Math.PI/4,rad=i%2?r*.32:r;ctx.lineTo(Math.cos(a)*rad,Math.sin(a)*rad);}ctx.closePath();ctx.fill();ctx.restore();}
export function drawScene(ctx,bank,art,stage,time,{fighters,skins,particles=[],reduced=false,shake=0,hero=false,height=590}={}){
 const w=1000,h=height,ground=510;ctx.clearRect(0,0,w,h);ctx.save();ctx.fillStyle='#292d24';ctx.fillRect(0,0,w,h);const camera=sceneCamera(fighters??[],height);if(shake)ctx.translate(Math.sin(time*80)*shake,Math.cos(time*100)*shake*.5);ctx.translate(500,height-80);ctx.scale(camera.zoom,camera.zoom);ctx.translate(-camera.x,-ground);if(height>590&&art.portrait)art.portrait(ctx,stage);else art.draw(ctx,stage,w,590);
 const actors=fighters??[{x:hero?420:350,z:0,facing:1,animation:0,time},{x:hero?650:650,z:0,facing:-1,animation:0,time:time+.3}];
 actors.forEach((f,i)=>{ctx.fillStyle='#39271d30';ctx.beginPath();ctx.ellipse(f.x,ground-2,53-(f.z??0)*.07,9,0,0,Math.PI*2);ctx.fill();const intro=f.animation===15;ctx.save();ctx.translate(f.x,ground-(f.z??0));if(f.action==='hit'&&!reduced){const recoil=Math.sin(Math.min(1,f.time/.46)*Math.PI);ctx.rotate(-f.facing*.12*recoil);ctx.scale(1+recoil*.035,1-recoil*.05);}bank.draw(ctx,0,0,hero?240:230,intro?15:f.animation,f.time,skins[i],f.facing,{once:![0,1,2,3].includes(f.animation)});ctx.restore();if(f.hold){ctx.globalAlpha=.5+.3*Math.sin(time*8);star(ctx,f.x+f.facing*55,ground-160,13,'#ffe5a3',time);ctx.globalAlpha=1;}});
 if(!reduced)for(const p of particles){const t=(time-p.born)/p.life;if(t<0||t>1)continue;ctx.globalAlpha=1-t;star(ctx,p.x+p.vx*t,p.y+p.vy*t+60*t*t,p.size*(1-t*.6),p.color,time+p.vx);ctx.globalAlpha=1;}
 ctx.restore();
}

export function sceneCamera(fighters,height){
 const actors=fighters.length?fighters:[{x:350},{x:650}],xs=actors.map(f=>f.x),left=Math.min(...xs),right=Math.max(...xs),desired=height>900?Math.min(1.7,(height-160)/590):1;
 const zoom=Math.min(desired,1000/(right-left+350));
 const half=500/zoom,mid=(left+right)/2;
 const worldCenter=half>500?500:Math.max(half,Math.min(1000-half,mid));const minCenter=right+175-half,maxCenter=left-175+half;return {zoom,x:Math.max(minCenter,Math.min(maxCenter,worldCenter))};
}

export const PORTRAIT_SPLITS={burrows:727,gardens:768,village:730,tournaments:720,championships:704};
export function portraitRegion(width,height,theme,panel){const halfWidth=width/2,split=PORTRAIT_SPLITS[theme],top=panel<2?0:split,tileHeight=panel<2?split:height-split,coreHeight=halfWidth/2,cropWidth=coreHeight*1000/590;return {x:(panel%2)*halfWidth+(halfWidth-cropWidth)/2,y:top,w:cropWidth,h:tileHeight,worldHeight:tileHeight*590/coreHeight};}
