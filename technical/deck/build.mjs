import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { buildSlides, SIZE, FONT, ASSETS } from './slides.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const staging=path.join(root,'.local/redesign/output');
const runtime=process.env.ARTIFACT_RUNTIME;
if (!runtime) throw new Error('Set ARTIFACT_RUNTIME to the bundled runtime dependencies directory.');
const modules=path.join(runtime,'node/node_modules');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(modules,'@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const {FontLibrary}=createRequire(path.join(modules,'@oai/artifact-tool/package.json'))('skia-canvas');
const dir=path.join(here,'assets');
FontLibrary.use(FONT, ['GolosText-Regular.ttf', 'GolosText-Bold.ttf'].map(file => path.join(dir, file)));
const assets=Object.fromEntries(await Promise.all(ASSETS.map(async name=>[name,new Uint8Array(await fs.readFile(path.join(dir,name)))])));
const evidence=JSON.parse(await fs.readFile(path.join(here,'evidence.json'),'utf8'));
const p=Presentation.create({slideSize:SIZE});
p.theme.defaultFont=FONT;
await buildSlides(p,{assets,evidence});
await fs.mkdir(staging,{recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(staging,'candidate.pptx'));
for(const [i,s] of p.slides.items.entries()){
  const png=await p.export({slide:s,format:'png',scale:2});
  await fs.writeFile(path.join(staging,`slide-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
const notes=p.slides.items.map((s,i)=>`## Слайд ${i+1}\n\n${s.speakerNotes.text}\n`).join('\n');
await fs.writeFile(path.join(root,'presentation/speaker_notes.md'),'# Заметки к защите\n\n'+notes,'utf8');
console.log('Built '+p.slides.items.length+' slides in '+staging);
