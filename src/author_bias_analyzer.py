import re
import numpy as np
from textblob import TextBlob
from typing import Dict, List, Any, Tuple
from src.preprocessor import TextPreprocessor

class AuthorBiasAnalyzer:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        
        self.sensational_lexicon = {
            "shocking", "unbelievable", "bombshell", "outrageous", "disastrous", "miracle",
            "destroy", "demolish", "slammed", "annihilated", "traitor", "scandalous",
            "conspiracy", "corrupt", "terrifying", "secret", "exposed", "furious",
            "catastrophe", "bizarre", "panic", "insane", "nightmare", "mind-blowing",
            "treason", "tyranny", "evil", "disgraceful", "shameful", "horrific"
        }
        
        self.intensifier_lexicon = {
            "absolutely", "completely", "totally", "utterly", "extremely", "massively",
            "insanely", "radically", "drastically", "overwhelmingly", "infinitely", "purely"
        }
        
        self.hedge_lexicon = {
            "allegedly", "reportedly", "supposedly", "rumored", "claims", "purportedly",
            "insiders say", "sources claim", "many believe", "some say", "it is said",
            "unconfirmed", "secretly", "ostensibly"
        }
        
        self.pronoun_lexicon = {
            "i", "me", "my", "myself", "we", "us", "our", "ourselves", "you", "your", "yours", "they", "them"
        }
        
        # Target Terms & Ideological Entities
        self.left_targets = {
            "left", "leftists", "democrats", "democrat", "biden", "liberals", "liberal",
            "progressives", "progressive", "socialists", "socialism", "woke", "wokeness",
            "green new deal", "climate activists", "marxists", "mainstream media"
        }
        
        self.right_targets = {
            "right", "conservatives", "conservative", "republicans", "republican", "trump",
            "nationalists", "traditionalists", "maga", "corporations", "corporate oligarchs",
            "billionaires", "wall street", "oil companies", "fossil fuel lobby"
        }
        
        self.left_positive_themes = {
            "systemic equality", "universal healthcare", "climate justice", "workers rights",
            "lgbtq rights", "wealth redistribution", "clean energy transition", "civil rights",
            "living wage", "public healthcare", "renewable future"
        }
        
        self.right_positive_themes = {
            "free market", "individual liberty", "law and order", "border security",
            "fiscal responsibility", "deregulation", "constitutional freedoms",
            "traditional family values", "tax relief", "national sovereignty"
        }
        
        # Negative / Attack Modifiers used in political rhetoric
        self.attack_modifiers = {
            "corrupt", "radical", "failed", "destroying", "dangerous", "insane", "hypocrisy",
            "ruining", "threat", "disaster", "incompetent", "fraud", "tyranny", "brainwashed",
            "authoritarian", "unhinged", "extremist", "criminal", "greed", "evil", "scam"
        }

    def evaluate_target_stance(self, text: str) -> Tuple[float, str]:
        lower_text = text.lower()
        sentences = self.preprocessor.split_sentences(text)
        
        left_criticism_score = 0.0
        left_praise_score = 0.0
        right_criticism_score = 0.0
        right_praise_score = 0.0
        
        for s in sentences:
            s_low = s.lower()
            blob = TextBlob(s)
            sentiment = blob.sentiment.polarity
            
            has_left_target = any(re.search(r'\b' + re.escape(t) + r'\b', s_low) for t in self.left_targets)
            has_right_target = any(re.search(r'\b' + re.escape(t) + r'\b', s_low) for t in self.right_targets)
            has_attack = any(re.search(r'\b' + re.escape(a) + r'\b', s_low) for a in self.attack_modifiers)
            
            # Stance 1: Criticism of the Left -> Indicates RIGHT-LEANING stance
            if has_left_target:
                if has_attack or sentiment < -0.15:
                    left_criticism_score += 1.5 + abs(sentiment)
                elif sentiment > 0.15:
                    left_praise_score += 1.0 + sentiment
                    
            # Stance 2: Criticism of the Right -> Indicates LEFT-LEANING stance
            if has_right_target:
                if has_attack or sentiment < -0.15:
                    right_criticism_score += 1.5 + abs(sentiment)
                elif sentiment > 0.15:
                    right_praise_score += 1.0 + sentiment

        for theme in self.left_positive_themes:
            if theme in lower_text:
                left_praise_score += 1.0
                
        for theme in self.right_positive_themes:
            if theme in lower_text:
                right_praise_score += 1.0

        # Right-leaning signal: criticizing Left OR praising Right
        total_right_lean = left_criticism_score + right_praise_score
        # Left-leaning signal: criticizing Right OR praising Left
        total_left_lean = right_criticism_score + left_praise_score
        
        total_signals = total_right_lean + total_left_lean
        if total_signals == 0.0:
            return 0.0, "Balanced / Neutral Factual Discourse"
            
        # Coordinate on [-1.0 (Left) to +1.0 (Right)]
        lean_x = (total_right_lean - total_left_lean) / max(1.0, total_signals)
        lean_x = float(np.clip(lean_x, -1.0, 1.0))
        
        if left_criticism_score > right_criticism_score and total_right_lean > 1.0:
            stance_summary = "Critique / Adversarial Stance towards Left-Wing Policies (Right-Leaning Perspective)"
        elif right_criticism_score > left_criticism_score and total_left_lean > 1.0:
            stance_summary = "Critique / Adversarial Stance towards Right-Wing / Corporate Entities (Left-Leaning Perspective)"
        elif left_praise_score > 1.0:
            stance_summary = "Supportive Advocacy for Progressive / Environmental Frameworks"
        elif right_praise_score > 1.0:
            stance_summary = "Supportive Advocacy for Conservative / Free-Market Principles"
        else:
            stance_summary = "Evenly Balanced / Objective Cross-Perspective Stance"
            
        return lean_x, stance_summary

    def analyze_tone_and_bias(self, text: str, title: str = "") -> Dict[str, Any]:
        if not isinstance(text, str) or not text.strip():
            text = "neutral factual baseline content text."
            
        sentences = self.preprocessor.split_sentences(text)
        n_sentences = max(1, len(sentences))
        tokens = self.preprocessor.extract_raw_tokens(text)
        lower_tokens = [w.lower() for w in tokens]
        n_words = max(1, len(lower_tokens))
        
        sens_lex = getattr(self, 'sensational_lexicon', {"shocking", "bombshell", "secret", "miracle", "furious", "panic"})
        int_lex = getattr(self, 'intensifier_lexicon', {"absolutely", "completely", "totally", "extremely"})
        hedge_lex = getattr(self, 'hedge_lexicon', {"allegedly", "reportedly", "supposedly", "rumored", "secretly"})
        pro_lex = getattr(self, 'pronoun_lexicon', {"i", "we", "our", "you", "they"})

        # 1. Subjectivity Index
        sentence_blobs = [TextBlob(s) for s in sentences]
        subjectivities = [b.sentiment.subjectivity for b in sentence_blobs]
        polarities = [b.sentiment.polarity for b in sentence_blobs]
        
        subjectivity_index = float(np.mean(subjectivities)) if subjectivities else 0.0
        overall_polarity = float(np.mean(polarities)) if polarities else 0.0
        polarity_variance = float(np.var(polarities)) if polarities else 0.0

        # 2. Emotional Hyperbole Factor
        sensational_hits = sum(1 for w in lower_tokens if w in sens_lex)
        intensifier_hits = sum(1 for w in lower_tokens if w in int_lex)
        emotional_hyperbole_factor = min(1.0, ((intensifier_hits + (1.5 * sensational_hits)) / n_words) * 8.0)

        # 3. Hedging & Uncertainty Ratio
        lower_text = text.lower()
        hedge_hits = sum(1 for phrase in hedge_lex if phrase in lower_text)
        hedge_uncertainty_ratio = min(1.0, hedge_hits / (n_sentences * 0.8))

        # 4. Personal Pronoun Ratio
        pronoun_hits = sum(1 for w in lower_tokens if w in pro_lex)
        personal_pronoun_ratio = min(1.0, (pronoun_hits / n_words) * 5.0)

        # 5. Title-Body Sentiment & Affect Divergence
        title_polarity = 0.0
        title_sensational = 0.0
        if title and title.strip():
            t_blob = TextBlob(title)
            title_polarity = float(t_blob.sentiment.polarity)
            t_tokens = [w.lower() for w in self.preprocessor.extract_raw_tokens(title)]
            t_sens_count = sum(1 for w in t_tokens if w in sens_lex or w in int_lex)
            title_sensational = min(1.0, t_sens_count / max(1, len(t_tokens)))
            
        title_body_sentiment_skew = abs(title_polarity - overall_polarity)
        clickbait_discrepancy_metric = min(1.0, (0.5 * title_body_sentiment_skew) + (0.5 * title_sensational))

        # 6. Affective Polarization Density
        extreme_sentences = sum(1 for p in polarities if abs(p) > 0.45)
        affective_polarization_density = extreme_sentences / n_sentences

        # 7. Composite Author Bias Score (ABS in [0, 100])
        raw_bias = (
            (0.25 * subjectivity_index) +
            (0.25 * emotional_hyperbole_factor) +
            (0.20 * affective_polarization_density) +
            (0.15 * hedge_uncertainty_ratio) +
            (0.15 * clickbait_discrepancy_metric)
        )
        author_bias_score = float(np.clip(raw_bias * 100.0, 0.0, 100.0))

        # --- Target-Stance Ideological Leaning Formulation ---
        ideological_lean_x, stance_summary = self.evaluate_target_stance(f"{title}. {text}")
        
        # Factuality Y-Coordinate: 0.0 (Low) to 1.0 (High)
        factuality_y = float(np.clip(1.0 - (author_bias_score / 100.0 * 0.7) - (emotional_hyperbole_factor * 0.3), 0.05, 0.98))

        # AllSides-Style Categorical Mapping
        if author_bias_score > 65.0:
            allsides_rating = "Partisan / Sensationalist"
            allsides_color = "#B33939"
            chart_zone = "Low Factuality / High Distortion"
        elif ideological_lean_x < -0.35:
            allsides_rating = "Left / Progressive Stance"
            allsides_color = "#2E86AB"
            chart_zone = "Left Spectrum"
        elif ideological_lean_x < -0.12:
            allsides_rating = "Lean Left"
            allsides_color = "#5B92E5"
            chart_zone = "Lean Left Spectrum"
        elif ideological_lean_x > 0.35:
            allsides_rating = "Right / Conservative Stance"
            allsides_color = "#C0392B"
            chart_zone = "Right Spectrum"
        elif ideological_lean_x > 0.12:
            allsides_rating = "Lean Right"
            allsides_color = "#E67E22"
            chart_zone = "Lean Right Spectrum"
        else:
            allsides_rating = "Center / Balanced Reporting"
            allsides_color = "#446353"
            chart_zone = "Balanced Center"

        if overall_polarity > 0.25:
            tone_sentiment = "Strongly Positive / Promotional"
        elif overall_polarity < -0.25:
            tone_sentiment = "Strongly Critical / Adversarial"
        else:
            tone_sentiment = "Balanced / Objective Tone"

        metrics_dict = {
            "subjectivity_index": float(subjectivity_index),
            "overall_polarity": float(overall_polarity),
            "polarity_variance": float(polarity_variance),
            "emotional_hyperbole_factor": float(emotional_hyperbole_factor),
            "hedge_uncertainty_ratio": float(hedge_uncertainty_ratio),
            "personal_pronoun_ratio": float(personal_pronoun_ratio),
            "title_body_sentiment_skew": float(title_body_sentiment_skew),
            "clickbait_discrepancy_metric": float(clickbait_discrepancy_metric),
            "affective_polarization_density": float(affective_polarization_density),
            "author_bias_score": float(author_bias_score),
            "ideological_lean_x": round(ideological_lean_x, 3),
            "factuality_y": round(factuality_y, 3)
        }

        diagnostic_summary = {
            "author_bias_score": round(author_bias_score, 2),
            "allsides_rating": allsides_rating,
            "allsides_color": allsides_color,
            "chart_zone": chart_zone,
            "stance_summary": stance_summary,
            "tone_sentiment": tone_sentiment,
            "subjectivity_pct": round(subjectivity_index * 100.0, 1),
            "sensationalism_pct": round(emotional_hyperbole_factor * 100.0, 1),
            "hedging_pct": round(hedge_uncertainty_ratio * 100.0, 1),
            "sensational_word_count": sensational_hits,
            "hedge_phrase_count": hedge_hits,
            "ideological_lean_x": round(ideological_lean_x, 2),
            "factuality_y": round(factuality_y, 2)
        }

        return {
            "metrics": metrics_dict,
            "diagnostics": diagnostic_summary
        }

    def get_feature_names(self) -> List[str]:
        return [
            "subjectivity_index", "overall_polarity", "polarity_variance",
            "emotional_hyperbole_factor", "hedge_uncertainty_ratio", "personal_pronoun_ratio",
            "title_body_sentiment_skew", "clickbait_discrepancy_metric", "affective_polarization_density",
            "author_bias_score"
        ]
