# aiparstxt — Sanitizador de texto multilíngue e analítico forense de IA

Um conjunto de ferramentas de linha de comando para limpar arquivos de texto substituindo caracteres não permitidos por '?'. Implementado em 6 linguagens para comparação de desempenho. Inclui remoção de marcas d'água de IA e **análise forense estatística** para detecção de textos gerados por IA.

## Funcionalidades

- **Sanitização de texto** — substituição de caracteres não permitidos por '?' em 6 implementações linguísticas
- **Remoção de marcas d'água de IA** — eliminação de caracteres Unicode invisíveis inseridos por sistemas de IA
- **Analítica forense de IA** — análise estatística heurística para estimar a probabilidade de autoria de IA (Python)

---

## Caracteres permitidos

- Dígitos: 0-9
- Letras latinas: A-Z, a-z
- Letras russas: А-Я, а-я (incluindo Ё/ё)
- Pontuação e símbolos: []{}()-=_+!@#$%&*;'/.,<>'"`~
- Espaços em branco: espaço, tabulação, nova linha

Todos os outros caracteres são substituídos por '?'.

## Remoção de marcas d'água de IA

O sanitizador suporta a remoção de caracteres de marca d'água invisíveis usados por vários sistemas de IA para marcar texto gerado:
- Caracteres de largura zero (ZWSP, ZWNJ, ZWJ, ZWNBSP)
- Caracteres de formatação invisíveis (Word Joiner, Invisible Times, etc.)
- Seletores de variação
- Caracteres de tag
- Caracteres de substituição bidirecional

Veja `ai-chart.txt` para referência completa.

---

## Uso da CLI — Sanitizador (todas as 6 linguagens)

```
partxt <arquivo_entrada> [opções]
```

Opções:
  -o, --output <arquivo>    Arquivo de saída (padrão: <entrada>.ed.txt)
  -r, --report <arquivo>    Arquivo de relatório (padrão: report_<lang>.txt)
  --no-edit                Não criar arquivo .ed.txt
  --no-report              Não criar relatório
  -w, --no-words           Excluir frequência de palavras do relatório
  --remove-watermark       Remover marcas d'água de IA (caracteres ocultos/invisíveis)
  -h, --help               Mostrar ajuda

### Individualmente

```bash
python3 partxtpy/partxt.py testdata/sample.txt
python3 partxtpy/partxt.py testdata/sample.txt --remove-watermark

cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt -- --remove-watermark

cd partxtgo && go run . testdata/sample.txt
cd partxtgo && go run . --remove-watermark testdata/sample.txt

cd partxtcpp && make && ./partxt testdata/sample.txt
cd partxtcpp && make && ./partxt testdata/sample.txt --remove-watermark

node partxtnode/partxt.js testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt --remove-watermark

bun run partxtjs/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt --remove-watermark
```

### Todos de uma vez

```bash
./run_all.sh testdata/sample.txt
```

---

## Uso da CLI — Analítica forense de IA (apenas Python)

```bash
python3 parscgptv2.py <arquivo_texto>
```

Três variantes de scripts analíticos estão disponíveis na raiz do projeto:

| Script | Descrição |
|--------|-----------|
| `parscgpt.py` | Versão inicial — métricas heurísticas básicas e pontuação de IA |
| `parscgptv1.py` | Estendida — filtragem de stop words, nível de confiança, interpretação, detecção de padrões suspeitos |
| `parscgptv2.py` | Versão completa — pontuação refinada, saída limpa, recomendada para uso |

### Métricas calculadas

| Métrica | Descrição |
|---------|-----------|
| `lexical_diversity` | Palavras únicas / total de palavras (após remoção de stop words) |
| `repetition_score` | Fração de palavras que aparecem mais de uma vez |
| `entropy` | Entropia de Shannon da distribuição de frequência de palavras |
| `burstiness` | Coeficiente de variação dos comprimentos das frases |
| `pattern_repetition_score` | Fração de padrões repetidos de comprimento de frases (codificação S/M/L) |
| `punctuation_density` | Contagem de pontuação / total de caracteres |
| `ai_phrase_hits` | Correspondências com 21 frases típicas de IA |
| `unicode_symbols` | Contagem de caracteres Unicode suspeitos (travessão, aspas tipográficas, etc.) |
| `top_bigrams` | Top 10 bigramas do texto filtrado |
| `top_trigrams` | Top 10 trigramas do texto filtrado |

