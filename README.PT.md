# aiparstxt — Sanitizador de texto multilíngue

Um conjunto de ferramentas de linha de comando para limpar arquivos de texto substituindo caracteres não permitidos por '?'. Implementado em 6 linguagens para comparação de desempenho.

## Caracteres permitidos
- Dígitos: 0-9
- Letras latinas: A-Z, a-z
- Letras russas: А-Я, а-я (incluindo Ё/ё)
- Pontuação e símbolos: []{}()-=_+!@#$%&*;'/.,<>'"`~
- Espaços em branco: espaço, tabulação, nova linha

Todos os outros caracteres são substituídos por '?'.

## Uso da CLI (igual para todas as linguagens)

partxt <arquivo_entrada> [opções]

Opções:
  -o, --output <arquivo>   Arquivo de saída (padrão: <entrada>.ed.txt)
  -r, --report <arquivo>   Arquivo de relatório (padrão: report_<lang>.txt)
  --no-edit               Não criar arquivo .ed.txt
  --no-report             Não criar relatório
  -w, --no-words          Excluir frequência de palavras do relatório
  -h, --help              Mostrar ajuda

## Formato do relatório
Cada relatório contém:
- Tempo de execução
- Tabela de caracteres substituídos com contagem
- Dicionário de frequência de palavras (ordenado por frequência crescente)

## Implementações

| Linguagem | Diretório    | Comando de build                  | Arquivo relatório |
|-----------|-------------|-----------------------------------|-------------------|
| Python    | partxtpy/   | (não necessário)                  | report_py.txt     |
| Rust      | partxtrs/   | cargo build --release             | report_rs.txt     |
| Go        | partxtgo/   | cd partxtgo && go build           | report_go.txt     |
| C++       | partxtcpp/  | make                              | report_cpp.txt    |
| Node.js   | partxtnode/ | (não necessário)                  | report_node.txt   |
| Bun       | partxtjs/   | (não necessário)                  | report_bun.txt    |

## Execução

### Individualmente
python3 partxtpy/partxt.py testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cd partxtgo && go run . testdata/sample.txt
cd partxtcpp && make && ./partxt testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt

### Todos de uma vez
./run_all.sh testdata/sample.txt

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

Versão atual: 0.0.0

## Licença
MIT
