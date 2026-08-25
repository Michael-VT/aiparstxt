# aiparstxt — Nettoyeur de Texte Multilingue et Analyseur Forensique IA

Ensemble d'utilitaires en ligne de commande pour nettoyer des fichiers texte en remplaçant les caractères non autorisés par '?'. Implémenté en 6 langages pour comparaison des performances. Inclut la suppression de filigranes IA et **analyse statistique forensique** pour détecter du texte généré par IA.

**Disponible en :** [English](README.md) | [Русский](README.RU.md) | [Українська](README.UA.md) | [Português](README.PT.md) | [Français](README.FR.md) | [Deutsch](README.DE.md)


## Fonctionnalités

- **Nettoyage de texte** — remplace les caractères non autorisés par '?' dans 6 implémentations linguistiques
- **Suppression de filigranes IA** — élimine les caractères Unicode invisibles insérés par les systèmes IA
- **Analytique forensique IA** — analyse statistique heuristique pour estimer la probabilité d'auteur IA (Python)
- **Versions étendues de détection** — analyse forensique améliorée disponible pour tous les 6 langages ⭐

---

## Caractères Autorisés

- Chiffres : 0-9
- Lettres latines : A-Z, a-z
- Lettres cyrilliques : А-Я, а-я (y compris Ё/ё)
- Ponctuation et symboles : []{}()-=_+!@#$%&*;'/.,<>'"`~
- Espaces : espace, tabulation, nouvelle ligne

Tous les autres caractères sont remplacés par '?'.

## Suppression de Filigranes IA

Le nettoyeur prend en charge la suppression de caractères de filigrane invisibles utilisés par divers systèmes IA pour marquer le texte généré :
- Caractères de largeur nulle (ZWSP, ZWNJ, ZWJ, ZWNBSP)
- Caractères de formatage invisibles (Word Joiner, Invisible Times, etc.)
- Sélecteurs de variation
- Caractères de balise
- Caractères de surcharge bidirectionnelle

Voir `ai-chart.txt` pour référence complète.

---

## CLI — Nettoyeur (tous les 6 langages)

```bash
partxt <fichier_entrée> [options]
```

Options :
  -o, --output <fichier>     Fichier de sortie (défaut : <entrée>.ed.txt)
  -r, --report <fichier>     Fichier de rapport (défaut : report_<langue>.txt)
  --no-edit                Ne pas créer de fichier .ed.txt
  --no-report              Ne pas créer de rapport
  -w, --no-words           Exclure la fréquence des mots du rapport
  --remove-watermark       Supprimer les caractères de filigrane IA (cachés/invisibles)
  -h, --help               Afficher l'aide

### Individuellement

```bash
# Versions standard
python3 partxtpy/partxt.py testdata/sample.txt
python3 partxtpy/partxt.py testdata/sample.txt --remove-watermark

# Versions étendues avec analyse forensique IA ⭐
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

### Tous en une fois

```bash
# Versions standard uniquement
./run_all.sh testdata/sample.txt

