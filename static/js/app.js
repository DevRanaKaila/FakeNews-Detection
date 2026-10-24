// Sula Truth Telemetry - Interactive JS Engine

document.addEventListener('DOMContentLoaded', () => {
    // 1. Tab Navigation
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            tabButtons.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const targetId = btn.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');

            if (targetId === 'tab-samples') {
                loadSamples();
            } else if (targetId === 'tab-benchmarks') {
                loadBenchmarks();
            }
        });
    });

    // 2. Forms Handling
    const formText = document.getElementById('form-verify-text');
    const formUrl = document.getElementById('form-verify-url');
    const btnRefreshPresets = document.getElementById('btn-refresh-presets');

    if (btnRefreshPresets) {
        btnRefreshPresets.addEventListener('click', () => {
            loadSamples(true);
        });
    }

    formText.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = document.getElementById('input-title').value.trim();
        const text = document.getElementById('input-body').value.trim();
        if (!text) return;
        await submitVerification('/api/verify-text', { title, text });
    });

    formUrl.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = document.getElementById('input-url').value.trim();
        if (!url) return;
        await submitVerification('/api/verify-url', { url });
    });

    // 3. API Submission & Verification Engine
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');
    const reportView = document.getElementById('report-view');

    async function submitVerification(endpoint, payload) {
        emptyState.classList.add('hidden');
        reportView.classList.add('hidden');
        loadingState.classList.remove('hidden');

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const data = await response.json();
            if (data.error) {
                alert(`Error: ${data.error}`);
                loadingState.classList.add('hidden');
                emptyState.classList.remove('hidden');
                return;
            }
            renderReport(data);
        } catch (err) {
            alert(`Network or Server Error: ${err.message}`);
            loadingState.classList.add('hidden');
            emptyState.classList.remove('hidden');
        }
    }

    // 4. Render Telemetry Results
    function renderReport(report) {
        loadingState.classList.add('hidden');
        reportView.classList.remove('hidden');

        // Headline & Verdict
        const dispTitle = document.getElementById('disp-title');
        dispTitle.textContent = report.title || "Analyzed Article Content";

        const badge = document.getElementById('badge-verdict');
        const scoreCircle = document.getElementById('score-circle');
        const dispScore = document.getElementById('disp-score');

        const isReal = report.prediction_verdict.includes('AUTHENTIC') || report.prediction_verdict.includes('RELIABLE');
        badge.textContent = report.prediction_verdict;
        badge.className = isReal ? 'verdict-badge badge-real' : 'verdict-badge badge-fake';

        dispScore.textContent = `${report.credibility_score}%`;
        if (isReal) {
            scoreCircle.classList.remove('fake');
        } else {
            scoreCircle.classList.add('fake');
        }

        // --- Stated Claim-by-Claim Line Verification ---
        const grounding = report.knowledge_grounding;
        const factStatus = document.getElementById('disp-fact-status');
        factStatus.textContent = grounding.factual_status;
        if (grounding.status_color === 'crimson') {
            factStatus.className = 'tag-status alert';
        } else if (grounding.status_color === 'amber') {
            factStatus.className = 'tag-status warn';
        } else {
            factStatus.className = 'tag-status';
        }

        const claimTableContainer = document.getElementById('claim-verification-table-container');
        claimTableContainer.innerHTML = '';

        const verifications = grounding.line_by_line_verifications || [];
        if (verifications.length > 0) {
            verifications.forEach(v => {
                const card = document.createElement('div');
                const isRefuted = v.verdict.includes('REFUTED');
                const isHalf = v.verdict.includes('HALF') || v.verdict.includes('VAGUE');
                
                card.className = `claim-card ${isRefuted ? 'refuted' : (isHalf ? 'half-truth' : 'supported')}`;
                card.innerHTML = `
                    <div class="claim-header">
                        <span class="claim-line-tag">Line #${v.line_number} • Topic: ${v.topic}</span>
                        <span class="claim-badge ${isRefuted ? 'badge-refuted' : (isHalf ? 'badge-half-truth' : 'badge-supported')}">
                            ${isRefuted ? '✖ REFUTED' : (isHalf ? '⚠️ HALF-TRUTH / VAGUE' : '✓ SUPPORTED')} [${v.badge_label}]
                        </span>
                    </div>
                    <div class="claim-text">"${v.stated_line}"</div>
                    <div class="claim-evidence">
                        <strong>Institutional Evidence & Data Point:</strong> ${v.evidence_datapoint}
                    </div>
                    <div class="claim-source">
                        Authoritative Source: <a href="${v.source_url}" target="_blank">${v.source_name} ↗</a>
                    </div>
                `;
                claimTableContainer.appendChild(card);
            });
        }

        // Wikipedia Grounding Card
        const wikiCard = document.getElementById('wiki-grounding-card');
        if (grounding.wikipedia_grounding) {
            document.getElementById('wiki-title').textContent = `Wikipedia: ${grounding.wikipedia_grounding.title}`;
            document.getElementById('wiki-summary').textContent = grounding.wikipedia_grounding.summary;
            document.getElementById('wiki-link').href = grounding.wikipedia_grounding.url;
            wikiCard.classList.remove('hidden');
        } else {
            wikiCard.classList.add('hidden');
        }

        // --- Target-Stance & AllSides 2D Chart Pin Positioning ---
        const bias = report.author_bias;
        const tagAllSides = document.getElementById('disp-allsides-rating');
        tagAllSides.textContent = bias.allsides_rating;
        tagAllSides.style.color = bias.allsides_color;

        const stanceSummary = document.getElementById('disp-stance-summary');
        stanceSummary.innerHTML = `<strong>Identified Target Stance:</strong> ${bias.stance_summary || 'Objective Factual Analysis'}`;

        // Map X: -1.0 -> 5%, 0.0 -> 50%, +1.0 -> 95%
        const pinX = 50 + (bias.ideological_lean_x * 45);
        // Map Y: Factuality 1.0 -> 15% (top), 0.0 -> 85% (bottom)
        const pinY = 85 - (bias.factuality_y * 70);

        const pin = document.getElementById('chart-pin');
        pin.style.left = `${Math.max(5, Math.min(95, pinX))}%`;
        pin.style.top = `${Math.max(10, Math.min(90, pinY))}%`;
        document.getElementById('pin-label').textContent = `${bias.allsides_rating} (${bias.author_bias_score}/100)`;

        // --- Logical Fallacy Cards ---
        const fallacyContainer = document.getElementById('fallacy-cards-container');
        fallacyContainer.innerHTML = '';
        const fallacyData = report.fallacy_analysis;

        const fallacyTag = document.getElementById('disp-fallacy-index');
        fallacyTag.textContent = `${fallacyData.total_fallacies_detected} Fallacies Detected (Severity: ${fallacyData.fallacy_severity_index}/100)`;
        if (fallacyData.total_fallacies_detected > 0) {
            fallacyTag.className = 'tag-status alert';
            fallacyData.detected_instances.forEach(f => {
                const fCard = document.createElement('div');
                fCard.className = 'fallacy-card';
                fCard.innerHTML = `
                    <div class="fallacy-top">
                        <span class="fallacy-name">🚨 ${f.type}</span>
                        <span class="fallacy-sev">${f.severity} Severity</span>
                    </div>
                    <p class="fallacy-text">"${f.sentence}"</p>
                    <p class="fallacy-desc"><strong>Linguistic Explanation:</strong> ${f.explanation}</p>
                `;
                fallacyContainer.appendChild(fCard);
            });
        } else {
            fallacyTag.className = 'tag-status';
            fallacyContainer.innerHTML = '<p style="font-size:0.85rem; color:var(--color-sage); font-weight:600;">✓ No critical rhetorical distortions or logical fallacies detected.</p>';
        }

        // --- Mathematical Author Bias Telemetry ---
        document.getElementById('val-abs').innerHTML = `${bias.author_bias_score} <small>/100</small>`;
        document.getElementById('sub-abs').textContent = bias.tone_sentiment;
        document.getElementById('val-subj').textContent = `${bias.subjectivity_pct}%`;
        document.getElementById('val-ehf').textContent = `${bias.sensationalism_pct}%`;
        document.getElementById('sub-ehf').textContent = `${bias.sensational_word_count} Sensational words`;
        document.getElementById('val-hur').textContent = `${bias.hedging_pct}%`;
        document.getElementById('sub-hur').textContent = `${bias.hedge_phrase_count} Unverified claims`;

        // Readability
        const read = report.readability;
        document.getElementById('val-fre').textContent = read.flesch_reading_ease;
        document.getElementById('val-fkgl').textContent = `Grade ${read.fkgl_grade_level}`;
        document.getElementById('val-gfi').textContent = read.gunning_fog;
        document.getElementById('val-ttr').textContent = read.lexical_diversity_ttr;

        // Flagged Sentences
        const flaggedContainer = document.getElementById('flagged-list');
        flaggedContainer.innerHTML = '';
        const flagged = report.flagged_deceptive_sentences || [];
        if (flagged.length > 0) {
            flagged.forEach(item => {
                const div = document.createElement('div');
                div.className = 'flagged-item';
                div.innerHTML = `
                    <p class="f-text">"${item.sentence_text}"</p>
                    <span class="f-tag">⚠️ Sentence #${item.sentence_idx} [Risk: ${item.risk_score}] — ${item.reasons.join(', ')}</span>
                `;
                flaggedContainer.appendChild(div);
            });
            document.getElementById('flagged-card').classList.remove('hidden');
        } else {
            flaggedContainer.innerHTML = '<p style="font-size:0.85rem; color:var(--color-sage); font-weight:600;">✓ No high-risk deceptive passages detected.</p>';
        }
    }

    // 5. Load Real-World Dynamic Presets
    async function loadSamples(forceRefresh = false) {
        const container = document.getElementById('samples-list');
        if (!forceRefresh && container.children.length > 0) return;

        container.innerHTML = '<p style="font-size:0.85rem; color:var(--color-muted);">Connecting to live RSS feeds & registries...</p>';

        try {
            const res = await fetch('/api/samples');
            const data = await res.json();
            container.innerHTML = '';

            data.samples.forEach(s => {
                const card = document.createElement('div');
                card.className = 'sample-card';
                card.innerHTML = `
                    <div class="sample-meta-row">
                        <span class="sample-cat ${s.badge_class}">${s.category}</span>
                        <span class="sample-source-tag">${s.source} • ${s.date}</span>
                    </div>
                    <h4 class="sample-title">${s.title}</h4>
                    <p class="sample-snippet">${s.text.substring(0, 140)}...</p>
                    <div class="sample-note">🔍 ${s.analysis_note}</div>
                `;
                card.addEventListener('click', () => {
                    document.getElementById('input-title').value = s.title;
                    document.getElementById('input-body').value = s.text;
                    tabButtons[0].click();
                    submitVerification('/api/verify-text', { title: s.title, text: s.text });
                });
                container.appendChild(card);
            });
        } catch (e) {
            container.innerHTML = '<p>Unable to load live samples from feeds.</p>';
        }
    }

    // 6. Load Research Model Benchmarks
    async function loadBenchmarks() {
        const container = document.getElementById('benchmark-table-container');
        try {
            const res = await fetch('/api/benchmark-stats');
            const data = await res.json();
            if (!data.benchmarks || data.benchmarks.length === 0) {
                container.innerHTML = '<p>No benchmark summary found. Run experiments/train_and_evaluate.py.</p>';
                return;
            }

            let html = `
                <table class="benchmark-table">
                    <thead>
                        <tr>
                            <th>Model Architecture</th>
                            <th>Accuracy</th>
                            <th>F1-Score</th>
                            <th>ROC-AUC</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            data.benchmarks.forEach(m => {
                const isStacking = m.model_name.includes('hybrid_stacking');
                html += `
                    <tr class="${isStacking ? 'highlight-row' : ''}">
                        <td>${m.display_name}</td>
                        <td>${(m.accuracy * 100).toFixed(2)}%</td>
                        <td>${m.f1_score.toFixed(4)}</td>
                        <td>${m.roc_auc.toFixed(4)}</td>
                    </tr>
                `;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        } catch (e) {
            container.innerHTML = '<p>Failed to load benchmark stats.</p>';
        }
    }
});
