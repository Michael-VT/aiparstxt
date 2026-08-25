#!/bin/bash
# analyze_all.sh - run EVERY analyzer in the project on one text file,
# build what is not built yet, and produce a summarized report.
#
# Usage:   ./analyze_all.sh <textfile>
#
# Included analyzers:
#   honest_ai_detector.py        technical (watermarks/formatting only)
#   parscgpt.py                  legacy basic
#   parscgptv1.py                legacy + confidence
#   parscgptv2.py                standard (conservative)
#   parscgpt-ext.py              extended (full report + AI EVIDENCE)
#   deepseek-AITextAnalyzer.py   marker-based (imported, no CLI of its own)
#   partxt-ext in Python / Rust / Go / C++ / Node.js / Bun (sanitizer+detector)

set -u

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ $# -lt 1 ]; then
    echo "Usage: $0 <textfile>"
    echo "Example: $0 aitext/textantig.txt"
    exit 1
fi

INPUT="$1"
if [ ! -f "$INPUT" ]; then
    echo "Error: file not found: $INPUT"
    exit 1
fi

# ------------------------------------------------------------------
# 0. Runtimes and builds
# ------------------------------------------------------------------
echo "=== Environment check ==="
MISSING=""
command -v python3 >/dev/null 2>&1 || MISSING="$MISSING python3"
command -v node    >/dev/null 2>&1 || echo "NOTE: node not found - Node.js variant will be skipped"
command -v bun     >/dev/null 2>&1 || echo "NOTE: bun not found - Bun variant will be skipped"
if [ -n "$MISSING" ]; then
    echo "Error: required runtimes missing:$MISSING"
    exit 1
fi
# no external modules are used anywhere in this project - nothing to install

build_if_needed() {  # $1=target $2=source $3=build command
    if [ ! -f "$1" ] || [ "$2" -nt "$1" ]; then
        echo "Building $1 ..."
        eval "$3" >/dev/null 2>&1 || eval "$3"
    fi
}
build_if_needed partxtrs/target/release/partxt-ext partxtrs/src/main-ext.rs \
    "cargo build --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext"
build_if_needed partxtgo/partxt-ext partxtgo/main-ext.go \
    "(cd partxtgo && go build -o partxt-ext main-ext.go)"
build_if_needed partxtcpp/partxt-ext partxtcpp/partxt-ext.cpp \
    "make -C partxtcpp partxt-ext"
echo ""

# ------------------------------------------------------------------
# 1. Extended analyzer - full report (this is the main output)
# ------------------------------------------------------------------
echo "=== parscgpt-ext.py (extended analyzer, full report) ==="
EXT_OUT=$(python3 parscgpt-ext.py "$INPUT" 2>&1)
echo "$EXT_OUT"
EXT_SCORE=$(echo "$EXT_OUT" | grep 'estimated_ai_probability' | grep -o '[0-9.]*' | head -1)
echo ""

# Evidence digest: what to look at / edit in the text
EVIDENCE=$(echo "$EXT_OUT" | awk '/AI EVIDENCE/{flag=1;next}/Metric Interpretations/{flag=0}flag' | grep -E '^\s+\[' | head -8)
VERDICT=$(echo "$EXT_OUT" | grep -E '^  verdict:' | head -1 | sed 's/^  verdict: //')

# ------------------------------------------------------------------
# 2. All other analyzers (quiet - score lines only)
# ------------------------------------------------------------------
grab() {  # $1=label  rest=command
    local label="$1"; shift
    local out line
    out=$("$@" 2>/dev/null)
    line=$(echo "$out" | grep -iE 'estimated_ai_probability|Вероятность ИИ' | grep -o '[0-9.]*' | head -1)
    echo "${label}=${line:-ERR}"
}

SCORES=""
SCORES="$SCORES $(grab legacy    python3 parscgpt.py "$INPUT")"
SCORES="$SCORES $(grab legacy_v1 python3 parscgptv1.py "$INPUT")"
SCORES="$SCORES $(grab standard  python3 parscgptv2.py "$INPUT")"
SCORES="$SCORES $(grab technical python3 honest_ai_detector.py "$INPUT")"
SCORES="$SCORES $(grab deepseek  python3 - "$INPUT" <<'PYEOF'
import importlib.util, io, contextlib
spec = importlib.util.spec_from_file_location("ds", "deepseek-AITextAnalyzer.py")
ds = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):   # silence its built-in demo
    spec.loader.exec_module(ds)
r = ds.analyze_ai_text(open(__import__('sys').argv[1], encoding="utf-8").read())
print(f"Вероятность ИИ: {r['ai_probability']}%")
PYEOF
)"

# Six sanitizer+detector implementations
six_scores=""
run_impl() {
    local name="$1"; shift
    local out line score conf
    out=$("$@" 2>/dev/null)
    line=$(echo "$out" | grep 'AI Probability')
    score=$(echo "$line" | grep -o '[0-9.]*%' | tr -d '%')
    conf=$(echo "$line" | grep -o 'confidence: [A-Z]*' | cut -d' ' -f2)
    if [ -z "$score" ]; then score="ERR"; conf="-"; fi
    printf '  %-10s %-8s %s\n' "$name" "$score%" "$conf"
    six_scores="$six_scores $score"
}

