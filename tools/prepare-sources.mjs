import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [workspace,output,tag,cutsFile]=process.argv.slice(2);
if(!workspace||!output||!tag||!/^[a-zA-Z0-9._-]+$/.test(tag))throw Error('Usage: node tools/prepare-sources.mjs WORKSPACE OUTPUT RELEASE_TAG [REVIEWED_CUTS_JSON]');
const initialRefs={documents:'8d9f98fc8d16239d0970644c5facac589c781043',spreadsheets:'5a731d57aa9373d6c65ca8dd9a8b583187138b59',presentations:'bf57d10a59d682e1189ae03bf40962ec127219f8',pdf:'b2ef57053a0ee06c223a70f0e264baa501655f34'};
// New immutable cuts provide real reviewed commits explicitly. Defaults retain
// the original release recipe; never infer a reviewed cut from a moving HEAD.
const refs=cutsFile?JSON.parse(await fs.readFile(cutsFile,'utf8')):initialRefs;
if(!refs||Array.isArray(refs)||Object.keys(refs).sort().join(',')!==Object.keys(initialRefs).sort().join(',')||Object.values(refs).some(ref=>typeof ref!=='string'||!/^[a-f0-9]{40}$/.test(ref)))throw Error('Exactly four real reviewed Office commits are required.');
const previous=cutsFile?JSON.parse(await fs.readFile(path.join(root,'sources.lock.json'),'utf8')):null;
const retainedN8n=previous?.sources?.find(source=>source.name==='n8n-automation');
if(cutsFile&&!retainedN8n)throw Error('The already published n8n source entry must be preserved.');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const run=(cwd,cmd,args)=>{const r=spawnSync(cmd,args,{cwd,encoding:'utf8',maxBuffer:8*1024*1024});if(r.status!==0)throw Error(cmd+' failed; no source accepted.');return r.stdout.trim();};
await fs.mkdir(output,{recursive:true});const sources=[];
for(const [name,revision]of Object.entries(refs)){
 const app=path.join(workspace,'micelclaw-os/apps',name);
 if(run(app,'git',['cat-file','-t',revision])!=='commit')throw Error('Missing reviewed app commit.');
 const version=JSON.parse(run(app,'git',['show',revision+':package.json'])).version;
 if(typeof version!=='string'||!/^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?$/.test(version))throw Error('Invalid reviewed application version.');
 if(cutsFile&&previous.sources.some(source=>source.name===name&&source.version===version))throw Error('A corrected immutable cut requires a new application version; do not replace the existing release.');
 const archive=path.join(path.resolve(output),`${name}-${version}-source.tar.gz`);
 if(await fs.stat(archive).catch(()=>null))throw Error('Refusing to overwrite a source archive.');
 run(app,'git',['archive','--format=tar.gz','--output='+archive,revision]);
 const bytes=await fs.readFile(archive);
 sources.push({name,version,source_revision:revision,source:{url:`https://github.com/micelclaw/registry/releases/download/${tag}/${path.basename(archive)}`,sha256:sha(bytes),bytes:bytes.length},export:'Exact reviewed git archive; no Git metadata or history.'});
}
if(retainedN8n)sources.push(retainedN8n);
else {
const temp=await fs.mkdtemp(path.join(os.tmpdir(),'registry-n8n-source-'));
try{
 const source=path.join(workspace,'micelclaw-os/core/apps/_sources/n8n-automation');
 for(const file of ['SKILL.md','NOTICES.md','launcher.html','references','ui/module.tsx']){
  await fs.mkdir(path.dirname(path.join(temp,file)),{recursive:true});await fs.cp(path.join(source,file),path.join(temp,file),{recursive:true});
 }
 const module=path.join(temp,'ui/module.tsx');
 await fs.writeFile(module,(await fs.readFile(module,'utf8')).split('\n').filter(line=>!line.includes('/home/victor/')).join('\n'));
 const manifest=JSON.parse(await fs.readFile(path.join(source,'manifest.json'),'utf8'));
 delete manifest.checksums;manifest.version='0.1.1';manifest.license='BUSL-1.1 AND MIT AND Apache-2.0';
 await fs.writeFile(path.join(temp,'manifest.template.json'),JSON.stringify(manifest,null,2)+'\n');
 await fs.copyFile(path.join(workspace,'micelclaw-os/LICENSE'),path.join(temp,'LICENSE'));
 await fs.mkdir(path.join(temp,'licenses'));
 for(const file of ['n8n-skills-MIT.txt','Apache-2.0.txt'])await fs.copyFile(path.join(output,file),path.join(temp,'licenses',file));
 await fs.writeFile(path.join(temp,'README.md'),'# n8n integration for Micelclaw\n\nIncludes launcher, skill, references and notices. Uses native Micelclaw Core automation APIs and the official n8n service managed by Core. The n8n server and its Sustainable Use License are not bundled or relicensed. No workflows, templates, credentials or runtime data are included. Template operations require templates supplied by Core; a host without them has an empty template catalogue.\n');
 const archive=path.join(path.resolve(output),'n8n-automation-0.1.1-source.tar.gz');
 if(await fs.stat(archive).catch(()=>null))throw Error('Refusing to overwrite a source archive.');
 run(temp,'tar',['--sort=name','--mtime=@0','--owner=0','--group=0','--numeric-owner','-czf',archive,'.']);
 const bytes=await fs.readFile(archive);
 sources.push({name:'n8n-automation',version:'0.1.1',source:{url:`https://github.com/micelclaw/registry/releases/download/${tag}/${path.basename(archive)}`,sha256:sha(bytes),bytes:bytes.length},export:'Allowlist: launcher, ui/module.tsx, SKILL.md, references, NOTICES, licences, README, manifest template. No workflows/templates/runtime data. Removed local-path comment; public package version/licence metadata generated separately.'});
}finally{await fs.rm(temp,{recursive:true,force:true});}
}
const recipes=[];for(const file of ['tools/package-office.mjs','tools/package-n8n.mjs','tools/prepare-sources.mjs','tools/publish-images.py','tools/build-images.mjs'])recipes.push({path:file,sha256:sha(await fs.readFile(path.join(root,file)))});
const lock={schema_version:1,repository:'https://github.com/micelclaw/registry',release_tag:tag,core_packager_sha256:sha(await fs.readFile(path.join(workspace,'micelclaw-os/core/scripts/package-reviewed-office.mjs'))),recipes,sources};
await fs.writeFile(path.join(root,'sources.lock.json'),JSON.stringify(lock,null,2)+'\n');
console.log('Five source archives and their lock prepared. No publication or installation.');
