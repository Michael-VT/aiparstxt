#!/bin/bash
# run_all_extended.sh - Run all extended AI forensic analyzers

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_file> [options]"
    echo "Example: $0 testdata/sample.txt --remove-watermark"
    exit 1
fi

INPUT="$1"
shift
OPTIONS="$@"

echo "=== Running all extended AI forensic analyzers ==="
echo "Input: $INPUT"
echo "Options: $OPTIONS"
echo ""

# Python Extended
echo "→ Running Python Extended..."
python3 partxtpy/partxt-ext.py "$INPUT" $OPTIONS || echo "  ✗ Python failed"
echo ""

# Rust Extended
echo "→ Running Rust Extended..."
if [ -f "partxtrs/target/release/partxt-ext" ]; then
    partxtrs/target/release/partxt-ext "$INPUT" $OPTIONS || echo "  ✗ Rust failed"
else
    echo "  Building Rust extended version..."
    cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext
    partxtrs/target/release/partxt-ext "$INPUT" $OPTIONS || echo "  ✗ Rust failed"
fi
echo ""

# Go Extended
echo "→ Running Go Extended..."
cd partxtgo && go run main-ext.go "../$INPUT" $OPTIONS && cd .. || echo "  ✗ Go failed"
echo ""

# C++ Extended
echo "→ Running C++ Extended..."
cd partxtcpp
if [ ! -f "partxt-ext" ]; then
    echo "  Building C++ extended version..."
    make partxt-ext
fi
./partxt-ext "../$INPUT" $OPTIONS && cd .. || echo "  ✗ C++ failed"
echo ""

# Node.js Extended
echo "→ Running Node.js Extended..."
node partxtnode/partxt-ext.js "$INPUT" $OPTIONS || echo "  ✗ Node.js failed"
echo ""

# Bun Extended
echo "→ Running Bun Extended..."
bun run partxtjs/partxt-ext.js "$INPUT" $OPTIONS || echo "  ✗ Bun failed"
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