echo "=== partxt-ext x6 (sanitizer + detector) ==="
run_impl "python" python3 partxtpy/partxt-ext.py "$INPUT" --no-edit --no-report
[ -x partxtrs/target/release/partxt-ext ] && run_impl "rust" ./partxtrs/target/release/partxt-ext "$INPUT" --no-edit --no-report
[ -x partxtgo/partxt-ext ]                && run_impl "go"   ./partxtgo/partxt-ext "$INPUT" --no-edit --no-report
[ -x partxtcpp/partxt-ext ]               && run_impl "cpp"  ./partxtcpp/partxt-ext "$INPUT" --no-edit --no-report
command -v node >/dev/null 2>&1 && run_impl "node" node partxtnode/partxt-ext.js "$INPUT" --no-edit --no-report
command -v bun  >/dev/null 2>&1 && run_impl "bun"  bun  run partxtjs/partxt-ext.js "$INPUT" --no-edit --no-report
echo ""

# ------------------------------------------------------------------
# 3. Summarized report
# ------------------------------------------------------------------
echo "================ SUMMARIZED REPORT ================"
echo "File: $INPUT"
echo ""
echo "Scores by analyzer:"
for kv in $SCORES; do printf '  %-12s %s\n' "${kv%%=*}" "${kv#*=}%"; done
echo "  extended      ${EXT_SCORE:-ERR}%   <- main analyzer (parscgpt-ext.py)"
for kv in $(echo "$SCORES"); do :; done
printf '  %-12s' "partxt x6:"
for s in $six_scores; do printf ' %s' "$s"; done
echo ""
echo ""
echo "Verdict (extended): $VERDICT"

# Consensus across STATISTICAL analyzers. Excluded: the technical watermark
# detector ("no watermarks" is not "human") and the two legacy analyzers
# (kept for reference only, they over-fire). Current generation: v2, ext,
# deepseek, partxt x6.
CURV="$six_scores $(echo "$SCORES" | tr ' ' '\n' | grep -E '^(standard|deepseek)=' | cut -d= -f2) $EXT_SCORE"
CONS=$(echo "$CURV" | tr ' ' '\n' | grep -E '^[0-9]+\.?[0-9]*$' | awk '{s+=$1;n++} END{if(n)printf "%.1f", s/n; else print "n/a"}')
WORST=$(echo "$CURV" | tr ' ' '\n' | grep -E '^[0-9]+\.?[0-9]*$' | sort -rn | head -1)
echo "Consensus (average, current analyzers): ${CONS}%"
echo "Worst case (strictest analyzer): ${WORST:--}%   <- the number a ban-happy site would act on"
BAND=$(awk -v c="$WORST" 'BEGIN{
    if (c=="") {print "no data"; exit}
    if (c>=70) print "STRONG AI-LIKE - very high ban-risk profile";
    else if (c>=55) print "PROBABLE AI - high risk: edit before publishing";
    else if (c>=35) print "MIXED - moderate risk: review the spots below";
    else if (c>=20) print "WEAK SIGNALS - low risk";
    else print "NO AI-LIKE SIGNALS - lowest risk"}')
echo "Risk band (by worst case): $BAND"
echo ""

# Parity check across the six partxt-ext implementations
vals=$(echo "$six_scores" | tr ' ' '\n' | grep -E '^[0-9]+\.?[0-9]*$' | tr '\n' ' ')
if [ -n "$vals" ]; then
    result=$(awk -v args="$vals" 'BEGIN {
        n = split(args, a, " "); mn = a[1]; mx = a[1]
        for (i = 2; i <= n; i++) { if (a[i] < mn) mn = a[i]; if (a[i] > mx) mx = a[i] }
        printf "%.1f %d", mx - mn, (mx - mn <= 2.0) ? 1 : 0
    }')
    spread=${result%% *}; ok=${result##* }
    echo "Parity of 6 implementations: spread ${spread} p.p. (tolerance 2.0) - $([ "$ok" = "1" ] && echo OK || echo MISMATCH)"
    echo ""
fi

if [ -n "$EVIDENCE" ]; then
    echo "Spots to review / edit before publishing (from AI EVIDENCE):"
    echo "$EVIDENCE"
    echo ""
fi

echo "---------------------------------------------------"
echo "Reading the numbers:"
echo "  The score is NOT a probability of AI authorship;"
echo "  it measures how many AI-typical signals were found."
echo "  <20  no signals found (good, but not a guarantee)"
echo "  20-35 weak signals - usually safe"
echo "  35-55 mixed - check the spots above, rewrite flagged phrases"
echo "  55+  probable AI profile - high chance third-party detectors flag it"
echo "  NOTE-annotations mean the verdict is withheld (short text /"
echo "  out-of-calibration genre) - treat as 'no data', not as 'human'."
