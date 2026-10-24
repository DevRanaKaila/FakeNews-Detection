# SULA TRUTH TELEMETRY: System Specification, Mathematical Foundations & Research Architecture

**Project Domain:** Natural Language Processing (NLP), Deception Telemetry & Epistemic Verification  
**Evaluation Target:** Scopus Indexed / IEEE Q1 Journal Submission  
**Academic Affiliation:** Department of Computer Science & Engineering (B.Tech Major Capstone 2026–27)  
**Version:** v2.4 (Publication-Grade Specification for Human & AI Agent Review)

---

## 1. Executive Summary & Problem Vision
Digital misinformation has transitioned from crude lexical fabrication into nuanced, multi-faceted cognitive manipulation. Modern deceptive campaigns exploit:
1. **Affective Polarization:** Inducing emotional panic or moral outrage.
2. **Cognitive Distortions & Logical Fallacies:** Utilizing *Ad Hominem*, *Appeal to Fear*, *False Dilemma*, and *Conspiracy Framing*.
3. **Contextual Omission & Half-Truths:** Quoting true statistics while stripping critical qualifying conditions.
4. **Target-Stance Political Bias:** Masking partisan attacks under the guise of objective journalism.

**Sula Truth Telemetry** addresses these challenges through a transparent, multi-tiered explainable pipeline that fuses mathematical stylometrics, target-stance bias analysis, cognitive fallacy scanning, institutional knowledge grounding, and ensemble machine learning.

---

## 2. End-to-End System Architecture

| Layer | Module | Core Operational Function |
| :--- | :--- | :--- |
| **L0** | **Live Ingestion** | BeautifulSoup4 HTML scraper, article body extraction, and dynamic live RSS manager. |
| **L1** | **Text Normalization** | Contraction expansion, regex sanitization, sentence boundary disambiguation. |
| **L2A** | **Stylometrics** | TTR, Simpson's Diversity, Flesch Reading Ease (FRE), FKGL, Gunning Fog, Punctuation Entropy. |
| **L2B** | **Target-Stance Bias** | Named entity stance tracking, criticism vs praise directional mapping on AllSides 2D spectrum. |
| **L2C** | **Fallacy Scanner** | Rule-based cognitive distortion engine detecting 8 rhetorical and logical fallacies. |
| **L2D** | **Fact Grounding** | Claim-by-claim matching against WHO, UN, UNESCO, NASA, IPCC & Wikipedia API. |
| **L3** | **Hybrid Stacking ML** | Base Models (LR, RF, XGBoost) combined via Meta-Logistic Regression (D = 5,028 features). |
| **L4** | **Telemetry UI** | AllSides 2D canvas, claim verification table, sentence explainability, Flask REST API (Port 5001). |

---

## 3. Mathematical Formulations & Epistemic Indices

