"""
Preprocessor Module
Handles text normalization, cleaning, regex token filtering, and structure preservation.
"""
import re
import string
import unicodedata
import nltk
from typing import List, Dict, Any, Tuple

# Ensure necessary NLTK corpora are available
for resource in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']:
    try:
        nltk.download(resource, quiet=True)
    except Exception:
        pass

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class TextPreprocessor:
    """
    Dual-mode text preprocessor:
    1. Preserves raw surface statistics (punctuation, capitalization) for stylometric feature extraction.
    2. Generates canonical, normalized tokens for lexical & TF-IDF / embedding models.
    """
    def __init__(self):
        try:
            self.stop_words = set(stopwords.words('english'))
        except Exception:
            self.stop_words = {"the", "a", "an", "in", "on", "of", "and", "is", "it", "to", "for"}
        self.lemmatizer = WordNetLemmatizer()
        
        self.contractions = {
            "ain't": "am not", "aren't": "are not", "can't": "cannot", "can't've": "cannot have",
            "'cause": "because", "could've": "could have", "couldn't": "could not",
            "didn't": "did not", "doesn't": "does not", "don't": "do not", "hadn't": "had not",
            "hasn't": "has not", "haven't": "have not", "he'd": "he would", "he'll": "he will",
            "he's": "he is", "how'd": "how did", "how'll": "how will", "how's": "how is",
            "i'd": "I would", "i'll": "I will", "i'm": "I am", "i've": "I have",
            "isn't": "is not", "it'd": "it would", "it'll": "it will", "it's": "it is",
            "let's": "let us", "might've": "might have", "must've": "must have",
            "shan't": "shall not", "she'd": "she would", "she'll": "she will",
            "she's": "she is", "should've": "should have", "shouldn't": "should not",
            "that's": "that is", "there's": "there is", "they'd": "they would",
            "they'll": "they will", "they're": "they are", "they've": "they have",
            "wasn't": "was not", "we'd": "we would", "we'll": "we will", "we're": "we are",
            "we've": "we have", "weren't": "were not", "what'll": "what will",
            "what're": "what are", "what's": "what is", "what've": "what have",
            "where's": "where is", "who'll": "who will", "who's": "who is",
            "won't": "will not", "would've": "would have", "wouldn't": "would not",
            "you'd": "you would", "you'll": "you will", "you're": "you are",
            "you've": "you have"
        }

    def expand_contractions(self, text: str) -> str:
        """Expands common English contractions."""
        pattern = re.compile(r'\b(' + '|'.join(re.escape(k) for k in self.contractions.keys()) + r')\b', re.IGNORECASE)
        def replace(match):
            key = match.group(0).lower()
            return self.contractions.get(key, match.group(0))
        return pattern.sub(replace, text)

    def normalize_unicode(self, text: str) -> str:
        """Normalizes unicode characters and strip non-printable bytes."""
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')

    def split_sentences(self, text: str) -> List[str]:
        """Splits paragraph text into discrete sentences with fallback."""
        if not text or not text.strip():
            return []
        try:
            return nltk.sent_tokenize(text)
        except Exception:
            # Fallback regex sentence splitter
            sentences = re.split(r'(?<=[.!?])\s+', text)
            return [s.strip() for s in sentences if s.strip()]

    def clean_for_modeling(self, text: str) -> str:
        """
        Produces clean, lemmatized, stopword-filtered string for TF-IDF / Vectorization.
        """
        if not isinstance(text, str) or not text.strip():
            return ""
        
        # 1. Expand contractions
        text = self.expand_contractions(text)
        # 2. Normalize unicode
        text = self.normalize_unicode(text)
        # 3. Strip URLs, emails, and HTML tags
        text = re.sub(r'https?://\S+|www\.\S+', ' ', text)
        text = re.sub(r'\S+@\S+', ' ', text)
        text = re.sub(r'<.*?>', ' ', text)
        # 4. Remove special characters and numeric noise
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # 5. Lowercase and token splitting
        tokens = text.lower().split()
        # 6. Stopwords removal and lemmatization
        cleaned_tokens = [
            self.lemmatizer.lemmatize(word)
            for word in tokens
            if word not in self.stop_words and len(word) > 2
        ]
        return " ".join(cleaned_tokens)

    def extract_raw_tokens(self, text: str) -> List[str]:
        """Extracts word tokens while preserving casing for stylometric evaluation."""
        if not text:
            return []
        return re.findall(r'\b[a-zA-Z0-9_\'-]+\b', text)
