#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TMP_DIR="$(mktemp -d /tmp/aiparstxt-tests.XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT

echo "Building implementations..."
make -C partxtcpp --no-print-directory all >/dev/null
cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt --quiet
cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext --quiet

(cd partxtgo && GOCACHE="$TMP_DIR/go-cache" go build -o "$TMP_DIR/partxtgo" main.go)
(cd partxtgo && GOCACHE="$TMP_DIR/go-cache" go build -o "$TMP_DIR/partxtgo-ext" main-ext.go)

echo "Checking standard output equivalence..."
python3 partxtpy/partxt.py testdata/sample.txt -l universal -o "$TMP_DIR/standard-py.txt" --no-report >/dev/null
./partxtrs/target/release/partxt testdata/sample.txt -o "$TMP_DIR/standard-rs.txt" --no-report >/dev/null
"$TMP_DIR/partxtgo" testdata/sample.txt -o "$TMP_DIR/standard-go.txt" --no-report >/dev/null
./partxtcpp/partxt testdata/sample.txt -o "$TMP_DIR/standard-cpp.txt" --no-report >/dev/null
node partxtnode/partxt.js testdata/sample.txt -o "$TMP_DIR/standard-node.txt" --no-report >/dev/null
bun run partxtjs/partxt.js testdata/sample.txt -o "$TMP_DIR/standard-bun.txt" --no-report >/dev/null

for implementation in rs go cpp node bun; do
    cmp "$TMP_DIR/standard-py.txt" "$TMP_DIR/standard-${implementation}.txt"
done

echo "Checking watermark removal and flag placement..."
python3 partxtpy/partxt.py testdata/comprehensive_watermark_test.txt -l universal --remove-watermark -o "$TMP_DIR/wm-py.txt" --no-report >/dev/null
./partxtrs/target/release/partxt testdata/comprehensive_watermark_test.txt --remove-watermark -o "$TMP_DIR/wm-rs.txt" --no-report >/dev/null
"$TMP_DIR/partxtgo" testdata/comprehensive_watermark_test.txt --remove-watermark -o "$TMP_DIR/wm-go.txt" --no-report >/dev/null
./partxtcpp/partxt testdata/comprehensive_watermark_test.txt --remove-watermark -o "$TMP_DIR/wm-cpp.txt" --no-report >/dev/null
node partxtnode/partxt.js testdata/comprehensive_watermark_test.txt --remove-watermark -o "$TMP_DIR/wm-node.txt" --no-report >/dev/null
bun run partxtjs/partxt.js testdata/comprehensive_watermark_test.txt --remove-watermark -o "$TMP_DIR/wm-bun.txt" --no-report >/dev/null

for implementation in rs go cpp node bun; do
    cmp "$TMP_DIR/wm-py.txt" "$TMP_DIR/wm-${implementation}.txt"
done

python3 - "$TMP_DIR/wm-py.txt" <<'PY'
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
watermarks = set("\u200b\u200c\u200d\ufeff\u00ad\u2060\u2061\u2062\u2063\u2064\u202a\u202b\u202c\u202d\u202e\u2028\u2029\u180e\U000e0001")
watermarks.update(chr(cp) for cp in range(0xFE00, 0xFE10))
watermarks.update(chr(cp) for cp in range(0xE0020, 0xE0080))
watermarks.update(chr(cp) for cp in range(0xE000, 0xE080))
assert not (set(text) & watermarks), "watermark character remained in cleaned output"
PY

echo "Checking extended entry points..."
python3 partxtpy/partxt-ext.py testdata/sample.txt -o "$TMP_DIR/extended-py.txt" --no-report >/dev/null
./partxtrs/target/release/partxt-ext testdata/sample.txt -o "$TMP_DIR/extended-rs.txt" --no-report >/dev/null
"$TMP_DIR/partxtgo-ext" testdata/sample.txt -o "$TMP_DIR/extended-go.txt" --no-report >/dev/null
./partxtcpp/partxt-ext testdata/sample.txt -o "$TMP_DIR/extended-cpp.txt" --no-report >/dev/null
node partxtnode/partxt-ext.js testdata/sample.txt -o "$TMP_DIR/extended-node.txt" --no-report >/dev/null
bun run partxtjs/partxt-ext.js testdata/sample.txt -o "$TMP_DIR/extended-bun.txt" --no-report >/dev/null

for implementation in rs go cpp node bun; do
    cmp "$TMP_DIR/extended-py.txt" "$TMP_DIR/extended-${implementation}.txt"
done

echo "All cross-language tests passed."
