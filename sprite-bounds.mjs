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
