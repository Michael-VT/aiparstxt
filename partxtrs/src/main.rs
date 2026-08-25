use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::Path;
use std::time::Instant;

const ALLOWED: &str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\
АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя\
[]{}()-=_+!@#$%&*;'/.,<>\"`~ \\t\\n\\r";

// AI Watermark Characters (невидимые маркеры, которые ИИ-системы используют для watermarking)
fn is_watermark(ch: char) -> bool {
    let cp = ch as u32;
    // Explicit watermark characters
    if matches!(cp,
        0x200B | // Zero Width Space (ZWSP)
        0x200C | // Zero Width Non-Joiner (ZWNJ)
        0x200D | // Zero Width Joiner (ZWJ)
        0xFEFF | // Zero Width No-Break Space (ZWNBSP, BOM)
        0x00AD | // Soft Hyphen (SHY)
        0x2060 | // Word Joiner
        0x2061 | // Function Application
        0x2062 | // Invisible Times
        0x2063 | // Invisible Separator
        0x2064 | // Invisible Plus
        0x202A | // Left-to-Right Embedding
        0x202B | // Right-to-Left Embedding
        0x202C | // Pop Directional Formatting
        0x202D | // Left-to-Right Override
        0x202E | // Right-to-Left Override
        0x2028 | // Line Separator
        0x2029 | // Paragraph Separator
        0xE0001 | // Language Tag
        0x180E | // Mongolian Separator (often abused as watermark)
        (0xFE00..=0xFE0F) | // Variation Selectors 1-16
        (0xE0020..=0xE007F)   // Tag characters
    ) {
        return true;
    }
    // Private Use Area - commonly abused for watermarking (E000-E07F, 128 chars)
    if cp >= 0xE000 && cp <= 0xE07F {
        return true;
    }
    false

}




const CANONICAL_ALLOWED: &str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюяҐґЄєІіЇїàáâãéêíóôõúçÀÁÂÃÉÊÍÓÔÕÚÇ[]{}():()-=_+!@#$%&*;'/.,<>\"`~—«» \t\n\r";

fn is_allowed(ch: char) -> bool {
    CANONICAL_ALLOWED.contains(ch)
}

fn process(text: &str, remove_watermark: bool) -> (String, HashMap<char, usize>, HashMap<char, usize>) {
    let mut replaced: HashMap<char, usize> = HashMap::new();
    let mut watermark_removed: HashMap<char, usize> = HashMap::new();
    let mut out = String::with_capacity(text.len());
    for ch in text.chars() {
        // Сначала проверяем watermark - он удаляется всегда, если включено
        if remove_watermark && is_watermark(ch) {
            *watermark_removed.entry(ch).or_insert(0) += 1;
            continue;
        }
        if is_allowed(ch) {
            out.push(ch);
        } else {
            *replaced.entry(ch).or_insert(0) += 1;
            out.push('?');
        }
    }
    (out, replaced, watermark_removed)
}


fn word_frequency(text: &str) -> HashMap<String, usize> {
    let mut freq: HashMap<String, usize> = HashMap::new();
    let mut cur = String::new();
    for ch in text.chars() {
        if ch.is_alphanumeric() || ch == '\'' || ch == '-' {
            cur.push(ch);
        } else {
            if !cur.is_empty() {
                *freq.entry(cur.clone()).or_insert(0) += 1;
                cur.clear();
            }
        }
    }
    if !cur.is_empty() {
        *freq.entry(cur).or_insert(0) += 1;
    }
    freq
}

fn build_report(
    input_file: &str,
    output_file: &str,
    replaced: &HashMap<char, usize>,
    watermark_removed: &HashMap<char, usize>,
    word_freq: &Option<HashMap<String, usize>>,
    elapsed: std::time::Duration,
    remove_watermark: bool,
) -> String {
    let mut lines: Vec<String> = Vec::new();
    let now = chrono_local_now();
    lines.push(format!("=== aiparstxt Report (Rust) ==="));
    lines.push(format!("Date: {}", now));
    lines.push(format!("Input file: {}", input_file));
    lines.push(format!("Output file: {}", output_file));
    let mut mode = "replace with '?'".to_string();
    if remove_watermark {
        mode.push_str(" + watermark removal");
    }
    lines.push(format!("Mode: {}", mode));
    lines.push(format!("Execution time: {:.6} s", elapsed.as_secs_f64()));
    lines.push(String::new());
    if !watermark_removed.is_empty() {
        lines.push("--- Watermark Characters Removed ---".to_string());
        let mut sorted: Vec<_> = watermark_removed.iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(a.1));
        let mut total = 0usize;
        for (&ch, &cnt) in &sorted {
            lines.push(format!("U+{:04X} : {}", ch as u32, cnt));
            total += cnt;
        }
        lines.push(format!("Total watermark chars removed: {}", total));
        lines.push(String::new());
    }
    lines.push("--- Replaced Characters ---".to_string());
    if replaced.is_empty() {
        lines.push("None".to_string());
    } else {
        let mut sorted: Vec<_> = replaced.iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(a.1));
        let mut total = 0usize;
        for (&ch, &cnt) in &sorted {
            let display = if ch == '\n' {
                "\\n".to_string()
            } else if ch == '\t' {
                "\\t".to_string()
            } else {
                ch.to_string()
            };
            lines.push(format!("{} → ? : {}", display, cnt));
            total += cnt;
        }
        lines.push(format!("Total replacements: {}", total));
    }
    lines.push(String::new());
    lines.push("--- Word Frequency (ascending) ---".to_string());
    if let Some(wf) = word_freq {
        if wf.is_empty() {
            lines.push("None".to_string());
        } else {
            let mut sorted: Vec<_> = wf.iter().collect();
            sorted.sort_by_key(|&(_, cnt)| cnt);
            let mut total_words = 0usize;
            for (word, &cnt) in &sorted {
                lines.push(format!("{}: {}", word, cnt));
                total_words += cnt;
            }
            lines.push(format!("Total unique words: {}", wf.len()));
            lines.push(format!("Total words: {}", total_words));
        }
    } else {
        lines.push("(skipped)".to_string());
    }
    lines.join("\n") + "\n"
}


