# aiparstxt — Nettoyeur de texte multilingue

Un ensemble d'outils en ligne de commande pour nettoyer les fichiers texte en remplaçant les caractères non autorisés par '?'. Implémenté dans 6 langages pour comparer les performances.

## Caractères autorisés
- Chiffres : 0-9
- Lettres latines : A-Z, a-z
- Lettres russes : А-Я, а-я (y compris Ё/ё)
- Ponctuation et symboles : []{}()-=_+!@#$%&*;'/.,<>'"`~
- Espaces : espace, tabulation, saut de ligne

Tous les autres caractères sont remplacés par '?'.

## Utilisation CLI (identique pour tous les langages)

partxt <fichier_entrée> [options]

Options :
  -o, --output <fichier>   Fichier de sortie (défaut : <entrée>.ed.txt)
  -r, --report <fichier>   Fichier de rapport (défaut : report_<lang>.txt)
  --no-edit               Ne pas créer le fichier .ed.txt
  --no-report             Ne pas créer le rapport
  -w, --no-words          Exclure la fréquence des mots du rapport
  -h, --help              Afficher l'aide

## Format du rapport
Chaque rapport contient :
- Temps d'exécution
- Tableau des caractères remplacés avec leur nombre
- Dictionnaire de fréquence des mots (trié par ordre croissant)

## Implémentations

| Langage   | Répertoire   | Commande de compilation            | Fichier rapport  |
|-----------|-------------|------------------------------------|------------------|
| Python    | partxtpy/   | (pas de compilation nécessaire)    | report_py.txt    |
| Rust      | partxtrs/   | cargo build --release              | report_rs.txt    |
| Go        | partxtgo/   | cd partxtgo && go build            | report_go.txt    |
| C++       | partxtcpp/  | make                               | report_cpp.txt   |
| Node.js   | partxtnode/ | (pas de compilation nécessaire)    | report_node.txt  |
| Bun       | partxtjs/   | (pas de compilation nécessaire)    | report_bun.txt   |

## Exécution

### Individuellement
python3 partxtpy/partxt.py testdata/sample.txt
cargo run --release --manifest-path partxtrs/Cargo.toml -- testdata/sample.txt
cd partxtgo && go run . testdata/sample.txt
cd partxtcpp && make && ./partxt testdata/sample.txt
node partxtnode/partxt.js testdata/sample.txt
bun run partxtjs/partxt.js testdata/sample.txt

### Tous en même temps
./run_all.sh testdata/sample.txt

## Résultats exemples (testdata/sample.txt, 197 remplacements)

| Langage  | Temps d'exécution |
|----------|------------------|
| Go       | ~0,0001 s        |
| Rust     | ~0,0003 s        |
| C++      | ~0,0004 s        |
| Python   | ~0,0014 s        |
| Node.js  | ~0,0013 s        |
| Bun      | ~0,0022 s        |

## Versionnage
- Patch (0.0.x) : corrections de bugs
- Mineur (0.x.0) : entièrement fonctionnel, répond aux exigences
| Majeur (x.0.0) : nouvelles fonctionnalités importantes

Version actuelle : 0.0.0

## Licence
MIT
