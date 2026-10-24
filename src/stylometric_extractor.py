"""
Stylometric & Readability Feature Extractor Module
Implements formal statistical, lexical diversity, and syntactic surface metrics.
"""
import re
import math
import numpy as np
from collections import Counter
from typing import Dict, List, Any
from src.preprocessor import TextPreprocessor

class StylometricExtractor:
    """
    Extracts high-dimensional stylometric, lexical diversity, and readability features
    for linguistic fingerprinting and misinformation detection.
    """
    def __init__(self):
        self.preprocessor = TextPreprocessor()

    def count_syllables(self, word: str) -> int:
        """
        Estimates syllable count using linguistic heuristics and vowel diphthong clustering.
        """
        word = word.lower().strip()
        if not word:
            return 0
        if len(word) <= 3:
            return 1
        # Remove trailing 'e', 'es', 'ed' if not preceded by certain consonants
        word = re.sub(r'(?:[^laeiouy]|ed|es|e)$', '', word)
        # Find consecutive vowel groups
        syllables = re.findall(r'[aeiouy]{1,2}', word)
        return max(1, len(syllables))

    def extract_features(self, text: str, title: str = "") -> Dict[str, float]:
        """
        Extracts a full dictionary of 18+ mathematical stylometric metrics.
        """
        if not isinstance(text, str) or not text.strip():
            text = "empty text placeholder"
            
        full_text = f"{title}. {text}" if title else text
        sentences = self.preprocessor.split_sentences(full_text)
        n_sentences = max(1, len(sentences))
        
        raw_tokens = self.preprocessor.extract_raw_tokens(full_text)
        n_words = max(1, len(raw_tokens))
        lower_tokens = [w.lower() for w in raw_tokens]
        
        # 1. Lexical Diversity Metrics
        vocab = Counter(lower_tokens)
        vocab_size = len(vocab)
        
        # Type-Token Ratio (TTR)
        ttr = vocab_size / n_words
        # Root TTR (Guiraud's Index)
        root_ttr = vocab_size / math.sqrt(n_words)
        # Hapax Legomena Ratio (Words occurring exactly once)
        hapax_count = sum(1 for _, count in vocab.items() if count == 1)
        hapax_ratio = hapax_count / n_words
        
        # Simpson's Diversity Index (D)
        if n_words > 1:
            simpson_index = sum(c * (c - 1) for c in vocab.values()) / (n_words * (n_words - 1))
        else:
            simpson_index = 0.0

        # 2. Structural & Surface Metrics
        char_count = max(1, len(full_text))
        uppercase_chars = sum(1 for c in full_text if c.isupper())
        uppercase_ratio = uppercase_chars / char_count
        
        # Punctuation Densities
        exclamation_count = full_text.count('!')
        question_count = full_text.count('?')
        quote_count = full_text.count('"') + full_text.count('\'')
        ellipsis_count = len(re.findall(r'\.\.\.', full_text))
        
        exclamation_density = exclamation_count / n_sentences
        question_density = question_count / n_sentences
        quote_density = quote_count / n_sentences
        ellipsis_density = ellipsis_count / n_sentences
        
        # Word Length Statistics
        word_lengths = [len(w) for w in raw_tokens]
        avg_word_length = float(np.mean(word_lengths)) if word_lengths else 0.0
        
        # Sentence Length Statistics
        sentence_lengths = [len(self.preprocessor.extract_raw_tokens(s)) for s in sentences]
        avg_sentence_length = float(np.mean(sentence_lengths)) if sentence_lengths else 0.0
        sentence_len_std = float(np.std(sentence_lengths)) if sentence_lengths else 0.0

        # 3. Readability & Cognitive Complexity Metrics
        syllable_counts = [self.count_syllables(w) for w in raw_tokens]
        total_syllables = sum(syllable_counts)
        complex_words = sum(1 for s in syllable_counts if s >= 3)
        complex_word_ratio = complex_words / n_words
        
        # Flesch Reading Ease (FRE)
        # FRE = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        flesch_reading_ease = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (total_syllables / n_words))
        flesch_reading_ease = max(0.0, min(100.0, flesch_reading_ease))
        
        # Flesch-Kincaid Grade Level (FKGL)
        # FKGL = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        fkgl = (0.39 * avg_sentence_length) + (11.8 * (total_syllables / n_words)) - 15.59
        fkgl = max(0.0, fkgl)
        
        # Gunning Fog Index (GFI)
        # GFI = 0.4 * [ (words/sentences) + 100 * (complex_words/words) ]
        gunning_fog = 0.4 * (avg_sentence_length + (100.0 * complex_word_ratio))
        gunning_fog = max(0.0, gunning_fog)

        # 4. Title Specific Metrics (if title provided)
        title_words = len(self.preprocessor.extract_raw_tokens(title)) if title else 0
        title_all_caps = 1.0 if title and title.isupper() else 0.0
        title_exclamation = 1.0 if title and '!' in title else 0.0

        return {
            "ttr": float(ttr),
            "root_ttr": float(root_ttr),
            "hapax_ratio": float(hapax_ratio),
            "simpson_index": float(simpson_index),
            "uppercase_ratio": float(uppercase_ratio),
            "exclamation_density": float(exclamation_density),
            "question_density": float(question_density),
            "quote_density": float(quote_density),
            "ellipsis_density": float(ellipsis_density),
            "avg_word_length": float(avg_word_length),
            "avg_sentence_length": float(avg_sentence_length),
            "sentence_len_std": float(sentence_len_std),
            "complex_word_ratio": float(complex_word_ratio),
            "flesch_reading_ease": float(flesch_reading_ease),
            "fkgl": float(fkgl),
            "gunning_fog": float(gunning_fog),
            "title_words": float(title_words),
            "title_all_caps": float(title_all_caps),
            "title_exclamation": float(title_exclamation)
        }

    def get_feature_names(self) -> List[str]:
        """Returns ordered list of stylometric feature keys."""
        dummy_features = self.extract_features("Sample text sentence for feature keys initialization.")
        return list(dummy_features.keys())
