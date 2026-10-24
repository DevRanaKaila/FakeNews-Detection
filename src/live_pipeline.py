import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional

from src.preprocessor import TextPreprocessor
from src.stylometric_extractor import StylometricExtractor
from src.author_bias_analyzer import AuthorBiasAnalyzer
from src.fallacy_detector import FallacyDetector
from src.knowledge_grounding import KnowledgeGroundingEngine
from src.models import HybridFakeNewsClassifier

class LiveVerificationPipeline:
    def __init__(self, model_path: Optional[str] = None):
        self.preprocessor = TextPreprocessor()
        self.stylometric_extractor = StylometricExtractor()
        self.bias_analyzer = AuthorBiasAnalyzer()
        self.fallacy_detector = FallacyDetector()
        self.knowledge_engine = KnowledgeGroundingEngine()
        
        if model_path:
            self.model = HybridFakeNewsClassifier.load(model_path)
        else:
            self.model = None

    def set_model(self, model: HybridFakeNewsClassifier):
        self.model = model

    def fetch_article_from_url(self, url: str) -> Dict[str, str]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            return {
                "error": f"Failed to retrieve URL ({str(e)})",
                "title": "",
                "text": "",
                "source_domain": ""
            }

        soup = BeautifulSoup(response.text, 'html.parser')
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.replace("www.", "")

        title = ""
        if soup.find('h1'):
            title = soup.find('h1').get_text().strip()
        elif soup.find('meta', property='og:title'):
            title = soup.find('meta', property='og:title').get('content', '').strip()
        elif soup.title:
            title = soup.title.get_text().strip()

        for element in soup(["script", "style", "nav", "header", "footer", "aside", "form"]):
            element.extract()

        paragraphs = soup.find_all('p')
        text_blocks = []
        for p in paragraphs:
            p_text = p.get_text().strip()
            if len(p_text.split()) >= 6:
                text_blocks.append(p_text)

        article_text = " ".join(text_blocks)
        if not article_text and soup.find('article'):
            article_text = soup.find('article').get_text(separator=' ').strip()

        return {
            "url": url,
            "source_domain": domain,
            "title": title,
            "text": article_text,
            "error": None if article_text else "Unable to parse meaningful article body text."
        }

    def explain_sentence_deception(self, text: str) -> List[Dict[str, Any]]:
        sentences = self.preprocessor.split_sentences(text)
        flagged_sentences = []
        
        for idx, s in enumerate(sentences):
            analysis = self.bias_analyzer.analyze_tone_and_bias(s)
            diag = analysis["diagnostics"]
            metrics = analysis["metrics"]
            
            sentence_risk = (
                (metrics["subjectivity_index"] * 30.0) +
                (metrics["emotional_hyperbole_factor"] * 40.0) +
                (metrics["hedge_uncertainty_ratio"] * 30.0)
            )
            
            reasons = []
            if diag["sensational_word_count"] > 0:
                reasons.append(f"{diag['sensational_word_count']} Sensational word(s)")
            if diag["hedge_phrase_count"] > 0:
                reasons.append(f"{diag['hedge_phrase_count']} Unverified Hedge claim(s)")
            if metrics["subjectivity_index"] > 0.6:
                reasons.append("High Subjective Bias")
                
            if sentence_risk > 25.0 or reasons:
                flagged_sentences.append({
                    "sentence_idx": idx + 1,
                    "sentence_text": s,
                    "risk_score": round(sentence_risk, 1),
                    "reasons": reasons
                })
                
        flagged_sentences.sort(key=lambda x: x["risk_score"], reverse=True)
        return flagged_sentences

    def verify_news(self, text: str, title: str = "", source_url: Optional[str] = None) -> Dict[str, Any]:
        # 1. Stylometrics
        stylometrics = self.stylometric_extractor.extract_features(text, title=title)
        
        # 2. Author Bias & AllSides 2D Coordinates
        bias_report = self.bias_analyzer.analyze_tone_and_bias(text, title=title)
        
        # 3. Logical Fallacy Detection
        fallacy_report = self.fallacy_detector.detect_fallacies(text, title=title)
        
        # 4. Institutional Fact Grounding (WHO, UNESCO, UN, NASA, Wikipedia)
        grounding_report = self.knowledge_engine.analyze_factual_grounding(text, title=title)
        
        # 5. Machine Learning Classification Prediction
        if self.model:
            model_pred = self.model.predict_single(text, title=title)
        else:
            abs_score = bias_report["diagnostics"]["author_bias_score"]
            fake_prob = round(min(1.0, abs_score / 100.0), 4)
            model_pred = {
                "prediction": 1 if fake_prob > 0.5 else 0,
                "verdict": "DECEPTIVE / FABRICATED" if fake_prob > 0.5 else "AUTHENTIC / RELIABLE",
                "credibility_score": round((1.0 - fake_prob) * 100.0, 2),
                "fake_probability": fake_prob,
                "real_probability": round(1.0 - fake_prob, 4)
            }

        # Calibrate credibility with Factuality & Fallacy scores
        if grounding_report["contradictions_count"] > 0:
            model_pred["credibility_score"] = min(model_pred["credibility_score"], 25.0)
            model_pred["verdict"] = "DECEPTIVE / CONTRADICTS FACTS"

        # 6. Flagged Deceptive Sentences
        flagged_sentences = self.explain_sentence_deception(text)

        return {
            "title": title,
            "source_url": source_url,
            "prediction_verdict": model_pred["verdict"],
            "credibility_score": model_pred["credibility_score"],
            "fake_probability": model_pred["fake_probability"],
            "real_probability": model_pred["real_probability"],
            "author_bias": bias_report["diagnostics"],
            "author_bias_metrics": bias_report["metrics"],
            "fallacy_analysis": fallacy_report,
            "knowledge_grounding": grounding_report,
            "readability": {
                "flesch_reading_ease": round(stylometrics["flesch_reading_ease"], 2),
                "fkgl_grade_level": round(stylometrics["fkgl"], 2),
                "gunning_fog": round(stylometrics["gunning_fog"], 2),
                "lexical_diversity_ttr": round(stylometrics["ttr"], 3)
            },
            "flagged_deceptive_sentences": flagged_sentences[:5]
        }
