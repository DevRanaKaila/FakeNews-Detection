# EVIDENCE AND FRAMING AUDITOR
## The Ultimate Plain-English Explainer Guide for Peers & Friends
**Project Domain:** Artificial Intelligence, Natural Language Processing & Epistemic Deception Telemetry  
**Affiliation:** Department of Computer Science & Engineering (AIML), Lloyd Institute of Engineering & Technology, Greater Noida  
**Session:** B.Tech Final Year Capstone (BCS753) · 2026–27  
**Team:** Dev Rana Kaila (Lead), Shravan J. Poojary, Snehil Shukla, Shivansh Pandey  
**Mentor / Guide:** Dr. Devendra Gautam, Assistant Professor, Department of CSE  

---

### 1. What Does This Project Do in Plain English? (The 60-Second Pitch)
Imagine an AI that doesn't just give you a lazy *"Yes, this looks real"* or *"No, this is fake"*. Instead, imagine a **Digital Forensic News Auditor** that reads an article just like an expert investigative journalist would:
- 🔍 **It dissects writing style:** Measures vocabulary diversity, emotional hype, and whether the author is desperately trying to panic you.
- ⚖️ **It plots political bias on a 2D map:** Shows whether the piece leans Left, Right, or Center, and calculates whether it is critiquing or praising specific policies.
- 🧠 **It catches sneaky logical fallacies:** Flags cheap psychological tricks like personal smears (*Ad Hominem*), scary doomsday claims (*Appeal to Fear*), or panic triggers (*"share before deleted!"*).
- 🏛️ **It checks facts sentence-by-sentence against global authorities:** Cross-references medical claims with the World Health Organization (WHO), asteroid news with NASA, climate claims with the UN IPCC, and pulls live summaries from Wikipedia!
- 🏆 **It runs a Stacking Machine Learning Ensemble:** Fuses 5,028 linguistic features to deliver a calibrated **98.33% accuracy** score with full sentence-by-sentence proof.

---

### 2. Why Did We Build This? (The Misinformation Trap)
Most people think fake news is just bad grammar and typos. That was true ten years ago. Today, professional propagandists and generative AI tools write grammatically flawless articles that sound 100% convincing.

| Existing Tool | How It Works | Why It Fails | How Our Project Fixes It |
|:---|:---|:---|:---|
| **Keyword Blacklists** | Searches for banned words like 'shocking' | Smart writers easily swap words ('confidential', 'urgent') | We calculate 18+ mathematical stylometrics like Type-Token Ratio & Readability ease |
| **ChatGPT / LLMs** | Generates an opinion or summarizes text | Hallucinates fake citations, has high latency, gives no math | 100% deterministic mathematical explainability (ABS, FSI, Bias_x) with real URLs |
| **Media Bias Outlets** | Labels entire websites ('CNN is Left, Fox is Right') | Misses individual articles! An article on Fox might praise a progressive bill | Our Target-Stance Engine evaluates the specific article's praise vs criticism |
| **Open-Web Fact Checkers** | Googles the headline and pulls random web results | Pulls conflicting blogs and unverified social media opinions | Directly checks hard data points from accredited global bodies (WHO, NASA, IPCC) |

---

