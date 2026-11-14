#!/usr/bin/env node
// Run the pinned rumdl installation for working-tree and indexed Markdown.
import { execFileSync, spawnSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { dirname, join, posix, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { checkMath } from './math-policy.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
process.chdir(root);
const maxBuffer = 128 * 1024 * 1024;
// Match rumdl's native Markdown discovery.
const markdown = (path) => /\.(md|markdown|mdown|mdwn|mkd|mkdn|mdx|qmd|rmd)$/.test(path);
const linkRules = new Set(['MD051', 'MD057']);
const included = (path) => markdown(path) && !path.startsWith('archives/') && !path.split('/').includes('_vendor');

function mathDiagnostics(documents, modules, render) {
  let failed = false;
  for (const [path, source] of documents) {
    for (const issue of checkMath(source, { modules, render })) {
      console.error(`${path}:${issue.line}: [${issue.rule}] ${issue.message}`);
      failed = true;
    }
  }
  return failed;
}

function git(...args) {
  return execFileSync('git', args, { encoding: 'utf8', maxBuffer });
}

function names(output) {
  return output.split('\0').filter(Boolean);
}

async function main() {
  const [mode = '--check', ...paths] = process.argv.slice(2);
  if (!['--check', '--write', '--staged'].includes(mode) || (mode === '--staged' && paths.length)) {
    throw new Error('Usage: node scripts/markdown.mjs [--check|--write] [paths...] or --staged');
  }
  let modules = process.env.RUG_NODE_MODULES;
  if (!modules) {
    const recorded = spawnSync('git', ['config', '--local', '--get', 'rug.nodeModules'], { encoding: 'utf8' });
    modules = recorded.status === 0 ? recorded.stdout.trim() : join(root, 'node_modules');
  }
  modules = resolve(root, modules);
  const packagePath = join(modules, 'rumdl/package.json');
  const pkg = await readFile(packagePath, 'utf8').then(JSON.parse).catch(() => {
    throw new Error('rumdl is unavailable. Run sh scripts/setup-rumdl.sh, preserving RUG_NPM_PREFIX for an external install.');
  });
  const executable = join(dirname(packagePath), typeof pkg.bin === 'string' ? pkg.bin : pkg.bin.rumdl);
  const run = (args, options = {}) => {
    const result = spawnSync(process.execPath, [executable, ...args], { maxBuffer, ...options });
    if (result.error) throw result.error;
    return result;
  };

  if (mode !== '--staged') {
    const args = ['check', '--deny-config-warnings'];
    if (mode === '--write') args.push('--fix');
    args.push(...(paths.length ? paths : ['.']));
    process.exitCode = run(args, { stdio: 'inherit' }).status ?? 1;
    const selected = paths.map((path) => relative(root, resolve(root, path)));
    const candidates = names(git('ls-files', '--cached', '--others', '--exclude-standard', '-z'));
    const documents = new Map();
    for (const path of new Set(candidates)) {
      if (included(path) && (!selected.length || selected.some((prefix) => prefix === '.' || path === prefix || path.startsWith(`${prefix}/`)))) {
        try {
          documents.set(path, await readFile(join(root, path), 'utf8'));
        } catch (error) {
          if (error.code !== 'ENOENT') throw error;
        }
      }
    }
    if (mathDiagnostics(documents, modules, true)) process.exitCode = 1;
    return;
  }

  const staged = new Set(names(git('diff', '--cached', '--name-only', '-z', '--diff-filter=ACMR')).filter(markdown));
  const ignored = new Set(names(git('ls-files', '--cached', '--ignored', '--exclude-standard', '-z')));
  const documents = new Map([['.', '']]);
  for (const entry of names(git('ls-files', '--stage', '-z'))) {
    const tab = entry.indexOf('\t');
    const path = entry.slice(tab + 1);
    const regular = ['100644', '100755'].includes(entry.slice(0, 6));
    documents.set(path, regular && markdown(path) ? git('show', `:${path}`) : '');
    for (let parent = posix.dirname(path); parent !== '.'; parent = posix.dirname(parent)) {
      if (!documents.has(parent)) documents.set(parent, '');
    }
  }
  const active = new Set([...documents.keys()].filter((path) =>
    included(path) && !ignored.has(path),
  ));
  if (!active.size) return;
  for (const path of active) {
    if (staged.has(path)) console.log(`Checking staged Markdown formatting and lint (rumdl): ${path}`);
  }
  if ([...active].some((path) => !staged.has(path))) console.log('Checking Markdown links in unchanged files (rumdl)');
  const payload = [];
  for (const [path, source] of documents) {
    if (source.includes('\0')) throw new Error(`Indexed Markdown contains a NUL byte: ${path}`);
    payload.push(Buffer.from(`${path}\0${source}\0`));
  }
  const result = run([
    'check', '--config', join(root, '.rumdl.toml'), '--stdin-batch', '--stdin-batch-closed-world',
    '--no-exclude', '--respect-gitignore=false', '--no-cache', '--deny-config-warnings', '--output-format', 'json',
  ], { input: Buffer.concat(payload), stdio: ['pipe', 'pipe', 'inherit'], encoding: 'utf8' });
  if (![0, 1].includes(result.status)) {
    process.stderr.write(result.stdout ?? '');
    process.exitCode = 1;
    return;
  }
  let failed = mathDiagnostics([...documents].filter(([path]) => active.has(path) && staged.has(path)), modules, false);
  for (const diagnostic of JSON.parse(result.stdout)) {
    if (active.has(diagnostic.file) && (staged.has(diagnostic.file) || linkRules.has(diagnostic.rule))) {
      console.error(`${diagnostic.file}:${diagnostic.line}:${diagnostic.column}: [${diagnostic.rule}] ${diagnostic.message}`);
      failed = true;
    }
  }
  if (failed) {
    console.error('Run npm run format:markdown for permitted fixes, resolve remaining issues, and stage the intended edits.');
    process.exitCode = 1;
  }
}

main().catch((error) => {
  console.error(`Error checking Markdown: ${error.message}`);
  process.exitCode = 1;
});
