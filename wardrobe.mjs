// Cosmetics share one saved record with their wallet: a purchase is one storage write.
export const WARDROBE_KEY='kb-wardrobe-v1';
// Each gi is a garment, not a wallpaper: jacket colour, piping (collar, cuffs, hems from assets/gi-parts-*.png),
// optional trouser and shoulder colours split at the belt, a body-anchored print, an embroidered chest patch,
// a back mark seen in back views, and a headband with its own edge stitching. color/accent stay for older callers.
export const GIS=Object.freeze([
 {id:'pumpkin-patch',name:'Pumpkin Patch',price:10,collection:'halloween',color:'#ec8f3a',accent:'#3f6a35',trim:'#3f6a35',band:'#ec8f3a',bandTrim:'#3f6a35',pattern:'halloween',motif:'pumpkin',print:{motif:'vine',ink:'#c96d22',scale:.55,alpha:.55},emblem:'pumpkin',back:'pumpkin',description:'Pumpkin orange with moss-green piping and a grinning pumpkin patch.'},
 {id:'friendly-ghost',name:'Friendly Ghost',price:10,collection:'halloween',color:'#f1eadb',accent:'#9b87c4',trim:'#9b87c4',band:'#f1eadb',bandTrim:'#9b87c4',pattern:'halloween',motif:'ghost',print:{motif:'ghosts',ink:'#ddd2ee',scale:.6,alpha:.9},emblem:'ghost',back:'ghost',description:'Soft ivory, lavender piping, and little ghosts who only say boo-nny.'},
 {id:'batty-lavender',name:'Batty Lavender',price:10,collection:'halloween',color:'#b493d6',accent:'#4e2d5c',trim:'#4e2d5c',lower:'#9a78c2',band:'#b493d6',bandTrim:'#4e2d5c',pattern:'halloween',motif:'bat',print:{motif:'bats',ink:'#7d5aa3',scale:.6,alpha:.7},emblem:'bat',back:'bat',description:'Dusty lavender, deep plum piping and a round-winged bat crest.'},
 {id:'candy-corn',name:'Candy Corn',price:10,collection:'halloween',color:'#f08a2c',accent:'#fff1d6',trim:'#fff1d6',upper:'#fff1d6',lower:'#f6c443',band:'#f08a2c',bandTrim:'#f6c443',pattern:'halloween',motif:'candy',emblem:'candy',back:'candy',description:'Ivory shoulders, pumpkin middle and honey-yellow trousers. Sweet little karate.'},
 {id:'moonlit-kitty',name:'Moonlit Kitty',price:10,collection:'halloween',color:'#33303d',accent:'#f2a77c',trim:'#f2a77c',band:'#33303d',bandTrim:'#f2a77c',pattern:'halloween',motif:'cat',print:{motif:'night',ink:'#f6d68c',scale:.5,alpha:.85},emblem:'cat',back:'moon',description:'Midnight charcoal, peach piping, a whiskered kitty and a sky of tiny stars.'},
 {id:'little-witch',name:'Little Witch',price:10,collection:'halloween',color:'#5d3a78',accent:'#9fd3b0',trim:'#9fd3b0',band:'#5d3a78',bandTrim:'#9fd3b0',pattern:'halloween',motif:'witch',print:{motif:'sparkles',ink:'#9fd3b0',scale:.55,alpha:.6},emblem:'witch',back:'witch',description:'Blackberry purple, mint piping and a little witch-hat patch.'},
 {id:'sakura',name:'Sakura Bloom',price:10,collection:'original',color:'#c4628f',accent:'#ffe3ee',trim:'#7a2e52',band:'#c4628f',bandTrim:'#ffe3ee',pattern:'blossom',print:{motif:'blossom',ink:'#ffe3ee',scale:.5,alpha:.95},emblem:'blossom',back:'blossom',description:'Soft pink blossoms drifting over rose cloth.'},
 {id:'carrot',name:'Carrot Club',price:10,collection:'original',color:'#4f8d69',accent:'#ffb85c',trim:'#ffb85c',band:'#4f8d69',bandTrim:'#ffb85c',pattern:'carrot',print:{motif:'carrot',ink:'#ffb85c',scale:.55,alpha:.95},emblem:'carrot',back:'carrot',description:'Garden green with tiny lucky carrots and carrot-orange piping.'},
 {id:'moon',name:'Moon & Stars',price:10,collection:'original',color:'#4b4791',accent:'#ffe7a1',trim:'#ffe7a1',lower:'#3b3778',band:'#4b4791',bandTrim:'#ffe7a1',pattern:'stars',print:{motif:'stars',ink:'#ffe7a1',scale:.5,alpha:.95},emblem:'moon',back:'moon',description:'Midnight violet, golden piping, sprinkled with starlight.'},
 {id:'bamboo',name:'Bamboo Breeze',price:10,collection:'original',color:'#3f8580',accent:'#c6ead0',trim:'#1f4f4b',band:'#3f8580',bandTrim:'#c6ead0',pattern:'bamboo',print:{motif:'bamboo',ink:'#bfe6cc',scale:.7,alpha:.8},emblem:'leaf',back:'leaf',description:'Cool teal with bamboo leaves and deep forest piping.'},
 {id:'flame',name:'Golden Flame',price:10,collection:'original',color:'#a8402f',accent:'#ffd476',trim:'#ffd476',lower:'#7e2a22',band:'#a8402f',bandTrim:'#ffd476',pattern:'flame',print:{motif:'flame',ink:'#ffc35a',scale:.42,alpha:1,from:.07},emblem:'flame',back:'flame',description:'Ember red with golden fire licking up from the hems.'},
 {id:'golden-knights',name:'Desert Knights',price:10,collection:'sports',color:'#b9975b',accent:'#fff0c3',trim:'#2b3238',lower:'#2b3238',band:'#2b3238',bandTrim:'#c62d43',pattern:'sports',sport:'hockey',crest:'knight',number:'71',description:'Gold armor, steel trousers, red stitching. Hockey knights of the desert.'},
 {id:'silver-knights',name:'Silver Squires',price:10,collection:'sports',color:'#a3acb2',accent:'#f2f1e9',trim:'#bca16d',lower:'#353d44',band:'#353d44',bandTrim:'#bca16d',pattern:'sports',sport:'hockey',crest:'knight',number:'27',description:'Silver ice, golden piping and brave little hockey paws.'},
 {id:'aces',name:'Lucky Aces',price:10,collection:'sports',color:'#29282e',accent:'#d9bf7f',trim:'#d9bf7f',band:'#29282e',bandTrim:'#c82f4d',pattern:'sports',sport:'basketball',crest:'ace',number:'12',description:'Black, gold and red. A little bunny with a big hoops dream.'},
 {id:'aviators',name:'Sky Pilots',price:10,collection:'sports',color:'#f6f1e6',accent:'#244863',trim:'#244863',band:'#244863',bandTrim:'#f5a55a',pattern:'sports',sport:'baseball',crest:'wings',number:'8',print:{motif:'pinstripe',ink:'#244863',scale:.36,alpha:.5},description:'Home whites with navy pinstripes and orange wings.'},
 {id:'athletics',name:'Green Sluggers',price:10,collection:'sports',color:'#28714e',accent:'#ffe09a',trim:'#ffe09a',lower:'#f4efe0',band:'#28714e',bandTrim:'#ffe09a',pattern:'sports',sport:'baseball',crest:'letter',mark:'S',number:'3',description:'Green and gold, home-run bunny spirit.'},
 {id:'unlv',name:'Scarlet Runners',price:10,collection:'sports',color:'#be3549',accent:'#fff3e7',trim:'#fff3e7',band:'#be3549',bandTrim:'#aeb8be',pattern:'sports',sport:'basketball',crest:'letter',mark:'R',number:'23',description:'Scarlet hoops pride for the tiniest fast-break runner.'},
 {id:'lights',name:'Neon Bolts FC',price:10,collection:'sports',color:'#335d9c',accent:'#ffe768',trim:'#ffe768',band:'#335d9c',bandTrim:'#ef9db8',pattern:'sports',sport:'soccer',crest:'bolt',number:'9',print:{motif:'hoops',ink:'#2a4f88',scale:.5,alpha:.7},description:'Electric blue, sunny gold and goal-scoring little paws.'},
 {id:'knight-hawks',name:'Steel Hawks',price:10,collection:'sports',color:'#33475b',accent:'#dde5e8',trim:'#dde5e8',band:'#33475b',bandTrim:'#879aaf',pattern:'sports',sport:'football',crest:'wings',number:'44',description:'Steel wings and gridiron spirit. Ready to soar!'},
 {id:'desert-dogs',name:'Desert Hares',price:10,collection:'sports',color:'#d9b47e',accent:'#3a3238',trim:'#3a3238',lower:'#3a3238',band:'#3a3238',bandTrim:'#d9b47e',pattern:'sports',sport:'lacrosse',crest:'paw',number:'5',description:'Sandstone and charcoal. A speedy pack of lacrosse hares.'},
 {id:'thrill',name:'Spike Stars',price:10,collection:'sports',color:'#56a7bf',accent:'#f2f6ff',trim:'#f2f6ff',band:'#56a7bf',bandTrim:'#ef9bbe',pattern:'sports',sport:'volleyball',crest:'star',number:'14',description:'Sky-blue volleyball dreams with pink star power.'},
 {id:'raiders',name:'Silver Bandits',price:10,collection:'sports',color:'#22252c',accent:'#c4c8cc',trim:'#c4c8cc',band:'#22252c',bandTrim:'#c4c8cc',pattern:'sports',sport:'football',crest:'shield',number:'00',description:'Black and silver. Game-day bunny swagger.'},
 {id:'strawberry',name:'Strawberry Sugar',price:10,collection:'glitter',color:'#e48eae',accent:'#fff0e4',trim:'#fff0e4',band:'#e48eae',bandTrim:'#c74d70',pattern:'strawberry',glitter:true,print:{motif:'strawberry',scale:.5,alpha:1},emblem:'heart',back:'strawberry',description:'Blushing berries, tiny hearts, sugar-sweet shimmer.'},
 {id:'cloud',name:'Cloud Cuddle',price:10,collection:'glitter',color:'#86bfd8',accent:'#fff6e8',trim:'#fff6e8',band:'#86bfd8',bandTrim:'#f2a4b7',pattern:'cloud',glitter:true,print:{motif:'cloud',scale:.55,alpha:1},emblem:'rainbow',back:'cloud',description:'Fluffy clouds and little rainbows, dusted in starlight.'},
 {id:'honey',name:'Honey Hug',price:10,collection:'glitter',color:'#d9a35f',accent:'#fff0c9',trim:'#93623f',band:'#d9a35f',bandTrim:'#fff0c9',pattern:'teddy',glitter:true,print:{motif:'teddy',scale:.55,alpha:1},emblem:'heart',back:'teddy',description:'Pocket-size teddy friends with honey-gold sparkle.'},
 {id:'lavender',name:'Lavender Lullaby',price:10,collection:'glitter',color:'#a58cce',accent:'#fff0b6',trim:'#fff0b6',band:'#a58cce',bandTrim:'#fff0b6',pattern:'sleepy',glitter:true,print:{motif:'sleepy',scale:.5,alpha:1},emblem:'moon',back:'moon',description:'Sleepy moons and star kisses. Dream, then sparkle.'},
 {id:'ribbon',name:'Rainbow Ribbon',price:10,collection:'glitter',color:'#7bbcab',accent:'#ffe5ec',trim:'#ffd7e7',band:'#7bbcab',bandTrim:'#fce5a8',pattern:'bows',glitter:true,print:{motif:'bows',scale:.5,alpha:1},emblem:'bow',back:'bow',description:'Pastel bows tied with a sprinkle of rainbow glitter.'},
 {id:'fairy',name:'Fairy Floss',price:10,collection:'glitter',color:'#c493cf',accent:'#ffeaf6',trim:'#ffeaf6',band:'#c493cf',bandTrim:'#d5e9dc',pattern:'fairy',glitter:true,print:{motif:'fairy',scale:.55,alpha:1},emblem:'heart',back:'fairy',description:'Fairy wings, candy hearts and a little wishful twinkle.'}
]);
export const giDesign=id=>GIS.find(g=>g.id===id)??null;
export const GI_COLLECTIONS=[{id:'all',name:'All Gi'},{id:'owned',name:'Owned'},{id:'halloween',name:'Halloween Collection'},{id:'glitter',name:'Glitter Collection'},{id:'sports',name:'Sports Collection'},{id:'original',name:'Original Favorites'}];
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