# Versions étendues avec détection IA
./run_all_extended.sh testdata/sample.txt
```

---

## CLI — Analytique Forensique IA (Python uniquement)

### Analyseurs Python Standard

```bash
python3 parscgptv2.py <fichier_texte>
```

Quatre variantes de scripts analytiques sont disponibles à la racine du projet :

| Script | Métriques | Phrases IA | Fonctionnalités | Utilisation Recommandée |
|--------|----------|-----------|------------------|-------------------------|
| `parscgpt.py` | 8 de base | 21 | Métriques de base uniquement | Héritage/tests |
| `parscgptv1.py` | 8 de base + interprétation | 21 | + Stopwords, confiance | Détection basique |
| `parscgptv2.py` | 8 de base + interprétation raffinée | 21 | + Sortie propre | **Détection standard** ✅ |
| `parscgpt-ext.py` | **17 métriques avancées** | **70+** | + Analyse linguistique, scoring pondéré | **Détection étendue** ⭐ |

### Analyseurs Étendus Intégrés (Tous les 6 Langages) ⭐

Les versions étendues des nettoyeurs de texte de base (`partxt-ext`) sont maintenant disponibles pour **toutes les 6 implémentations linguistiques** avec analyse forensique IA améliorée :

| Langage | Binaire Étendu | Fichier de Rapport | Fonctionnalités |
|----------|----------------|-------------------|-----------------|
| Python | `partxtpy/partxt-ext.py` | report_py-ext.txt | 11 métriques principales + scoring de probabilité IA |
| Rust | `partxtrs/target/partxt-ext` | report_rs-ext.txt | Mêmes métriques que Python, performances compilées |
| Go | `partxtgo/main-ext.go` | report_go-ext.txt | Mêmes métriques, performances compilées |
| C++ | `partxtcpp/partxt-ext` | report_cpp-ext.txt | Mêmes métriques, performances compilées |
| Node.js | `partxtnode/partxt-ext.js` | report_node-ext.txt | Mêmes métriques, runtime JavaScript |
| Bun | `partxtjs/partxt-ext.js` | report_bun-ext.txt | Mêmes métriques, JavaScript optimisé |

**Fonctionnalités Améliorées dans les Versions Étendues :**
- 11 métriques forensiques IA principales (diversité lexicale, entropie, burstiness, répétition de motifs, etc.)
- Détection de phrases IA avec 70+ phrases suspectes
- Détection de caractères Unicode suspects
- Scoring statistique de probabilité IA (0-100%)
- Niveaux de confiance (FAIBLE/MOYEN/HAUT) basés sur la longueur du texte
- Analyse détaillée des signaux avec indicateurs visuels
- Interprétation de chaque métrique avec insights actionnables

---

## Métriques Standard (Toutes les Versions Étendues)

| Métrique | Description | Valeur de Détection IA |
|--------|-------------|---------------------|
| `lexical_diversity` | Mots uniques / total des mots (après suppression des stopwords) | IA a une diversité moindre |
| `repetition_score` | Fraction de mots apparaissant plus d'une fois | IA répète plus |
| `entropy` | Entropie de Shannon de la distribution de fréquence des mots | IA a distribution unnaturellement uniforme |
| `burstiness` | Coefficient de variation des longueurs de phrases | IA a une structure de phrases excessivement uniforme (signal principal) |
| `paragraph_length_cv` | Coefficient de variation du nombre de mots par paragraphe | Les paragraphes IA sont unnaturellement égaux (signal principal) |
| `joint_uniformity` | CV faibles à la fois pour les phrases et les paragraphes | Plus fort signal structurel IA |
| `connective_density` | Connecteurs discursifs par phrase (multilingue) | IA surutilise les connecteurs |
| `pattern_repetition` | Fraction de motifs de longueurs de phrases répétés | IA utilise des motifs de modèle |
| `punctuation_density` | Nombre de ponctuation / total des caractères | IA peut utiliser la ponctuation excessivement |
| `ai_phrase_hits` | ~150 expressions typiques IA sélectionnées en 3 niveaux (EN/RU/UK/PT) | Signature directe IA |
| `unicode_symbols` | Nombre de caractères Unicode suspects | Marqueurs techniques IA |
| `avg_word_length` | Longueur moyenne des mots | IA utilise un vocabulaire plus simple |
| `word_length_variance` | Variance des longueurs de mots | Textes IA plus uniformes |
| `confidence` | Basé sur le nombre de mots (FAIBLE <300, MOYEN 300-999, HAUT ≥1000) | Indicateur de fiabilité |

### Localisation des indices — AI EVIDENCE (v0.4.0+)

Chaque indicateur déclenché est rapporté avec son emplacement exact dans le texte :
numéro de ligne, extrait (~110 caractères) où le déclencheur est surligné sous la
forme `>>>phrase<<<`, et — pour les signaux d'uniformité — les séquences de
longueurs de phrases/paragraphes. La section `AI EVIDENCE` apparaît dans les
rapports des nettoyeurs étendus et dans la sortie de `parscgpt-ext.py`.

### Abstention honnête (v0.4.1–v0.4.3)

- Textes courts (< 150 mots ou < 5 phrases) : les signaux structurels sont pondérés
  par la fiabilité statistique de l'échantillon au lieu d'être silencieusement
  désactivés, et le verdict est annoté comme non fiable — plus aucun « humain »
  affirmé sur des textes trop petits pour être analysés.
- Répétition d'en-têtes modèles (v0.4.2) : lignes d'en-tête courtes répétées à
  l'identique (« Что верно » ×7, « Итог » ×7) — marqueur fort des réponses LLM
  structurées ; zéro faux positifs sur le corpus humain.
- Registre promotionnel/réseaux sociaux (v0.4.3) : les textes saturés d'emojis et
  de points d'exclamation reçoivent une note de genre au lieu d'un verdict
  « humain » — ce registre est produit à la fois par les IA et par les rédacteurs
  SMM humains, donc aucun point IA n'est attribué, le verdict est simplement retiré.

### Analyse d'un fichier avec tous les détecteurs

```bash
./analyze_all.sh input.txt
```

Compile les binaires manquants, exécute tous les analyseurs du projet
(technique, héritage ×2, standard, étendu, basé sur les marqueurs, et les six
`partxt-ext`), vérifie la parité entre implémentations et imprime un rapport
résumé : consensus, pire cas (analyseur le plus strict), bande de risque et liste
des passages à corriger avant publication.

### Validation (v0.4.0+)

Scoring calibré et validé sur 34 réponses IA confirmées (8 services × 4 langues)
et 20 textes humains sourcés — voir `validation/AI_CORPUS_REPORT.md` et
`AI_SIGNALS_SPEC.md`. Au seuil de classification 50 : rappel 93,9 %, taux de faux
positifs 0 %. Les scores sont heuristiques et ne constituent pas une preuve de
paternité.

### Scoring de Probabilité IA (Versions Étendues)

| Condition | Points | Amélioration |
|-----------|--------|-------------|
| Diversité lexicale < 0.45 | **+25** | ↑ +5 vs standard |
| Entropie < 5.0 | **+25** | ↑ +5 vs standard |
| Burstiness < 0.35 | **+20** | ↑ +5 vs standard |
| Répétition de motifs > 0.35 | **+20** | ↑ +5 vs standard |
| Phrases IA ≥ 3 | **+20** | ↑ +5 vs standard |
| Score de répétition > 0.5 | +15 | Identique |
| Densité de ponctuation > 0.04 | +5 | Identique |
| Caractères Unicode suspects présents | +5 | Identique |
| Longueur moyenne des mots < 4.0 | **+10** | 🆕 Nouvelle métrique |
| Variance de longueur des mots < 1.5 | **+8** | 🆕 Nouvelle métrique |

**Total** limité à 100% avec ajustement du facteur de confiance (80%-100% basé sur la longueur du texte).

### Format de Sortie (Versions Étendues)

```
======================================================================
aiparstxt-ext — Rapport Amélioré d'Analyse Forensique IA
======================================================================

