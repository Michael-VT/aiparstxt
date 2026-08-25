# aiparstxt — Desinfetador de Texto Multilíngue e Analista Forense de IA

Conjunto de utilitários de linha de comando para limpar arquivos de texto substituindo caracteres não permitidos por '?'. Implementado em 6 idiomas para comparação de desempenho. Inclui remoção de marcas d'água de IA e **análise forense estatística** para detecção de texto gerado por IA.

**Disponível em:** [English](README.md) | [Русский](README.RU.md) | [Українська](README.UA.md) | [Português](README.PT.md) | [Français](README.FR.md) | [Deutsch](README.DE.md)


## Funcionalidades

- **Limpeza de texto** — substitui caracteres não permitidos por '?' em 6 implementações de idiomas
- **Remoção de marcas d'água de IA** — remove caracteres Unicode invisíveis inseridos por sistemas de IA
- **Análise forense de IA** — análise estatística heurística para estimar probabilidade de autoria de IA (Python)
- **Versões estendidas de detecção** — análise forense aprimorada disponível para todos os 6 idiomas ⭐

---

## Caracteres Permitidos

- Dígitos: 0-9
- Letras latinas: A-Z, a-z
- Letras cirílicas: А-Я, а-я (incluindo Ё/ё)
- Pontuação e símbolos: []{}()-=_+!@#$%&*;'/.,<>'"`~
- Espaço em branco: espaço, tabulação, nova linha

Todos os outros caracteres são substituídos por '?'.

## Remoção de Marcas d'Água de IA

O limpador suporta remoção de caracteres invisíveis de marcas d'água usados por vários sistemas de IA para marcar texto gerado:
- Caracteres de largura zero (ZWSP, ZWNJ, ZWJ, ZWNBSP)
- Caracteres de formatação invisíveis (Word Joiner, Invisible Times, etc.)
- Seletores de variação
- Caracteres de tag
- Caracteres de sobrescrita bidirecional

Veja `ai-chart.txt` para referência completa.

---

## CLI — Desinfetador (todos os 6 idiomas)

```bash
partxt <arquivo_entrada> [opções]
```

Opções:
  -o, --output <arquivo>      Arquivo de saída (padrão: <entrada>.ed.txt)
  -r, --report <arquivo>      Arquivo de relatório (padrão: report_<idioma>.txt)
  --no-edit                Não criar arquivo .ed.txt
  --no-report              Não criar relatório
  -w, --no-words           Excluir frequência de palavras do relatório
  --remove-watermark       Remover caracteres de marcas d'água de IA (ocultos/invisíveis)
  -h, --help               Mostrar ajuda

### Individualmente

```bash
# Versões padrão
python3 partxtpy/partxt.py testdata/sample.txt
python3 partxtpy/partxt.py testdata/sample.txt --remove-watermark

# Versões estendidas com análise forense de IA ⭐
python3 partxtpy/partxt-ext.py testdata/sample.txt
python3 partxtpy/partxt-ext.py testdata/sample.txt --remove-watermark

cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml --bin partxt-ext -- testdata/sample.txt -- --remove-watermark

cd partxtgo && go run . testdata/sample.txt
cd partxtgo && go run main-ext.go testdata/sample.txt --remove-watermark

cd partxtcpp && make && ./partxt testdata/sample.txt
cd partxtcpp && make && ./partxt-ext testdata/sample.txt --remove-watermark

node partxtnode/partxt.js testdata/sample.txt
node partxtnode/partxt-ext.js testdata/sample.txt --remove-watermark

bun run partxtjs/partxt.js testdata/sample.txt
bun run partxtjs/partxt-ext.js testdata/sample.txt --remove-watermark
```

### Todos de uma vez

```bash
# Apenas versões padrão
./run_all.sh testdata/sample.txt

# Versões estendidas com detecção de IA
./run_all_extended.sh testdata/sample.txt
```

---

## CLI — Análise Forense de IA (apenas Python)

### Analisadores Python Padrão

```bash
python3 parscgptv2.py <arquivo_texto>
```

Quatro variantes de scripts analíticos estão disponíveis na raiz do projeto:

| Script | Métricas | Frases IA | Recursos | Uso Recomendado |
|--------|----------|-----------|----------|----------------|
| `parscgpt.py` | 8 básicas | 21 | Apenas métricas básicas | Legado/testes |
| `parscgptv1.py` | 8 básicas + interpretação | 21 | + Stopwords, confiança | Detecção básica |
| `parscgptv2.py` | 8 básicas + interpretação refinada | 21 | + Saída limpa | **Detecção padrão** ✅ |
| `parscgpt-ext.py` | **17 métricas avançadas** | **70+** | + Análise linguística, pontuação ponderada | **Detecção estendida** ⭐ |

