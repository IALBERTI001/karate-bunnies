// Atlas grid cells identify poses; they must not limit the silhouette of a pose.
export function extractSpriteFrames(width,height,rgba,columns,rows,{alphaThreshold=32,padding=2}={}){
 const labels=new Uint32Array(width*height),frames=Array(columns*rows).fill(null),tw=width/columns,th=height/rows;let id=0;
 for(let origin=0;origin<labels.length;origin++){
  if(labels[origin]||rgba[origin*4+3]<alphaThreshold)continue;
  const component=++id,stack=[origin];labels[origin]=component;let count=0,minX=width,minY=height,maxX=0,maxY=0;
  while(stack.length){const p=stack.pop(),x=p%width,y=Math.floor(p/width);count++;minX=Math.min(minX,x);minY=Math.min(minY,y);maxX=Math.max(maxX,x);maxY=Math.max(maxY,y);
   for(const next of [x?p-1:-1,x<width-1?p+1:-1,y?p-width:-1,y<height-1?p+width:-1]){if(next<0||labels[next]||rgba[next*4+3]<alphaThreshold)continue;labels[next]=component;stack.push(next);}
  }
  if(count<20)continue;
  const col=Math.min(columns-1,Math.floor((minX+maxX)/2/tw)),row=Math.min(rows-1,Math.floor((minY+maxY)/2/th)),slot=row*columns+col;
  if(frames[slot]&&frames[slot].count>=count)continue;
  const x=Math.max(0,minX-padding),y=Math.max(0,minY-padding),right=Math.min(width,maxX+1+padding),bottom=Math.min(height,maxY+1+padding);
  frames[slot]={id:component,count,x,y,w:right-x,h:bottom-y,localX:x-col*tw,localY:y-row*th,tw,th,pivotX:(minX+maxX+1)/2-col*tw,pivotY:maxY+1-row*th};
 }
 const slots=new Map(frames.flatMap((r,n)=>r?[[r.id,n+1]]:[])),mask=new Uint8Array(width*height*4);
 for(let p=0;p<labels.length;p++){mask[p*4]=slots.get(labels[p])??0;mask[p*4+3]=255;}
 return {frames,mask};
}

export function spritePlacement(frame,standingFrame,size){
 const scale=size/(standingFrame.h*1.08);
 return {x:(frame.localX-frame.pivotX)*scale,y:(frame.localY-frame.pivotY)*scale,width:frame.w*scale,height:frame.h*scale,scale};
}

