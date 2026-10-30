// Cosmetics share one saved record with their wallet: a purchase is one storage write.
export const WARDROBE_KEY='kb-wardrobe-v1';
export const GIS=Object.freeze([
 {id:'sakura',name:'Sakura Bloom',price:10,collection:'original',color:'#b85e8b',accent:'#ffe3ee',pattern:'blossom',description:'Soft pink blossoms for brave little paws.'},
 {id:'carrot',name:'Carrot Club',price:10,collection:'original',color:'#4f8d69',accent:'#ffc16a',pattern:'carrot',description:'Garden green with tiny lucky carrots.'},
 {id:'moon',name:'Moon & Stars',price:10,collection:'original',color:'#555091',accent:'#ffe7a1',pattern:'stars',description:'Midnight violet, sprinkled with starlight.'},
 {id:'bamboo',name:'Bamboo Breeze',price:10,collection:'original',color:'#418783',accent:'#c6ead0',pattern:'bamboo',description:'Cool teal with a little forest magic.'},
 {id:'flame',name:'Golden Flame',price:10,collection:'original',color:'#a84a37',accent:'#ffd476',pattern:'flame',description:'Warm ember red with golden fire.'},
 {id:'golden-knights',name:'Vegas Golden Knights',price:10,collection:'sports',color:'#b9975b',accent:'#fff0c3',trim:'#c62d43',dark:'#293137',pattern:'sports',sport:'hockey',crest:'knight',mark:'VGK',description:'Gold armor, red trim, tiny knight crests. Go Knights Go!'},
 {id:'silver-knights',name:'Henderson Silver Knights',price:10,collection:'sports',color:'#8f999f',accent:'#f2f1e9',trim:'#bca16d',dark:'#2e353c',pattern:'sports',sport:'hockey',crest:'knight',mark:'HSK',description:'Silver ice, golden details, and brave little hockey paws.'},
 {id:'aces',name:'Las Vegas Aces',price:10,collection:'sports',color:'#29282e',accent:'#cfb67d',trim:'#c82f4d',pattern:'sports',sport:'basketball',crest:'ace',mark:'ACES',description:'Black, gold, and red. A little bunny with a big hoops dream.'},
 {id:'aviators',name:'Las Vegas Aviators',price:10,collection:'sports',color:'#244863',accent:'#f5b567',trim:'#8bc7dd',pattern:'sports',sport:'baseball',crest:'wings',mark:'LV',description:'Navy skies, orange wings, and home-run bunny spirit.'},
 {id:'athletics',name:'Athletics · Vegas-bound',price:10,collection:'sports',color:'#28714e',accent:'#ffe09a',trim:'#f9f4de',pattern:'sports',sport:'baseball',crest:'letter',mark:'A',description:'Green and gold for the Athletics. Vegas ballpark planned for 2028.'},
 {id:'unlv',name:'UNLV Runnin’ Rebels',price:10,collection:'sports',color:'#be3549',accent:'#fff3e7',trim:'#aeb8be',pattern:'sports',sport:'basketball',crest:'letter',mark:'UNLV',description:'Scarlet hoops pride for the tiniest Runnin’ Rebel.'},
 {id:'lights',name:'Las Vegas Lights FC',price:10,collection:'sports',color:'#335d9c',accent:'#ffe768',trim:'#ef9db8',pattern:'sports',sport:'soccer',crest:'bolt',mark:'LV',description:'Electric blue, sunny gold, and goal-scoring little paws.'},
 {id:'knight-hawks',name:'Vegas Knight Hawks',price:10,collection:'sports',color:'#33475b',accent:'#dde5e8',trim:'#879aaf',pattern:'sports',sport:'football',crest:'wings',mark:'VKH',description:'Steel wings and indoor football spirit. Ready to soar!'},
 {id:'desert-dogs',name:'Las Vegas Desert Dogs',price:10,collection:'sports',color:'#353138',accent:'#f0e9de',trim:'#a5afb4',pattern:'sports',sport:'lacrosse',crest:'paw',mark:'LVDD',description:'A tiny paw pack, crossed sticks, and desert-day courage.'},
 {id:'thrill',name:'Vegas Thrill',price:10,collection:'sports',color:'#56a7bf',accent:'#f2f6ff',trim:'#ef9bbe',pattern:'sports',sport:'volleyball',crest:'star',mark:'THRILL',description:'Sky-blue volleyball dreams with pink star power.'},
 {id:'raiders',name:'Raiders Football',price:10,collection:'sports',color:'#20232a',accent:'#c4c8cc',pattern:'raiders',sport:'football',description:'Black and silver. Game-day bunny spirit.'},
 {id:'strawberry',name:'Strawberry Sugar',price:10,collection:'glitter',color:'#df88aa',accent:'#fff0e4',pattern:'strawberry',glitter:true,description:'Blushing berries, tiny hearts, sugar-sweet shimmer.'},
 {id:'cloud',name:'Cloud Cuddle',price:10,collection:'glitter',color:'#82bcd5',accent:'#fff6e8',pattern:'cloud',glitter:true,description:'Fluffy clouds and little rainbows, dusted in starlight.'},
 {id:'honey',name:'Honey Hug',price:10,collection:'glitter',color:'#d5a05d',accent:'#fff0c9',pattern:'teddy',glitter:true,description:'Pocket-size teddy friends with honey-gold sparkle.'},
 {id:'lavender',name:'Lavender Lullaby',price:10,collection:'glitter',color:'#a38aca',accent:'#fff0b6',pattern:'sleepy',glitter:true,description:'Sleepy moons and star kisses. Dream, then sparkle.'},
 {id:'ribbon',name:'Rainbow Ribbon',price:10,collection:'glitter',color:'#79b9a9',accent:'#ffe5ec',pattern:'bows',glitter:true,description:'Pastel bows tied with a sprinkle of rainbow glitter.'},
 {id:'fairy',name:'Fairy Floss',price:10,collection:'glitter',color:'#c18fcb',accent:'#ffeaf6',pattern:'fairy',glitter:true,description:'Fairy wings, candy hearts, and a little wishful twinkle.'}
]);
export const giDesign=id=>GIS.find(g=>g.id===id)??null;
export const GI_COLLECTIONS=[{id:'all',name:'All Gi'},{id:'owned',name:'Owned'},{id:'glitter',name:'Glitter Collection'},{id:'sports',name:'Sports Collection'},{id:'original',name:'Original Favorites'}];
export const collectionGis=(id,owned=[])=>id==='all'?GIS:GIS.filter(g=>id==='owned'?Array.isArray(owned)&&owned.includes(g.id):g.collection===id);
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
