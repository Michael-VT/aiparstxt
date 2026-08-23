# aiparstxt — Nettoyeur de texte multilingue et analyse forensique IA

Un ensemble d'outils en ligne de commande pour nettoyer les fichiers texte en remplaçant les caractères non autorisés par '?'. Implémenté dans 6 langages pour comparer les performances. Inclut la suppression des filigranes IA et **l'analyse forensique statistique** pour détecter les textes générés par l'IA.

## Fonctionnalités

- **Nettoyage de texte** — remplacement des caractères non autorisés par '?' dans 6 implémentations linguistiques
- **Suppression des filigranes IA** — élimination des caractères Unicode invisibles insérés par les systèmes d'IA
- **Analytique forensique IA** — analyse statistique heuristique pour estimer la probabilité de paternité de l'IA (Python)

---

## Caractères autorisés

- Chiffres : 0-9
- Lettres latines : A-Z, a-z
- Lettres russes : А-Я, а-я (y compris Ё/ё)
- Ponctuation et symboles : []{}()-=_+!@#$%&*;'/.,<>'"`~
- Espaces : espace, tabulation, saut de ligne

Tous les autres caractères sont remplacés par '?'.

## Suppression des filigranes IA

Le nettoyeur prend en charge la suppression des caractères de filigrane invisibles utilisés par divers systèmes d'IA pour marquer le texte généré :
- Caractères de largeur nulle (ZWSP, ZWNJ, ZWJ, ZWNBSP)
- Caractères de formatage invisibles (Word Joiner, Invisible Times, etc.)
- Sélecteurs de variation
- Caractères de balisage
- Caractères de remplacement bidirectionnel

Voir `ai-chart.txt` pour la référence complète.

---

## Utilisation CLI — Nettoyage de texte (les 6 langages)

```
partxt <fichier_entrée> [options]
```

Options :
  -o, --output <fichier>     Fichier de sortie (défaut : <entrée>.ed.txt)
  -r, --report <fichier>     Fichier de rapport (défaut : report_<lang>.txt)
  --no-edit                 Ne pas créer le fichier .ed.txt
  --no-report               Ne pas créer le rapport
  -w, --no-words            Exclure la fréquence des mots du rapport
  --remove-watermark        Supprimer les filigranes IA (caractères cachés/invisibles)
  -h, --help                Afficher l'aide

### Individuellement

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

### Tous en même temps

```bash
./run_all.sh testdata/sample.txt
```

---

## Utilisation CLI — Analyse forensique IA (Python uniquement)

```bash
python3 parscgptv2.py <fichier_texte>
```

Trois variantes de scripts analytiques sont disponibles à la racine du projet :

| Script | Description |
|--------|-------------|
| `parscgpt.py` | Version initiale — métriques heuristiques de base et score IA |
| `parscgptv1.py` | Étendue — filtrage des mots vides, niveau de confiance, interprétation, détection de motifs suspects |
| `parscgptv2.py` | Version complète — scoring affiné, sortie épurée, recommandée |

### Métriques calculées

| Métrique | Description |
|----------|-------------|
| `lexical_diversity` | Mots uniques / total des mots (après suppression des mots vides) |
| `repetition_score` | Fraction des mots apparaissant plus d'une fois |
| `entropy` | Entropie de Shannon de la distribution de fréquence des mots |
| `burstiness` | Coefficient de variation des longueurs de phrases |
| `pattern_repetition_score` | Fraction des motifs de longueurs de phrases répétés (encodage S/M/L) |
| `punctuation_density` | Nombre de ponctuations / nombre total de caractères |
| `ai_phrase_hits` | Correspondances avec 21 phrases typiques de l'IA |
| `unicode_symbols` | Nombre de caractères Unicode suspects (tirets, guillemets typographiques, etc.) |
| `top_bigrams` | Top 10 des bigrammes du texte filtré |
| `top_trigrams` | Top 10 des trigrammes du texte filtré |

### Scoring de probabilité IA

| Condition | Points |
|-----------|--------|
| Diversité lexicale < 0.45 | +20 |
| Entropie < 5.0 | +20 |
| Burstiness < 0.35 | +15 |
| Répétition de motifs > 0.35 | +15 |
| Score de répétition > 0.5 | +10 |
| Phrases IA ≥ 3 | +15 |
| Densité de ponctuation > 0.04 | +5 |
| Symboles Unicode suspects présents | +5 |

