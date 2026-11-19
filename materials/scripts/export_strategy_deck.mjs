// Rebuild native slides and export a candidate PPTX plus previews for PDF packaging.
// Requires the bundled @oai/artifact-tool runtime; no external dependencies.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {pathToFileURL} from 'node:url';
const root=process.cwd();
const runtime=process.env.ARTIFACT_RUNTIME || path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies');
const {Presentation,PresentationFile}=await import(pathToFileURL(path.join(runtime,'node/node_modules/@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const src=await fs.readFile(path.join(root,'materials/scripts/build_strategy_deck.session.js'),'utf8');
const build=new Function(src.split('// Live editor entry point.')[0]+'; return buildStrategyDeck;')();
const p=Presentation.create({slideSize:{width:1280,height:720}});
const evidence=JSON.parse(await fs.readFile(path.join(root,'materials/presentation/evidence.json'),'utf8'));
await build(p,evidence);
const staging=path.join(root,'.local/deck-build');
const dest=path.join(root,'presentation');
await fs.mkdir(staging,{recursive:true});
await fs.mkdir(dest,{recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(staging,'candidate.pptx'));
// Native PDF export in this runtime has a missing standard-fonts module.
// The final PDF is assembled from these high-resolution previews below.
for(let i=0;i<p.slides.items.length;i++){
  const b=await p.export({slide:p.slides.items[i],format:'png',scale:2});
  await fs.writeFile(path.join(staging,`slide-${i+1}.png`),new Uint8Array(await b.arrayBuffer()));
}
const notes=p.slides.items.map((s,i)=>`## Слайд ${i+1}\n\n${s.speakerNotes.text}\n`).join('\n');
await fs.writeFile(path.join(dest,'speaker_notes.md'),'# Заметки к защите и источники\n\n'+notes,'utf8');
console.log(JSON.stringify({slides:p.slides.items.length,candidate:path.join(staging,'candidate.pptx')}));
