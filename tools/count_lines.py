#!/usr/bin/env python3
import argparse
import ast
import os
from pathlib import Path
from typing import Iterable, Tuple, Set, List


def is_excluded(path: Path, excluded: Set[str]) -> bool:
    # Exclude if any path segment exactly matches an excluded name (e.g., ".venv")
    return any(part in excluded for part in path.parts)


def find_python_files(paths: Iterable[str], excluded: Set[str]) -> Iterable[Path]:
    for p in paths:
        path = Path(p)
        if path.is_file() and path.suffix == ".py":
            if not is_excluded(path, excluded):
                yield path
        elif path.is_dir():
            # Walk and prune excluded directories
            for root, dirnames, filenames in os.walk(path, topdown=True):
                root_path = Path(root)

                # Prune excluded directories in-place
                dirnames[:] = [d for d in dirnames if d not in excluded]

                # Skip this root if it's inside an excluded directory
                if is_excluded(root_path, excluded):
                    continue

                for filename in filenames:
                    if filename.endswith(".py"):
                        file_path = root_path / filename
                        if not is_excluded(file_path, excluded):
                            yield file_path


def docstring_ranges(source: str) -> Set[Tuple[int, int]]:
    ranges: Set[Tuple[int, int]] = set()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return ranges

    def maybe_add_doc(node):
        if not hasattr(node, "body") or not node.body:
            return
        first = node.body[0]
        if isinstance(first, ast.Expr) and isinstance(
            getattr(first, "value", None), (ast.Constant, ast.Constant)
        ):
            value = first.value.value if isinstance(first.value, ast.Constant) else first.value.value
            if isinstance(value, str):
                lineno = getattr(first, "lineno", None)
                end_lineno = getattr(first, "end_lineno", lineno)
                if lineno is not None and end_lineno is not None:
                    ranges.add((lineno, end_lineno))

    maybe_add_doc(tree)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            maybe_add_doc(node)

    return ranges


def in_any_range(line_no: int, ranges: Set[Tuple[int, int]]) -> bool:
    return any(start <= line_no <= end for start, end in ranges)


def count_lines_in_source(source: str) -> Tuple[int, int, int]:
    """
    Returns (total_lines, non_empty_lines, code_lines)
    code_lines excludes blank lines, full-line comments, and docstrings.
    """
    lines = source.splitlines()
    total = len(lines)
    non_empty = 0
    code = 0

    ds_ranges = docstring_ranges(source)

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped:
            non_empty += 1

        if in_any_range(i, ds_ranges):
            continue
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue

        code += 1

    return total, non_empty, code


def count_file(path: Path) -> Tuple[int, int, int]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(errors="ignore")
    return count_lines_in_source(text)


def parse_excludes(values: List[str] | None) -> Set[str]:
    # Default excludes include .venv
    excludes = {".venv"}
    if values:
        for v in values:
            # Support comma-separated or repeated flags
            for name in v.split(","):
                name = name.strip()
                if name:
                    excludes.add(name)
    return excludes


def main():
    parser = argparse.ArgumentParser(description="Count Python lines in files/directories.")
    parser.add_argument("paths", nargs="+", help="Files or directories to scan (recursively for .py files).")
    parser.add_argument("--per-file", action="store_true", help="Show counts per file instead of just totals.")
    parser.add_argument("--relative", action="store_true", help="Show file paths relative to current working directory.")
    parser.add_argument(
        "--exclude",
        action="append",
        help="Directory names to exclude (exact folder name match). Can be used multiple times or comma-separated. "
             "Defaults to '.venv'.",
    )
    args = parser.parse_args()

    excluded = parse_excludes(args.exclude)

    files = list(find_python_files(args.paths, excluded))
    if not files:
        print("No .py files found.")
        return

    grand_total = grand_non_empty = grand_code = 0

    for f in files:
        t, n, c = count_file(f)
        grand_total += t
        grand_non_empty += n
        grand_code += c

        if args.per_file:
            display = os.path.relpath(f) if args.relative else str(f)
            print(f"{display}: total={t}, non-empty={n}, code={c}")

    print("Totals:")
    print(f"  total lines:     {grand_total}")
    print(f"  non-empty lines: {grand_non_empty}")
    print(f"  code lines:      {grand_code}")


if __name__ == "__main__":
    main()