### Pontuação de probabilidade de IA

| Condição | Pontos |
|----------|--------|
| Diversidade lexical < 0.45 | +20 |
| Entropia < 5.0 | +20 |
| Burstiness < 0.35 | +15 |
| Repetição de padrões > 0.35 | +15 |
| Pontuação de repetição > 0.5 | +10 |
| Frases de IA ≥ 3 | +15 |
| Densidade de pontuação > 0.04 | +5 |
| Símbolos Unicode suspeitos presentes | +5 |

**Total** limitado a 100%. Confiança: baixa (<300 palavras), média (300–999), alta (≥1000).

### A saída inclui

- Todas as métricas brutas com valores arredondados
- `estimated_ai_probability` — pontuação heurística
- `confidence` — baseada no comprimento do texto
- `interpretation` — veredicto legível para cada métrica
- `overall_profile` — veredicto e sinais positivos
- `suspicious_patterns` — frases e trigramas do tipo IA detectados

### Exemplo de saída

```
=== AI TEXT FORENSIC ANALYSIS ===

word_count: 198
sentence_count: 11
lexical_diversity: 0.832
entropy: 6.655
burstiness: 0.52
estimated_ai_probability: 0%
confidence: low
interpretation:
  lexical_diversity: High lexical diversity → richer and more human-like vocabulary.
  entropy: Moderate entropy.
  burstiness: Moderate burstiness.
overall_profile:
  verdict: Text statistically appears more human-like.
  signals: ['high lexical diversity']

=== END OF REPORT ===
```

---

## Portando a analítica para outras linguagens

O motor analítico está disponível apenas em Python. Consulte **`ANALYTICS_RECOMMENDATIONS.md`** para um guia completo de portabilidade:
- Fórmulas de cálculo de métricas
- Pesos e limiares do modelo de pontuação
- Regras de interpretação
- Orientação específica para Rust, Go, C++, Node.js, Bun

---

## Implementações

| Linguagem | Diretório    | Comando de build                  | Arquivo relatório |
|-----------|-------------|-----------------------------------|-------------------|
| Python    | partxtpy/   | (não necessário)                  | report_py.txt     |
| Rust      | partxtrs/   | cargo build --release             | report_rs.txt     |
| Go        | partxtgo/   | cd partxtgo && go build           | report_go.txt     |
| C++       | partxtcpp/  | make                              | report_cpp.txt    |
| Node.js   | partxtnode/ | (não necessário)                  | report_node.txt   |
| Bun       | partxtjs/   | (não necessário)                  | report_bun.txt    |

---

## Formato do relatório (Sanitizador)

Cada relatório contém:
- Tempo de execução
- Modo (substituir/remover + status de remoção de marca d'água)
- Caracteres de marca d'água removidos (com pontos de código Unicode)
- Caracteres substituídos (com contagem)
- Dicionário de frequência de palavras (ordenado por frequência crescente)

---

## Resultados de exemplo (testdata/sample.txt, 197 substituições)

| Linguagem | Tempo de execução |
|-----------|------------------|
| Go        | ~0,0001 s        |
| Rust      | ~0,0003 s        |
| C++       | ~0,0004 s        |
| Python    | ~0,0014 s        |
| Node.js   | ~0,0013 s        |
| Bun       | ~0,0022 s        |

## Versionamento

- Patch (0.0.x): correções de bugs
- Minor (0.x.0): totalmente funcional, atende aos requisitos
- Major (x.0.0): novas funcionalidades significativas

Versão atual: 0.1.0

## Licença

MIT
