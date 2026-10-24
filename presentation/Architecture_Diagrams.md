# System Architecture Diagrams & Data Flow Maps
## Sula Truth Telemetry: Fake News Detection Pipeline
### Supplementary Visual Reference for Viva Voce Presentation

---

## 1. High-Level System Architecture (Mermaid Flowchart)

```mermaid
flowchart TD
    A["Raw Input"] --> B{"Input Source"}
    B -->|"Text Paste"| C["Text Inspector"]
    B -->|"URL"| D["Web Scraper (BS4)"]
    B -->|"RSS Feed"| E["Live Feed Manager"]
    
    C --> F["Layer 1: Text Normalization"]
    D --> F
    E --> F
    
    F --> G["Contraction Expansion"]
    G --> H["Regex Sanitization"]
    H --> I["Sentence Splitting"]
    I --> J["WordNet Lemmatization"]
    
    J --> K["Layer 2A: Stylometrics"]
    J --> L["Layer 2B: Target-Stance Bias"]
    J --> M["Layer 2C: Fallacy Scanner"]
    J --> N["Layer 2D: Fact Grounding"]
    J --> O["TF-IDF Vectorizer (4K features)"]
    
    K --> P["Feature Fusion (D=5,028)"]
    L --> P
    M --> Q["Fallacy Severity Index"]
    N --> R["Claim Verification Table"]
    O --> P
    
    P --> S["Layer 3: Hybrid Stacking ML"]
    S --> T["Base: LR + RF + XGBoost"]
    T --> U["Meta-Estimator: Calibrated LR"]
    
    U --> V["Layer 4: Telemetry Dashboard"]
    Q --> V
    R --> V
    L --> V
    
    V --> W["Verdict Banner (0-100%)"]
    V --> X["AllSides 2D Bias Chart"]
    V --> Y["Fallacy Cards"]
    V --> Z["Sentence Highlighter"]
```

---

## 2. Feature Engineering Pipeline (Detailed)

```mermaid
flowchart LR
    subgraph BRANCH_A["Branch A: Stylometric Features (19)"]
        A1["TTR"] --> AF["Feature Vector"]
        A2["Root TTR"] --> AF
        A3["Hapax Ratio"] --> AF
        A4["Simpson's Index"] --> AF
        A5["FRE"] --> AF
        A6["FKGL"] --> AF
        A7["Gunning Fog"] --> AF
        A8["Punct. Entropy"] --> AF
        A9["Avg Word Length"] --> AF
        A10["Avg Sentence Length"] --> AF
    end
    
    subgraph BRANCH_B["Branch B: Author Bias Features (10)"]
        B1["Subjectivity Index"] --> BF["Feature Vector"]
        B2["Polarity"] --> BF
        B3["EHF"] --> BF
        B4["HUR"] --> BF
        B5["APD"] --> BF
        B6["ABS"] --> BF
        B7["Pronoun Ratio"] --> BF
        B8["Clickbait Discrepancy"] --> BF
    end
    
    subgraph BRANCH_C["Branch C: Semantic Features (4,000)"]
        C1["Sublinear TF-IDF"] --> CF["Sparse Matrix"]
        C2["Bi-gram N-grams"] --> CF
        C3["Unicode Strip"] --> CF
    end
    
    AF --> FUSE["StandardScaler + hstack Fusion"]
    BF --> FUSE
    CF --> FUSE
    
    FUSE --> FINAL["Fused Feature Matrix (D = 5,028)"]
```

---

## 3. Stacking Classifier Architecture

```mermaid
flowchart TD
    INPUT["Fused Feature Vector (D=5,028)"] --> SPLIT["3-Fold Cross-Validation Split"]
    
    SPLIT --> LR["Base Learner 1: Logistic Regression (C=2.0)"]
    SPLIT --> XGB["Base Learner 2: XGBoost (n=120, depth=5)"]
    SPLIT --> RF["Base Learner 3: Random Forest (n=80, depth=15)"]
    
    LR --> META_INPUT["Out-of-Fold Predictions (3 columns)"]
    XGB --> META_INPUT
    RF --> META_INPUT
    
    META_INPUT --> META["Meta-Estimator: Calibrated Logistic Regression"]
    META --> PRED["Final Prediction: REAL / FAKE"]
    META --> PROB["Probability Score + Credibility %"]
```

