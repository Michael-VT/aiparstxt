#!/bin/bash
# test_web_parity.sh - the browser analyzer (docs/analyzer.js) must produce the
# same AI Probability as the Node.js console implementation (partxtnode).
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

node - <<'EOF'
const analyzer = require("./docs/analyzer.js");
const { execFileSync } = require("child_process");
const fs = require("fs");

const files = [
  "aitext/textantig.txt",
  "aitext/textantig-0.txt",
  "aitext/chatgpt-com-prompt0-en-answer.txt",
  "aitext/chatgpt-com-prompt0-ru-answer.txt",
  "aitext/chat-deepseek-com-prompt0-uk-answer.txt",
  "aitext/chat-deepseek-com-prompt0-pt-answer.txt",
  "tmp/validation_corpus/ru/amur.txt",
  "testdata/sample.txt",
];

let bad = 0;
for (const f of files) {
  const text = fs.readFileSync(f, "utf-8");
  const metrics = analyzer.calculateAIForensicMetrics(text);
  const result = analyzer.calculateAIProbability(metrics);
  const web = result.probability.toFixed(1);

  const out = execFileSync("node", ["partxtnode/partxt-ext.js", f, "--no-edit", "--no-report"],
                           { encoding: "utf-8" });
  const cli = (out.match(/AI Probability: ([0-9.]+)%/) || [])[1];

  const ok = cli !== undefined && Math.abs(parseFloat(web) - parseFloat(cli)) <= 1.0;
  if (!ok) bad++;
  console.log(`${ok ? "OK " : "BAD"} web=${web}% cli=${cli}%  ${f}`);
}
console.log(bad === 0 ? "Web parity: PASS" : "Web parity: FAIL");
process.exit(bad === 0 ? 0 : 1);
EOF
