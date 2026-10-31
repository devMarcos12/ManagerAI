import { readFileSync, writeFileSync } from 'node:fs';
const schemas = JSON.parse(readFileSync('openapi.json', 'utf8')).components.schemas;
const pairs = { venues: ['AnalysisPayload', 'venue'], contexts: ['AnalysisPayload', 'match_context'], objectives: ['AnalysisPayload', 'strategic_objective'],
  strategies: ['AnalysisBody', 'intended_strategy'], explanations: ['AnalysisBody', 'explanation'], planIds: ['PlanBody', 'plan_id'] };
const content = '// Gerado de openapi.json; não editar manualmente.\n' + Object.entries(pairs).map(([name, [model, key]]) => {
  const values = schemas[model].properties[key].enum;
  if (!Array.isArray(values)) throw new Error(`Enum ausente: ${model}.${key}`);
  return `export const ${name} = ${JSON.stringify(values)} as const;`;
}).join('\n') + '\n';
const output = 'src/generated/options.ts';
if (process.argv.includes('--check')) { if (readFileSync(output, 'utf8') !== content) throw new Error('Opções divergentes: npm run types'); }
else writeFileSync(output, content);
