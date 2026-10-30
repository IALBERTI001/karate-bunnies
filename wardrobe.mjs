// Cosmetics share one saved record with their wallet: a purchase is one storage write.
export const WARDROBE_KEY='kb-wardrobe-v1';
export const GIS=Object.freeze([
 {id:'sakura',name:'Sakura Bloom',price:10,color:'#b85e8b',accent:'#ffe3ee',pattern:'blossom',description:'Soft pink blossoms for brave little paws.'},
 {id:'carrot',name:'Carrot Club',price:10,color:'#4f8d69',accent:'#ffc16a',pattern:'carrot',description:'Garden green with tiny lucky carrots.'},
 {id:'moon',name:'Moon & Stars',price:10,color:'#555091',accent:'#ffe7a1',pattern:'stars',description:'Midnight violet, sprinkled with starlight.'},
 {id:'bamboo',name:'Bamboo Breeze',price:10,color:'#418783',accent:'#c6ead0',pattern:'bamboo',description:'Cool teal with a little forest magic.'},
 {id:'flame',name:'Golden Flame',price:10,color:'#a84a37',accent:'#ffd476',pattern:'flame',description:'Warm ember red with golden fire.'},
 {id:'raiders',name:'Raiders Football',price:10,color:'#20232a',accent:'#c4c8cc',pattern:'raiders',description:'Black and silver. Game-day bunny spirit.'},
 {id:'strawberry',name:'Strawberry Sugar',price:10,color:'#df88aa',accent:'#fff0e4',pattern:'strawberry',glitter:true,description:'Blushing berries, tiny hearts, sugar-sweet shimmer.'},
 {id:'cloud',name:'Cloud Cuddle',price:10,color:'#82bcd5',accent:'#fff6e8',pattern:'cloud',glitter:true,description:'Fluffy clouds and little rainbows, dusted in starlight.'},
 {id:'honey',name:'Honey Hug',price:10,color:'#d5a05d',accent:'#fff0c9',pattern:'teddy',glitter:true,description:'Pocket-size teddy friends with honey-gold sparkle.'},
 {id:'lavender',name:'Lavender Lullaby',price:10,color:'#a38aca',accent:'#fff0b6',pattern:'sleepy',glitter:true,description:'Sleepy moons and star kisses. Dream, then sparkle.'},
 {id:'ribbon',name:'Rainbow Ribbon',price:10,color:'#79b9a9',accent:'#ffe5ec',pattern:'bows',glitter:true,description:'Pastel bows tied with a sprinkle of rainbow glitter.'},
 {id:'fairy',name:'Fairy Floss',price:10,color:'#c18fcb',accent:'#ffeaf6',pattern:'fairy',glitter:true,description:'Fairy wings, candy hearts, and a little wishful twinkle.'}
]);
export const giDesign=id=>GIS.find(g=>g.id===id)??null;
export const balanceValue=value=>Number.isFinite(Number(value))?Math.max(0,Math.min(Number.MAX_SAFE_INTEGER,Math.floor(Number(value)))):0;
export function loadWardrobe(raw,legacyBalance=0){
 try{const v=typeof raw==='string'?JSON.parse(raw):raw;
  if(!v||v.version!==1)return {version:1,balance:balanceValue(legacyBalance),owned:[],equipped:null};
  const owned=[...new Set((Array.isArray(v.owned)?v.owned:[]).filter(id=>giDesign(id)))];
  return {version:1,balance:balanceValue(v.balance),owned,equipped:owned.includes(v.equipped)?v.equipped:null};
 }catch{return {version:1,balance:balanceValue(legacyBalance),owned:[],equipped:null};}
}
export function purchaseGi(wallet,id){
 const item=giDesign(id);if(!item)return {ok:false,reason:'Unknown gi.'};
 if(wallet.owned.includes(id))return {ok:false,reason:'Already in your wardrobe.'};
 if(wallet.balance<item.price)return {ok:false,reason:`You need ${item.price-wallet.balance} more carrots.`};
 return {ok:true,wallet:{...wallet,balance:wallet.balance-item.price,owned:[...wallet.owned,id],equipped:id}};
}
export function equipGi(wallet,id){
 if(id!==null&&!wallet.owned.includes(id))return {ok:false,reason:'Buy this gi before wearing it.'};
 return {ok:true,wallet:{...wallet,equipped:id}};
}
// The old carrot key is a compatibility mirror; only this single record owns the balance.
export function persistWardrobe(storage,wallet){
 if(!storage.write(WARDROBE_KEY,wallet))return false;
 storage.write('kb-carrots-v1',wallet.balance);return true;
}
