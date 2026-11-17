/** Update presentation metadata without changing immutable package/source assets. */
import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const core = args.find(arg => arg !== '--check');
if (!core) throw new Error('Usage: node tools/update-catalog-display.mjs CORE_DIRECTORY [--check]');
const file = resolve(root, 'catalog.json');
const before = await readFile(file, 'utf8');
const catalogue = JSON.parse(before);
const display = { schema_version: 1, packages: [] };
const officeColors = { documents: '#3b82f6', spreadsheets: '#22c55e', presentations: '#eab308', pdf: '#ef4444' };
// Owner-approved editorial labels, 17 November 2026. New names, versions or bytes need a new explicit decision.
const approvedDistinctions = new Map([
  [
    "documents@0.2.1",
    "c0d8ed0f27970e4df9d70541b3fdaae68c8eb06d4b92f67351163999854db5ba"
  ],
  [
    "spreadsheets@0.2.1",
    "f6606e104d36d27841349bf87bdf9dd26f7712fea951ecf5ec9e1a63163b58d2"
  ],
  [
    "presentations@0.2.1",
    "38ade11bf93ff16d89f726b0643e0c0e339dd4a1cd2056dae2c6cbbfd48a5567"
  ],
  [
    "pdf@0.2.1",
    "1a2ec195ba8bfd6b2dcd8cc0076ccba338ea60eeec9ef4eeedf4c8dcaebafd87"
  ],
  [
    "n8n-automation@0.1.1",
    "217fad4458d1fb4a6f122c7e544abdeafe90ec4aa18d9ba3c0efb3ee5010b82d"
  ]
]);
for (const entry of catalogue.packages) {
  if (!/^[a-z0-9][a-z0-9_-]{0,63}$/.test(entry.name)) throw new Error('Invalid application name');
  const manifest = JSON.parse(await readFile(resolve(core, 'apps', entry.name, 'manifest.json'), 'utf8'));
  if (manifest.name !== entry.name || manifest.version !== entry.version) throw new Error(`Version mismatch for ${entry.name}; use the corresponding reviewed source.`);
  const module = manifest.ui?.module;
  const metadata = { name: entry.name, version: entry.version, package_sha256: entry.package.sha256 };
  metadata.author = manifest.author;
  metadata.origin = /^micelclaw\b/i.test(manifest.author ?? '') ? 'Micelclaw' : 'Community';
  metadata.tier_required = manifest.tier_required;
  metadata.icon = module?.icon ?? manifest.icon;
  metadata.icon_kind = module?.icon ? 'lucide' : 'emoji';
  metadata.color = officeColors[entry.name] ?? module?.color ?? manifest.color;
  // Editorial badges require an explicit declaration; never infer verification.
  metadata.tags = [...new Set([...(Array.isArray(manifest.tags) ? manifest.tags.filter(tag => !['verified', 'featured'].includes(tag)) : []),
    ...(approvedDistinctions.get(entry.name + '@' + entry.version) === entry.package.sha256 ? ['verified', 'featured'] : [])])];
  display.packages.push(metadata);
}
const displayFile = resolve(root, 'catalog-display.json');
const after = `${JSON.stringify(display, null, 2)}\n`;
const previous = await readFile(displayFile, 'utf8').catch(error => { if (error.code === 'ENOENT') return ''; throw error; });
if (args.includes('--check')) {
  if (after !== previous) throw new Error('Catalogue display metadata is out of date.');
} else if (after !== previous) await writeFile(displayFile, after);
