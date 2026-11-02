// Gi artwork painted once per design into small textures the sprite shader places on the body:
//  - tile:   a seamless 256px print, repeated in body space (anchored at the belt, sized to the bunny), so motifs keep
//            one size in every pose instead of stretching with the frame box
//  - emblem: an embroidered chest patch (front views) that also decorates the headband knot area
//  - back:   a large back mark (team number or a big motif) seen in back views
//  - swatch: the shop's cloth sample
const TAU=Math.PI*2;
export function glitterPhase(time,reduced=false){return reduced||!Number.isFinite(time)?0:((Math.floor(time*4)%8)+8)%8;}
function heart(ctx,x,y,r,color){ctx.fillStyle=color;ctx.beginPath();ctx.moveTo(x,y+r);ctx.bezierCurveTo(x-r*2,y,x-r,y-r*1.4,x,y-r*.35);ctx.bezierCurveTo(x+r,y-r*1.4,x+r*2,y,x,y+r);ctx.fill();}
function glint(ctx,x,y,r){ctx.beginPath();ctx.moveTo(x,y-r);ctx.quadraticCurveTo(x+r*.16,y-r*.16,x+r,y);ctx.quadraticCurveTo(x+r*.16,y+r*.16,x,y+r);ctx.quadraticCurveTo(x-r*.16,y+r*.16,x-r,y);ctx.quadraticCurveTo(x-r*.16,y-r*.16,x,y-r);ctx.fill();}
function star(ctx,x,y,r,inner=.42){ctx.beginPath();for(let p=0;p<10;p++){const a=p*Math.PI/5-Math.PI/2,q=p%2?r*inner:r;ctx.lineTo(x+Math.cos(a)*q,y+Math.sin(a)*q);}ctx.closePath();ctx.fill();}
function crescent(ctx,x,y,r,color,bg){ctx.fillStyle=color;ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.fill();ctx.save();ctx.globalCompositeOperation=bg?'source-over':'destination-out';ctx.fillStyle=bg||'#000';ctx.beginPath();ctx.arc(x+r*.45,y-r*.3,r*.85,0,TAU);ctx.fill();ctx.restore();}

