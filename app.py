import os
import sys
import json
from flask import Flask, render_template, request, jsonify

from src.live_pipeline import LiveVerificationPipeline
from src.live_feed_manager import LiveFeedManager

app = Flask(__name__)

# Initialize pipeline with trained hybrid stacking model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "data", "processed", "best_hybrid_model.joblib")
if os.path.exists(MODEL_PATH):
    print(f"Loading trained hybrid model from {MODEL_PATH}...")
    pipeline = LiveVerificationPipeline(model_path=MODEL_PATH)
else:
    print("Warning: Trained model artifact not found. Initializing heuristic pipeline.")
    pipeline = LiveVerificationPipeline()

feed_manager = LiveFeedManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Evidence & Framing Auditor Telemetry Engine",
        "model_loaded": os.path.exists(MODEL_PATH)
    }), 200

@app.route('/api/verify-text', methods=['POST'])
def verify_text():
    data = request.get_json(force=True)
    text = data.get('text', '').strip()
    title = data.get('title', '').strip()

    if not text:
        return jsonify({"error": "Article body text cannot be empty."}), 400

    try:
        report = pipeline.verify_news(text, title=title)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": f"Verification failed: {str(e)}"}), 500

@app.route('/api/verify-url', methods=['POST'])
def verify_url():
    data = request.get_json(force=True)
    url = data.get('url', '').strip()

    if not url:
        return jsonify({"error": "URL parameter is required."}), 400

    scraped = pipeline.fetch_article_from_url(url)
    if scraped.get("error"):
        return jsonify({"error": scraped["error"]}), 400

    try:
        report = pipeline.verify_news(scraped["text"], title=scraped["title"], source_url=url)
        report["source_domain"] = scraped["source_domain"]
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": f"Verification failed: {str(e)}"}), 500

@app.route('/api/samples', methods=['GET'])
def get_samples():
    """
    Returns dynamically fetched real-world presets that change with live internet events:
    2 Authentic Neutral, 1 Clickbait, 1 Conspiracy, 1 Pseudoscience, 2 Biased (Left & Right)
    """
    presets = feed_manager.get_dynamic_curated_presets()
    return jsonify({"samples": presets}), 200

@app.route('/api/benchmark-stats', methods=['GET'])
def get_benchmark_stats():
    summary_path = os.path.join(os.path.dirname(__file__), "data", "processed", "benchmark_summary.json")
    if os.path.exists(summary_path):
        with open(summary_path, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        clean_benchmarks = []
        raw_list = stats if isinstance(stats, list) else stats.get('benchmarks', [])
        for item in raw_list:
            clean_benchmarks.append({
                "model_name": item.get("model_name", "unknown"),
                "display_name": item.get("display_name", item.get("model_name", "")),
                "accuracy": item.get("accuracy", 0.0),
                "precision": item.get("precision", 0.0),
                "recall": item.get("recall", 0.0),
                "f1_score": item.get("f1_score", 0.0),
                "macro_f1": item.get("macro_f1", 0.0),
                "roc_auc": item.get("roc_auc", 0.0),
                "train_time_sec": item.get("train_time_sec", 0.0)
            })
        return jsonify({"benchmarks": clean_benchmarks}), 200
    return jsonify({"benchmarks": []}), 200

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    print("=" * 70)
    print(f"   Starting Sula Truth & Bias Telemetry Web Server")
    print(f"   Access Dashboard at: http://127.0.0.1:{port}")
    print("=" * 70)
    app.run(host='127.0.0.1', port=port, debug=False)
