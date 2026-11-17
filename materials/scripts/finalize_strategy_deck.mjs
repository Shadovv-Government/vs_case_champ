import path from 'node:path';
import {pathToFileURL} from 'node:url';
const root=process.cwd();
const skill='C:/Users/kiril/.codex/plugins/cache/openai-primary-runtime/presentations/26.1116.12020/skills/presentations';
const runtime='C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1116-1220-0_26.1116.1220.0_x64__3k8sg7r9htsxt/dependencies';
process.env.RUNTIME_NODE_MODULES=path.join(runtime,'node/node_modules');
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({
  workspaceDir:root,candidatePath:path.join(root,'.local/deck-build/candidate.pptx'),
  finalPath:path.join(root,'presentation/Теневое Правительство_strategy_msk.pptx'),
  pythonExecutable:path.join(runtime,'python/python.exe'),
  integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit','--require-native-table-slide','5'],
  explicitTotalSlideCount:8,requiredNativeTableOwnerSlides:[5],requiredNativeChartOwnerSlides:[4,7],
  materializeLiteralChartWorkbooks:true,
  fontPolicy:{basis:'design',families:['Arial']},
  verifyArtifactToolImport:true,
  receiptPath:path.join(root,'.local/deck-build/validation.json'),
});
console.log(JSON.stringify(result));
