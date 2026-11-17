// Packaging entry point for maintainers with an installed Micelclaw Core.
// Core's official packer, scanner and Office provenance gates remain authoritative.
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
const [core,app,binding,proof]=process.argv.slice(2);
if(!core||!app||!binding)throw Error('Usage: node tools/package-office.mjs CORE_DIRECTORY APP BINDING_JSON [REVIEWED_BUILD_PROOF_JSON]');
const metadata=JSON.parse(await readFile(binding,'utf8'));
const registry=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const locked=spawnSync('git',['show',metadata.revision+':sources.lock.json'],{cwd:registry,encoding:'utf8'});
if(locked.status!==0)throw Error('A real registry source-lock commit is required.');
const expected=JSON.parse(locked.stdout).core_packager_sha256;
const actual=createHash('sha256').update(await readFile(path.resolve(core,'scripts/package-reviewed-office.mjs'))).digest('hex');
if(!expected||actual!==expected)throw Error('The official Core packaging helper differs from the reviewed source lock.');
const args=[path.resolve(core,'scripts/package-reviewed-office.mjs'),'--app',app,'--binding',path.resolve(binding)];
if(proof)args.push('--proof',path.resolve(proof));
const result=spawnSync(process.execPath,args,{stdio:'inherit'});
if(result.status!==0)process.exit(result.status??1);