fn chrono_local_now() -> String {
    let output = std::process::Command::new("date")
        .arg("+%Y-%m-%d %H:%M:%S")
        .output();
    match output {
        Ok(o) => String::from_utf8_lossy(&o.stdout).trim().to_string(),
        Err(_) => "unknown".to_string(),
    }
}

struct Args {
    input: String,
    output: Option<String>,
    report: Option<String>,
    no_edit: bool,
    no_report: bool,
    no_words: bool,
    remove_watermark: bool,
}

fn parse_args() -> Result<Args, String> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        return Err("Usage: partxt <input_file> [options]".to_string());
    }
    let mut a = Args {
        input: args[1].clone(),
        output: None,
        report: None,
        no_edit: false,
        no_report: false,
        no_words: false,
        remove_watermark: false,
    };
    let mut i = 2;

    while i < args.len() {

        match args[i].as_str() {
            "-o" | "--output" => {
                i += 1;
                if i >= args.len() {
                    return Err("Missing value for --output".to_string());
                }
                a.output = Some(args[i].clone());
            }
            "-r" | "--report" => {
                i += 1;
                if i >= args.len() {
                    return Err("Missing value for --report".to_string());
                }
                a.report = Some(args[i].clone());
            }
            "--no-edit" => a.no_edit = true,
            "--no-report" => a.no_report = true,
            "-w" | "--no-words" => a.no_words = true,
            "--remove-watermark" => a.remove_watermark = true,
            "-h" | "--help" => {
                println!("Usage: partxt <input_file> [options]");
                println!("  -o, --output <file>   Output file");
                println!("  -r, --report <file>   Report file");
                println!("  --no-edit             Do not create .ed.txt");
                println!("  --no-report           Do not create report");
                println!("  -w, --no-words        Exclude word frequency");
                println!("  --remove-watermark    Remove AI watermark characters");
                std::process::exit(0);
            }
            other => return Err(format!("Unknown option: {}", other)),
        }
        i += 1;
    }
    Ok(a)
}

fn main() {
    let args = match parse_args() {
        Ok(a) => a,
        Err(e) => {
            eprintln!("{}", e);
            std::process::exit(1);
        }
    };

    let input_path = Path::new(&args.input);
    if !input_path.exists() {
        eprintln!("Error: file not found: {}", args.input);
        std::process::exit(1);
    }

    let output_file = match &args.output {
        Some(o) => o.clone(),
        None => {
            let stem = input_path.file_stem().unwrap().to_str().unwrap();
            let parent = input_path.parent().unwrap_or(Path::new("."));
            parent.join(format!("{}.ed.txt", stem)).to_str().unwrap().to_string()
        }
    };

    let report_file = match &args.report {
        Some(r) => r.clone(),
        None => "report_rs.txt".to_string(),
    };

    let start = Instant::now();
    let text = fs::read_to_string(input_path).expect("Failed to read input file");
    let (cleaned, replaced, watermark_removed) = process(&text, args.remove_watermark);

    let word_freq = if args.no_words {
        None
    } else {
        Some(word_frequency(&cleaned))
    };
    let elapsed = start.elapsed();

    if !args.no_edit {
        fs::write(&output_file, &cleaned).expect("Failed to write output file");
    }

    if !args.no_report {
        let report = build_report(&args.input, &output_file, &replaced, &watermark_removed, &word_freq, elapsed, args.remove_watermark);

        fs::write(&report_file, &report).expect("Failed to write report file");
    }

    let total: usize = replaced.values().sum();
    let wm_total: usize = watermark_removed.values().sum();
    println!("Done in {:.6}s. Replacements: {}, Watermark removed: {}", elapsed.as_secs_f64(), total, wm_total);
}