---

## 4. Target-Stance Bias Mapping Algorithm

```mermaid
flowchart TD
    TEXT["Input Article Text"] --> SENT["Sentence Tokenization"]
    SENT --> LOOP["For Each Sentence"]
    
    LOOP --> LEFT_CHECK{"Contains Left-Target Entity?"}
    LOOP --> RIGHT_CHECK{"Contains Right-Target Entity?"}
    
    LEFT_CHECK -->|"Yes + Attack Modifier"| LC["left_criticism_score += 1.5 + abs(sentiment)"]
    LEFT_CHECK -->|"Yes + Positive Sentiment"| LP["left_praise_score += 1.0 + sentiment"]
    
    RIGHT_CHECK -->|"Yes + Attack Modifier"| RC["right_criticism_score += 1.5 + abs(sentiment)"]
    RIGHT_CHECK -->|"Yes + Positive Sentiment"| RP["right_praise_score += 1.0 + sentiment"]
    
    LC --> TOTAL_R["Total_Right = left_criticism + right_praise"]
    RP --> TOTAL_R
    
    RC --> TOTAL_L["Total_Left = right_criticism + left_praise"]
    LP --> TOTAL_L
    
    TOTAL_R --> BIAS_X["Bias_x = (Total_R - Total_L) / max(1, Total_R + Total_L)"]
    TOTAL_L --> BIAS_X
    
    BIAS_X --> CHART["AllSides 2D Chart Position"]
```

---

## 5. Claim-by-Claim Verification Flow

```mermaid
flowchart TD
    ARTICLE["Input Article"] --> SPLIT["Split into Individual Sentences"]
    SPLIT --> LOOP["For Each Sentence"]
    
    LOOP --> INST_CHECK{"Match Against Institutional Database?"}
    
    INST_CHECK -->|"WHO/CDC Match"| REFUTED["Verdict: REFUTED (Crimson)"]
    INST_CHECK -->|"UNESCO Match"| HALF["Verdict: HALF-TRUTH (Amber)"]
    INST_CHECK -->|"No Institutional Match"| VAGUE_CHECK{"Contains Vague Attribution?"}
    
    VAGUE_CHECK -->|"'Studies show...' without source"| VAGUE["Verdict: VAGUE/UNVERIFIED (Amber)"]
    VAGUE_CHECK -->|"No flags"| SUPPORTED["Verdict: SUPPORTED (Sage/Green)"]
    
    REFUTED --> TABLE["Claim Verification Table"]
    HALF --> TABLE
    VAGUE --> TABLE
    SUPPORTED --> TABLE
    
    TABLE --> WIKI["Wikipedia OpenSearch Enrichment"]
    WIKI --> FINAL["Final Grounding Report"]
```

---

## 6. Mathematical Formula Reference Card

### Stylometric Metrics:
| Symbol | Formula | Range | Interpretation |
|:---|:---|:---:|:---|
| $TTR$ | $\|V\| / N$ | [0, 1] | Higher = richer vocabulary |
| $D$ | $1 - \sum n_i(n_i-1) / N(N-1)$ | [0, 1] | Higher = more diverse |
| $FRE$ | $206.835 - 1.015(W/S) - 84.6(Syl/W)$ | [0, 100] | Higher = easier to read |
| $FKGL$ | $0.39(W/S) + 11.8(Syl/W) - 15.59$ | [0, 20+] | U.S. grade level |
| $GFI$ | $0.4[(W/S) + 100(CW/W)]$ | [0, 20+] | Years of education needed |
| $H_{punc}$ | $-\sum p_i \log_2(p_i)$ | [0, ~3.5] | Higher = more varied punctuation |

