// Vector cloth prints are masked by the original painted gi material in the sprite shader.
// This preserves bare paws, fur, outlines and the separately recoloured rank belt in every pose.
export function paintGiPattern(ctx,item){
 ctx.clearRect(0,0,256,256);ctx.fillStyle=item.accent;ctx.strokeStyle=item.accent;
 if(item.collection==='halloween'){paintHalloweenPrint(ctx,item);return;}
 if(item.pattern==='sports'){paintSportsPrint(ctx,item);return;}
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

function sportsBall(ctx,sport,accent,trim){
 ctx.fillStyle=accent;ctx.strokeStyle=trim;ctx.lineWidth=1.4;
 if(sport==='hockey'||sport==='lacrosse'){
  for(const d of [-1,1]){ctx.save();ctx.scale(d,1);ctx.beginPath();ctx.moveTo(-9,-12);ctx.lineTo(7,10);ctx.lineTo(14,10);ctx.stroke();if(sport==='lacrosse'){ctx.beginPath();ctx.ellipse(-9,-13,4,6,-.5,0,7);ctx.stroke();}ctx.restore();}
  if(sport==='hockey'){ctx.fillStyle=accent;ctx.beginPath();ctx.ellipse(0,12,5,2,0,0,7);ctx.fill();}return;
 }
 if(sport==='football'){ctx.beginPath();ctx.ellipse(0,0,11,6,-.5,0,7);ctx.fill();ctx.beginPath();ctx.moveTo(-5,3);ctx.lineTo(5,-3);ctx.stroke();for(let x=-3;x<=3;x+=3){ctx.beginPath();ctx.moveTo(x-2,-2);ctx.lineTo(x+2,2);ctx.stroke();}return;}
 ctx.beginPath();ctx.arc(0,0,10,0,7);ctx.fill();
 if(sport==='basketball'){ctx.beginPath();ctx.moveTo(-10,0);ctx.lineTo(10,0);ctx.moveTo(0,-10);ctx.lineTo(0,10);ctx.stroke();for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(d*7,-7);ctx.quadraticCurveTo(-d*3,0,d*7,7);ctx.stroke();}}
 if(sport==='baseball'){for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(d*6,-8);ctx.quadraticCurveTo(-d*1,0,d*6,8);ctx.stroke();for(let y=-5;y<=5;y+=5){ctx.beginPath();ctx.moveTo(d*2,y);ctx.lineTo(d*6,y+2);ctx.stroke();}}}
 if(sport==='soccer'){ctx.beginPath();for(let k=0;k<5;k++)ctx.lineTo(Math.cos(k*1.256-1.57)*4,Math.sin(k*1.256-1.57)*4);ctx.closePath();ctx.stroke();for(let k=0;k<5;k++){const a=k*1.256-1.57;ctx.beginPath();ctx.moveTo(Math.cos(a)*4,Math.sin(a)*4);ctx.lineTo(Math.cos(a)*10,Math.sin(a)*10);ctx.stroke();}}
 if(sport==='volleyball'){for(let k=0;k<3;k++){ctx.save();ctx.rotate(k*Math.PI*2/3);ctx.beginPath();ctx.moveTo(0,0);ctx.quadraticCurveTo(8,-1,5,-8);ctx.moveTo(0,4);ctx.quadraticCurveTo(9,4,9,-3);ctx.stroke();ctx.restore();}}
}
function paintSportsPrint(ctx,item){
 const dark=item.dark??'#252a32',trim=item.trim??item.accent;
 ctx.save();
 // Jersey bands and woven piping, masked to gi fabric at runtime.
 ctx.fillStyle=dark;ctx.globalAlpha=.9;ctx.fillRect(0,113,256,14);ctx.fillRect(0,220,256,22);
 ctx.fillStyle=trim;ctx.globalAlpha=1;ctx.fillRect(0,130,256,4);ctx.fillRect(0,215,256,4);
 ctx.fillStyle=item.accent;ctx.globalAlpha=.7;ctx.fillRect(25,0,6,256);ctx.fillRect(225,0,6,256);ctx.globalAlpha=1;
 for(let row=0;row<5;row++)for(let col=0;col<5;col++){ctx.save();ctx.translate(24+col*56+(row%2?18:0),24+row*57);ctx.scale(.68,.68);sportsBall(ctx,item.sport,item.accent,trim);ctx.restore();}
 // Original fan crest: a knight visor, ace, wing, paw or team-letter patch.
 ctx.save();ctx.translate(128,173);ctx.fillStyle=dark;ctx.strokeStyle=item.accent;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(-31,-32);ctx.lineTo(31,-32);ctx.lineTo(27,13);ctx.lineTo(0,35);ctx.lineTo(-27,13);ctx.closePath();ctx.fill();ctx.stroke();
 ctx.fillStyle=item.accent;ctx.strokeStyle=item.accent;ctx.lineWidth=2;
 if(item.crest==='knight'){
  ctx.beginPath();ctx.moveTo(0,-23);ctx.lineTo(20,-13);ctx.lineTo(15,13);ctx.lineTo(3,24);ctx.lineTo(3,2);ctx.lineTo(12,-7);ctx.lineTo(3,-4);ctx.lineTo(0,3);ctx.lineTo(-3,-4);ctx.lineTo(-12,-7);ctx.lineTo(-3,2);ctx.lineTo(-3,24);ctx.lineTo(-15,13);ctx.lineTo(-20,-13);ctx.closePath();ctx.fill();
 }else if(item.crest==='ace'){
  ctx.beginPath();ctx.moveTo(0,-21);ctx.bezierCurveTo(33,0,8,19,0,7);ctx.bezierCurveTo(-8,19,-33,0,0,-21);ctx.fill();ctx.fillRect(-3,3,6,13);
 }else if(item.crest==='wings'){
  for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(0,6);ctx.lineTo(d*23,-17);ctx.lineTo(d*20,-2);ctx.lineTo(d*10,4);ctx.lineTo(d*18,2);ctx.lineTo(d*10,13);ctx.closePath();ctx.fill();}
 }else if(item.crest==='paw'){
  ctx.beginPath();ctx.ellipse(0,7,11,9,0,0,7);ctx.fill();for(const [x,y]of [[-13,-3],[-5,-12],[5,-12],[13,-3]]){ctx.beginPath();ctx.ellipse(x,y,4,5,0,0,7);ctx.fill();}
 }else if(item.crest==='bolt'){
  ctx.beginPath();ctx.moveTo(4,-24);ctx.lineTo(-14,3);ctx.lineTo(-2,3);ctx.lineTo(-8,23);ctx.lineTo(16,-7);ctx.lineTo(3,-7);ctx.closePath();ctx.fill();
 }else if(item.crest==='star'){glint(ctx,0,0,23);}
 else{ctx.font=`bold ${item.mark.length>2?14:30}px Georgia`;ctx.textAlign='center';ctx.fillText(item.mark,0,8);}
 ctx.restore();
 ctx.restore();
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

