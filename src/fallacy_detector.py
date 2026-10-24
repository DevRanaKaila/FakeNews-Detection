import re
from typing import Dict, List, Any
from src.preprocessor import TextPreprocessor

class FallacyDetector:
    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.fear_patterns = [
            r'\b(terrifying|catastrophe|apocalypse|doomsday|imminent disaster|deadly threat|pure panic|frightening truth|deadly secret|run for your lives)\b',
            r'\b(nightmare scenario|total annihilation|fatal consequences|deadly danger|destruction is near)\b'
        ]
        self.adhominem_patterns = [
            r'\b(corrupt|traitor|evil globalists|scumbag|imbecile|bought and paid for|shill|puppet|hypocrite|disgraced|clueless idiots|enemies of the people)\b',
            r'\b(brainwashed|scammer|criminal cabal|crooked|pathological liar)\b'
        ]
        self.vague_authority_patterns = [
            r'\b(insiders (say|claim|reveal)|secret sources (say|confirm)|whistleblowers (claim|report)|top scientists secretly|anonymous officials|experts are terrified|doctors don\'t want you to know|unnamed insiders)\b',
            r'\b(many people are saying|everyone knows that|studies secretly prove|confidential memos reveal)\b'
        ]
        self.false_dilemma_patterns = [
            r'\b(either you are with us or|if you don\'t believe this you are|the only choice is|you must choose between|there is no alternative but)\b',
            r'\b(wake up or remain blind|accept this truth or suffer)\b'
        ]
        self.cherry_picking_patterns = [
            r'\b(this one case proves|i know a person who|my cousin tried this and|one single example shows|ignoring all other studies|forget what official data says)\b'
        ]
        self.generalization_patterns = [
            r'\b(all politicians are|every single doctor is|the entire media is lying|nobody can be trusted|always|never|100% of the time|without exception everyone)\b'
        ]
        self.conspiracy_patterns = [
            r'\b(secret plot|hidden agenda|deep state|cabal|cover-up|illuminati|shadow government|they are hiding the cure|deliberately poisoned|planned destruction)\b'
        ]
        self.urgency_patterns = [
            r'\b(share before (it gets )?deleted|banned video|what they won\'t show you|act now before it\'s too late|urgent warning|they are trying to censor this)\b'
        ]

    def detect_fallacies(self, text: str, title: str = "") -> Dict[str, Any]:
        full_text = f"{title}. {text}" if title else text
        sentences = self.preprocessor.split_sentences(full_text)
        n_sentences = max(1, len(sentences))
        
        detected_fallacies = []
        fallacy_counts = {
            "appeal_to_fear": 0, "ad_hominem": 0, "vague_authority": 0,
            "false_dilemma": 0, "cherry_picking": 0, "hasty_generalization": 0,
            "conspiracy_framing": 0, "false_urgency": 0
        }

        for idx, sentence in enumerate(sentences):
            s_lower = sentence.lower()
            
            for p in self.fear_patterns:
                matches = re.findall(p, s_lower)
                if matches:
                    fallacy_counts["appeal_to_fear"] += len(matches)
                    cue = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    detected_fallacies.append({
                        "type": "Appeal to Fear / Catastrophizing",
                        "severity": "High",
                        "sentence_idx": idx + 1,
                        "sentence": sentence,
                        "explanation": "Uses emotionally charged existential threats or catastrophic panic instead of objective evidence.",
                        "matched_cue": cue
                    })
                    break

            for p in self.adhominem_patterns:
                matches = re.findall(p, s_lower)
                if matches:
                    fallacy_counts["ad_hominem"] += len(matches)
                    cue = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    detected_fallacies.append({
                        "type": "Ad Hominem / Smear Attack",
                        "severity": "High",
                        "sentence_idx": idx + 1,
                        "sentence": sentence,
                        "explanation": "Attacks the moral character or motives of individuals rather than addressing the substantive facts.",
                        "matched_cue": cue
                    })
                    break

            for p in self.vague_authority_patterns:
                matches = re.findall(p, s_lower)
                if matches:
                    fallacy_counts["vague_authority"] += len(matches)
                    cue = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    detected_fallacies.append({
                        "type": "Appeal to Vague / Phantom Authority",
                        "severity": "Moderate",
                        "sentence_idx": idx + 1,
                        "sentence": sentence,
                        "explanation": "Attributes critical claims to unsubstantiated anonymous insiders or unnamed 'experts' without verifiable credentials.",
                        "matched_cue": cue
                    })
                    break

            for p in self.false_dilemma_patterns:
                matches = re.findall(p, s_lower)
                if matches:
                    fallacy_counts["false_dilemma"] += len(matches)
                    cue = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    detected_fallacies.append({
                        "type": "False Dilemma (Black-and-White Framing)",
                        "severity": "Moderate",
                        "sentence_idx": idx + 1,
                        "sentence": sentence,
                        "explanation": "Forces an artificial binary choice while ignoring nuanced middle-ground solutions or legitimate complexities.",
                        "matched_cue": cue
                    })
                    break

            for p in self.cherry_picking_patterns:
                matches = re.findall(p, s_lower)
                if matches:
                    fallacy_counts["cherry_picking"] += len(matches)
                    cue = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    detected_fallacies.append({
                        "type": "Cherry-Picking / Anecdotal Fallacy",
                        "severity": "Moderate",
                        "sentence_idx": idx + 1,
                        "sentence": sentence,
                        "explanation": "Cites isolated personal anecdotes while disregarding comprehensive peer-reviewed data and statistical consensus.",
                        "matched_cue": cue
                    })
                    break

            for p in self.generalization_patterns:
                matches = re.findall(p, s_lower)
                if matches:
                    fallacy_counts["hasty_generalization"] += len(matches)
                    cue = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    detected_fallacies.append({
                        "type": "Hasty Generalization / Sweeping Claim",
                        "severity": "Low",
                        "sentence_idx": idx + 1,
                        "sentence": sentence,
                        "explanation": "Makes absolute universal generalizations about entire professions or populations without sufficient proof.",
                        "matched_cue": cue
                    })
                    break

            for p in self.conspiracy_patterns:
                matches = re.findall(p, s_lower)
                if matches:
                    fallacy_counts["conspiracy_framing"] += len(matches)
                    cue = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    detected_fallacies.append({
                        "type": "Conspiracy / Secret Cabal Framing",
                        "severity": "Critical",
                        "sentence_idx": idx + 1,
                        "sentence": sentence,
                        "explanation": "Alleges complex covert malice by coordinated entities to explain socio-scientific events without falsifiable evidence.",
                        "matched_cue": cue
                    })
                    break

            for p in self.urgency_patterns:
                matches = re.findall(p, s_lower)
                if matches:
                    fallacy_counts["false_urgency"] += len(matches)
                    cue = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    detected_fallacies.append({
                        "type": "Manufactured Urgency & Censorship Stance",
                        "severity": "Moderate",
                        "sentence_idx": idx + 1,
                        "sentence": sentence,
                        "explanation": "Fabricates artificial scarcity or censorship panic ('share before deleted') to bypass critical evaluation.",
                        "matched_cue": cue
                    })
                    break

        total_fallacies = sum(fallacy_counts.values())
        fallacy_density = min(1.0, total_fallacies / n_sentences)
        
        weighted_severity = (
            (fallacy_counts["conspiracy_framing"] * 25.0) +
            (fallacy_counts["appeal_to_fear"] * 20.0) +
            (fallacy_counts["ad_hominem"] * 20.0) +
            (fallacy_counts["vague_authority"] * 15.0) +
            (fallacy_counts["false_dilemma"] * 10.0) +
            (fallacy_counts["false_urgency"] * 10.0)
        )
        fallacy_index = min(100.0, weighted_severity)

        return {
            "total_fallacies_detected": total_fallacies,
            "fallacy_density": round(fallacy_density, 3),
            "fallacy_severity_index": round(fallacy_index, 1),
            "breakdown": fallacy_counts,
            "detected_instances": detected_fallacies[:8]
        }
