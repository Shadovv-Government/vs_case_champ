import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { FONT } from './slides.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const runtime=process.env.ARTIFACT_RUNTIME;
const skill=process.env.PRESENTATIONS_SKILL;
if(!runtime || !skill) throw new Error('Set ARTIFACT_RUNTIME and PRESENTATIONS_SKILL.');
const check=path.join(skill,'container_tools');
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {finalizePresentation}=await import(pathToFileURL(path.join(check,'artifact_tool_utils.mjs')).href);
const staging=path.join(root,'.local/redesign/output');
const validated=await fs.mkdtemp(path.join(staging,'validated-'));
const name='Теневое Правительство_strategy_msk.pptx';
const validatedPath=path.join(validated,name);
const destination=path.join(root,'presentation',name);
const python=process.env.CASE_PYTHON || path.join(runtime,
  process.platform==='win32'?'python/python.exe':'python/bin/python3');
const report=await finalizePresentation({
  workspaceDir:staging,
  candidatePath:path.join(staging,'candidate.pptx'),
  finalPath:validatedPath,
  pythonExecutable:python,
  integrityValidatorPath:path.join(check,'inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(check,'inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
  explicitTotalSlideCount:8,
  requiredNativeChartOwnerSlides:[3,4,7,8],
  materializeLiteralChartWorkbooks:true,
  fontPolicy:{basis:'design',families:[FONT]},
  verifyArtifactToolImport:true,
  receiptPath:path.join(staging,`validation-${Date.now()}.json`),
});
await fs.rename(validatedPath,destination);
console.log(JSON.stringify({file:destination,charts:report.nativeChartValidation,bytes:report.byteCount}));
