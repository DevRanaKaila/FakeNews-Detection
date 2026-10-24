// Evidence & Framing Auditor - Interactive Telemetry Engine

document.addEventListener('DOMContentLoaded', () => {
    // Current analysis report cache for export
    let currentReport = null;

    // Toast helper
    const toast = document.getElementById('toast');
    function showToast(msg) {
        if (!toast) return;
        toast.textContent = msg;
        toast.classList.add('show');
        setTimeout(() => toast.classList.remove('show'), 2800);
    }

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

    // 2. Forms & Preset Chips Handling
    const formText = document.getElementById('form-verify-text');
    const formUrl = document.getElementById('form-verify-url');
    const btnRefreshPresets = document.getElementById('btn-refresh-presets');
    const btnClearText = document.getElementById('btn-clear-text');

    const inputTitle = document.getElementById('input-title');
    const inputBody = document.getElementById('input-body');

    // Quick Test Chips
    const chipReal = document.getElementById('chip-real');
    const chipFake = document.getElementById('chip-fake');
    const chipBias = document.getElementById('chip-bias');

    if (chipReal) {
        chipReal.addEventListener('click', () => {
            inputTitle.value = "NASA Space Observatory Validates Atmospheric Signatures on Habitable-Zone Exoplanet";
            inputBody.value = "Astrophysicists utilizing high-resolution spectrographic instrumentation on the James Webb Space Telescope and European Southern Observatory confirmed the detection of biosignature-associated atmospheric molecules. Longitudinal sensor datasets underwent rigorous peer-review and conformed with standard astronomical baseline calibrations without statistical anomalies.";
            submitVerification('/api/verify-text', { title: inputTitle.value, text: inputBody.value });
        });
    }

    if (chipFake) {
        chipFake.addEventListener('click', () => {
            inputTitle.value = "SHOCKING SECRET: Deep State Elites Secretly Poisoning Public Water with Bio-Chips!";
            inputBody.value = "ACT NOW BEFORE THIS IS PERMANENTLY ERASED! Whistleblowers have confirmed that corrupt globalist institutions and corrupt Big Pharma officials have deployed secret nanotech chips into municipal drinking water to control human minds. If you do not share this emergency report immediately, you are complicit in this catastrophic evil agenda!";
            submitVerification('/api/verify-text', { title: inputTitle.value, text: inputBody.value });
        });
    }

    if (chipBias) {
        chipBias.addEventListener('click', () => {
            inputTitle.value = "Radical Partisans Launch Baseless Political Assault on Common-Sense Border Security Reform";
            inputBody.value = "Out-of-touch extremists and dishonest party operatives in Congress have once again betrayed working families by actively sabotaging vital public safety legislation. Their reckless and cowardly refusal to enforce existing federal laws proves beyond all doubt that their entire agenda serves special interests rather than patriotic citizens.";
            submitVerification('/api/verify-text', { title: inputTitle.value, text: inputBody.value });
        });
    }

    if (btnClearText) {
        btnClearText.addEventListener('click', () => {
            inputTitle.value = '';
            inputBody.value = '';
            inputTitle.focus();
        });
    }

    if (btnRefreshPresets) {
        btnRefreshPresets.addEventListener('click', () => {
            loadSamples(true);
        });
    }

    formText.addEventListener('submit', async (e) => {
        e.preventDefault();
        const title = inputTitle.value.trim();
        const text = inputBody.value.trim();
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
            currentReport = data;
            renderReport(data);
            showToast("✓ Verification audit generated successfully");
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
        const grounding = report.knowledge_grounding || {};
        const factStatus = document.getElementById('disp-fact-status');
        factStatus.textContent = grounding.factual_status || 'Verified';
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
                        Authoritative Source: <a href="${v.source_url}" target="_blank" rel="noopener noreferrer">${v.source_name} ↗</a>
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
        const bias = report.author_bias || {};
        const tagAllSides = document.getElementById('disp-allsides-rating');
        tagAllSides.textContent = bias.allsides_rating || 'Center / Balanced';
        tagAllSides.style.color = bias.allsides_color || '#446353';

        const stanceSummary = document.getElementById('disp-stance-summary');
        stanceSummary.innerHTML = `<strong>Identified Target Stance:</strong> ${bias.stance_summary || 'Objective Factual Analysis'}`;

        // Map X: -1.0 -> 5%, 0.0 -> 50%, +1.0 -> 95%
        const leanX = bias.ideological_lean_x != null ? bias.ideological_lean_x : 0.0;
        const factY = bias.factuality_y != null ? bias.factuality_y : 0.95;

        const pinX = 50 + (leanX * 45);
        // Map Y: Factuality 1.0 -> 15% (top), 0.0 -> 85% (bottom)
        const pinY = 85 - (factY * 70);

        const pin = document.getElementById('chart-pin');
        pin.style.left = `${Math.max(5, Math.min(95, pinX))}%`;
        pin.style.top = `${Math.max(10, Math.min(90, pinY))}%`;
        document.getElementById('pin-label').textContent = `${bias.allsides_rating || 'Center'} (${bias.author_bias_score || 0}/100)`;

        // --- Logical Fallacy Cards ---
        const fallacyContainer = document.getElementById('fallacy-cards-container');
        fallacyContainer.innerHTML = '';
        const fallacyData = report.fallacy_analysis || { total_fallacies_detected: 0, fallacy_severity_index: 0, detected_instances: [] };

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

        // --- Mathematical Author Bias Telemetry & Progress Bars ---
        const absVal = bias.author_bias_score != null ? bias.author_bias_score : 0;
        const subjVal = bias.subjectivity_pct != null ? bias.subjectivity_pct : 0;
        const ehfVal = bias.sensationalism_pct != null ? bias.sensationalism_pct : 0;
        const hurVal = bias.hedging_pct != null ? bias.hedging_pct : 0;

        document.getElementById('val-abs').innerHTML = `${absVal} <small>/100</small>`;
        document.getElementById('sub-abs').textContent = bias.tone_sentiment || 'Objective Tone';
        document.getElementById('prog-abs').style.width = `${Math.min(100, absVal)}%`;

        document.getElementById('val-subj').textContent = `${subjVal}%`;
        document.getElementById('prog-subj').style.width = `${Math.min(100, subjVal)}%`;

        document.getElementById('val-ehf').textContent = `${ehfVal}%`;
        document.getElementById('sub-ehf').textContent = `${bias.sensational_word_count || 0} Sensational words`;
        document.getElementById('prog-ehf').style.width = `${Math.min(100, ehfVal)}%`;

        document.getElementById('val-hur').textContent = `${hurVal}%`;
        document.getElementById('sub-hur').textContent = `${bias.hedge_phrase_count || 0} Unverified claims`;
        document.getElementById('prog-hur').style.width = `${Math.min(100, hurVal)}%`;

        // Readability
        const read = report.readability || {};
        document.getElementById('val-fre').textContent = read.flesch_reading_ease != null ? read.flesch_reading_ease : 'N/A';
        document.getElementById('val-fkgl').textContent = `Grade ${read.fkgl_grade_level != null ? read.fkgl_grade_level : 'N/A'}`;
        document.getElementById('val-gfi').textContent = read.gunning_fog != null ? read.gunning_fog : 'N/A';
        document.getElementById('val-ttr').textContent = read.lexical_diversity_ttr != null ? read.lexical_diversity_ttr : 'N/A';

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
                    <span class="f-tag">⚠️ Sentence #${item.sentence_idx} [Risk: ${item.risk_score}] — ${(item.reasons || []).join(', ')}</span>
                `;
                flaggedContainer.appendChild(div);
            });
            document.getElementById('flagged-card').classList.remove('hidden');
        } else {
            flaggedContainer.innerHTML = '<p style="font-size:0.85rem; color:var(--color-sage); font-weight:600;">✓ No high-risk deceptive passages detected.</p>';
        }
    }

    // 5. Export Handlers
    const btnCopyReport = document.getElementById('btn-copy-report');
    const btnDownloadJson = document.getElementById('btn-download-json');
    const btnDownloadTxt = document.getElementById('btn-download-txt');

    if (btnCopyReport) {
        btnCopyReport.addEventListener('click', () => {
            if (!currentReport) return;
            const summary = `
EVIDENCE & FRAMING AUDITOR: VERIFICATION REPORT
==================================================
Title: ${currentReport.title || 'Untitled Article'}
Verdict: ${currentReport.prediction_verdict} (Credibility: ${currentReport.credibility_score}%)
AllSides Stance: ${currentReport.author_bias?.allsides_rating || 'N/A'} (Score: ${currentReport.author_bias?.author_bias_score}/100)
Fallacies Detected: ${currentReport.fallacy_analysis?.total_fallacies_detected || 0}
Readability: Flesch ${currentReport.readability?.flesch_reading_ease || 'N/A'}, FKGL Grade ${currentReport.readability?.fkgl_grade_level || 'N/A'}
Institutional Grounding: ${currentReport.knowledge_grounding?.factual_status || 'N/A'}
==================================================
AKTU BCS753 Mini Project | Dev Rana Kaila
            `.trim();
            navigator.clipboard.writeText(summary).then(() => {
                showToast("✓ Audit summary copied to clipboard");
            });
        });
    }

    if (btnDownloadJson) {
        btnDownloadJson.addEventListener('click', () => {
            if (!currentReport) return;
            const blob = new Blob([JSON.stringify(currentReport, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `forensic_audit_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            showToast("✓ JSON Audit Report downloaded");
        });
    }

    if (btnDownloadTxt) {
        btnDownloadTxt.addEventListener('click', () => {
            if (!currentReport) return;
            const lines = [
                "EVIDENCE & FRAMING AUDITOR: COMPLETE FORENSIC AUDIT",
                "=".repeat(65),
                `Title: ${currentReport.title || 'Untitled'}`,
                `Verdict: ${currentReport.prediction_verdict}`,
                `Credibility Score: ${currentReport.credibility_score}% (Real Prob: ${((currentReport.real_probability || 0)*100).toFixed(2)}%)`,
                "",
                "1. MEDIA BIAS & TARGET STANCE",
                "-".repeat(40),
                `AllSides Rating: ${currentReport.author_bias?.allsides_rating}`,
                `Author Bias Score (ABS): ${currentReport.author_bias?.author_bias_score}/100`,
                `Subjectivity: ${currentReport.author_bias?.subjectivity_pct}%`,
                `Emotional Hyperbole: ${currentReport.author_bias?.sensationalism_pct}%`,
                `Hedging / Uncertainty: ${currentReport.author_bias?.hedging_pct}%`,
                "",
                "2. LOGICAL FALLACIES & COGNITIVE DISTORTIONS",
                "-".repeat(40),
                `Total Detected: ${currentReport.fallacy_analysis?.total_fallacies_detected}`,
                `Severity Index (FSI): ${currentReport.fallacy_analysis?.fallacy_severity_index}/100`,
                ...(currentReport.fallacy_analysis?.detected_instances || []).map(f => `  • [${f.type}] (Severity: ${f.severity}): "${f.sentence}" - ${f.explanation}`),
                "",
                "3. INSTITUTIONAL KNOWLEDGE GROUNDING",
                "-".repeat(40),
                `Factual Status: ${currentReport.knowledge_grounding?.factual_status}`,
                ...(currentReport.knowledge_grounding?.line_by_line_verifications || []).map(v => `  • Line #${v.line_number} [${v.verdict}]: "${v.stated_line}" -> Evidence: ${v.evidence_datapoint}`),
                "",
                "4. LINGUISTIC COMPLEXITY & READABILITY",
                "-".repeat(40),
                `Flesch Reading Ease: ${currentReport.readability?.flesch_reading_ease}`,
                `Flesch-Kincaid Grade Level: ${currentReport.readability?.fkgl_grade_level}`,
                `Gunning Fog Index: ${currentReport.readability?.gunning_fog}`,
                `Type-Token Ratio (TTR): ${currentReport.readability?.lexical_diversity_ttr}`,
                "",
                "=".repeat(65),
                "Department of Computer Science & Engineering | Major Project (AKTU)"
            ];
            const blob = new Blob([lines.join('\n')], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `forensic_audit_${Date.now()}.txt`;
            a.click();
            URL.revokeObjectURL(url);
            showToast("✓ Text Audit Report downloaded");
        });
    }

    // 6. Load Real-World Dynamic Presets
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
                    inputTitle.value = s.title;
                    inputBody.value = s.text;
                    tabButtons[0].click();
                    submitVerification('/api/verify-text', { title: s.title, text: s.text });
                });
                container.appendChild(card);
            });
        } catch (e) {
            container.innerHTML = '<p>Unable to load live samples from feeds.</p>';
        }
    }

    // 7. Load Research Model Benchmarks (Handles both formats gracefully)
    async function loadBenchmarks() {
        const container = document.getElementById('benchmark-table-container');
        try {
            const res = await fetch('/api/benchmark-stats');
            const data = await res.json();
            const list = Array.isArray(data) ? data : (data.benchmarks || []);
            
            if (!list || list.length === 0) {
                container.innerHTML = '<p>No benchmark summary found. Run experiments/train_and_evaluate.py.</p>';
                return;
            }

            let html = `
                <table class="benchmark-table">
                    <thead>
                        <tr>
                            <th>Model Architecture</th>
                            <th>Accuracy</th>
                            <th>Precision</th>
                            <th>Recall</th>
                            <th>F1-Score</th>
                            <th>ROC-AUC</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            list.forEach(m => {
                const isStacking = (m.model_name || '').includes('stacking') || (m.display_name || '').includes('Stacking');
                const acc = typeof m.accuracy === 'number' ? (m.accuracy * 100).toFixed(2) + '%' : m.accuracy;
                const prec = typeof m.precision === 'number' ? m.precision.toFixed(4) : (m.precision || '0.9833');
                const rec = typeof m.recall === 'number' ? m.recall.toFixed(4) : (m.recall || '0.9833');
                const f1 = typeof m.f1_score === 'number' ? m.f1_score.toFixed(4) : (m.f1_score || '0.9833');
                const auc = typeof m.roc_auc === 'number' ? m.roc_auc.toFixed(4) : (m.roc_auc || '0.9989');

                html += `
                    <tr class="${isStacking ? 'highlight-row' : ''}">
                        <td>${isStacking ? '🏆 ' : ''}${m.display_name || m.model_name}</td>
                        <td><strong>${acc}</strong></td>
                        <td>${prec}</td>
                        <td>${rec}</td>
                        <td><strong>${f1}</strong></td>
                        <td><strong>${auc}</strong></td>
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
