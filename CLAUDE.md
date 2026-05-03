# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**aiparstxt** — Multi-language text sanitizer. Six implementations (Python, Rust, Go, C++, Node.js, Bun) that sanitize text files by replacing disallowed characters with '?'. Designed for cross-language performance comparison.

## Build & Run Commands

### Build all
```bash
# From project root
make -C partxtcpp
cargo build --release --manifest-path partxtrs/Cargo.toml
(cd partxtgo && go build -o partxtgo .)
# Python, Node.js, Bun — no build needed
```

### Run individual
```bash
python3 partxtpy/partxt.py testdata/sample.txt
./partxtrs/target/release/partxt testdata/sample.txt
./partxtgo/partxtgo testdata/sample.txt
./partxtcpp/partxt testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt
```

### Run all + timing comparison
```bash
./run_all.sh testdata/sample.txt
```

## CLI Interface (consistent across all implementations)

```
partxt <input_file> [-o output] [-r report] [--no-edit] [--no-report] [-w]
```

- `-o` / `--output`: output file (default: `<input>.ed.txt`)
- `-r` / `--report`: report file (default: `report_<lang>.txt`)
- `--no-edit`: skip writing .ed.txt
- `--no-report`: skip writing report
- `-w` / `--no-words`: exclude word frequency from report

## Allowed Characters

Digits `0-9`, Latin `A-Za-z`, Russian `А-Яа-я` (incl. Ёё), punctuation `[]{}()-=_+!@#$%&*;'/.,<>'"\`~`, whitespace. Everything else → `?`.

## Architecture

Each implementation in its own subdirectory follows the same structure:

1. **Parse CLI args** → input file, output path, report path, flags
2. **Read input** as UTF-8
3. **Process**: iterate characters, check against allowed set, replace disallowed with '?', count replacements per character
4. **Word frequency**: split processed text on non-alphanumeric boundaries (keeping `'` and `-`), count occurrences
5. **Write output** (.ed.txt) and **report** (replacements table + word frequency sorted ascending + execution time)

Report filenames include language prefix: `report_py.txt`, `report_rs.txt`, `report_go.txt`, `report_cpp.txt`, `report_node.txt`, `report_bun.txt`.

## Versioning

Semantic: patch (0.0.x) = bug fixes, minor (0.x.0) = meets requirements, major (x.0.0) = significant new features. Current: 0.0.0.

## Key Files

- `testdata/sample.txt` — test file with diverse Unicode characters
- `run_all.sh` — builds and runs all implementations, shows timing comparison
- `partxtcpp/Makefile` — C++ build (g++, C++20, -O2)
- `partxtrs/Cargo.toml` — Rust project (no external deps)
- `partxtgo/go.mod` — Go module
