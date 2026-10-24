import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from src.preprocessor import TextPreprocessor
from src.stylometric_extractor import StylometricExtractor
from src.author_bias_analyzer import AuthorBiasAnalyzer
from src.models import HybridFakeNewsClassifier
from src.live_pipeline import LiveVerificationPipeline

def test_preprocessor():
    p = TextPreprocessor()
    text = "Don't click https://malicious.com! It's a 100% scam."
    cleaned = p.clean_for_modeling(text)
    assert "https" not in cleaned
    assert "not" in cleaned or "click" in cleaned
    
    sentences = p.split_sentences("First sentence. Second sentence! Third one?")
    assert len(sentences) == 3

def test_stylometric_extractor():
    s = StylometricExtractor()
    text = "This is a formal and rigorous scientific evaluation of linguistic structures."
    features = s.extract_features(text, title="Scientific Title")
    
    assert "flesch_reading_ease" in features
    assert "ttr" in features
    assert "gunning_fog" in features
    assert 0.0 <= features["ttr"] <= 1.0

def test_author_bias_analyzer():
    b = AuthorBiasAnalyzer()
    neutral_text = "The quarterly financial report was published on Monday with official figures."
    neutral_res = b.analyze_tone_and_bias(neutral_text)
    
    sensational_text = "SHOCKING BOMBSHELL: Insiders allegedly expose a terrifying secret conspiracy that completely destroys everything!"
    sensational_res = b.analyze_tone_and_bias(sensational_text, title="OUTRAGEOUS SCANDAL!")
    
    assert neutral_res["diagnostics"]["author_bias_score"] < sensational_res["diagnostics"]["author_bias_score"]
    assert sensational_res["diagnostics"]["sensational_word_count"] >= 2
    assert "metrics" in sensational_res

def test_hybrid_model_training_and_inference():
    texts = [
        "NASA announces satellite launch following successful engineering trials.",
        "Bank of England adjusts baseline interest rate by 25 basis points.",
        "Medical researchers confirm clinical efficacy in randomized oncology trial.",
        "European Union updates regulatory standards on renewable infrastructure.",
        "SHOCKING: Secret alien technology leaked by furious whistleblower!",
        "MIRACLE CURE: Doctors are terrified of this one simple secret trick!",
        "BOMBSHELL: Corrupt globalists allegedly conspire to destroy public health!",
        "ALERT: Asteroid secretly heading towards Earth while governments hide!"
    ]
    labels = [0, 0, 0, 0, 1, 1, 1, 1]
    titles = ["NASA Launch", "Bank Policy", "Medical Trial", "EU Energy", "Alien Secret", "Miracle Cure", "Conspiracy Leaked", "Asteroid Alert"]
    
    clf = HybridFakeNewsClassifier(model_type="hybrid_stacking")
    clf.train(texts, labels, titles=titles)
    
    pred_res = clf.predict_single(texts[0], title=titles[0])
    assert pred_res["prediction"] in [0, 1]
    assert 0.0 <= pred_res["credibility_score"] <= 100.0

def test_live_pipeline_verification():
    pipeline = LiveVerificationPipeline()
    report = pipeline.verify_news(
        "A regular verified news article discussing international diplomatic trade agreements.",
        title="Diplomatic Summit"
    )
    assert "prediction_verdict" in report
    assert "author_bias" in report
    assert "readability" in report
