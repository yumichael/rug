import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { checkMath } from '../math-policy.mjs';

const root = fileURLToPath(new URL('../../', import.meta.url));
const modules = resolve(root, 'node_modules');
const fixtures = JSON.parse(readFileSync(new URL('fixtures/math-cases.json', import.meta.url), 'utf8'));

test('renderer upgrades require updating the compatibility record', () => {
  const pkg = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
  for (const [name, version] of Object.entries(fixtures.localReference)) {
    assert.equal(pkg.devDependencies[name], version, `Retest compatibility after changing ${name}`);
  }
});

test('plain documents need no parser installation', () => {
  assert.deepEqual(checkMath('# Plain\n\nText.\n', { modules: '/missing' }), []);
});

for (const fixture of fixtures.cases) {
  test(fixture.name, () => {
    for (const render of [false, true]) {
      const expected = render ? fixture.rules : (fixture.fastRules ?? fixture.rules);
      const issues = checkMath(fixture.source, { modules, render });
      assert.deepEqual([...new Set(issues.map((issue) => issue.rule))].sort(), [...expected].sort());
    }
  });
}

test('reports original source lines, including table cells', () => {
  const issues = checkMath('# Heading\n\n| A |\n| --- |\n| $a\\|b$ |\n\nword-$H$\n', { modules });
  assert.equal(issues.find((issue) => issue.rule === 'MATH010').line, 5);
  assert.equal(issues.find((issue) => issue.rule === 'MATH002').line, 7);
});

test('the real staged runner checks indexed math and ignores unchanged math', () => {
  // Stub only Git reads; execute the real runner, parser, and rumdl. No Git mutations.
  const directory = mkdtempSync(join(tmpdir(), 'rug-markdown-test-'));
  try {
    const stub = join(directory, process.platform === 'win32' ? 'git.cmd' : 'git');
    if (process.platform === 'win32') return; // Hooks and this executable stub target POSIX.
    writeFileSync(stub, `#!${process.execPath}\nconst a=process.argv.slice(2);\nconst files=JSON.parse(process.env.RUG_TEST_FILES);\nlet out='';\nif(a[0]==='diff') out=JSON.parse(process.env.RUG_TEST_STAGED).join('\\0')+'\\0';\nelse if(a.includes('--ignored')) out='';\nelse if(a.includes('--stage')) out=Object.keys(files).map(p=>'100644 '+'a'.repeat(40)+' 0\\t'+p).join('\\0')+'\\0';\nelse if(a[0]==='show') out=files[a[1].slice(1)];\nelse throw Error('Unexpected Git read: '+a.join(' '));\nprocess.stdout.write(out);\n`, { mode: 0o755 });
    const run = (files, staged) => spawnSync(process.execPath, ['scripts/markdown.mjs', '--staged'], {
      cwd: root, encoding: 'utf8', env: {
        ...process.env, PATH: `${directory}:${process.env.PATH}`, RUG_NODE_MODULES: modules,
        RUG_TEST_FILES: JSON.stringify(files), RUG_TEST_STAGED: JSON.stringify(staged),
      },
    });
    const invalid = '# Test\n\nword-$H$\n';
    const bad = run({ 'README.md': invalid }, ['README.md']);
    assert.equal(bad.status, 1, bad.stderr);
    assert.match(bad.stderr, /README.md:3: \[MATH002\]/);
    const good = run({ 'README.md': '# Test\n\nTake $H$.\n', 'unchanged.md': invalid }, ['README.md']);
    assert.equal(good.status, 0, good.stderr);
    assert.doesNotMatch(good.stderr, /MATH/);
    // Full KaTeX rendering belongs to CI/on-demand, not the hook.
    const syntax = run({ 'README.md': '# Test\n\n$\\unknownRugCommand{x}$\n' }, ['README.md']);
    assert.equal(syntax.status, 0, syntax.stderr);
    const links = run({ 'README.md': '# Test\n\n[Missing](missing.md)\n' }, []);
    assert.equal(links.status, 1, links.stderr);
    assert.match(links.stderr, /MD057/);
  } finally {
    rmSync(directory, { recursive: true, force: true });
  }
});