### Analisadores Estendidos Integrados (Todos os 6 Idiomas) ⭐

Versões estendidas dos limpadores de texto básicos (`partxt-ext`) agora estão disponíveis para **todas as 6 implementações de idiomas** com análise forense de IA aprimorada:

| Idioma | Binário Estendido | Arquivo de Relatório | Recursos |
|----------|----------------|-------------|-----------|
| Python | `partxtpy/partxt-ext.py` | report_py-ext.txt | 11 métricas principais + pontuação de probabilidade de IA |
| Rust | `partxtrs/target/partxt-ext` | report_rs-ext.txt | Mesmas métricas que Python, desempenho compilado |
| Go | `partxtgo/main-ext.go` | report_go-ext.txt | Mesmas métricas, desempenho compilado |
| C++ | `partxtcpp/partxt-ext` | report_cpp-ext.txt | Mesmas métricas, desempenho compilado |
| Node.js | `partxtnode/partxt-ext.js` | report_node-ext.txt | Mesmas métricas, runtime JavaScript |
| Bun | `partxtjs/partxt-ext.js` | report_bun-ext.txt | Mesmas métricas, JavaScript otimizado |

**Recursos Aprimorados nas Versões Estendidas:**
- 11 métricas forenses de IA principais (diversidade lexical, entropia, burstiness, repetição de padrões, etc.)
- Detecção de frases de IA com 70+ frases suspeitas
- Detecção de caracteres Unicode suspeitos
- Pontuação estatística de probabilidade de IA (0-100%)
- Níveis de confiança (BAIXO/MÉDIO/ALTO) baseados no comprimento do texto
- Análise detalhada de sinais com indicadores visuais
- Interpretação de cada métrica com insights acionáveis

---

## Métricas Padrão (Todas as Versões Estendidas)

| Métrica | Descrição | Valor de Detecção de IA |
|--------|-------------|---------------------|
| `lexical_diversity` | Palavras únicas / total de palavras (após remoção de stopwords) | IA tem menor diversidade |
| `repetition_score` | Fração de palavras que aparecem mais de uma vez | IA repete mais |
| `entropy` | Entropia de Shannon da distribuição de frequência de palavras | IA tem distribuição unnaturamente uniforme |
| `burstiness` | Coeficiente de variação dos comprimentos de sentenças | IA tem estrutura de sentenças excessivamente uniforme (sinal principal) |
| `paragraph_length_cv` | CV da contagem de palavras por parágrafo | Parágrafos de IA são iguais demais, de forma não natural (sinal principal) |
| `joint_uniformity` | CV baixo tanto de sentenças quanto de parágrafos | Mais forte sinal estrutural de IA |
| `connective_density` | Conectivos discursivos por sentença (multilíngue) | IA usa conectivos excessivamente |
| `pattern_repetition` | Fração de padrões de comprimento de sentenças repetidos | IA usa padrões de modelo |
| `punctuation_density` | Contagem de pontuação / total de caracteres | IA pode usar pontuação excessivamente |
| `ai_phrase_hits` | ~150 frases típicas de IA curadas em 3 níveis (EN/RU/UK/PT) | Assinatura direta de IA |
| `unicode_symbols` | Contagem de caracteres Unicode suspeitos | Marcadores técnicos de IA |
| `avg_word_length` | Comprimento médio das palavras | IA usa vocabulário mais simples |
| `word_length_variance` | Variância nos comprimentos das palavras | Textos de IA mais uniformes |
| `confidence` | Baseado na contagem de palavras (BAIXO <300, MÉDIO 300-999, ALTO ≥1000) | Indicador de confiabilidade |

### Localização das evidências — AI EVIDENCE (v0.4.0+)

Cada indicador disparado é reportado com sua localização exata no texto:
número da linha, um trecho com o gatilho destacado como `>>>frase<<<`, e
sequências de comprimentos de sentenças/parágrafos para os sinais de
uniformidade. A seção `AI EVIDENCE` aparece nos relatórios dos limpadores
estendidos e na saída de `parscgpt-ext.py`.

### Abstenção honesta (v0.4.1–v0.4.3)

- Textos curtos (< 150 palavras ou < 5 sentenças): os sinais estruturais são
  escalados pela confiabilidade estatística em vez de silenciosamente
  desativados, e o veredicto é anotado como não confiável — chega de
  veredictos confiantes de "humano" em textos pequenos demais para analisar.
- Repetição de cabeçalhos-modelo (v0.4.2): linhas curtas de cabeçalho
  repetidas literalmente ("Что верно" ×7, "Итог" ×7) — um marcador forte de
  respostas estruturadas de LLMs; zero falsos positivos no corpus humano.