// Isolate the headband from the jacket using painted material components and the face.
// The green atlas source is a material ID, not a costume texture UV layout.
export function markHeadbands(width,height,rgba,frames,mask){
 const green=p=>rgba[p*4+3]>100&&rgba[p*4+1]>40&&rgba[p*4+1]-Math.max(rgba[p*4],rgba[p*4+2])>7;
 const white=p=>{const i=p*4,hi=Math.max(rgba[i],rgba[i+1],rgba[i+2]),lo=Math.min(rgba[i],rgba[i+1],rgba[i+2]);return rgba[i+3]>180&&lo>145&&hi-lo<58;};
 frames.forEach((r,slot)=>{
  const components=predicate=>{const seen=new Set(),out=[];for(let y=r.y;y<r.y+r.h;y++)for(let x=r.x;x<r.x+r.w;x++){const p=y*width+x;if(seen.has(p)||mask[p*4]!==slot+1||!predicate(p))continue;const pixels=[],todo=[p];seen.add(p);let x0=x,x1=x,y0=y,y1=y,sx=0,sy=0;while(todo.length){const q=todo.pop(),qx=q%width,qy=Math.floor(q/width);pixels.push(q);sx+=qx;sy+=qy;x0=Math.min(x0,qx);x1=Math.max(x1,qx);y0=Math.min(y0,qy);y1=Math.max(y1,qy);for(const n of [q-1,q+1,q-width,q+width]){const nx=n%width,ny=Math.floor(n/width);if(nx<r.x||nx>=r.x+r.w||ny<r.y||ny>=r.y+r.h||seen.has(n)||mask[n*4]!==slot+1||!predicate(n))continue;seen.add(n);todo.push(n);}}out.push({pixels,x0,x1,y0,y1,x:sx/pixels.length,y:sy/pixels.length});}return out;};
  const face=components(white).sort((a,b)=>b.pixels.length-a.pixels.length)[0],parts=components(green);if(!face||!parts.length)return;
  const pixels=parts.flatMap(c=>c.pixels);let sx=0,sy=0;for(const q of pixels){sx+=q%width;sy+=Math.floor(q/width);}let dx=face.x-sx/pixels.length,dy=face.y-sy/pixels.length;const length=Math.hypot(dx,dy)||1;dx/=length;dy/=length;
  // Follow the head's anatomical direction, including rotated launch poses.
  for(const q of pixels){const x=q%width,y=Math.floor(q/width);const headward=(x-face.x)*dx+(y-face.y)*dy,sideways=Math.abs((x-face.x)*dy-(y-face.y)*dx);if(headward> -r.h*.025||(sideways>r.w*.25&&headward> -r.h*.36))mask[q*4+1]=255;}
  let best=Infinity,bandPoint=null;for(const q of pixels)if(mask[q*4+1]){const x=q%width,y=Math.floor(q/width),forward=(x-face.x)*dx+(y-face.y)*dy,side=Math.abs((x-face.x)*dy-(y-face.y)*dx),score=(Math.abs(dy)>.7?Math.abs(x-face.x)*3:side*3)+Math.abs(forward);if(forward>=0&&score<best){best=score;bandPoint=[x,y];}}
  if(bandPoint)r.bandStamp=[(bandPoint[0]-r.x)/r.w,(bandPoint[1]-r.y)/r.h,r.h*.06/r.w,.06];
  // Distance from visible cloth edges keeps a small chest badge clear of paws and lapels.
  const rw=r.w,rh=r.h,dist=new Float32Array(rw*rh),cloth=(x,y)=>{const q=(r.y+y)*width+r.x+x;return mask[q*4]===slot+1&&!mask[q*4+1]&&green(q);};
  for(let y=0;y<rh;y++)for(let x=0;x<rw;x++)dist[y*rw+x]=cloth(x,y)?999:0;
  for(let y=0;y<rh;y++)for(let x=0;x<rw;x++){const q=y*rw+x;if(dist[q])dist[q]=Math.min(dist[q],x?dist[q-1]+1:1,y?dist[q-rw]+1:1,x&&y?dist[q-rw-1]+1.414:999);}
  for(let y=rh-1;y>=0;y--)for(let x=rw-1;x>=0;x--){const q=y*rw+x;if(dist[q])dist[q]=Math.min(dist[q],x<rw-1?dist[q+1]+1:1,y<rh-1?dist[q+rw]+1:1,x<rw-1&&y<rh-1?dist[q+rw+1]+1.414:999);}
  let score=-Infinity;const side=rh*.06,targetX=face.x-r.x-dx*rh*.25-dy*side,targetY=face.y-r.y-dy*rh*.25+dx*side,minSize=rh*.06;
  for(let y=0;y<rh;y++)for(let x=0;x<rw;x++){const headward=(r.x+x-face.x)*dx+(r.y+y-face.y)*dy;if(headward> -rh*.09||headward< -rh*.30)continue;const d=dist[y*rw+x],value=Math.min(d,minSize*.6)-Math.hypot(x-targetX,y-targetY)*.25;if(d>=Math.max(2,minSize*.3)&&value>score){score=value;const size=Math.min(Math.max(d*1.35,minSize),rh*.085);r.chestStamp=[x/rw,y/rh,size/rw,size/rh];}}


 });
 return mask;
}