Fichier d'entrée :  sample.txt
Fichier de sortie : sample.ed.txt
Temps d'exécution : 0.000560s

--- AI Watermark Analysis ---
Caractères de filigrane supprimés : 17
Types de caractères de filigrane supprimés :
  U+200B : 5
  U+200C : 3
  ...

--- Caractères Remplacés ---
Caractères remplacés : 197

======================================================================
AI FORENSIC ANALYSIS
======================================================================

Verdict Général : Probabilité modérée d'implication IA (35.2%)
Niveau de Confiance : MOYEN

Métriques Détaillées :
  Nombre de mots :            198
  Nombre de phrases :        11
  Diversité lexicale :     0.832
  Score de répétition :      0.202
  Entropie :               6.655
  Burstiness :            1.590
  Répétition de motifs :    0.000
  Densité de ponctuation :   0.037
  Occurrences de phrases IA :        2
  Unicode suspect :    0
  Longueur moyenne des mots :       4.52
  Variance de longueur des mots :  2.18

Analyse des Signaux :
  ✓ Forte diversité lexicale - variation riche du vocabulaire
  ✓ Bonne entropie - distribution naturelle des mots
  ✓ Bon burstiness - variation naturelle des phrases
  ⚠️ Trouvé 2 phrases typiques IA
