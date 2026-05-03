#include <chrono>
#include <codecvt>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>
#include <cstdio>

namespace fs = std::filesystem;

static const std::u32string ALLOWED = U"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    U"АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    U"[]{}()-=_+!@#$%&*;'/.,<>'\"`~ \t\n\r";

static std::set<char32_t> build_allowed() {
    std::set<char32_t> s;
    for (char32_t c : ALLOWED) s.insert(c);
    return s;
}

static const std::set<char32_t> ALLOWED_SET = build_allowed();

struct Replacement {
    char32_t ch;
    int count;
};

struct Args {
    std::string input;
    std::string output;
    std::string report;
    bool no_edit = false;
    bool no_report = false;
    bool no_words = false;
};

static void print_usage() {
    std::cerr << "Usage: partxt <input_file> [options]\n"
              << "  -o, --output <file>   Output file\n"
              << "  -r, --report <file>   Report file\n"
              << "  --no-edit             Do not create .ed.txt\n"
              << "  --no-report           Do not create report\n"
              << "  -w, --no-words        Exclude word frequency\n";
}

static Args parse_args(int argc, char* argv[]) {
    Args a;
    if (argc < 2) { print_usage(); exit(1); }
    a.input = argv[1];
    for (int i = 2; i < argc; i++) {
        std::string arg = argv[i];
        if ((arg == "-o" || arg == "--output") && i + 1 < argc) {
            a.output = argv[++i];
        } else if ((arg == "-r" || arg == "--report") && i + 1 < argc) {
            a.report = argv[++i];
        } else if (arg == "--no-edit") {
            a.no_edit = true;
        } else if (arg == "--no-report") {
            a.no_report = true;
        } else if (arg == "-w" || arg == "--no-words") {
            a.no_words = true;
        } else if (arg == "-h" || arg == "--help") {
            print_usage(); exit(0);
        } else {
            std::cerr << "Unknown option: " << arg << "\n";
            exit(1);
        }
    }
    return a;
}

static std::u32string to_u32(const std::string& s) {
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
    return conv.from_bytes(s);
}

static std::string to_u8(const std::u32string& s) {
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
    return conv.to_bytes(s);
}

static std::string read_file(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f) { std::cerr << "Error: cannot open " << path << "\n"; exit(1); }
    std::ostringstream ss;
    ss << f.rdbuf();
    return ss.str();
}

static void write_file(const std::string& path, const std::string& content) {
    std::ofstream f(path, std::ios::binary);
    if (!f) { std::cerr << "Error: cannot write " << path << "\n"; exit(1); }
    f << content;
}

int main(int argc, char* argv[]) {
    Args args = parse_args(argc, argv);

    if (!fs::exists(args.input)) {
        std::cerr << "Error: file not found: " << args.input << "\n";
        return 1;
    }

    if (args.output.empty()) {
        fs::path p(args.input);
        args.output = (p.parent_path() / (p.stem().string() + ".ed" + p.extension().string())).string();
    }
    if (args.report.empty()) {
        args.report = "report_cpp.txt";
    }

    auto start = std::chrono::high_resolution_clock::now();

    std::string raw = read_file(args.input);
    std::u32string text = to_u32(raw);

    std::unordered_map<char32_t, int> replaced;
    std::u32string cleaned;
    cleaned.reserve(text.size());
    for (char32_t ch : text) {
        if (ALLOWED_SET.count(ch)) {
            cleaned.push_back(ch);
        } else {
            replaced[ch]++;
            cleaned.push_back(U'?');
        }
    }

    std::unordered_map<std::u32string, int> word_freq;
    if (!args.no_words) {
        std::u32string cur;
        for (char32_t ch : cleaned) {
            if (ch == U'\'' || ch == U'-' ||
                (ch >= U'0' && ch <= U'9') ||
                (ch >= U'a' && ch <= U'z') || (ch >= U'A' && ch <= U'Z') ||
                (ch >= U'а' && ch <= U'я') || (ch >= U'А' && ch <= U'Я') ||
                ch == U'ё' || ch == U'Ё') {
                cur.push_back(ch);
            } else {
                if (!cur.empty()) {
                    word_freq[cur]++;
                    cur.clear();
                }
            }
        }
        if (!cur.empty()) word_freq[cur]++;
    }

    auto elapsed = std::chrono::high_resolution_clock::now() - start;
    double elapsed_s = std::chrono::duration<double>(elapsed).count();

    if (!args.no_edit) {
        write_file(args.output, to_u8(cleaned));
    }

    if (!args.no_report) {
        std::ostringstream rpt;
        rpt << "=== aiparstxt Report (C++) ===\n";
        auto now = std::chrono::system_clock::now();
        auto time_t_now = std::chrono::system_clock::to_time_t(now);
        rpt << "Date: " << std::put_time(std::localtime(&time_t_now), "%Y-%m-%d %H:%M:%S") << "\n";
        rpt << "Input file: " << args.input << "\n";
        rpt << "Output file: " << args.output << "\n";
        rpt << std::fixed << std::setprecision(6) << "Execution time: " << elapsed_s << " s\n\n";
        rpt << "--- Replaced Characters ---\n";

        if (replaced.empty()) {
            rpt << "None\n";
        } else {
            std::vector<std::pair<char32_t, int>> sorted(replaced.begin(), replaced.end());
            std::sort(sorted.begin(), sorted.end(), [](auto& a, auto& b) { return a.second > b.second; });
            int total = 0;
            for (auto& [ch, cnt] : sorted) {
                std::string display;
                if (ch == U'\n') display = "\\n";
                else if (ch == U'\t') display = "\\t";
                else display = to_u8(std::u32string(1, ch));
                rpt << display << " → ? : " << cnt << "\n";
                total += cnt;
            }
            rpt << "Total replacements: " << total << "\n";
        }

        rpt << "\n--- Word Frequency (ascending) ---\n";
        if (!args.no_words) {
            if (word_freq.empty()) {
                rpt << "None\n";
            } else {
                std::vector<std::pair<std::u32string, int>> wf_sorted(word_freq.begin(), word_freq.end());
                std::sort(wf_sorted.begin(), wf_sorted.end(), [](auto& a, auto& b) { return a.second < b.second; });
                int total_words = 0;
                for (auto& [w, cnt] : wf_sorted) {
                    rpt << to_u8(w) << ": " << cnt << "\n";
                    total_words += cnt;
                }
                rpt << "Total unique words: " << word_freq.size() << "\n";
                rpt << "Total words: " << total_words << "\n";
            }
        } else {
            rpt << "(skipped)\n";
        }

        write_file(args.report, rpt.str());
    }

    int total = 0;
    for (auto& [_, c] : replaced) total += c;
    std::cout << std::fixed << std::setprecision(6)
              << "Done in " << elapsed_s << "s. Replacements: " << total << "\n";

    return 0;
}
