import path from 'node:path';
import os from 'node:os';
import fs from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const root=process.cwd();
const skill=process.env.PRESENTATION_SKILL_DIR;
if (!skill) throw new Error('Set PRESENTATION_SKILL_DIR to the installed presentations skill directory');
const runtime=process.env.ARTIFACT_RUNTIME || path.join(os.homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies');
const pythonExecutable=process.env.CASE_PYTHON || (process.platform==='win32'
  ? path.join(runtime,'python/python.exe')
  : path.join(runtime,'python/bin/python3'));
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const staging=path.join(root,'.local/deck-build');
const validatedDir=await fs.mkdtemp(path.join(staging,'validated-'));
const name='Теневое Правительство_strategy_msk.pptx';
const validatedPath=path.join(validatedDir,name);
const result=await finalizePresentation({
  workspaceDir:staging,candidatePath:path.join(staging,'candidate.pptx'),
  finalPath:validatedPath,
  pythonExecutable,
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--require-native-table-slide','5'],
  explicitTotalSlideCount:8,requiredNativeTableOwnerSlides:[5],requiredNativeChartOwnerSlides:[4,7],
  materializeLiteralChartWorkbooks:true,
  fontPolicy:{basis:'design',families:['Arial']},
  verifyArtifactToolImport:true,
  receiptPath:path.join(staging,`${path.basename(validatedDir)}.json`),
});
await fs.rename(validatedPath,path.join(root,'presentation',name));
console.log(JSON.stringify(result));
