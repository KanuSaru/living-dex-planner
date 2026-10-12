"""A tiny bundler for this project's own ES modules, used only for the single-file build.

The website serves src/js as plain ES modules. The single-file page can't load extra files, so this
wraps each module in a function scope and wires imports to exports, in dependency order.

It supports exactly the module syntax this project uses:
    import { a, b } from './x.js';      import * as X from './x.js';
    export function f() / export async function f() / export const|let|class x
"""
import os
import re


def _text(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


IMPORT_NAMED = re.compile(r"^import\s*\{([^}]*)\}\s*from\s*'([^']+)';\s*$", re.M)
IMPORT_STAR = re.compile(r"^import\s*\*\s*as\s+(\w+)\s+from\s*'([^']+)';\s*$", re.M)
EXPORT_DECL = re.compile(r'^export\s+((?:async\s+)?function\s*\*?\s*(\w+)|(?:const|let|class)\s+(\w+))', re.M)
ANY_IMPORT = re.compile(r'^\s*import\b', re.M)
ANY_EXPORT = re.compile(r'^\s*export\b', re.M)


def _resolve(from_key, spec):
    if not spec.startswith('.'):
        raise ValueError(f'{from_key}: only relative imports are supported ({spec})')
    return os.path.normpath(os.path.join(os.path.dirname(from_key), spec)).replace(os.sep, '/')


def _parse(root, key, modules):
    if key in modules:
        return
    src = _text(os.path.join(root, key))
    deps, lines = [], []
    for m in IMPORT_NAMED.finditer(src):
        dep = _resolve(key, m.group(2))
        names = [n.strip() for n in m.group(1).split(',') if n.strip()]
        binds = ', '.join(n.replace(' as ', ': ') for n in names)
        lines.append(f"const {{ {binds} }} = __m['{dep}'];")
        deps.append(dep)
    for m in IMPORT_STAR.finditer(src):
        dep = _resolve(key, m.group(2))
        lines.append(f"const {m.group(1)} = __m['{dep}'];")
        deps.append(dep)
    body = IMPORT_STAR.sub('', IMPORT_NAMED.sub('', src))
    if ANY_IMPORT.search(body):
        raise ValueError(f'{key}: unsupported import syntax')
    exports = []

    def strip_export(m):
        exports.append(m.group(2) or m.group(3))
        return m.group(1)
    body = EXPORT_DECL.sub(strip_export, body)
    if ANY_EXPORT.search(body):
        raise ValueError(f'{key}: unsupported export syntax')
    modules[key] = {'deps': deps, 'code': '\n'.join(lines) + '\n' + body, 'exports': exports}
    for d in deps:
        _parse(root, d, modules)


def bundle(root, entry):
    modules = {}
    _parse(root, entry, modules)
    order, seen = [], set()

    def visit(k, stack=()):
        if k in seen:
            return
        if k in stack:
            raise ValueError('import cycle: ' + ' -> '.join(stack + (k,)))
        for d in modules[k]['deps']:
            visit(d, stack + (k,))
        seen.add(k)
        order.append(k)
    visit(entry)
    out = ['(function () {', "'use strict';", 'const __m = {};']
    for k in order:
        m = modules[k]
        out.append(f'// ---- {k}')
        out.append(f"__m['{k}'] = (function () {{\n{m['code']}\nreturn {{ {', '.join(m['exports'])} }};\n}})();")
    out.append('})();')
    return '\n'.join(out)