- Registo promocional/redes sociais (v0.4.3): textos carregados de emojis e
  exclamações recebem uma nota de género em vez de um veredicto de "humano" —
  esse registo é produzido tanto por IA quanto por redatores humanos de SMM,
  portanto nenhum ponto de IA é atribuído, o veredicto simplesmente é retido.

### Análise de um ficheiro com todos os detetores

```bash
./analyze_all.sh input.txt
```

Compila os binários em falta, executa todos os analisadores do projeto
(técnico, legado ×2, padrão, estendido, baseado em marcadores e todos os seis
`partxt-ext`), verifica a paridade entre implementações e imprime um
relatório resumido: consenso, worst-case (analisador mais rigoroso), faixa de
risco e a lista de pontos a rever/editar antes de publicar.

### Validação (v0.4.0+)

Calibrado e validado contra 34 respostas confirmadas de IA (8 serviços × 4
idiomas) e 20 textos humanos com fonte verificada — veja
`validation/AI_CORPUS_REPORT.md` e `AI_SIGNALS_SPEC.md`. No limiar de
classificação 50: recall 93.9%, taxa de falsos positivos 0%. As pontuações
são heurísticas, não prova de autoria.

### Pontuação de Probabilidade de IA (Versões Estendidas)

| Condição | Pontos | Melhoria |
|-----------|--------|-------------|
| Diversidade lexical < 0.45 | **+25** | ↑ +5 vs padrão |
| Entropia < 5.0 | **+25** | ↑ +5 vs padrão |
| Burstiness < 0.35 | **+20** | ↑ +5 vs padrão |
| Repetição de padrões > 0.35 | **+20** | ↑ +5 vs padrão |
| Frases de IA ≥ 3 | **+20** | ↑ +5 vs padrão |
| Pontuação de repetição > 0.5 | +15 | Igual |
| Densidade de pontuação > 0.04 | +5 | Igual |
| Caracteres Unicode suspeitos presentes | +5 | Igual |
| Comprimento médio de palavras < 4.0 | **+10** | 🆕 Nova métrica |
| Variância de comprimento de palavras < 1.5 | **+8** | 🆕 Nova métrica |

**Total** limitado a 100% com ajuste de fator de confiança (80%-100% baseado no comprimento do texto).

### Formato de Saída (Versões Estendidas)

```
======================================================================
aiparstxt-ext — Relatório Aprimorado de Análise Forense de IA
======================================================================

Arquivo de entrada:  sample.txt
Arquivo de saída: sample.ed.txt
Tempo de execução: 0.000560s

--- AI Watermark Analysis ---
Caracteres de marca d'água removidos: 17
Tipos de caracteres de marca d'água removidos:
  U+200B: 5
  U+200C: 3
  ...

--- Caracteres Substituídos ---
Caracteres substituídos: 197

======================================================================
AI FORENSIC ANALYSIS
======================================================================

Veredito Geral: Probabilidade moderada de envolvimento de IA (35.2%)
Nível de Confiança: MÉDIO

Métricas Detalhadas:
  Contagem de palavras:            198
  Contagem de sentenças:        11
  Diversidade lexical:     0.832
  Pontuação de repetição:      0.202
  Entropia:               6.655
  Burstiness:            1.590
  Repetição de padrões:    0.000
  Densidade de pontuação:   0.037
  Acertos de frases IA:        2
  Unicode suspeito:    0
  Comprimento médio de palavras:       4.52
  Variância de comprimento de palavras:  2.18

Análise de Sinais:
  ✓ Alta diversidade lexical - variação rica de vocabulário
  ✓ Boa entropia - distribuição natural de palavras
  ✓ Bom burstiness - variação natural de sentenças
  ⚠️ Encontradas 2 frases típicas de IA
```

---

## Métricas Estendidas (apenas parscgpt-ext.py) ⭐

Para a análise mais abrangente, o autônomo `parscgpt-ext.py` fornece 17 métricas avançadas:

| Métrica | Descrição | Valor de Detecção de IA |
|--------|-------------|---------------------|
| `avg_word_length` | Comprimento médio das palavras | IA usa vocabulário mais simples |
| `word_length_variance` | Variância nos comprimentos das palavras | Textos de IA mais uniformes |
| `pronoun_ratio` | Razão de pronomes para total de palavras | IA usa pronomes excessivamente |
| `readability_score` | Pontuação de Flesch Reading Ease | Textos de IA "muito legíveis" |
| `passive_voice_density` | Frequência de construções voz passiva | IA prefere voz passiva |
| `adj_noun_pair_diversity` | Combinações únicas adjetivo-substantivo | IA tem combinações limitadas |
| `structural_uniformity` | Repetição de padrões de início de sentenças | IA usa modelos |
| `quantifier_overuse` | Frequência de palavras de qualificação | IA usa qualificadores excessivamente |

