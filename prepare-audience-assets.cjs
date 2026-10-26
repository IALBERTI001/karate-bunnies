const sharp=require('sharp');
const root=process.env.KB_ART_SOURCE_DIR;if(!root)throw Error('Set KB_ART_SOURCE_DIR to the original generated PNG folder, including a trailing slash.');
const edits=[['burrows','exec-9bc33228-3aa5-449d-b12a-f72b81f6ade2.png'],['gardens','exec-050ac7bd-70be-4627-bfc6-ea875eb398d4.png'],['village','exec-d56ec2a1-5665-43d8-ab14-5bc14532a129.png'],['tournaments','exec-4c25a045-b934-4042-920a-565dbe219d03.png']];
(async()=>{for(const [name,file]of edits)await sharp(root+file).webp({quality:92}).toFile(__dirname+'/assets/'+name+'-audience.webp');})();
