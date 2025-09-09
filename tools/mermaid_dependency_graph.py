#!/usr/bin/env python3
# mermaid_deps.py
# Generate a Mermaid dependency graph (imports) for a Python codebase.
# Requires: Python 3.8+ (tested with 3.13) and click (optional for CLI ergonomics).

import ast
import os
import sys
import fnmatch
import click
from collections import defaultdict
from typing import Dict, Set, Tuple, Iterable, List, Optional

# -------- Filesystem & module resolution --------

def is_package_dir(path: str) -> bool:
    return os.path.isfile(os.path.join(path, "__init__.py"))

def iter_python_files(root: str, excludes: List[str]) -> Iterable[str]:
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        # Apply directory-level excludes early
        pruned = []
        for d in list(dirnames):
            full = os.path.join(dirpath, d)
            rel = os.path.relpath(full, root)
            if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(full, pat) for pat in excludes):
                pruned.append(d)
        for d in pruned:
            dirnames.remove(d)

        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            full = os.path.join(dirpath, filename)
            rel = os.path.relpath(full, root)
            if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(full, pat) for pat in excludes):
                continue
            yield full

def find_package_anchor(root: str, file_path: str) -> str:
    """
    For a given file, find the highest directory (<= root) that is still part of the package
    chain (i.e., contains __init__.py). If none, return the file's directory.
    """
    root = os.path.abspath(root)
    d = os.path.dirname(os.path.abspath(file_path))
    last_pkg_dir = None
    while True:
        if is_package_dir(d):
            last_pkg_dir = d
        # Stop if we reached or crossed root
        if os.path.normpath(d) == os.path.normpath(root):
            break
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return last_pkg_dir or os.path.dirname(os.path.abspath(file_path))

def module_name_from_path(root: str, file_path: str) -> str:
    """
    Determine the module name for file_path relative to root. If the file is within a package
    chain, use package-based qualification. Otherwise, derive dotted path from root.
    """
    root = os.path.abspath(root)
    file_path = os.path.abspath(file_path)
    anchor = find_package_anchor(root, file_path)
    # Build from anchor if package; else from root
    base = anchor if is_package_dir(anchor) else root
    rel = os.path.relpath(file_path, base)
    mod = rel[:-3] if rel.endswith(".py") else rel  # strip .py
    parts = []
    for p in mod.split(os.sep):
        if p == "__init__":
            continue
        parts.append(p)
    dotted = ".".join(parts).strip(".")
    return dotted or os.path.basename(base)

def current_package_name(module_name: str) -> str:
    """Return the package portion of a module (everything before last dot)."""
    return module_name.rsplit(".", 1)[0] if "." in module_name else ""

def ascend_package(pkg: str, levels: int) -> str:
    if levels <= 0 or not pkg:
        return pkg
    parts = pkg.split(".")
    if levels >= len(parts):
        return ""
    return ".".join(parts[:-levels])

# -------- AST import extraction --------