// One motif centred on (0,0), about 32px across. Colours come from the design.
export function drawMotif(ctx,type,ink='#fff',item={}){
 ctx.save();ctx.fillStyle=ink;ctx.strokeStyle=ink;ctx.lineWidth=2;ctx.lineJoin='round';ctx.lineCap='round';
 switch(type){
 case 'pumpkin':ctx.fillStyle=ink==='auto'?'#ec8f3a':ink;for(const [x,w]of [[-6,8],[6,8],[0,9]]){ctx.beginPath();ctx.ellipse(x,2,w,11,0,0,TAU);ctx.fill();}ctx.strokeStyle='#b8621f';ctx.lineWidth=1.4;for(const x of [-5,5]){ctx.beginPath();ctx.moveTo(x,-7);ctx.quadraticCurveTo(x*1.5,2,x,12);ctx.stroke();}ctx.strokeStyle='#3f6a35';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(0,-8);ctx.quadraticCurveTo(-1,-14,4,-15);ctx.stroke();ctx.fillStyle='#5b8a3f';ctx.beginPath();ctx.ellipse(-6,-11,5,2.6,-.5,0,TAU);ctx.fill();ctx.fillStyle='#3b2a1d';for(const x of [-4.5,4.5]){ctx.beginPath();ctx.moveTo(x-2.5,1);ctx.lineTo(x+2.5,1);ctx.lineTo(x,-3);ctx.fill();}ctx.beginPath();ctx.moveTo(-6,5);ctx.quadraticCurveTo(0,11,6,5);ctx.quadraticCurveTo(0,8,-6,5);ctx.fill();break;
 case 'vine':ctx.globalAlpha*=1;ctx.lineWidth=2.2;ctx.beginPath();ctx.moveTo(-16,8);ctx.bezierCurveTo(-8,-6,4,10,16,-6);ctx.stroke();for(const [x,y,a]of [[-8,1,-.6],[3,3,.7],[11,-3,-.5]]){ctx.beginPath();ctx.ellipse(x,y-4,4,2.2,a,0,TAU);ctx.fill();}ctx.beginPath();ctx.arc(16,-7,2,0,TAU);ctx.stroke();break;
 case 'ghost':case 'ghosts':{const s=type==='ghosts'?.75:1;ctx.scale(s,s);ctx.beginPath();ctx.moveTo(-10,12);ctx.lineTo(-10,-1);ctx.bezierCurveTo(-10,-17,10,-17,10,-1);ctx.lineTo(10,12);ctx.lineTo(5,8);ctx.lineTo(0,12);ctx.lineTo(-5,8);ctx.closePath();ctx.fill();ctx.fillStyle=item.trim||'#5a4a72';for(const x of [-4,4]){ctx.beginPath();ctx.ellipse(x,-2,1.6,2.4,0,0,TAU);ctx.fill();}ctx.fillStyle='#f2a4b7';ctx.globalAlpha*=.7;for(const x of [-6.5,6.5]){ctx.beginPath();ctx.arc(x,2.5,1.6,0,TAU);ctx.fill();}break;}
 case 'bat':case 'bats':{const s=type==='bats'?.7:1;ctx.scale(s,s);ctx.beginPath();ctx.moveTo(0,-6);ctx.quadraticCurveTo(-6,-11,-9,-4);ctx.quadraticCurveTo(-14,-10,-20,-6);ctx.quadraticCurveTo(-15,0,-15,5);ctx.quadraticCurveTo(-10,1,-7,5);ctx.quadraticCurveTo(-4,2,0,7);ctx.quadraticCurveTo(4,2,7,5);ctx.quadraticCurveTo(10,1,15,5);ctx.quadraticCurveTo(15,0,20,-6);ctx.quadraticCurveTo(14,-10,9,-4);ctx.quadraticCurveTo(6,-11,0,-6);ctx.fill();ctx.beginPath();ctx.arc(0,-1,5.5,0,TAU);ctx.fill();for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(d*2,-5);ctx.lineTo(d*5,-10);ctx.lineTo(d*5.5,-4);ctx.fill();}if(type==='bat'){ctx.fillStyle='#fff3dc';for(const d of [-1,1]){ctx.beginPath();ctx.arc(d*2.2,-1.5,1.2,0,TAU);ctx.fill();}}break;}
 case 'candy':{ctx.beginPath();ctx.moveTo(0,-15);ctx.quadraticCurveTo(12,8,11,12);ctx.quadraticCurveTo(0,16,-11,12);ctx.quadraticCurveTo(-12,8,0,-15);ctx.closePath();ctx.save();ctx.clip();ctx.fillStyle='#fff3dc';ctx.fillRect(-14,-16,28,10);ctx.fillStyle='#f08a2c';ctx.fillRect(-14,-6,28,10);ctx.fillStyle='#f6c443';ctx.fillRect(-14,4,28,14);ctx.restore();ctx.strokeStyle='#8a4a1c';ctx.lineWidth=1.3;ctx.stroke();break;}
 case 'cat':{ctx.fillStyle=ink;ctx.beginPath();ctx.moveTo(-12,4);ctx.lineTo(-12,-14);ctx.lineTo(-4,-7);ctx.quadraticCurveTo(0,-9,4,-7);ctx.lineTo(12,-14);ctx.lineTo(12,4);ctx.quadraticCurveTo(10,13,0,15);ctx.quadraticCurveTo(-10,13,-12,4);ctx.fill();ctx.fillStyle='#c4687a';for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(d*10,-10);ctx.lineTo(d*6,-6);ctx.lineTo(d*10,-5);ctx.fill();}ctx.fillStyle='#302737';for(const d of [-1,1]){ctx.beginPath();ctx.ellipse(d*4.5,1,1.8,3,0,0,TAU);ctx.fill();}ctx.beginPath();ctx.moveTo(-2,6);ctx.lineTo(2,6);ctx.lineTo(0,8.5);ctx.closePath();ctx.fill();ctx.strokeStyle='#302737';ctx.lineWidth=1;for(const d of [-1,1])for(const y of [5,8]){ctx.beginPath();ctx.moveTo(d*8,y);ctx.lineTo(d*16,y-1.5);ctx.stroke();}break;}
 case 'witch':{ctx.beginPath();ctx.moveTo(-10,6);ctx.quadraticCurveTo(-3,-6,-1,-15);ctx.quadraticCurveTo(4,-14,10,-17);ctx.quadraticCurveTo(5,-10,8,6);ctx.closePath();ctx.fill();ctx.beginPath();ctx.ellipse(-1,7,16,4,0,0,TAU);ctx.fill();ctx.fillStyle=item.color||'#5d3a78';ctx.fillRect(-8,1,15,3.2);ctx.fillStyle='#f6d68c';ctx.fillRect(-1.5,.6,4,4);break;}
 case 'moon':crescent(ctx,0,0,13,ink,null);ctx.fillStyle=ink;star(ctx,13,-11,4);break;
 case 'night':crescent(ctx,-6,-4,6.5,ink,null);ctx.fillStyle=ink;star(ctx,9,6,3.6);ctx.beginPath();ctx.arc(9,-10,1.3,0,TAU);ctx.arc(-12,11,1.1,0,TAU);ctx.fill();break;
 case 'sparkles':glint(ctx,-5,-3,7);glint(ctx,8,8,4);ctx.beginPath();ctx.arc(9,-8,1.4,0,TAU);ctx.fill();break;
 case 'stars':star(ctx,0,0,9);ctx.beginPath();ctx.arc(12,10,1.6,0,TAU);ctx.arc(-11,-10,1.2,0,TAU);ctx.fill();break;
 case 'blossom':for(let p=0;p<5;p++){ctx.save();ctx.rotate(p*TAU/5);ctx.beginPath();ctx.moveTo(0,0);ctx.bezierCurveTo(-6,-4,-5,-11,0,-11);ctx.bezierCurveTo(5,-11,6,-4,0,0);ctx.fill();ctx.restore();}ctx.fillStyle='#f1b05e';ctx.beginPath();ctx.arc(0,0,2.6,0,TAU);ctx.fill();break;
 case 'carrot':ctx.rotate(.5);ctx.beginPath();ctx.moveTo(-5,-6);ctx.quadraticCurveTo(0,-9,5,-6);ctx.lineTo(1,12);ctx.quadraticCurveTo(0,13,-1,12);ctx.closePath();ctx.fill();ctx.strokeStyle='#c76a1f';ctx.lineWidth=1.1;for(const y of [-1,4]){ctx.beginPath();ctx.moveTo(-3,y);ctx.lineTo(0,y+1);ctx.stroke();}ctx.strokeStyle='#bfe3a1';ctx.lineWidth=2.4;for(const a of [-.5,0,.5]){ctx.beginPath();ctx.moveTo(0,-7);ctx.lineTo(Math.sin(a)*8,-7-Math.cos(a)*8);ctx.stroke();}break;
 case 'bamboo':ctx.lineWidth=2.6;ctx.beginPath();ctx.moveTo(-3,16);ctx.lineTo(-3,-16);ctx.stroke();ctx.lineWidth=1.4;for(const y of [-7,5]){ctx.beginPath();ctx.moveTo(-6,y);ctx.lineTo(0,y);ctx.stroke();}for(const [y,d]of [[-9,1],[0,-1],[9,1]]){ctx.beginPath();ctx.ellipse(-3+d*8,y,8,2.6,d*-.45,0,TAU);ctx.fill();}break;
 case 'leaf':ctx.beginPath();ctx.moveTo(0,14);ctx.bezierCurveTo(-14,4,-10,-12,0,-15);ctx.bezierCurveTo(10,-12,14,4,0,14);ctx.fill();ctx.strokeStyle=item.color||'#3f8580';ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(0,12);ctx.lineTo(0,-11);for(const y of [-5,1,7]){ctx.moveTo(0,y);ctx.lineTo(-5,y-4);ctx.moveTo(0,y);ctx.lineTo(5,y-4);}ctx.stroke();break;
 case 'flame':ctx.beginPath();ctx.moveTo(0,-16);ctx.bezierCurveTo(13,-3,12,12,0,13);ctx.bezierCurveTo(-11,12,-11,0,-5,-6);ctx.quadraticCurveTo(-4,4,0,4);ctx.quadraticCurveTo(5,0,0,-16);ctx.fill();ctx.fillStyle='#fff0b0';ctx.beginPath();ctx.moveTo(1,-3);ctx.bezierCurveTo(6,3,5,10,0,10);ctx.bezierCurveTo(-4,10,-4,5,1,-3);ctx.fill();break;
 case 'heart':heart(ctx,0,0,9,ink);break;
 case 'rainbow':['#f2a4b7','#f3d393','#b9d5aa','#a9cbe8'].forEach((c,i)=>{ctx.strokeStyle=c;ctx.lineWidth=3.2;ctx.beginPath();ctx.arc(0,6,15-i*3.3,Math.PI,TAU);ctx.stroke();});ctx.fillStyle='#fff8ee';for(const [x,r]of [[-13,4.5],[-8,5],[8,5],[13,4.5]]){ctx.beginPath();ctx.arc(x,7,r,0,TAU);ctx.fill();}break;
 case 'strawberry':ctx.fillStyle='#d64f72';ctx.beginPath();ctx.moveTo(-9,-3);ctx.bezierCurveTo(-14,5,-5,15,0,15);ctx.bezierCurveTo(5,15,14,5,9,-3);ctx.quadraticCurveTo(0,-9,-9,-3);ctx.fill();ctx.fillStyle='#ffe7ad';for(const [x,y]of [[-4,1],[4,1],[0,6],[-4,10],[4,10],[0,-2]]){ctx.beginPath();ctx.ellipse(x,y,1,1.5,0,0,TAU);ctx.fill();}ctx.fillStyle='#4f8a55';for(const a of [-1,-.35,.35,1]){ctx.beginPath();ctx.ellipse(Math.sin(a)*5,-5,2.6,5,a,0,TAU);ctx.fill();}break;
 case 'cloud':['#f2a4b7','#f3d393','#b9d5aa'].forEach((c,i)=>{ctx.strokeStyle=c;ctx.lineWidth=2.6;ctx.beginPath();ctx.arc(0,3,14-i*3,Math.PI,TAU);ctx.stroke();});ctx.fillStyle='#fffaf0';for(const [x,y,r]of [[-8,6,6],[0,2,8],[9,6,6]]){ctx.beginPath();ctx.arc(x,y,r,0,TAU);ctx.fill();}ctx.fillRect(-8,5,17,7);break;
 case 'teddy':ctx.fillStyle='#93623f';for(const x of [-8,8]){ctx.beginPath();ctx.arc(x,-8,5,0,TAU);ctx.fill();}ctx.fillStyle='#f6e2bd';ctx.beginPath();ctx.ellipse(0,1,12,11,0,0,TAU);ctx.fill();ctx.fillStyle='#93623f';for(const x of [-4,4]){ctx.beginPath();ctx.arc(x,-1,1.4,0,TAU);ctx.fill();}ctx.beginPath();ctx.ellipse(0,4,2.4,1.7,0,0,TAU);ctx.fill();heart(ctx,13,12,3.4,'#ed9ca7');break;
 case 'sleepy':crescent(ctx,0,0,12,'#fff0b6',null);ctx.strokeStyle='#8b6d9e';ctx.lineWidth=1.4;ctx.beginPath();ctx.arc(-4,1,2.4,0,Math.PI);ctx.stroke();ctx.fillStyle='#fff7df';glint(ctx,15,-12,4);glint(ctx,-15,11,3);break;
 case 'bow':case 'bows':{const colors=['#ffd7e7','#fce5a8','#dcd7ff'];ctx.fillStyle=type==='bow'?ink:colors[(item._k||0)%3];for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(0,0);ctx.bezierCurveTo(d*17,-15,d*18,10,0,0);ctx.fill();ctx.beginPath();ctx.moveTo(d*2,1);ctx.lineTo(d*10,13);ctx.lineTo(d*5,12);ctx.lineTo(d*2,15);ctx.closePath();ctx.fill();}ctx.fillStyle='#fff5de';ctx.beginPath();ctx.arc(0,0,3,0,TAU);ctx.fill();break;}
 case 'fairy':for(const d of [-1,1]){ctx.fillStyle='#ffeaf6';ctx.beginPath();ctx.ellipse(d*7,-4,6,11,d*.6,0,TAU);ctx.fill();ctx.fillStyle='#d5e9dc';ctx.beginPath();ctx.ellipse(d*6,7,5,6,-d*.7,0,TAU);ctx.fill();}heart(ctx,0,1,4,'#f3a2bc');ctx.fillStyle='#fff1b4';glint(ctx,16,-14,4);break;
 }
 ctx.restore();
}

