import {giDesign} from './wardrobe.mjs?v=78109aebf0b2';
export const FURS={White:'#FFFDF9',Cream:'#E9D0AA',Gray:'#AAA1A3',Tan:'#D09A64'};
export const COLORS={Coral:'#EF8E85',Mint:'#91C8A0',Lavender:'#B6A0D5','Sky blue':'#87BCE6',Purple:'#8053BA',Pink:'#EE9BC4',Black:'#292831'};
// Belt colours by rank. Black (null) leaves the original painted belt untouched.
export const BELTS={White:'#FFFDF7',Yellow:'#FFD24A',Green:'#5E9E57',Brown:'#8A5A34',Red:'#D94A3D',Black:null};
export const BELT_ORDER=['White','Yellow','Green','Brown','Red','Black'];
// Stage whose win awards each belt after White.
export const BELT_AWARDS={4:'Yellow',8:'Green',12:'Brown',16:'Red',20:'Black'};
export function beltFor(progress){const won=new Set(progress?.cleared??[]);let belt='White';for(const [stage,b] of Object.entries(BELT_AWARDS))if(won.has(Number(stage)))belt=b;return belt;}
const chapters=['Beneath the roots','Into the gardens','A village favorite','Across the mountains','The world is watching'];
const rows=[
 ['Tiny Paws Dojo','Your journey begins beneath the roots. Two coaches, one little dream.','burrows',2,'Mochi','Cream','Mint'],
 ['Nibbles’ Root Cellar','A few curious neighbors have heard about your paws.','burrows',3,'Pip','Tan','Sky blue'],
 ['Peekabun Burrow','A little daylight. A little bigger audience.','burrows',5,'Pebble','Gray','Pink'],
 ['Cottontail Hollow','Step out of the burrow. Your story is spreading.','burrows',8,'Clover','White','Purple'],
 ['Cloverhop Garden','Your first garden bout, beneath the morning sun.','gardens',12,'Dew','Cream','Lavender'],
 ['Crunchy Carrot Patch','The gardeners have put down their watering cans to watch.','gardens',16,'Nibbles','Tan','Coral'],
 ['Petal Paws Pond','Pink petals fall as your little fan club grows.','gardens',20,'Petal','White','Pink'],
 ['Moonbun Garden','Fireflies and fans gather for a moonlit match.','gardens',24,'Luna','Gray','Sky blue'],
 ['Buttonnose Square','The village is cheering your name.','village',32,'Buttons','Cream','Purple'],
 ['Hoppy Harvest Festival','A festival bout with a whole street watching.','village',40,'Poppy','Tan','Mint'],
 ['Binkies’ Willow Bridge','A calm river. A very excited audience.','village',48,'Ripple','Gray','Coral'],
 ['Bun & Bamboo Teahouse','The teahouse tournament has a new favorite.','village',60,'Jasmine','White','Black'],
 ['Cloudhop Temple','Your reputation has reached the mountains.','tournaments',75,'Nimbus','Cream','Sky blue'],
 ['Maple Munch Pavilion','Autumn leaves and tournament applause.','tournaments',90,'Maple','Tan','Pink'],
 ['Snowpaws Summit','Cold air, warm lanterns, and a roaring welcome.','tournaments',110,'Snowdrop','White','Purple'],
 ['Golden Whisker Rooftop','Fight above the city that knows your name.','tournaments',140,'Sunny','Gray','Mint'],
 ['Grand Fluffle Hall','Your first grand arena. Take a breath, then bow.','championships',650,'Velvet','Tan','Black'],
 ['Starlop Stadium','Under the lights, a thousand little ears lean forward.','championships',900,'Nova','White','Lavender'],
 ['Cottontail Crown Coliseum','One fight stands between you and the ultimate arena.','championships',1400,'Ember','Gray','Coral'],
 ['The Great Bunny Bowl','The super arena. The biggest crowd. Your championship moment.','championships',2400,'Grandmaster Bun','Cream','Black']
];
export const STAGES=rows.map((r,i)=>({id:i+1,name:r[0],story:r[1],art:r[2],panel:i%4,fans:r[3],opponent:r[4],fur:r[5],gi:r[6],chapter:chapters[Math.floor(i/4)],chapterIndex:Math.floor(i/4),difficulty:i/19}));
export function loadProgress(raw){try{const v=typeof raw==='string'?JSON.parse(raw):raw;const cleared=[...new Set((v?.cleared??[]).filter(n=>Number.isInteger(n)&&n>=1&&n<=20))].sort((a,b)=>a-b);let count=0;while(cleared.includes(count+1))count++;return {cleared:cleared.filter(n=>n<=count),unlocked:Math.min(20,count+1)};}catch{return {cleared:[],unlocked:1};}}
export function clearStage(progress,id){if(!Number.isInteger(id)||id<1||id>progress.unlocked||id>20)return progress;return loadProgress({cleared:[...progress.cleared,id]});}
export function validSkin(s){return {fur:Object.hasOwn(FURS,s?.fur)?s.fur:'White',gi:Object.hasOwn(COLORS,s?.gi)?s.gi:'Coral',...(giDesign(s?.design)?{design:s.design}:{})};}