// Halloween is a cloth print: the existing shader clips every mark to the gi.
function halloweenMotif(ctx,type,accent){
 ctx.fillStyle=accent;ctx.strokeStyle=accent;ctx.lineWidth=2;ctx.lineJoin='round';ctx.lineCap='round';
 if(type==='pumpkin'){
  ctx.beginPath();ctx.ellipse(-4,1,7,10,0,0,7);ctx.ellipse(4,1,7,10,0,0,7);ctx.fill();ctx.beginPath();ctx.moveTo(0,-8);ctx.quadraticCurveTo(-4,-15,4,-15);ctx.stroke();ctx.fillStyle='#ffe6af';for(const x of [-4,4]){ctx.beginPath();ctx.arc(x,-1,1.7,0,7);ctx.fill();}ctx.strokeStyle='#ffe6af';ctx.beginPath();ctx.moveTo(-4,5);ctx.quadraticCurveTo(0,9,4,5);ctx.stroke();
 }else if(type==='ghost'){
  ctx.beginPath();ctx.moveTo(-10,12);ctx.lineTo(-10,-1);ctx.bezierCurveTo(-10,-17,10,-17,10,-1);ctx.lineTo(10,12);ctx.lineTo(4,8);ctx.lineTo(0,12);ctx.lineTo(-5,8);ctx.closePath();ctx.fill();ctx.fillStyle='#fff5e4';for(const x of [-4,4]){ctx.beginPath();ctx.ellipse(x,-1,1.5,2.5,0,0,7);ctx.fill();}ctx.strokeStyle='#fff5e4';ctx.beginPath();ctx.moveTo(-3,5);ctx.quadraticCurveTo(0,8,3,5);ctx.stroke();
 }else if(type==='bat'){
  ctx.beginPath();ctx.moveTo(-3,-4);ctx.lineTo(-5,-10);ctx.lineTo(0,-7);ctx.lineTo(5,-10);ctx.lineTo(3,-4);ctx.quadraticCurveTo(9,-11,17,-6);ctx.lineTo(11,7);ctx.quadraticCurveTo(5,2,3,12);ctx.lineTo(-3,12);ctx.quadraticCurveTo(-5,2,-11,7);ctx.lineTo(-17,-6);ctx.quadraticCurveTo(-9,-11,-3,-4);ctx.fill();ctx.fillStyle='#ffeacb';for(const x of [-2,2]){ctx.beginPath();ctx.arc(x,0,1,0,7);ctx.fill();}
 }else if(type==='candy'){
  ctx.beginPath();ctx.moveTo(0,-13);ctx.lineTo(11,11);ctx.quadraticCurveTo(0,15,-11,11);ctx.closePath();ctx.fillStyle='#fff1d0';ctx.fill();ctx.save();ctx.clip();ctx.fillStyle='#ef9143';ctx.fillRect(-14,-4,28,9);ctx.fillStyle='#f5c24f';ctx.fillRect(-14,5,28,12);ctx.restore();
 }else if(type==='cat'){
  ctx.beginPath();ctx.moveTo(-11,8);ctx.lineTo(-11,-11);ctx.lineTo(-4,-5);ctx.lineTo(4,-5);ctx.lineTo(11,-11);ctx.lineTo(11,8);ctx.quadraticCurveTo(0,16,-11,8);ctx.fill();ctx.fillStyle='#38313f';for(const x of [-4,4]){ctx.beginPath();ctx.arc(x,2,1.7,0,7);ctx.fill();}ctx.beginPath();ctx.moveTo(-2,7);ctx.lineTo(2,7);ctx.lineTo(0,10);ctx.fill();
 }else if(type==='witch'){
  ctx.beginPath();ctx.moveTo(-11,7);ctx.lineTo(-4,-12);ctx.lineTo(9,-15);ctx.lineTo(4,-7);ctx.lineTo(11,7);ctx.closePath();ctx.fill();ctx.beginPath();ctx.ellipse(0,9,16,4,0,0,7);ctx.fill();ctx.strokeStyle='#efc67d';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(-7,3);ctx.lineTo(7,3);ctx.stroke();
 }
}
function paintHalloweenPrint(ctx,item){
 ctx.save();
 if(item.motif==='candy'){ctx.fillStyle='#fff0d3';ctx.fillRect(0,105,256,35);ctx.fillStyle='#ec9344';ctx.fillRect(0,140,256,40);ctx.fillStyle='#f2bd4d';ctx.fillRect(0,180,256,76);}
 // Small trim follows the same cloth UV mapping as the existing collections.
 ctx.fillStyle=item.accent;ctx.globalAlpha=.65;ctx.fillRect(20,0,4,256);ctx.fillRect(232,0,4,256);ctx.globalAlpha=1;
 for(let row=0;row<5;row++)for(let col=0;col<5;col++){
  ctx.save();ctx.translate(22+col*54+(row%2?18:0),24+row*55);ctx.scale(.7,.7);halloweenMotif(ctx,item.motif,item.accent);ctx.restore();
 }
 // One larger readable emblem is surrounded by the small fabric repeats.
 ctx.save();ctx.translate(128,161);ctx.scale(1.45,1.45);halloweenMotif(ctx,item.motif,item.accent);ctx.restore();
 ctx.restore();
}
