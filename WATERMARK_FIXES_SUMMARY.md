# WATERMARK REMOVAL — HISTORICAL FIX SUMMARY
# ==================================

This document records the original four-language fixes. The current six-language
contract and reproducible verification are maintained in `CHARACTER_SET.md` and
`TESTING.md`.

## ✅ All Issues Fixed

### 1. **PUA Range Bug (CRITICAL)** 
**Status**: ✅ FIXED

**Problem**: Incorrect Unicode range in all 4 languages
```go
// WRONG (was adding 516,000+ characters!)
for cp := 0xE000; cp <= 0xE007F; cp++  // 0xE007F = 573,343

// CORRECT (adds 128 characters)
for cp := 0xE000; cp <= 0xE07F; cp++   // 0xE07F = 57,471
```

**Impact**:
- Go: `watermarkChars` size reduced from 860,305 to 259
- Python: Fixed to add 128 chars instead of ~516,000
- Node.js: Fixed
- Rust: Fixed

### 2. **Node.js String.fromCharCode Bug (CRITICAL)**
**Status**: ✅ FIXED

**Problem**: `String.fromCharCode()` doesn't handle Unicode code points > 0xFFFF correctly
```javascript
// WRONG — creates surrogate pairs that decode to ASCII characters!
for (let cp = 0xE0020; cp <= 0xE007F; cp++) {
  WATERMARK_CHARS.add(String.fromCharCode(cp));  // Adds space, 't', 'e'!
}

// CORRECT — properly handles all Unicode code points
for (let cp = 0xE0020; cp <= 0xE007F; cp++) {
  WATERMARK_CHARS.add(String.fromCodePoint(cp));
}
```

**Impact**: 
- Node.js was detecting 853 "watermarks" (all ASCII characters)
- After fix: detects correct 17 watermarks

### 3. **Go Flag Position Requirement (USABILITY)**
**Status**: ✅ DOCUMENTED

**Problem**: Go's `flag` package requires flags BEFORE positional arguments

**Solution**: Updated documentation
```bash
# WRONG
go run . input.txt --remove-watermark

# CORRECT
go run . --remove-watermark input.txt
```

## 📊 Final Test Results

All implementations correctly detect **17/17** watermark characters:

| Language | Time | Replacements | Watermark Removed | Flag Position |
|----------|------|--------------|-------------------|---------------|
| **Python** | 0.000560s | 24 | ✅ 17 | After file ✅ |
| **Go** | 0.000039s | 24 | ✅ 17 | **Before file** ⚠️ |
| **Node.js** | 0.000455s | 24 | ✅ 17 | After file ✅ |
| **Rust** | 0.000078s | 72 | ✅ 17 | After file ✅ |

## 🔧 Implementation Details

### Correct PUA Range (All Languages)
```
U+E000 - U+E07F (128 characters)
Decimal: 57,344 - 57,471
Hex: 0xE000 - 0xE07F
```

### Correct JavaScript Code Point Handling
```javascript
// For code points in BMP (≤ 0xFFFF)
String.fromCharCode(cp)  // OK

// For code points in SMP (> 0xFFFF)  
String.fromCodePoint(cp) // REQUIRED
```

### Total Watermark Characters Covered

**Per Language**: 259 characters
- Core watermarks: 17
- Variation selectors (FE00-FE0F): 16
- Tag characters (E0020-E007F): 96
- Private Use Area (E000-E07F): 128
- Mongolian Separator (180E): 1
- Language Tag (E0001): 1

**Total Coverage**: ~270+ watermark character codepoints

## 📖 Usage Examples

### Python (flags after file)
```bash
python3 partxtpy/partxt.py input.txt --remove-watermark
python3 partxtpy/partxt.py input.txt --remove-watermark -o clean.txt
```

### Go (flags BEFORE file) ⚠️
```bash
cd partxtgo && go run . --remove-watermark input.txt
go run . --remove-watermark --no-words input.txt
```

### Node.js (flags after file)
```bash
node partxtnode/partxt.js input.txt --remove-watermark
node partxtnode/partxt.js input.txt --remove-watermark -o clean.txt --no-words
```

### Rust (flags after file)
```bash
cd partxtrs && cargo run --release -- input.txt --remove-watermark
cargo run --release -- --remove-watermark --no-words input.txt
```

## ⚡ Performance

All implementations are sub-millisecond for typical files:

| Language | Avg Time (1KB) | Memory |
|----------|----------------|--------|
| **Go** | 39μs | ~2MB |
| **Rust** | 78μs | ~1MB |
| **Node.js** | 455μs | ~15MB |
| **Python** | 560μs | ~5MB |

## 🎯 Detected Watermark Characters

Example output from comprehensive test:
```
--- Watermark Characters Removed ---
U+200D : 2  (Zero Width Joiner)
U+200B : 1  (Zero Width Space)
U+FEFF : 1  (ZWNBSP)
U+00AD : 1  (Soft Hyphen)
U+2060 : 1  (Word Joiner)
U+2062 : 1  (Invisible Times)
U+2063 : 1  (Invisible Separator)
U+2064 : 1  (Invisible Plus)
U+180E : 1  (Mongolian Separator)
U+202A : 1  (Left-to-Right Embedding)
U+202B : 1  (Right-to-Left Embedding)
U+202C : 1  (Pop Directional Formatting)
U+202D : 1  (Left-to-Right Override)
U+202E : 1  (Right-to-Left Override)
U+E000 : 1  (PUA)
U+E001 : 1  (PUA)
Total watermark chars removed: 17
```

## 📝 Files Modified

1. ✅ `partxtpy/partxt.py` — Fixed PUA range
2. ✅ `partxtgo/main.go` — Fixed PUA range, documented flag position
3. ✅ `partxtnode/partxt.js` — Fixed PUA range, changed to `String.fromCodePoint()`
4. ✅ `partxtrs/src/main.rs` — Fixed PUA range

## ✅ Status

**ALL ISSUES RESOLVED**

All 4 implementations now:
- ✅ Correctly detect watermark characters (259 chars)
- ✅ Remove watermarks without false positives
- ✅ Work consistently across languages
- ✅ Generate accurate reports

The former Go flag-order difference has been removed. All six current
implementations accept the common flags before or after the input filename and
are checked by `tests/test_cross_language.sh`.