class ImportCollector(ast.NodeVisitor):
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.deps: Set[str] = set()

    def visit_Import(self, node: ast.Import):
        for alias in node.names:
            # Keep full top-level or full name? Use full for precision.
            if alias.name:
                self.deps.add(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # node.module can be None (e.g., from . import x)
        level = getattr(node, "level", 0) or 0
        base_pkg = ascend_package(current_package_name(self.module_name), level)
        base = node.module or ""
        qualified_base = base if not base_pkg else (f"{base_pkg}.{base}" if base else base_pkg)

        for alias in node.names:
            if alias.name == "*":
                # Can't know all star-imported names statically; depend on the base module
                target = qualified_base
            else:
                target = f"{qualified_base}.{alias.name}" if qualified_base else alias.name
            if target:
                self.deps.add(target)

def extract_imports_from_file(file_path: str, module_name: str) -> Set[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            src = f.read()
        tree = ast.parse(src, filename=file_path)
    except (SyntaxError, UnicodeDecodeError):
        return set()
    collector = ImportCollector(module_name)
    collector.visit(tree)
    return collector.deps

# -------- Graph building --------

def canonicalize_internal_roots(modules: Iterable[str]) -> Set[str]:
    """
    Determine plausible "internal" root names. We take the first segment of every module name.
    """
    roots = set()
    for m in modules:
        roots.add(m.split(".", 1)[0])
    return roots

def resolve_dependency_targets(deps: Set[str]) -> Set[str]:
    """
    Normalize dependency targets to reasonable module ids:
    - Strip trailing dots
    - Remove leading dots (shouldn't exist after resolution)
    """
    out = set()
    for d in deps:
        d = d.strip(".")
        if d:
            out.add(d)
    return out

# -------- Mermaid emission --------

def safe_node_id(name: str) -> str:
    # Mermaid node id rules: letters, numbers, underscore recommended.
    # Replace other characters with underscore and ensure it doesn't start with a number.
    import re
    s = re.sub(r"[^0-9A-Za-z_]", "_", name)
    if s and s[0].isdigit():
        s = "_" + s
    return s or "_"

def shorten_label(name: str, max_len: int) -> str:
    if max_len <= 0:
        return name
    if len(name) <= max_len:
        return name
    head = max_len - 1
    return name[:head] + "…"

def render_mermaid(
    edges: Set[Tuple[str, str]],
    nodes: Set[str],
    direction: str,
    internal_roots: Set[str],
    only_internal: bool,
    max_label_len: int,
) -> str:
    dir_map = {"TD", "LR", "BT", "RL"}
    direction = direction if direction in dir_map else "TD"

    # Filter edges if only_internal
    if only_internal:
        def is_internal(m: str) -> bool:
            return m.split(".", 1)[0] in internal_roots
        edges = {(a, b) for (a, b) in edges if is_internal(a) and is_internal(b)}
        nodes = {n for n in nodes if is_internal(n)}

    # Build id map
    all_modules = sorted(nodes)
    id_map: Dict[str, str] = {m: safe_node_id(m) for m in all_modules}

    # Prepare class membership
    internal_class: Set[str] = set()
    external_class: Set[str] = set()
    for m in all_modules:
        root = m.split(".", 1)[0]
        (internal_class if root in internal_roots else external_class).add(id_map[m])

    lines = []
    lines.append(f"graph {direction}")
    # Node declarations with labels
    for m in all_modules:
        nid = id_map[m]
        label = shorten_label(m, max_label_len)
        # Backtick labels are safer for dots and punctuation in Mermaid
        lines.append(f'  {nid}["`{label}`"]')

    # Edges
    for a, b in sorted(edges):
        if a not in id_map or b not in id_map:
            # Might have been filtered by only-internal
            continue
        lines.append(f"  {id_map[a]} --> {id_map[b]}")

    # Styles
    lines.append("  classDef internal fill:#e7f5ff,stroke:#1c7ed6,color:#0b7285;")
    lines.append("  classDef external fill:#f8f9fa,stroke:#adb5bd,color:#495057,stroke-dasharray: 3 3;")

    if internal_class:
        lines.append("  class " + ",".join(sorted(internal_class)) + " internal;")
    if external_class and not only_internal:
        lines.append("  class " + ",".join(sorted(external_class)) + " external;")

    return "\n".join(lines)

# -------- CLI --------

@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option("--root", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True), default=".", help="Project root to scan.")
@click.option("--direction", type=click.Choice(["TD", "LR", "BT", "RL"]), default="TD", help="Mermaid graph direction.")
@click.option("--exclude", "-x", multiple=True, help="Glob(s) to exclude (relative to root), e.g. '*/tests/*' or '.venv/*'. Can be repeated.")
@click.option("--only-internal", is_flag=True, default=False, help="Include only edges where both ends are internal modules.")
@click.option("--max-label-len", type=int, default=60, help="Truncate long labels to this many characters (0 to disable).")
@click.option("--follow-namespace", is_flag=True, default=False, help="Placeholder: namespace pkg handling is not required; kept for compatibility.")
def main(root: str, direction: str, exclude: Tuple[str, ...], only_internal: bool, max_label_len: int, follow_namespace: bool):
    root = os.path.abspath(root)
    excludes = list(exclude)

    # Gather modules and dependencies
    file_to_mod: Dict[str, str] = {}
    all_modules: Set[str] = set()
    for py in iter_python_files(root, excludes):
        mod = module_name_from_path(root, py)
        file_to_mod[py] = mod
        all_modules.add(mod)

    deps_by_mod: Dict[str, Set[str]] = defaultdict(set)
    for file_path, mod_name in file_to_mod.items():
        deps = extract_imports_from_file(file_path, mod_name)
        deps_by_mod[mod_name] |= resolve_dependency_targets(deps)

    # Build edge set
    edges: Set[Tuple[str, str]] = set()
    nodes: Set[str] = set(all_modules)
    # Determine internal roots from discovered modules (first segment)
    internal_roots = canonicalize_internal_roots(all_modules)

    # Fold external dependency names to their root module for sanity
    for src, deps in deps_by_mod.items():
        for dep in deps:
            # Keep full internal module names when possible, but for external modules,
            # reduce to their top-level package to avoid noisy graphs.
            dep_root = dep.split(".", 1)[0]
            if dep_root in internal_roots:
                # Keep full internal dependency if present among discovered modules; otherwise keep root
                target = dep if dep in all_modules else dep_root
            else:
                target = dep_root
            edges.add((src, target))
            nodes.add(target)

    mermaid = render_mermaid(
        edges=edges,
        nodes=nodes,
        direction=direction,
        internal_roots=internal_roots,
        only_internal=only_internal,
        max_label_len=max_label_len,
    )
    sys.stdout.write(mermaid + "\n")

if __name__ == "__main__":
    main()
