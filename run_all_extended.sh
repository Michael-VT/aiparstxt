#!/bin/bash
# run_all_extended.sh - Run all extended AI forensic analyzers

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_file> [options]"
    echo "Example: $0 testdata/sample.txt --remove-watermark"
    exit 1
fi

INPUT="$1"
shift
OPTIONS=("$@")

echo "=== Running all extended AI forensic analyzers ==="
echo "Input: $INPUT"
printf 'Options:'
printf ' %q' ${OPTIONS+"${OPTIONS[@]}"}
printf '\n'
echo ""

# Python Extended
echo "→ Running Python Extended..."
python3 partxtpy/partxt-ext.py "$INPUT" ${OPTIONS+"${OPTIONS[@]}"}
echo ""

# Rust Extended
echo "→ Running Rust Extended..."
cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext
partxtrs/target/release/partxt-ext "$INPUT" ${OPTIONS+"${OPTIONS[@]}"}
echo ""

# Go Extended
echo "→ Running Go Extended..."
(cd partxtgo && GOCACHE=/tmp/aiparstxt-go-cache go build -o partxt-ext main-ext.go)
partxtgo/partxt-ext "$INPUT" ${OPTIONS+"${OPTIONS[@]}"}
echo ""

# C++ Extended
echo "→ Running C++ Extended..."
make -C partxtcpp --no-print-directory partxt-ext
partxtcpp/partxt-ext "$INPUT" ${OPTIONS+"${OPTIONS[@]}"}
echo ""

# Node.js Extended
echo "→ Running Node.js Extended..."
node partxtnode/partxt-ext.js "$INPUT" ${OPTIONS+"${OPTIONS[@]}"}
echo ""

# Bun Extended
echo "→ Running Bun Extended..."
bun run partxtjs/partxt-ext.js "$INPUT" ${OPTIONS+"${OPTIONS[@]}"}
echo ""

echo "=== All extended analyzers completed ==="
echo ""
echo "Generated reports:"
echo "  - report_py-ext.txt (Python)"
echo "  - report_rs-ext.txt (Rust)"
echo "  - report_go-ext.txt (Go)"
echo "  - report_cpp-ext.txt (C++)"
echo "  - report_node-ext.txt (Node.js)"
echo "  - report_bun-ext.txt (Bun)"