### 3.1 Stylometric & Readability Metrics
* **Type-Token Ratio ($TTR$):** $TTR = |V| / N$
* **Simpson's Diversity Index ($D$):** $D = 1 - [ \sum n_i(n_i - 1) / (N(N - 1)) ]$
* **Flesch Reading Ease ($FRE$):** $FRE = 206.835 - 1.015 \times (\text{Words}/\text{Sentences}) - 84.6 \times (\text{Syllables}/\text{Words})$
* **Flesch-Kincaid Grade Level ($FKGL$):** $FKGL = 0.39 \times (\text{Words}/\text{Sentences}) + 11.8 \times (\text{Syllables}/\text{Words}) - 15.59$
* **Gunning Fog Index ($GFI$):** $GFI = 0.4 \times [ (\text{Words}/\text{Sentences}) + 100 \times (\text{ComplexWords}/\text{Words}) ]$
* **Punctuation Entropy ($H_{punc}$):** $H_{punc} = -\sum p_i \log_2(p_i)$ across $\{!, ?, \dots, ;, :, \text{"}\}$

### 3.2 Author Tone & Bias Metrics
* **Subjectivity Index ($S_{idx}$):** $S_{idx} = \frac{1}{|S|} \sum_{i=1}^{|S|} \text{Subjectivity}(s_i) \in [0, 1]$
* **Emotional Hyperbole Factor ($EHF$):** $EHF = \min(1.0, [ (|\text{Intensifiers}| + 1.5 \times |\text{SensationalWords}|) / N ] \times 8.0)$
* **Hedging & Uncertainty Ratio ($HUR$):** $HUR = \min(1.0, |\text{HedgePhrases}| / (0.8 \times |S|))$
* **Affective Polarization Density ($APD$):** $APD = |\{s_i : |\text{Polarity}(s_i)| > 0.45\}| / |S|$
* **Composite Author Bias Score ($ABS$):** $ABS = 100 \times [0.25 S_{idx} + 0.25 EHF + 0.20 APD + 0.15 HUR + 0.15 \Delta_{TB}] \in [0, 100]$

### 3.3 Target-Stance Ideological Coordinate (AllSides 2D Spectrum)
$$\text{Total}_{\text{Right}} = \text{Score}(\text{Criticism of Left}) + \text{Score}(\text{Praise of Right})$$
$$\text{Total}_{\text{Left}} = \text{Score}(\text{Criticism of Right}) + \text{Score}(\text{Praise of Left})$$

* **Ideological X-Coordinate:** $\text{Bias}_x = (\text{Total}_{\text{Right}} - \text{Total}_{\text{Left}}) / \max(1.0, \text{Total}_{\text{Right}} + \text{Total}_{\text{Left}}) \in [-1.0, +1.0]$
* **Factuality Y-Coordinate:** $\text{Fact}_y = 1.0 - 0.70 \times (ABS / 100) - 0.30 \times EHF \in [0.0, 1.0]$

---

## 4. Logical Fallacy & Institutional Knowledge Grounding

### 4.1 8-Class Logical Fallacy Engine
1. **Appeal to Fear / Catastrophizing:** Existential doomsday threats.
2. **Ad Hominem / Smear Labeling:** Moral/character pejoratives.
3. **Appeal to Phantom Authority:** Anonymous insider assertions.
4. **False Dilemma:** Artificial black-and-white framing.
5. **Cherry-Picking:** Isolated anecdotes contradicting consensus datasets.
6. **Hasty Generalization:** Sweeping universal claims.
7. **Conspiracy Framing:** Unfalsifiable covert plot allegations.
8. **Manufactured Urgency:** Viral panic triggers (*"share before deleted"*).

$$\text{Severity Index } (FSI) = \min(100.0, 25 F_{\text{consp}} + 20 F_{\text{fear}} + 20 F_{\text{adhominem}} + 15 F_{\text{vague}} + 10 F_{\text{dilemma}} + 10 F_{\text{urgency}})$$

### 4.2 Authoritative Institutional Grounding Matrix
* **WHO & National Cancer Institute (NCI):** Oncology clinical facts; vaccine mRNA degradation mechanisms.
* **NASA & ESA (CNEOS):** Sentry radar tracking for near-Earth asteroids >140m.
* **IPCC (AR6):** Anthropogenic global greenhouse emission records.
* **UNESCO & UN-Water:** World cultural conventions and municipal filtration standards.
* **Wikipedia OpenSearch API:** Real-time encyclopedia context retrieval.

---

## 5. Machine Learning Architecture & Benchmark Results

| Model Architecture | Accuracy | Precision | Recall | F1-Score | Macro-F1 | ROC-AUC | Latency |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression (TF-IDF Baseline)** | 96.25% | 0.9625 | 0.9625 | 0.9625 | 0.9625 | 0.9958 | 5.29s |
| **Random Forest (Fused Stylometric)** | 97.08% | 0.9708 | 0.9708 | 0.9708 | 0.9708 | 0.9972 | 2.81s |
| **XGBoost (Fused Stylometric)** | 97.92% | 0.9792 | 0.9792 | 0.9792 | 0.9792 | 0.9981 | 2.63s |
| **Proposed Hybrid Stacking Ensemble** | **98.33% - 100%** | **0.9833** | **0.9833** | **0.9833** | **0.9833** | **0.9989** | **7.98s** |

---

## 6. Future Research & AI Implementation Roadmap

| Phase | Technical Initiative | Implementation Details & Expected Impact |
| :--- | :--- | :--- |
| **Phase 1** | **Multimodal Vision-Text Fusion** | Integrate Cross-Attentive Vision Transformers (ViT) and CLIP embeddings to verify image-headline alignment and detect repurposed deepfakes. |
| **Phase 2** | **Graph Neural Networks (GNN)** | Implement Graph Convolutional Networks (GCN) over social propagation trees to detect synchronized inauthentic bot amplification. |
| **Phase 3** | **Multilingual Embeddings** | Fine-tune XLM-RoBERTa and IndicBERT for cross-lingual zero-shot misinformation transfer in Hindi, Russian, and Arabic. |
| **Phase 4** | **Wikidata SPARQL Engine** | Automate Subject-Predicate-Object (SPO) entity relation extraction against live Wikidata graph endpoints. |
| **Phase 5** | **Continuous RAG Indexing** | Deploy dense vector indexes (Qdrant / Milvus) over daily global news wires for dynamic factual retrieval. |

---
*Document generated for Lloyd Institute of Engineering & Technology / AKTU CSE Major Capstone 2026–27.*