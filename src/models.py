"""
Machine Learning & Hybrid Fusion Models Module
Implements Baseline Classifiers, XGBoost, and the Proposed Hybrid Stylometric-Semantic Fusion Architecture.
"""
import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, StackingClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score, confusion_matrix
import xgboost as xgb

from src.preprocessor import TextPreprocessor
from src.stylometric_extractor import StylometricExtractor
from src.author_bias_analyzer import AuthorBiasAnalyzer

class FeaturePipeline:
    """
    Unified extractor combining Text Cleaning, TF-IDF Vectorization,
    Stylometrics, and Author Bias metrics into a fused feature matrix.
    """
    def __init__(self, max_tfidf_features: int = 5000):
        self.preprocessor = TextPreprocessor()
        self.stylometric_extractor = StylometricExtractor()
        self.bias_analyzer = AuthorBiasAnalyzer()
        
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=max_tfidf_features,
            ngram_range=(1, 2),
            sublinear_tf=True,
            strip_accents='unicode'
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        
        self.dense_feature_names = (
            self.stylometric_extractor.get_feature_names() +
            self.bias_analyzer.get_feature_names()
        )

    def extract_dense_features(self, texts: List[str], titles: Optional[List[str]] = None) -> np.ndarray:
        """Extracts numerical matrix of stylometric and author bias features."""
        if titles is None:
            titles = ["" for _ in range(len(texts))]
            
        dense_rows = []
        for text, title in zip(texts, titles):
            sty_dict = self.stylometric_extractor.extract_features(text, title=title)
            bias_dict = self.bias_analyzer.analyze_tone_and_bias(text, title=title)["metrics"]
            
            row = [sty_dict[k] for k in self.stylometric_extractor.get_feature_names()] + \
                  [bias_dict[k] for k in self.bias_analyzer.get_feature_names()]
            dense_rows.append(row)
            
        return np.array(dense_rows, dtype=np.float32)

    def fit_transform(self, texts: List[str], titles: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Fits TF-IDF and Scaler on training data and returns fused feature representation."""
        cleaned_texts = [self.preprocessor.clean_for_modeling(t) for t in texts]
        
        # 1. TF-IDF Semantic features
        X_tfidf = self.tfidf_vectorizer.fit_transform(cleaned_texts).toarray()
        
        # 2. Dense Stylometric & Bias features
        X_dense_raw = self.extract_dense_features(texts, titles)
        X_dense_scaled = self.scaler.fit_transform(X_dense_raw)
        
        # 3. Fused Concatenation
        X_fused = np.hstack((X_tfidf, X_dense_scaled))
        self.is_fitted = True
        
        return X_tfidf, X_dense_scaled, X_fused

    def transform(self, texts: List[str], titles: Optional[List[str]] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Transforms new unseen texts using fitted vectorizer and scaler."""
        if not self.is_fitted:
            raise ValueError("FeaturePipeline has not been fitted yet!")
            
        cleaned_texts = [self.preprocessor.clean_for_modeling(t) for t in texts]
        X_tfidf = self.tfidf_vectorizer.transform(cleaned_texts).toarray()
        X_dense_raw = self.extract_dense_features(texts, titles)
        X_dense_scaled = self.scaler.transform(X_dense_raw)
        X_fused = np.hstack((X_tfidf, X_dense_scaled))
        
        return X_tfidf, X_dense_scaled, X_fused


class HybridFakeNewsClassifier:
    """
    Proposed Novel Multi-Branch Architecture:
    Combines high-capacity XGBoost and Calibrated Stacking meta-estimator
    over semantic TF-IDF and engineered psycholinguistic features.
    """
    def __init__(self, model_type: str = "hybrid_stacking"):
        self.model_type = model_type
        self.pipeline = FeaturePipeline(max_tfidf_features=4000)
        
        if model_type == "logistic_baseline":
            self.clf = LogisticRegression(max_iter=1000, C=1.5, random_state=42)
        elif model_type == "random_forest":
            self.clf = RandomForestClassifier(n_estimators=150, max_depth=20, random_state=42, n_jobs=-1)
        elif model_type == "xgboost":
            self.clf = xgb.XGBClassifier(
                n_estimators=200, max_depth=6, learning_rate=0.08,
                subsample=0.8, colsample_bytree=0.8, random_state=42, n_jobs=-1
            )
        elif model_type == "hybrid_stacking":
            base_estimators = [
                ('lr', LogisticRegression(max_iter=500, C=2.0, random_state=42)),
                ('xgb', xgb.XGBClassifier(n_estimators=120, max_depth=5, learning_rate=0.1, random_state=42, n_jobs=-1)),
                ('rf', RandomForestClassifier(n_estimators=80, max_depth=15, random_state=42, n_jobs=-1))
            ]
            self.clf = StackingClassifier(
                estimators=base_estimators,
                final_estimator=LogisticRegression(),
                cv=3,
                n_jobs=-1
            )
        else:
            raise ValueError(f"Unknown model_type: {model_type}")

    def train(self, texts: List[str], labels: List[int], titles: Optional[List[str]] = None) -> Dict[str, float]:
        """Trains feature pipeline and classifier model."""
        X_tfidf, X_dense, X_fused = self.pipeline.fit_transform(texts, titles)
        
        # If baseline, train only on TF-IDF; if hybrid/tree, train on full fused matrix
        if self.model_type == "logistic_baseline":
            X_train = X_tfidf
        else:
            X_train = X_fused
            
        self.clf.fit(X_train, labels)
        preds = self.clf.predict(X_train)
        acc = accuracy_score(labels, preds)
        return {"training_accuracy": float(acc)}

    def evaluate(self, texts: List[str], labels: List[int], titles: Optional[List[str]] = None) -> Dict[str, Any]:
        """Comprehensive evaluation producing standard IEEE metrics."""
        X_tfidf, X_dense, X_fused = self.pipeline.transform(texts, titles)
        X_test = X_tfidf if self.model_type == "logistic_baseline" else X_fused
        
        preds = self.clf.predict(X_test)
        probs = self.clf.predict_proba(X_test)[:, 1] if hasattr(self.clf, "predict_proba") else preds
        
        acc = accuracy_score(labels, preds)
        prec, rec, f1, _ = precision_recall_fscore_support(labels, preds, average='binary', zero_division=0)
        macro_prec, macro_rec, macro_f1, _ = precision_recall_fscore_support(labels, preds, average='macro', zero_division=0)
        try:
            auc = roc_auc_score(labels, probs)
        except Exception:
            auc = 0.0
            
        cm = confusion_matrix(labels, preds).tolist()
        
        return {
            "model_name": self.model_type,
            "accuracy": round(float(acc), 4),
            "precision": round(float(prec), 4),
            "recall": round(float(rec), 4),
            "f1_score": round(float(f1), 4),
            "macro_f1": round(float(macro_f1), 4),
            "roc_auc": round(float(auc), 4),
            "confusion_matrix": cm,
            "predictions": preds.tolist(),
            "probabilities": probs.tolist()
        }

    def predict_single(self, text: str, title: str = "") -> Dict[str, Any]:
        """Inference for a single article returning prediction, probability, and credibility score."""
        X_tfidf, X_dense, X_fused = self.pipeline.transform([text], [title])
        X_input = X_tfidf if self.model_type == "logistic_baseline" else X_fused
        
        pred = int(self.clf.predict(X_input)[0])
        prob_fake = float(self.clf.predict_proba(X_input)[0][1])
        prob_real = 1.0 - prob_fake
        
        # Credibility Score: 0% (Definitely Fake) to 100% (High Confidence Authentic)
        credibility_score = round(prob_real * 100.0, 2)
        verdict = "REAL / RELIABLE" if pred == 0 else "FAKE / MISINFORMATION"
        
        return {
            "prediction": pred,
            "verdict": verdict,
            "credibility_score": credibility_score,
            "fake_probability": round(prob_fake, 4),
            "real_probability": round(prob_real, 4)
        }

    def save(self, filepath: str):
        """Serializes trained pipeline and model to disk."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "clf": self.clf, "model_type": self.model_type}, filepath)

    @classmethod
    def load(cls, filepath: str) -> "HybridFakeNewsClassifier":
        """Loads trained pipeline and model from disk."""
        data = joblib.load(filepath)
        instance = cls(model_type=data["model_type"])
        instance.pipeline = data["pipeline"]
        instance.clf = data["clf"]
        return instance
