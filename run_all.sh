#!/bin/bash
# run_all.sh — Run all aiparstxt implementations with full flags
# Usage: ./run_all.sh [test_file]
set -euo pipefail

TESTFILE="${1:-testdata/sample.txt}"
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== aiparstxt run_all.sh ==="
echo "Test file: $TESTFILE"
echo ""

# Build binaries
echo "--- Building ---"
echo "[C++]"
make -C partxtcpp --no-print-directory partxt

echo "[Rust]"
cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt

echo "[Go]"
(cd partxtgo && GOCACHE=/tmp/aiparstxt-go-cache go build -o partxtgo main.go)
echo ""

# Run each implementation
echo "=== Running all implementations ==="
echo ""

# 1. Python — full flags
echo "[1/6] Python"
python3 partxtpy/partxt.py "$TESTFILE" \
  -l universal \
  -o "${TESTFILE%.txt}.py.ed.txt" \
  -r report_py.txt
echo ""

# 2. Rust — full flags
echo "[2/6] Rust"
./partxtrs/target/release/partxt "$TESTFILE" \
  -o "${TESTFILE%.txt}.rs.ed.txt" \
  -r report_rs.txt
echo ""

# 3. Go — full flags
echo "[3/6] Go"
./partxtgo/partxtgo "$TESTFILE" \
  -o "${TESTFILE%.txt}.go.ed.txt" \
  -r report_go.txt
echo ""

# 4. C++ — full flags
echo "[4/6] C++"
./partxtcpp/partxt "$TESTFILE" \
  -o "${TESTFILE%.txt}.cpp.ed.txt" \
  -r report_cpp.txt
echo ""

# 5. Node.js — full flags
echo "[5/6] Node.js"
node partxtnode/partxt.js "$TESTFILE" \
  -o "${TESTFILE%.txt}.node.ed.txt" \
  -r report_node.txt
echo ""

# 6. Bun — full flags
echo "[6/6] Bun"
bun run partxtjs/partxt.js "$TESTFILE" \
  -o "${TESTFILE%.txt}.bun.ed.txt" \
  -r report_bun.txt
echo ""

# Summary
echo "=== Timing Summary ==="
for report in report_py.txt report_rs.txt report_go.txt report_cpp.txt report_node.txt report_bun.txt; do
  if [ -f "$report" ]; then
    lang=$(grep -m1 "^=== " "$report" | sed 's/=== aiparstxt Report (\(.*\)) ===/\1/' || true)
    if [ -z "$lang" ]; then
      lang=$(grep -m1 "Text Sanitizer Report" "$report" | sed 's/.*Report (\(.*\))/\1/' || true)
    fi
    time=$(grep -m1 "Execution time:" "$report" | awk '{print $3, $4}' || true)
    printf "%-10s %s\n" "$lang" "$time"
  fi
done

echo ""
echo "=== Comparison ==="
echo "Checking that all .ed.txt files have the same number of ? characters:"
for f in "${TESTFILE%.txt}".*.ed.txt; do
  if [ -f "$f" ]; then
    cnt=$(awk -F'?' '{total += NF - 1} END {print total + 0}' "$f")
    echo "  $(basename "$f"): $cnt question marks"
  fi
done

echo ""
echo "Done. Report files: report_*.txt"
