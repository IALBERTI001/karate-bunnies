// Vector cloth prints are masked by the original painted gi material in the sprite shader.
// This preserves bare paws, fur, outlines and the separately recoloured rank belt in every pose.
export function paintGiPattern(ctx,item){
 ctx.clearRect(0,0,256,256);ctx.fillStyle=item.accent;ctx.strokeStyle=item.accent;
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