**Total** plafonné à 100 %. Confiance : faible (<300 mots), moyenne (300–999), élevée (≥1000).

### La sortie inclut

- Toutes les métriques brutes avec valeurs arrondies
- `estimated_ai_probability` — score heuristique
- `confidence` — basé sur la longueur du texte
- `interpretation` — verdict lisible pour chaque métrique
- `overall_profile` — verdict et signaux positifs
- `suspicious_patterns` — phrases et trigrammes de type IA détectés

### Exemple de sortie

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

## Portage de l'analytique vers d'autres langages

Le moteur analytique n'est actuellement disponible qu'en Python. Voir **`ANALYTICS_RECOMMENDATIONS.md`** pour un guide complet de portage :
- Formules de calcul des métriques
- Poids et seuils du modèle de scoring
- Règles d'interprétation
- Recommandations spécifiques pour Rust, Go, C++, Node.js, Bun

---

## Implémentations

| Langage   | Répertoire   | Commande de compilation            | Fichier rapport  |
|-----------|-------------|------------------------------------|------------------|
| Python    | partxtpy/   | (pas de compilation nécessaire)    | report_py.txt    |
| Rust      | partxtrs/   | cargo build --release              | report_rs.txt    |
| Go        | partxtgo/   | cd partxtgo && go build            | report_go.txt    |
| C++       | partxtcpp/  | make                               | report_cpp.txt   |
| Node.js   | partxtnode/ | (pas de compilation nécessaire)    | report_node.txt  |
| Bun       | partxtjs/   | (pas de compilation nécessaire)    | report_bun.txt   |

---

## Format du rapport (Nettoyeur)

Chaque rapport contient :
- Temps d'exécution
- Mode (remplacement/suppression + statut de suppression des filigranes)
- Caractères de filigrane supprimés (avec points de code Unicode)
- Caractères remplacés (avec leur nombre)
- Dictionnaire de fréquence des mots (trié par ordre croissant)

---

## Résultats exemples (testdata/sample.txt, 197 remplacements)

| Langage  | Temps d'exécution |
|----------|------------------|
| Go       | ~0,00004 s       |
| Rust     | ~0,00008 s       |
| C++      | ~0,00040 s       |
| Node.js  | ~0,00046 s       |
| Python   | ~0,00056 s       |
| Bun      | ~0,00220 s       |

---

## Corrections Récentes (v0.2.0)

### Améliorations de la Suppression des Filigranes

**Corrections critiques des bugs de détection des filigranes IA dans les 4 implémentations :**

1. **Bug de plage PUA** — Correction de la plage Unicode de `E000-E007F` (573 343 caractères) à `E000-E07F` (128 caractères)
   - Ensemble de caractères de filigrane réduit de 860 305 à 259 caractères
   - Corrigé dans : Python, Go, Node.js, Rust

2. **Gestion des points de code Node.js** — Remplacement de `String.fromCharCode()` par `String.fromCodePoint()`
   - Détectait précédemment 853 filigranes faux (caractères ASCII)
   - Détecte maintenant correctement 17 filigranes

3. **Position des indicateurs Go** — Documenté que Go exige les indicateurs AVANT le nom de fichier
   ```bash
   # Utilisation correcte pour Go :
   cd partxtgo && go run . --remove-watermark input.txt
   ```

### Résultats des tests (testdata/comprehensive_watermark_test.txt)

Toutes les implémentations détectent maintenant correctement **17/17 filigranes** :

| Langage  | Temps (s) | Filigranes supprimés |
|----------|----------|---------------------|
| Python   | 0.000560 | ✅ 17 (tous) |
| Go       | 0.000039 | ✅ 17 (tous) |
| Node.js  | 0.000455 | ✅ 17 (tous) |
| Rust     | 0.000078 | ✅ 17 (tous) |

**Couverture totale des filigranes :** ~270+ points de code de caractères

## Versionnage

- Patch (0.0.x) : corrections de bugs
- Mineur (0.x.0) : entièrement fonctionnel, répond aux exigences
- Majeur (x.0.0) : nouvelles fonctionnalités importantes

Version actuelle : 0.2.0

## Licence

MIT
