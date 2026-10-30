// Vector cloth prints are masked by the original painted gi material in the sprite shader.
// This preserves bare paws, fur, outlines and the separately recoloured rank belt in every pose.
export function paintGiPattern(ctx,item){
 ctx.clearRect(0,0,256,256);ctx.fillStyle=item.accent;ctx.strokeStyle=item.accent;
 if(item.glitter){paintCutePrint(ctx,item);return;}
 if(item.pattern==='raiders'){
  ctx.globalAlpha=.8;ctx.fillRect(24,0,12,256);ctx.fillRect(220,0,12,256);
  ctx.globalAlpha=.25;ctx.fillRect(44,0,3,256);ctx.fillRect(209,0,3,256);ctx.globalAlpha=1;
  // Original football fan crest, rather than a pasted logo outside the clothing silhouette.
  ctx.save();ctx.translate(128,160);ctx.beginPath();ctx.moveTo(-31,-31);ctx.lineTo(31,-31);ctx.lineTo(27,14);ctx.lineTo(0,35);ctx.lineTo(-27,14);ctx.closePath();
  ctx.fillStyle='#c4c8cc';ctx.fill();ctx.lineWidth=3;ctx.strokeStyle='#f6f4ec';ctx.stroke();
  ctx.fillStyle='#16191e';ctx.fillRect(-27,-26,54,17);ctx.font='bold 10px sans-serif';ctx.textAlign='center';ctx.fillStyle='#fff';ctx.fillText('RAIDERS',0,-14);
  ctx.strokeStyle='#20232a';ctx.lineWidth=3;for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(-17*d,19);ctx.lineTo(17*d,-2);ctx.stroke();}
  ctx.fillStyle='#20232a';ctx.beginPath();ctx.ellipse(0,4,14,9,-.4,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(-7,7);ctx.lineTo(7,1);ctx.stroke();for(let i=-4;i<=4;i+=4){ctx.beginPath();ctx.moveTo(i-1,1);ctx.lineTo(i+2,7);ctx.stroke();}ctx.restore();return;
 }
 for(let row=0;row<7;row++)for(let col=0;col<7;col++){
  ctx.save();ctx.translate(col*42+(row%2?18:0),row*42);ctx.rotate((col%3-1)*.25);ctx.globalAlpha=.88;
  if(item.pattern==='blossom'){for(let p=0;p<5;p++){ctx.save();ctx.rotate(p*Math.PI*2/5);ctx.beginPath();ctx.ellipse(0,-5,3.5,5,0,0,Math.PI*2);ctx.fill();ctx.restore();}ctx.fillStyle='#f1ba69';ctx.beginPath();ctx.arc(0,0,2,0,Math.PI*2);ctx.fill();}
  if(item.pattern==='stars'){ctx.beginPath();for(let p=0;p<10;p++){const a=p*Math.PI/5-Math.PI/2,r=p%2?3:8;ctx.lineTo(Math.cos(a)*r,Math.sin(a)*r);}ctx.closePath();ctx.fill();ctx.beginPath();ctx.arc(13,12,1.5,0,7);ctx.fill();}
  if(item.pattern==='carrot'){ctx.beginPath();ctx.moveTo(-5,-5);ctx.quadraticCurveTo(0,-10,5,-5);ctx.lineTo(0,10);ctx.closePath();ctx.fill();ctx.strokeStyle='#d5edb6';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,-5);ctx.lineTo(-4,-12);ctx.moveTo(0,-5);ctx.lineTo(4,-12);ctx.stroke();}
  if(item.pattern==='bamboo'){ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,-16);ctx.lineTo(0,16);ctx.moveTo(-3,-7);ctx.lineTo(3,-7);ctx.moveTo(-3,7);ctx.lineTo(3,7);ctx.stroke();for(const d of [-1,1]){ctx.beginPath();ctx.ellipse(d*6,-2,3,8,d*.7,0,7);ctx.fill();}}
  if(item.pattern==='flame'){ctx.beginPath();ctx.moveTo(0,-13);ctx.bezierCurveTo(12,-1,11,10,0,11);ctx.bezierCurveTo(-10,10,-9,0,-4,-5);ctx.quadraticCurveTo(-3,4,0,4);ctx.quadraticCurveTo(4,0,0,-13);ctx.fill();}
  ctx.restore();
 }
}

