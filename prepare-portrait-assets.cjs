const sharp=require('sharp');
const root=process.env.KB_ART_SOURCE_DIR;if(!root)throw Error('Set KB_ART_SOURCE_DIR to the original generated PNG folder, including a trailing slash.');
const edits=[['burrows','exec-e77d4219-654a-4bd2-8252-6adf4e1991d3.png'],['gardens','exec-249a97ee-23e8-45a3-a2bd-58d587f18f8b.png'],['village','exec-9df07d88-454d-4300-8644-cfcc7d40fc72.png'],['tournaments','exec-80484a50-08d2-4856-9f7c-b15a2b50d6e9.png'],['championships','exec-05bc3fd9-a92d-45ef-b289-120b5af79760.png']];
(async()=>{for(const [name,file]of edits)await sharp(root+file).webp({quality:92}).toFile(__dirname+'/assets/'+name+'-portrait.webp');})();