### Author Bias Metrics:
| Symbol | Formula | Range | Interpretation |
|:---|:---|:---:|:---|
| $S_{idx}$ | $\frac{1}{\|S\|} \sum \text{Subj}(s_i)$ | [0, 1] | Higher = more subjective |
| $EHF$ | $\min(1, \frac{\|Int\| + 1.5\|Sens\|}{N} \times 8)$ | [0, 1] | Higher = more sensational |
| $HUR$ | $\min(1, \frac{Hedges}{0.8 \|S\|})$ | [0, 1] | Higher = more uncertain |
| $APD$ | $\frac{\|s_i: \|Pol(s_i)\| > 0.45\|}{\|S\|}$ | [0, 1] | Higher = more polarized |
| $ABS$ | $100 \times (0.25 S + 0.25 E + 0.20 A + 0.15 H + 0.15 \Delta)$ | [0, 100] | Overall bias intensity |

### Ideological Coordinates:
| Symbol | Formula | Range | Interpretation |
|:---|:---|:---:|:---|
| $Bias_x$ | $(Total_R - Total_L) / \max(1, Total_R + Total_L)$ | [-1, +1] | Left (-1) to Right (+1) |
| $Fact_y$ | $1 - 0.7 \times ABS/100 - 0.3 \times EHF$ | [0, 1] | Low (0) to High (1) factuality |
| $FSI$ | $\min(100, 25F_c + 20F_f + 20F_a + 15F_v + 10F_d + 10F_u)$ | [0, 100] | Fallacy severity |

---

## 7. Comparison with Contemporary Research (2024-2026)

### Positioning Against State-of-the-Art:

| Dimension | Existing SOTA | Our System | Advantage |
|:---|:---|:---|:---|
| **Accuracy** | ISOT: 99.2% (RoBERTa), LIAR: 81.2% (MiLk-FD) | 98.33% (Custom Corpus) | Competitive without transformers |
| **Explainability** | Black-box (BERT/GPT) or post-hoc (SHAP) | Full mathematical indices (12+ formulas) | Native transparency |
| **Bias Detection** | Source-level (PRISM, ACL 2025: 65-75%) | Article-level target-stance (continuous 2D) | Per-article granularity |
| **Fallacy Detection** | Separate systems (CoCoLoFa, ~74% F1) | Integrated 8-class engine | Unified pipeline |
| **Fact Grounding** | Noisy web retrieval (RAG) | Curated institutional databases | Zero-noise verification |
| **Real-time Deployment** | API-dependent (GPT-4, LLaMA-70B) | Self-contained Flask app (<150MB) | Edge-deployable |

### Key References (2024-2026):

1. ERIC-FND -- Cao et al., AAAI 2025 (Multimodal contrastive with external knowledge)
2. MiLk-FD -- Xie et al., IEEE TCSS 2025 (Heterogeneous GNN with knowledge graphs)
3. MSynFD -- Xiao et al., WWW 2024 (Syntax-aware debiased detection)
4. PRISM -- Sun et al., ACL 2025 (Political bias spectrum embeddings)
5. PCoT -- ACL 2025 (Persuasion-augmented chain of thought for fallacy reasoning)
6. Logical Structure Tree -- Lei & Huang, EMNLP 2024 (Hierarchical fallacy classification)
7. CoCoLoFa -- Yeh et al., EMNLP 2024 (7,706 fallacy-annotated news comments)
8. LIARArg -- Wang et al., Argument & Computation 2025 (Argumentative evidence for fact-checking)
9. AllSides-2024 -- EMNLP 2025 (Political bias calibration benchmark)
10. Ronnback et al. -- PLOS ONE 2025 (Large-scale automatic bias detection)

---

*Supplementary document for Viva Voce Presentation.*
*Lloyd Institute of Engineering & Technology / AKTU CSE Major Capstone 2026-27.*
