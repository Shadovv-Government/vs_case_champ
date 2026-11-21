import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { ICONS, iconFile, iconSvg } from './layout.mjs';

const runtime=process.env.ARTIFACT_RUNTIME;
if(!runtime)throw new Error('Set ARTIFACT_RUNTIME to the bundled runtime dependencies directory.');
const require=createRequire(path.join(runtime,'node/node_modules/@oai/artifact-tool/package.json'));
const { Canvas, loadImage }=require('skia-canvas');
const dir=path.join(path.dirname(fileURLToPath(import.meta.url)),'assets');
await fs.mkdir(path.join(dir,'icons'),{recursive:true});
for(const [id,color] of ICONS){
  const image=await loadImage(Buffer.from(iconSvg(id,color)));
  const canvas=new Canvas(96,96);
  canvas.getContext('2d').drawImage(image,0,0);
  await fs.writeFile(path.join(dir,iconFile(id,color)),await canvas.toBuffer('png'));
}
