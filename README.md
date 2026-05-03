# aiparstxt — Multi-language Text Sanitizer

A set of command-line utilities that sanitize text files by replacing disallowed characters with '?'. Implemented in 6 languages for performance comparison.

## Allowed Characters
- Digits: 0-9
- Latin letters: A-Z, a-z
- Russian letters: А-Я, а-я (including Ё/ё)
- Punctuation and symbols: []{}()-=_+!@#$%&*;'/.,<>'"`~
- Whitespace: space, tab, newline

All other characters are replaced with '?'.

## CLI Usage (same for all languages)

partxt <input_file> [options]

Options:
  -o, --output <file>   Output file (default: <input>.ed.txt)
  -r, --report <file>   Report file (default: report_<lang>.txt)
  --no-edit             Do not create .ed.txt file
  --no-report           Do not create report file
  -w, --no-words        Exclude word frequency from report
  -h, --help            Show help

## Report Format
Each report includes:
- Execution time
- Table of replaced characters with counts
- Word frequency dictionary (sorted ascending by count)

## Implementations

| Language   | Directory    | Build command                    | Report file      |
|------------|-------------|----------------------------------|------------------|
| Python     | partxtpy/   | (no build needed)                | report_py.txt    |
| Rust       | partxtrs/   | cargo build --release            | report_rs.txt    |
| Go         | partxtgo/   | cd partxtgo && go build          | report_go.txt    |
| C++        | partxtcpp/  | make                             | report_cpp.txt   |
| Node.js    | partxtnode/ | (no build needed)                | report_node.txt  |
| Bun        | partxtjs/   | (no build needed)                | report_bun.txt   |

## Running

### Individual
python3 partxtpy/partxt.py testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cd partxtgo && go run . testdata/sample.txt
cd partxtcpp && make && ./partxt testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt

### All at once
./run_all.sh testdata/sample.txt

## Sample Results (testdata/sample.txt, 197 replacements)

| Language | Execution Time |
|----------|---------------|
| Go       | ~0.0001 s     |
| Rust     | ~0.0003 s     |
| C++      | ~0.0004 s     |
| Python   | ~0.0014 s     |
| Node.js  | ~0.0013 s     |
| Bun      | ~0.0022 s     |

## Versioning
- Patch (0.0.x): bug fixes
- Minor (0.x.0): fully functional, meets requirements
- Major (x.0.0): significant new features

Current version: 0.0.0

## License
MIT
