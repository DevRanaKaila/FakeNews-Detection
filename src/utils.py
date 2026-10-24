"""
Utility Module
Provides benchmark dataset generators, metric formatters, and publication-ready plot generation.
"""
import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Any, Tuple

def generate_benchmark_dataset(num_samples: int = 1200) -> pd.DataFrame:
    np.random.seed(42)
    real_topics = [
        ("NASA James Webb Telescope Discovers Distant Galaxy Cluster",
         "Astronomers utilizing the James Webb Space Telescope have identified a high-redshift galaxy cluster dating back 13 billion years. The spectroscopic data confirmed standard cosmological models with unprecedented resolution and minimal optical distortion. Peer-reviewed findings were published in the Astrophysical Journal following rigorous multi-institution validation.",
         0),
        ("Federal Reserve Announces Interest Rate Decision Following Inflation Report",
         "The Federal Reserve announced a 25 basis point adjustment following quarterly economic indicators. Officials noted that core consumer price inflation moderated steadily while labor market participation remained resilient across key industrial sectors according to official government economic data.",
         0),
        ("Global Climate Summit Concludes with Multi-Nation Renewable Energy Accord",
         "Representatives from 85 nations ratified an international agreement to increase solar and offshore wind capacity by 2030. Independent energy policy analysts noted that the binding treaty includes structured monitoring mechanisms and financial allocations for developing infrastructure.",
         0),
        ("Medical Researchers Conclude Phase 3 Clinical Trial for Novel Oncology Therapy",
         "A double-blind randomized clinical trial involving 1,400 oncology patients demonstrated statistically significant improvements in progression-free survival. The oncology study, conducted across twelve medical centers, reported a 34 percent reduction in disease progression compared to standard regimens.",
         0),
        ("European Union Approves Comprehensive AI Regulatory Compliance Framework",
         "The European Parliament has formally voted to adopt a risk-based artificial intelligence governance framework. The legislation establishes strict transparency requirements for foundation models and prohibits high-risk biometric categorizations in public spaces.",
         0)
    ]
    
    fake_topics = [
        ("SHOCKING: Secret Government Underground Base Exposed by Whistleblower!",
         "You won't believe what insiders are secretly claiming! A bombshell report reveals that elite conspirators have allegedly hidden alien technology in subterranean vaults. Mainstream media is totally terrified to report this insane truth! Sources claim disaster is imminent and politicians are panicking!",
         1),
        ("MIRACLE CURE: Doctors Hate This Simple Household Trick That Cures All Illness!",
         "Big Pharma is completely furious! Whistleblowers have reportedly leaked a bizarre 100% natural cure that utterly destroys cancer and diabetes overnight without any medicine. Millions of people are using this shocking secret remedy while corrupt officials panic and scramble!",
         1),
        ("OUTRAGEOUS SCANDAL: Top Politician Caught in Massive Treasonous Scheme!",
         "Bombshell evidence has allegedly surfaced exposing that corrupt treasonous officials secretly accepted billions to destroy our nation's economy! Insiders claim unconfirmed documents prove a catastrophic conspiracy that the radical mainstream media refuses to cover!",
         1),
        ("ALERT: Space Agency Hiding Incoming Catastrophic Asteroid Collision Next Week!",
         "Insane leaked memos allegedly prove astronomers are in pure panic over a terrifying celestial body heading straight for Earth! Secret sources claim governments are silently building bunkers while deceiving the public with fake peaceful telescope pictures!",
         1),
        ("EXPOSED: Secret Mind-Control Microchips Discovered in Public Drinking Water!",
         "Shocking undercover footage purportedly reveals dangerous chemical additives designed to radically alter human DNA. Whistleblowers allegedly report that corrupt globalists are totally celebrating this horrific plot. Share this viral truth before it gets deleted!",
         1)
    ]
    
    records = []
    for i in range(num_samples):
        is_fake = (i % 2 == 1)
        base_pool = fake_topics if is_fake else real_topics
        title_base, text_base, label = base_pool[i % len(base_pool)]
        prefix = f"Update {i+1}: " if i >= 10 else ""
        title = f"{prefix}{title_base}"
        text = f"{text_base} (Report Reference ID: {1000 + i}). Additional coverage on ongoing developments confirms these perspectives."
        records.append({"id": i, "title": title, "text": text, "label": label})
        
    return pd.DataFrame(records)

def plot_confusion_matrix(cm: List[List[int]], output_path: str, model_name: str = "Proposed Hybrid Model"):
    plt.figure(figsize=(6, 5), dpi=300)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Predicted Real", "Predicted Fake"],
                yticklabels=["Actual Real", "Actual Fake"],
                annot_kws={"size": 13, "weight": "bold"})
    plt.title(f"Confusion Matrix: {model_name}", fontsize=12, fontweight="bold", pad=12)
    plt.ylabel("True Class", fontsize=11, fontweight="semibold")
    plt.xlabel("Predicted Class", fontsize=11, fontweight="semibold")
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_model_comparison_bar(results: List[Dict[str, Any]], output_path: str):
    df = pd.DataFrame(results)
    metrics = ["accuracy", "precision", "recall", "f1_score", "roc_auc"]
    
    plt.figure(figsize=(10, 5.5), dpi=300)
    x = np.arange(len(df))
    width = 0.15
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]
    for i, m in enumerate(metrics):
        plt.bar(x + (i * width), df[m], width=width, label=m.upper().replace("_", "-"), color=colors[i])
        
    plt.xlabel("Evaluated Models", fontsize=11, fontweight="bold")
    plt.ylabel("Score (0.0 to 1.0)", fontsize=11, fontweight="bold")
    plt.title("Performance Comparison across Evaluated NLP & Hybrid Architectures", fontsize=12, fontweight="bold", pad=12)
    plt.xticks(x + (width * 2), df["model_name"], rotation=15, ha="right", fontsize=9, fontweight="semibold")
    plt.ylim(0.70, 1.02)
    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.legend(loc="lower right", frameon=True)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()

def plot_author_bias_radar(bias_metrics: Dict[str, float], output_path: str, title: str = "Author Bias Profile"):
    categories = [
        "Subjectivity\n(S_idx)",
        "Sensationalism\n(EHF)",
        "Affective Skew\n(Delta_pol)",
        "Hedging\n(HUR)",
        "Clickbait Gap\n(CDM)"
    ]
    values = [
        bias_metrics.get("subjectivity_index", 0.0),
        bias_metrics.get("emotional_hyperbole_factor", 0.0),
        bias_metrics.get("affective_polarization_density", 0.0),
        bias_metrics.get("hedge_uncertainty_ratio", 0.0),
        bias_metrics.get("clickbait_discrepancy_metric", 0.0)
    ]
    values += values[:1]
    angles = [n / float(len(categories)) * 2 * np.pi for n in range(len(categories))]
    angles += angles[:1]
    
    plt.figure(figsize=(6, 6), dpi=300)
    ax = plt.subplot(111, polar=True)
    plt.xticks(angles[:-1], categories, size=10, fontweight="semibold")
    ax.set_rlabel_position(25)
    plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=8)
    plt.ylim(0, 1.0)
    
    ax.plot(angles, values, color="#d62728", linewidth=2, linestyle="solid")
    ax.fill(angles, values, color="#d62728", alpha=0.3)
    plt.title(f"{title}", size=12, fontweight="bold", pad=20)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300)
    plt.close()