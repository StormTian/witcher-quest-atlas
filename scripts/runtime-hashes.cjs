const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
module.exports=()=>Object.fromEntries(require('./runtime-inputs.json').map(name=>[name,crypto.createHash('sha256').update(fs.readFileSync(path.join(__dirname,'../dist',name))).digest('hex')]));