function sportsCrest(ctx,item,size=1){
 const dark=item.lower&&item.lower!==item.color?item.lower:shade(item.color,-.35),gold=item.trim;
 ctx.save();ctx.scale(size,size);ctx.lineJoin='round';
 ctx.fillStyle=dark;ctx.strokeStyle=gold;ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(-17,-18);ctx.lineTo(17,-18);ctx.lineTo(16,4);ctx.quadraticCurveTo(12,15,0,20);ctx.quadraticCurveTo(-12,15,-16,4);ctx.closePath();ctx.fill();ctx.stroke();
 ctx.fillStyle=item.accent;ctx.strokeStyle=item.accent;ctx.lineWidth=2;
 const c=item.crest;
 if(c==='knight'){ctx.beginPath();ctx.moveTo(0,-13);ctx.quadraticCurveTo(11,-11,10,0);ctx.lineTo(8,10);ctx.lineTo(-8,10);ctx.lineTo(-10,0);ctx.quadraticCurveTo(-11,-11,0,-13);ctx.fill();ctx.fillStyle=dark;ctx.fillRect(-7,-3,14,3);ctx.fillRect(-1,-3,2,11);}
 else if(c==='ace'){ctx.beginPath();ctx.moveTo(0,-12);ctx.bezierCurveTo(18,1,5,12,0,4);ctx.bezierCurveTo(-5,12,-18,1,0,-12);ctx.fill();ctx.fillRect(-2,2,4,9);ctx.fillRect(-5,10,10,2);}
 else if(c==='wings'){for(const d of [-1,1]){ctx.beginPath();ctx.moveTo(0,4);ctx.lineTo(d*15,-11);ctx.lineTo(d*13,-2);ctx.lineTo(d*6,3);ctx.lineTo(d*12,2);ctx.lineTo(d*6,9);ctx.closePath();ctx.fill();}ctx.beginPath();ctx.arc(0,3,3,0,TAU);ctx.fill();}
 else if(c==='paw'){ctx.beginPath();ctx.ellipse(0,5,7,6,0,0,TAU);ctx.fill();for(const [x,y]of [[-8,-3],[-3,-9],[3,-9],[8,-3]]){ctx.beginPath();ctx.ellipse(x,y,2.6,3.4,0,0,TAU);ctx.fill();}}
 else if(c==='bolt'){ctx.beginPath();ctx.moveTo(3,-15);ctx.lineTo(-9,2);ctx.lineTo(-1,2);ctx.lineTo(-5,15);ctx.lineTo(10,-4);ctx.lineTo(2,-4);ctx.closePath();ctx.fill();}
 else if(c==='star'){star(ctx,0,0,13,.45);}
 else if(c==='shield'){for(const d of [-1,1]){ctx.save();ctx.rotate(d*.7);ctx.fillRect(-1.5,-14,3,26);ctx.restore();}ctx.beginPath();ctx.arc(0,-1,6,0,TAU);ctx.fill();ctx.fillStyle=dark;ctx.fillRect(-4,-3,8,2.4);}
 else{ctx.font='bold 22px Georgia, serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.fillText(item.mark||'B',0,1);}
 ctx.restore();
}
function shade(hex,amount){const v=hex.match(/[a-f\d]{2}/gi).map(h=>parseInt(h,16));return '#'+v.map(c=>Math.round(Math.max(0,Math.min(255,amount<0?c*(1+amount):c+(255-c)*amount))).toString(16).padStart(2,'0')).join('');}

// Seamless print tile. Motifs sit on a jittered 3x3 grid and are drawn again across the wrap edges.
export function paintGiTile(ctx,item){
 ctx.clearRect(0,0,256,256);const p=item.print;if(!p)return;
 ctx.save();
 if(p.motif==='pinstripe'){ctx.fillStyle=p.ink;for(let x=0;x<256;x+=32){ctx.fillRect(x+15,0,2.4,256);}ctx.restore();return;}
 if(p.motif==='hoops'){ctx.fillStyle=p.ink;ctx.fillRect(0,0,256,64);ctx.fillRect(0,128,256,64);ctx.restore();return;}
 const n=3,step=256/n;let k=0;
 for(let row=0;row<n;row++)for(let col=0;col<n;col++){
  const x=col*step+step/2+(row%2?step/2:0)+Math.sin(row*7+col*3)*7,y=row*step+step/2+Math.cos(col*5+row)*6,rot=Math.sin(row*3+col*5)*.35;
  for(const dx of [-256,0,256])for(const dy of [-256,0,256]){const cx=x+dx,cy=y+dy;if(cx<-40||cx>296||cy<-40||cy>296)continue;ctx.save();ctx.translate(cx,cy);ctx.rotate(rot);ctx.scale(1.25,1.25);drawMotif(ctx,p.motif,p.ink??item.accent,{...item,_k:k});ctx.restore();}
  k++;
 }
 ctx.restore();
}

// Embroidered patch: a cloth disc in the piping colour with a stitched rim and the motif on top.
export function paintGiEmblem(ctx,item){
 ctx.clearRect(0,0,256,256);ctx.save();ctx.translate(128,128);
 if(item.pattern==='sports'){sportsCrest(ctx,item,5.4);ctx.restore();return;}
 const motif=item.emblem||item.motif;if(!motif){ctx.restore();return;}
 ctx.fillStyle=item.trim||item.accent;ctx.beginPath();ctx.arc(0,0,112,0,TAU);ctx.fill();
 ctx.strokeStyle=shade(item.color,.55);ctx.lineWidth=7;ctx.setLineDash([16,11]);ctx.beginPath();ctx.arc(0,0,96,0,TAU);ctx.stroke();ctx.setLineDash([]);
 ctx.fillStyle=item.color;ctx.beginPath();ctx.arc(0,0,86,0,TAU);ctx.fill();
 ctx.scale(4.6,4.6);drawMotif(ctx,motif,emblemInk(item,motif),item);ctx.restore();
}
function emblemInk(item,motif){return {pumpkin:'#ec8f3a',ghost:'#f6f1ff',bat:'#3a2142',cat:'#f2a77c',witch:'#9fd3b0'}[motif]??item.accent;}
export function paintGiBack(ctx,item){
 ctx.clearRect(0,0,256,256);ctx.save();ctx.translate(128,128);
 if(item.pattern==='sports'){ctx.font='bold 150px Georgia, serif';ctx.textAlign='center';ctx.textBaseline='middle';ctx.lineWidth=16;ctx.strokeStyle=item.trim;ctx.lineJoin='round';ctx.strokeText(item.number||'1',0,8);ctx.fillStyle=item.lower&&item.lower!==item.color?item.lower:item.accent;ctx.fillText(item.number||'1',0,8);ctx.restore();return;}
 const motif=item.back||item.emblem;if(motif){ctx.scale(6.4,6.4);drawMotif(ctx,motif,emblemInk(item,motif),item);}
 ctx.restore();
}

// Shop cloth sample: jacket cloth, trouser cloth, piping and the chest patch, so the rack reads like the real gi.
export function paintGiSwatch(ctx,item,size=96){
 const s=size/96;ctx.save();ctx.clearRect(0,0,size,size);ctx.scale(s,s);
 ctx.fillStyle=item.color;ctx.fillRect(0,0,96,96);
 if(item.upper){ctx.fillStyle=item.upper;ctx.fillRect(0,0,96,22);}
 if(item.lower){ctx.fillStyle=item.lower;ctx.fillRect(0,64,96,32);}
 if(item.print){const t=document.createElement('canvas');t.width=t.height=256;paintGiTile(t.getContext('2d'),item);ctx.globalAlpha=item.print.alpha??1;ctx.drawImage(t,0,item.print.from?64:0,96,item.print.from?32:96);ctx.globalAlpha=1;}
 ctx.fillStyle='#2a2422';ctx.fillRect(0,56,96,9);
 ctx.fillStyle=item.trim;ctx.beginPath();ctx.moveTo(18,0);ctx.lineTo(48,46);ctx.lineTo(78,0);ctx.lineTo(70,0);ctx.lineTo(48,34);ctx.lineTo(26,0);ctx.fill();
 const e=document.createElement('canvas');e.width=e.height=256;paintGiEmblem(e.getContext('2d'),item);ctx.drawImage(e,58,18,28,28);
 ctx.restore();
}
// Older callers (and tests) paint the print tile.
export const paintGiPattern=(ctx,item)=>paintGiTile(ctx,item);
