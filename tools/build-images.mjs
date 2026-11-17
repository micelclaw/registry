import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const registry=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [workspace,output,revision]=process.argv.slice(2);
if(!workspace||!output||!/^[a-f0-9]{40}$/.test(revision??''))throw Error('Usage: node tools/build-images.mjs WORKSPACE OUTPUT REGISTRY_COMMIT');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const run=(cmd,args,options={})=>{const result=spawnSync(cmd,args,{encoding:'utf8',maxBuffer:32*1024*1024,...options});if(result.status!==0)throw Error(cmd+' failed; inspect the local build log.');return result.stdout.trim();};
const lock=JSON.parse(run('git',['show',revision+':sources.lock.json'],{cwd:registry}));
const base='node@sha256:47725aca53d3295ec2d3be8f62726599b3033cc262edc2c7e429909b3ac599fc';
const images=[];await fs.mkdir(output,{recursive:true});
for(const source of lock.sources.filter(s=>['documents','spreadsheets','presentations','pdf'].includes(s.name))){
 const app=path.join(workspace,'micelclaw-os/apps',source.name);
 const proof=JSON.parse(await fs.readFile(path.join(workspace,'_artifacts/scratch/s09-office/prepared',source.name+'.json'),'utf8'));
 const archive=path.join(output,path.basename(new URL(source.source.url).pathname));
 const bytes=await fs.readFile(archive);
 if(sha(bytes)!==source.source.sha256||bytes.length!==source.source.bytes||proof.revision!==source.source_revision||proof.source_archive_sha256!==source.source.sha256)throw Error('Source/proof mismatch.');
 const artifacts=[];
 async function walk(dir){for(const item of await fs.readdir(path.join(app,dir),{withFileTypes:true})){const name=dir+'/'+item.name;if(item.isDirectory())await walk(name);else if(item.isFile())artifacts.push([name,sha(await fs.readFile(path.join(app,name)))]);else throw Error('Unexpected generated artifact.');}}
 await walk('ui');await walk('runtime');
 if(sha(JSON.stringify(artifacts.sort((a,b)=>a[0].localeCompare(b[0]))))!==proof.artifacts_sha256)throw Error('Prepared UI/runtime changed; no rebuild by inference.');
 const inputs=sha(JSON.stringify({source:source.source.sha256,artifacts:proof.artifacts_sha256,revision,base}));
 if(!/^\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?$/.test(source.version))throw Error('Invalid locked application version.');
 const tag=`micelclaw-registry-office-${source.name}:${source.version}-${revision.slice(0,12)}`;
 const prior=spawnSync('docker',['image','inspect',tag,'--format','{{json .}}'],{encoding:'utf8'});
 let image;
 if(prior.status===0){
  const info=JSON.parse(prior.stdout);if(info.Config.Labels?.['io.micelclaw.registry.inputs']!==inputs)throw Error('Existing image tag has different inputs; no overwrite.');image=info.Id;
 }else{
  const context=await fs.mkdtemp(path.join(path.resolve(output),'.office-build-'));
  try{
   run('tar',['-xzf',archive,'-C',context]);
   for(const dir of ['ui','runtime'])await fs.cp(path.join(app,dir),path.join(context,dir),{recursive:true});
   const result=spawnSync('docker',['build','--platform','linux/amd64','--build-arg','OFFICE_BASE_IMAGE='+base,
    '--label','org.opencontainers.image.source=https://github.com/micelclaw/registry','--label','org.opencontainers.image.revision='+revision,
    '--label','io.micelclaw.office.source-revision='+source.source_revision,'--label','io.micelclaw.registry.inputs='+inputs,
    '--label','io.micelclaw.registry.owner=s09','--tag',tag,context],{encoding:'utf8',maxBuffer:64*1024*1024,env:{...process.env,DOCKER_BUILDKIT:'0'}});
   await fs.writeFile(path.join(output,source.name+'-image-build.log'),(result.stdout??'')+(result.stderr??''));
   if(result.status!==0)throw Error('Image build failed: '+source.name);
   image=run('docker',['image','inspect',tag,'--format','{{.Id}}']);
  }finally{await fs.rm(context,{recursive:true,force:true});}
 }
 images.push({app:source.name,repository:'ghcr.io/micelclaw/office-'+source.name,tag:source.version,local_id:image,local_tag:tag,inputs_sha256:inputs,source_revision:source.source_revision,registry_revision:revision});
 await fs.writeFile(path.join(output,'images.json'),JSON.stringify({schema_version:1,registry:'https://github.com/micelclaw/registry',publisher:'Titunito',base_image:base,images},null,2)+'\n');
 console.log(source.name+': current image prepared, no workers or Core started.');
}
if(images.length!==4)throw Error('Expected four Office images.');