```

---

## Métriques Étendues (uniquement parscgpt-ext.py) ⭐

Pour l'analyse la plus complète, l'autonome `parscgpt-ext.py` fournit 17 métriques avancées :

| Métrique | Description | Valeur de Détection IA |
|--------|-------------|---------------------|
| `avg_word_length` | Longueur moyenne des mots | IA utilise un vocabulaire plus simple |
| `word_length_variance` | Variance des longueurs de mots | Textes IA plus uniformes |
| `pronoun_ratio` | Ratio des pronoms sur le total des mots | IA utilise excessivement les pronoms |
| `readability_score` | Score de lisibilité Flesch | Textes IA "trop lisibles" |
| `passive_voice_density` | Fréquence des constructions voix passive | IA préfère la voix passive |
| `adj_noun_pair_diversity` | Combinaisons uniques adjectif-nom | IA a des combinaisons limitées |
| `structural_uniformity` | Répétition des motifs de début de phrases | IA utilise des modèles |
| `quantifier_overuse` | Fréquence des mots de qualification | IA utilise excessivement les qualificateurs |

Utilisez `parscgpt-ext.py` lorsque vous avez besoin de l'analyse linguistique la plus profonde au-delà des nettoyeurs intégrés.

**Différences Clés : Versions Étendues vs Standard**
- Fournit **9 métriques supplémentaires** pour une analyse plus profonde
- Affiche un **scoring détaillé** au lieu d'une seule probabilité
- Inclut une **interprétation spécifique** pour chaque métrique
- Offre une **fiabilité améliorée** avec adaptation à la longueur du texte
- Détecte **plus de motifs IA** — 70+ phrases vs 21 dans la version standard

---

## Portage de l'Analytique vers d'Autres Langages

Le moteur d'analyse amélioré est maintenant disponible dans **toutes les 6 implémentations linguistiques** via les versions `-ext`. L'autonome Python `parscgpt-ext.py` fournit l'analyse la plus complète de 17 métriques pour référence.

Voir **`ANALYTICS_RECOMMENDATIONS.md`** pour un guide complet de portabilité avec :
- Formules de calcul des métriques
- Poids et seuils du modèle de scoring
- Règles d'interprétation
- Guidance spécifique par langage

---

## Implémentations

| Langage   | Répertoire    | Commande de construction                | Fichier de rapport  | Rapport étendu     |
|-----------|---------------|------------------------------------------|---------------------|--------------------|
| Python    | partxtpy/     | (pas de construction nécessaire)        | report_py.txt       | report_py-ext.txt  |
| Rust      | partxtrs/     | cargo build --release                   | report_rs.txt       | report_rs-ext.txt  |
| Go        | partxtgo/     | cd partxtgo && go build                 | report_go.txt       | report_go-ext.txt  |
| C++       | partxtcpp/    | make                                     | report_cpp.txt      | report_cpp-ext.txt |
| Node.js   | partxtnode/   | (pas de construction nécessaire)        | report_node.txt     | report_node-ext.txt |
| Bun       | partxtjs/     | (pas de construction nécessaire)        | report_bun.txt      | report_bun-ext.txt  |

---

## Format de Rapport (Nettoyeur)

Chaque rapport inclut :
- Temps d'exécution
- Mode (remplacer/supprimer + statut de suppression de filigrane)
- Caractères de filigrane supprimés (avec points de code Unicode)
- Caractères remplacés (avec comptes)
- Fréquence des mots (ordre croissant)

**Les versions étendues** incluent également :
- Section de métriques forensiques IA
- Score de probabilité IA avec niveau de confiance
- Analyse des signaux avec indicateurs visuels
- Interprétations spécifiques aux métriques

---

## Résultats d'Exemple (testdata/sample.txt, 197 remplacements)

| Langage  | Temps d'Exécution | Temps Étendu |
|----------|------------------|-------------|
| Go       | ~0.00004 s       | ~0.00006 s   |
| Rust     | ~0.00008 s       | ~0.00010 s   |
| C++      | ~0.00040 s       | ~0.00050 s   |
| Node.js  | ~0.00046 s       | ~0.00060 s   |
| Python   | ~0.00056 s       | ~0.00070 s   |
| Bun      | ~0.00220 s       | ~0.00280 s   |

---

## Corrections Récentes (v0.3.0)

### Nouvelles Versions Étendues ⭐

**L'analyse forensique IA améliorée est maintenant disponible dans tous les 6 langages :**

1. **Python Étendu** (`partxtpy/partxt-ext.py`)
   - Intégration complète des métriques forensiques IA
   - Scoring basé sur la probabilité
   - Analyse des signaux avec interprétations

2. **JavaScript Étendu** (Bun + Node.js)
   - `partxtjs/partxt-ext.js` pour Bun
   - `partxtnode/partxt-ext.js` pour Node.js
   - Mêmes métriques que la version Python

3. **Rust Étendu** (`partxtrs/src/main-ext.rs`)
   - Performances compilées
   - Traitement mémoire efficace
   - Ensemble complet de métriques

4. **Go Étendu** (`partxtgo/main-ext.go`)
   - Implémentation sûre des types
   - Bibliothèque standard uniquement
   - Métriques complètes

5. **C++ Étendu** (`partxtcpp/partxt-ext.cpp`)
   - Hautes performances
   - C++20 moderne
   - Fonctionnalité complète

6. **Node.js Étendu** (`partxtnode/partxt-ext.js`)
   - Compatibilité Node.js
   - Mêmes métriques et fonctionnalités

---

## Versionnement

- Patch (0.0.x) : corrections de bugs
- Mineure (0.x.0) : entièrement fonctionnel, répond aux exigences
- Majeure (x.0.0) : nouvelles fonctionnalités significatives

Version actuelle : 0.4.3

## Licence

MIT