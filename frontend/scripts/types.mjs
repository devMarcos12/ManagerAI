import { execFileSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
const check = process.argv.includes('--check');
const temporary = check ? mkdtempSync(join(tmpdir(), 'managerai-contract-')) : null;
const target = 'src/generated/api.d.ts';
try {
  const output = temporary ? join(temporary, 'api.d.ts') : target;
  execFileSync(process.execPath, ['node_modules/.bin/openapi-typescript', 'openapi.json', '-o', output], { stdio: 'inherit' });
  if (check && readFileSync(output, 'utf8') !== readFileSync(target, 'utf8')) throw new Error('Tipos divergentes: npm run types');
} finally { if (temporary) rmSync(temporary, { recursive: true }); }