Use `parscgpt-ext.py` quando você precisar da análise linguística mais profunda além dos limpadores integrados.

**Diferenças Chave: Versões Estendidas vs Padrão**
- Fornece **9 métricas adicionais** para análise mais profunda
- Mostra **pontuação detalhada** em vez de única probabilidade
- Inclui **interpretação específica** para cada métrica
- Oferece **confiabilidade aprimorada** com adaptação ao comprimento do texto
- Detecta **mais padrões de IA** — 70+ frases vs 21 na versão padrão

---

## Portabilidade da Análise para Outros Idiomas

O mecanismo de análise aprimorado agora está disponível em **todas as 6 implementações de idiomas** através das versões `-ext`. O autônomo Python `parscgpt-ext.py` fornece a análise mais abrangente de 17 métricas para referência.

Veja **`ANALYTICS_RECOMMENDATIONS.md`** para um guia completo de portabilidade com:
- Fórmulas de cálculo de métricas
- Pesos e limites do modelo de pontuação
- Regras de interpretação
- Orientação específica por idioma

---

## Implementações

| Idioma   | Diretório    | Comando de compilação              | Arquivo de relatório  | Relatório estendido     |
|----------|-------------|------------------------------------|----------------------|------------------------|
| Python   | partxtpy/   | (não necessário)                   | report_py.txt        | report_py-ext.txt      |
| Rust     | partxtrs/   | cargo build --release              | report_rs.txt        | report_rs-ext.txt      |
| Go       | partxtgo/   | cd partxtgo && go build            | report_go.txt        | report_go-ext.txt      |
| C++      | partxtcpp/  | make                               | report_cpp.txt       | report_cpp-ext.txt    |
| Node.js  | partxtnode/ | (não necessário)                   | report_node.txt      | report_node-ext.txt    |
| Bun      | partxtjs/   | (não necessário)                   | report_bun.txt       | report_bun-ext.txt     |

---

## Formato de Relatório (Desinfetador)

Cada relatório inclui:
- Tempo de execução
- Modo (substituir/remover + status de remoção de marca d'água)
- Caracteres de marca d'água removidos (com pontos de código Unicode)
- Caracteres substituídos (com contagens)
- Frequência de palavras (ordem crescente)

**Versões estendidas** adicionalmente incluem:
- Seção de métricas forenses de IA
- Pontuação de probabilidade de IA com nível de confiança
- Análise de sinais com indicadores visuais
- Interpretações específicas de métricas

---

## Resultados de Exemplo (testdata/sample.txt, 197 substituições)

| Idioma   | Tempo de Execução | Tempo Estendido |
|----------|------------------|-----------------|
| Go       | ~0.00004 s       | ~0.00006 s      |
| Rust     | ~0.00008 s       | ~0.00010 s      |
| C++      | ~0.00040 s       | ~0.00050 s      |
| Node.js  | ~0.00046 s       | ~0.00060 s      |
| Python   | ~0.00056 s       | ~0.00070 s      |
| Bun      | ~0.00220 s       | ~0.00280 s      |

---

## Correções Recentes (v0.3.0)

### Novas Versões Estendidas ⭐

**Análise forense de IA aprimorada agora disponível em todos os 6 idiomas:**

1. **Python Estendido** (`partxtpy/partxt-ext.py`)
   - Integração completa de métricas forenses de IA
   - Pontuação baseada em probabilidade
   - Análise de sinais com interpretações

2. **JavaScript Estendido** (Bun + Node.js)
   - `partxtjs/partxt-ext.js` para Bun
   - `partxtnode/partxt-ext.js` para Node.js
   - Mesmas métricas que versão Python

3. **Rust Estendido** (`partxtrs/src/main-ext.rs`)
   - Desempenho compilado
   - Processamento eficiente de memória
   - Conjunto completo de métricas

4. **Go Estendido** (`partxtgo/main-ext.go`)
   - Implementação type-safe
   - Apenas biblioteca padrão
   - Métricas abrangentes

5. **C++ Estendido** (`partxtcpp/partxt-ext.cpp`)
   - Alto desempenho
   - C++20 moderno
   - Funcionalidade completa

6. **Node.js Estendido** (`partxtnode/partxt-ext.js`)
   - Compatibilidade com Node.js
   - Mesmas métricas e recursos

---

## Versionamento

- Patch (0.0.x): correções de bugs
- Minor (0.x.0): completamente funcional, atende aos requisitos
- Major (x.0.0): recursos novos significativos

Versão atual: 0.4.3

## Licença

MIT