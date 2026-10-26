const fs=require('fs');const sharp=require('sharp');
const root=process.env.KB_ART_SOURCE_DIR;if(!root)throw Error('Set KB_ART_SOURCE_DIR to the original generated PNG folder, including a trailing slash.');
const list=[['burrows','exec-c278b4ac-8556-4a3f-948a-60765f8155f1.png'],['gardens','exec-4b608784-baef-4d47-9876-18f17939e72a.png'],['village','exec-f8d9538f-663d-468a-b372-194af7736226.png'],['tournaments','exec-c43935ff-2f48-425b-80e0-18aefbac8e3e.png'],['championships','exec-726de3fa-d9fc-472f-a6b6-ffca4c32fa47.png']];
(async()=>{for(const [name,file]of list)await sharp(root+file).webp({quality:90}).toFile(__dirname+'/assets/'+name+'.webp');})();
