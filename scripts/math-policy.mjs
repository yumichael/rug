// Local checks for the shared Markdown math policy. No subprocesses or network.
import { createRequire } from 'node:module';
import { join } from 'node:path';

let parser;
let katex;
const rendered = new Map();

function load(modules) {
  if (!parser) {
    const require = createRequire(join(modules, 'package.json'));
    const MarkdownIt = require('markdown-it');
    const plugin = require('@vscode/markdown-it-katex').default;
    parser = new MarkdownIt({ html: true }).use(plugin);
    katex = require('katex');
  }
}

function maskCode(text) {
  return text.replace(/(`+)([\s\S]*?)\1(?!`)/g, (match) => match.replace(/[^\n]/g, ' '));
}

export function checkMath(source, { modules, render = false } = {}) {
  if (!source.includes('$') && !/\\[([]/.test(source) && !/^\s*```math\b/m.test(source)) return [];
  load(modules);
  const lines = source.split('\n');
  const issues = [];
  const add = (line, rule, message) => issues.push({ line: line + 1, rule, message });
  const formula = (math, line, display) => {
    if (/\\operatorname\b/.test(math)) add(line, 'MATH003', 'Use \\mathrm{...}; GitHub rejects \\operatorname.');
    if (/\\\\/.test(math)) add(line, 'MATH004', 'Rewrite row breaks as separate equations or conditions; GitHub can alter backslashes.');
    if (math.includes('`')) add(line, 'MATH005', 'Use plain $...$ delimiters; backticks inside math differ between renderers.');
    if (render) {
      const key = `${display}:${math}`;
      if (!rendered.has(key)) {
        try {
          katex.renderToString(math, { displayMode: display, throwOnError: true, strict: 'error', trust: false });
          rendered.set(key, null);
        } catch (error) {
          rendered.set(key, error.message);
        }
      }
      if (rendered.get(key)) add(line, 'MATH008', rendered.get(key));
    }
  };
  const tokens = parser.parse(source, {});
  const stack = [];
  let mappedLine = 0;
  for (const token of tokens) {
    if (token.map) mappedLine = token.map[0];
    if (token.nesting === -1) stack.pop();
    if (token.type === 'fence' && token.info.trim() === 'math') {
      add(token.map[0], 'MATH007', 'Use top-level $$ display math; reserve code fences for code.');
    }
    if (token.type === 'math_block') {
      const [start, end] = token.map;
      if (lines[start] !== '$$' || lines[end - 1] !== '$$' || stack.length || /\n\s*\n/.test(token.content)) {
        add(start, 'MATH007', 'Use unindented $$ delimiters on their own lines, outside lists/quotes, without blank formula lines.');
      }
      formula(token.content.trim(), start, true);
    }
    if (token.type === 'inline') {
      const text = maskCode(token.content);
      const startLine = token.map?.[0] ?? mappedLine;
      const atLine = (offset) => startLine + text.slice(0, offset).split('\n').length - 1;
      if (/\\[([]/.test(text)) add(startLine, 'MATH001', 'Use $...$ or $$...$$ instead of parenthesis/bracket math delimiters.');
      let emphasis = 0;
      for (const child of token.children ?? []) {
        if (child.type === 'em_open') emphasis++;
        if (child.type === 'em_close') emphasis--;
        if (emphasis && child.type.startsWith('math_')) add(startLine, 'MATH006', 'Move math outside italic spans; the tested GitHub layout leaves it literal.');
      }
      for (let i = 0; i < text.length; i++) {
        if (text[i] === '\\') { i++; continue; }
        if (text[i] !== '$') continue;
        const line = atLine(i);
        if (text[i + 1] === '$') {
          add(line, 'MATH007', 'Use $$ display delimiters on separate top-level lines.');
          const end = text.indexOf('$$', i + 2);
          i = end < 0 ? text.length : end + 1;
          continue;
        }
        let end = i + 1;
        while (end < text.length && text[end] !== '\n') {
          if (text[end] === '\\') { end += 2; continue; }
          if (text[end] === '$') break;
          end++;
        }
        if (text[end] !== '$') {
          if (!/\d/.test(text[i + 1] ?? '')) add(line, 'MATH001', 'Unclosed inline math delimiter; escape a literal dollar sign.');
          break;
        }
        const math = text.slice(i + 1, end);
        if (!math.trim() || math !== math.trim()) add(line, 'MATH001', 'Keep nonempty inline math on one line, without spaces just inside the dollars.');
        if (i > 0 && /[\p{L}\p{N}_\p{Pd}\u2212]/u.test(text[i - 1])) add(line, 'MATH002', 'Separate the opening $ from preceding words and hyphens.');
        if (/[\p{L}\p{N}_]/u.test(text[end + 1] ?? '')) add(line, 'MATH002', 'Separate the closing $ from following letters or digits.');
        if (stack.includes('heading_open')) add(line, 'MATH009', 'Use plain text or Unicode in headings for stable navigation.');
        if (stack.includes('table_open') && math.includes('|')) add(line, 'MATH010', 'Use \\lvert, \\rvert, or \\mid instead of table pipes.');
        formula(math, line, false);
        i = end;
      }
    }
    if (token.nesting === 1) stack.push(token.type);
  }
  return issues.filter((issue, i) => issues.findIndex((other) => JSON.stringify(other) === JSON.stringify(issue)) === i);
}