// Eight reusable shimmer frames keep sprite caching bounded; reduced motion is a still finish.
export function glitterPhase(time,reduced=false){return reduced||!Number.isFinite(time)?0:((Math.floor(time*4)%8)+8)%8;}
function heart(ctx,x,y,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(x,y+r);ctx.bezierCurveTo(x-r*2,y,x-r,y-r*1.4,x,y-r*.35);ctx.bezierCurveTo(x+r,y-r*1.4,x+r*2,y,x,y+r);ctx.fill();}
function glint(ctx,x,y,r){ctx.beginPath();ctx.moveTo(x,y-r);ctx.quadraticCurveTo(x+r*.16,y-r*.16,x+r,y);ctx.quadraticCurveTo(x+r*.16,y+r*.16,x,y+r);ctx.quadraticCurveTo(x-r*.16,y+r*.16,x-r,y);ctx.quadraticCurveTo(x-r*.16,y-r*.16,x,y-r);ctx.fill();}
function paintCutePrint(ctx,item){
 for(let row=0;row<6;row++)for(let col=0;col<6;col++){
  ctx.save();ctx.translate(18+col*46+(row%2?20:0),18+row*46);ctx.rotate((col%3-1)*.14);ctx.fillStyle=item.accent;ctx.strokeStyle=item.accent;ctx.lineWidth=2;
  if(item.pattern==='strawberry'){
   ctx.fillStyle='#c74d70';ctx.beginPath();ctx.moveTo(-8,-3);ctx.bezierCurveTo(-13,4,-5,14,0,15);ctx.bezierCurveTo(5,14,13,4,8,-3);ctx.quadraticCurveTo(0,-9,-8,-3);ctx.fill();
   ctx.fillStyle='#fce7ad';for(const [x,y]of [[-4,1],[4,1],[0,6],[-3,9],[3,9]]){ctx.beginPath();ctx.ellipse(x,y,1,1.5,0,0,7);ctx.fill();}
   ctx.fillStyle='#527e58';for(const x of [-5,0,5]){ctx.beginPath();ctx.ellipse(x,-5,3,5,x*.15,0,7);ctx.fill();}heart(ctx,15,-13,3,item.accent);
  }
  if(item.pattern==='cloud'){
   const rainbow=['#f2a4b7','#f3d393','#b9d5aa'];rainbow.forEach((c,i)=>{ctx.strokeStyle=c;ctx.lineWidth=2.5;ctx.beginPath();ctx.arc(0,1,14-i*3,Math.PI,Math.PI*2);ctx.stroke();});
   ctx.fillStyle=item.accent;for(const [x,y,r]of [[-8,5,6],[0,1,8],[9,5,6]]){ctx.beginPath();ctx.arc(x,y,r,0,7);ctx.fill();}ctx.fillRect(-8,4,17,6);
  }
  if(item.pattern==='teddy'){
   ctx.fillStyle='#93623f';for(const x of [-8,8]){ctx.beginPath();ctx.arc(x,-7,5,0,7);ctx.fill();}ctx.fillStyle=item.accent;ctx.beginPath();ctx.ellipse(0,1,12,11,0,0,7);ctx.fill();ctx.fillStyle='#93623f';for(const x of [-4,4]){ctx.beginPath();ctx.arc(x,0,1.3,0,7);ctx.fill();}ctx.beginPath();ctx.ellipse(0,5,2.2,1.6,0,0,7);ctx.fill();heart(ctx,13,14,3.5,'#ed9ca7');
  }
  if(item.pattern==='sleepy'){
   ctx.beginPath();ctx.arc(0,0,12,-Math.PI*.65,Math.PI*.65);ctx.bezierCurveTo(-4,6,-4,-6,-5,-11);ctx.closePath();ctx.fill();ctx.strokeStyle='#8b6d9e';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(3,1,2.5,0,Math.PI);ctx.stroke();ctx.fillStyle='#ffeaf4';glint(ctx,16,-12,4);glint(ctx,-16,10,3);
  }
  if(item.pattern==='bows'){
   const color=['#ffd7e7','#fce5a8','#dcd7ff'][(row+col)%3];ctx.fillStyle=color;for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(0,0);ctx.bezierCurveTo(d*17,-16,d*18,10,0,0);ctx.fill();ctx.beginPath();ctx.moveTo(d*2,1);ctx.lineTo(d*10,13);ctx.lineTo(d*5,12);ctx.lineTo(d*2,15);ctx.closePath();ctx.fill();}ctx.fillStyle='#fff5de';ctx.beginPath();ctx.arc(0,0,3,0,7);ctx.fill();
  }
  if(item.pattern==='fairy'){
   for(const d of [-1,1]){ctx.fillStyle=item.accent;ctx.beginPath();ctx.ellipse(d*7,-4,6,11,d*.6,0,7);ctx.fill();ctx.fillStyle='#d5e9dc';ctx.beginPath();ctx.ellipse(d*6,7,5,6,-d*.7,0,7);ctx.fill();}heart(ctx,0,1,4,'#f3a2bc');ctx.fillStyle='#fff1b4';glint(ctx,17,-14,4);
  }
  ctx.restore();
 }
 // Tiny pearly flecks and four-point glints also show on the shop's cloth swatches.
 ctx.save();ctx.fillStyle='#fff9e6';for(let i=0;i<130;i++){const x=(i*73+19)%256,y=(i*113+37)%256;ctx.globalAlpha=.35+(i%4)*.14;ctx.fillRect(x,y,i%5===0?1.5:.8,i%5===0?1.5:.8);}
 ctx.globalAlpha=.9;for(let i=0;i<13;i++)glint(ctx,(i*67+28)%256,(i*97+31)%256,i%3===0?4:2.5);ctx.restore();
}