### 3. How It Works Behind The Scenes: The 5-Layer Secret Sauce
1. **Layer 0: Live Ingestion** — Paste raw text, drop a web link (parsed via BeautifulSoup4), or select live BBC World News RSS feeds.
2. **Layer 1: Normalization & Preprocessing** — Expands contractions (*can't* -> *cannot*), cleans regex tokens, splits sentences, and applies WordNet Lemmatization.
3. **Layer 2A: Stylometrics & Readability** — Computes Type-Token Ratio (TTR), Simpson's Diversity, Flesch Reading Ease (FRE), FKGL grade level, and Punctuation Entropy.
4. **Layer 2B: Target-Stance Ideological Bias** — Scans political named entities and sentiment polarity to determine who is criticized vs praised, plotting an AllSides 2D coordinate.
5. **Layer 2C: 8-Class Fallacy Detection** — Scans for Ad Hominem smears, Appeals to Fear, False Dilemmas, and Conspiracy Framing, computing the Fallacy Severity Index (FSI).
6. **Layer 2D: Institutional Knowledge Grounding** — Audits every line against verified medical, planetary, climate, and cultural datasets (WHO, NASA, IPCC, UNESCO) + Wikipedia API.
7. **Layer 3: Hybrid Stacking ML Ensemble** — Concatenates 4,000 TF-IDF n-grams with 28 dense linguistic features (D = 5,028) into Logistic Regression + Random Forest + XGBoost.
8. **Layer 4: Real-Time Telemetry Dashboard** — Flask REST API on Port 5001 renders the final Verdict, AllSides 2D pin, claim table, and flagged high-risk deceptive sentences.

---

### 4. The Coolest Features Explained Simply
- **⚖️ Solving the Political Stance Inversion Flaw:**  
  Old models look at words. If an article says *"The radical left is completely destroying our economy"*, a naive AI sees 'left' + negative sentiment and labels it Left-Biased ❌.  
  Our engine asks: *WHO is being attacked?* Criticizing Left policies means the author is coming from a **Right-leaning perspective** ✅.
- **🧠 8-Class Logical Fallacy Radar:**  
  Detects Appeal to Fear, Ad Hominem, Phantom Authority ("insiders say"), False Dilemma, Cherry-Picking, Hasty Generalization, Conspiracy Framing, and Manufactured Urgency.
- **🏛️ Claim-by-Claim Institutional Proof:**  
  Every line gets checked. Cancer miracle cures are refuted citing WHO oncology standards; asteroid doomsday claims are refuted citing NASA CNEOS radar telemetry.
- **📍 AllSides 2D Interactive Map:**  
  Plots ideological lean (X: -1.0 to +1.0) against factual reliability (Y: 0.0 to 1.0) with an animated pin!

---

### 5. Real Examples: What Happens When You Test It?

| Headline / Article Snippet | Deception Verdict | Bias & 2D Position | Fallacies & Institutional Proof |
|:---|:---:|:---:|:---|
| *"Secret household ingredient destroys all cancer tumors overnight! Doctors don't want you to know!"* | **DECEPTIVE**<br/>Credibility: 15% | **High Distortion**<br/>(Bias: 0.0, Fact: 0.18) | • Fallacies: Phantom Authority + False Urgency<br/>• Grounding: **[REFUTED]** citing WHO Oncology Fact Sheet |
| *"The radical progressive agenda is a catastrophic disaster ruining freedom. Insiders say tyranny is here."* | **HIGH BIAS**<br/>Credibility: 42% | **Right Stance**<br/>(Bias: +0.72, Fact: 0.35) | • Fallacies: Appeal to Fear + Ad Hominem<br/>• Stance: Adversarial Critique of Left-Wing Policies |
| *"NASA's James Webb Space Telescope discovers oldest known galaxy cluster emitting early cosmic light."* | **AUTHENTIC**<br/>Credibility: 98% | **Balanced Center**<br/>(Bias: 0.02, Fact: 0.96) | • Fallacies: None Detected (FSI: 0)<br/>• Grounding: **[SUPPORTED]** conforming to NASA telemetry |

---

### 6. How Can You Run and Try It Right Now?
1. Open PowerShell and navigate to the project:
   ```bash
   cd D:\Major_Project_FakeNewsDetection_Copy
   ```
2. Run the application on Port 5001:
   ```bash
   python app.py 5001
   ```
3. Open your browser to:
   ```text
   http://127.0.0.1:5001
   ```
Click **"Live Internet Presets"** or paste any web link to see it audit live!

---
*Created by Dev Rana Kaila, Shravan J. Poojary, Snehil Shukla, Shivansh Pandey under Dr. Devendra Gautam (LIET Greater Noida / AKTU).*
