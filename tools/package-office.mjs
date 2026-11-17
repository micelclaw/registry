// Packaging entry point for maintainers with an installed Micelclaw Core.
// Core's official packer, scanner and Office provenance gates remain authoritative.
import path from 'node:path';
import {spawnSync} from 'node:child_process';
const [core,app,binding]=process.argv.slice(2);
if(!core||!app||!binding)throw Error('Usage: node tools/package-office.mjs CORE_DIRECTORY APP BINDING_JSON');
const result=spawnSync(process.execPath,[path.resolve(core,'scripts/package-reviewed-office.mjs'),'--app',app,'--binding',path.resolve(binding)],{stdio:'inherit'});
if(result.status!==0)process.exit(result.status??1);
