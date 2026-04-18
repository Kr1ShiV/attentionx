/**
 * AttentionX — Main Application
 * Core UI logic, view management, and feature orchestration
 */

(function () {
    'use strict';

    // ═══ STATE ═══════════════════════════════════════════════

    const state = {
        currentView: 'upload',
        jobId: null,
        analysisData: null,
        selectedSegment: null,
        selectedSegmentForRemix: null,
        audioType: 'energy',
        pollTimer: null,
    };

    // ═══ INITIALIZATION ══════════════════════════════════════

    window.addEventListener('DOMContentLoaded', () => {
        // Remove loader
        setTimeout(() => {
            const loader = document.getElementById('app-loader');
            const app = document.getElementById('app');
            if (loader) loader.classList.add('fade-out');
            if (app) app.classList.remove('hidden');
            setTimeout(() => { if (loader) loader.remove(); }, 600);
        }, 1200);

        setupNavigation();
        setupUpload();
        setupAudioToggles();
        setupSortButtons();
        setupStoryBuilder();
        setupPersonaCards();
        setupPlatformCards();
        setupDetailOverlay();
        setupDemoButton();

        Viz.setupHeatmapTooltip('heatmap-canvas', 'heatmap-tooltip');
        Viz.setupResizeHandler(() => { if (state.analysisData) redrawVisualizations(); });
    });

    // ═══ NAVIGATION ══════════════════════════════════════════

    function setupNavigation() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const view = btn.dataset.view;
                if (btn.disabled) return;
                switchView(view);
            });
        });
    }

    function switchView(viewName) {
        state.currentView = viewName;

        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

        const viewEl = document.getElementById(`view-${viewName}`);
        const navEl = document.querySelector(`[data-view="${viewName}"]`);

        if (viewEl) viewEl.classList.add('active');
        if (navEl) navEl.classList.add('active');

        // Redraw canvases when switching to dashboard
        if (viewName === 'dashboard' && state.analysisData) {
            setTimeout(redrawVisualizations, 100);
        }
    }

    function enableNavButtons() {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.disabled = false;
        });
    }

    // ═══ UPLOAD ══════════════════════════════════════════════

    function setupUpload() {
        const zone = document.getElementById('upload-zone');
        const fileInput = document.getElementById('file-input');
        const browseBtn = document.getElementById('btn-browse');

        if (!zone) return;

        // Click to browse
        browseBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            fileInput.click();
        });

        zone.addEventListener('click', () => fileInput.click());

        // Drag and drop
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('video/')) {
                handleFileUpload(file);
            } else {
                showToast('Please upload a video file', 'error');
            }
        });

        // File input change
        fileInput.addEventListener('change', () => {
            const file = fileInput.files[0];
            if (file) handleFileUpload(file);
        });
    }

    async function handleFileUpload(file) {
        showToast(`Uploading "${file.name}"...`, 'info');
        switchView('processing');

        try {
            const result = await api.uploadVideo(file);
            state.jobId = result.job_id;
            showToast('Upload complete! Processing started.', 'success');
            startPolling(result.job_id);
        } catch (err) {
            showToast(`Upload failed: ${err.message}`, 'error');
            switchView('upload');
        }
    }

    // ═══ POLLING ═════════════════════════════════════════════

    function startPolling(jobId) {
        if (state.pollTimer) clearInterval(state.pollTimer);

        state.pollTimer = setInterval(async () => {
            try {
                const status = await api.getStatus(jobId);
                updateProcessingUI(status);

                if (status.status === 'completed') {
                    clearInterval(state.pollTimer);
                    state.pollTimer = null;
                    await loadAnalysisResults(jobId);
                } else if (status.status === 'failed') {
                    clearInterval(state.pollTimer);
                    state.pollTimer = null;
                    showToast(`Processing failed: ${status.message}`, 'error');
                    switchView('upload');
                }
            } catch (err) {
                console.error('Polling error:', err);
            }
        }, 2000);
    }

    function updateProcessingUI(status) {
        const statusEl = document.getElementById('processing-status');
        const progressFill = document.getElementById('processing-progress-fill');
        const progressText = document.getElementById('processing-progress-text');

        if (statusEl) statusEl.textContent = status.current_step;
        if (progressFill) progressFill.style.width = status.progress + '%';
        if (progressText) progressText.textContent = status.progress + '%';

        // Update step indicators
        const steps = document.querySelectorAll('#processing-steps .step');
        const statusOrder = [
            'extracting_audio', 'transcribing', 'analyzing_audio',
            'detecting_faces', 'scoring_virality', 'generating_clips',
        ];

        const currentIdx = statusOrder.indexOf(status.status);
        steps.forEach((step, i) => {
            step.classList.remove('active', 'completed');
            if (i < currentIdx) step.classList.add('completed');
            else if (i === currentIdx) step.classList.add('active');
        });
    }

    // ═══ ANALYSIS RESULTS ════════════════════════════════════

    async function loadAnalysisResults(jobId) {
        try {
            const data = await api.getAnalysis(jobId);
            if (data.status && data.status !== 'completed') {
                showToast('Still processing...', 'info');
                return;
            }

            state.analysisData = data;
            state.jobId = data.job_id || jobId;

            renderDashboard(data);
            renderClips(data);
            setupRemixSegments(data);
            enableNavButtons();
            switchView('dashboard');

            showToast(`Analysis complete! Found ${data.segments.length} viral segments.`, 'success');
        } catch (err) {
            showToast(`Failed to load results: ${err.message}`, 'error');
        }
    }

    // ═══ DASHBOARD RENDERING ═════════════════════════════════

    function renderDashboard(data) {
        // Stats
        const stats = data.overall_stats || {};
        setText('stat-duration', Viz.formatTime(data.duration || stats.total_duration || 0));
        setText('stat-segments', stats.segments_found || data.segments.length);
        setText('stat-avg-score', stats.avg_virality_score || 0);
        setText('stat-top-score', stats.top_score || 0);
        setText('stat-high-count', stats.high_virality_count || 0);
        setText('stat-words', stats.transcript_word_count || 0);

        // Heatmap
        const duration = data.duration || stats.total_duration || 120;
        Viz.drawHeatmap('heatmap-canvas', data.attention_timeline || [], data.segments, duration);

        // Waveform
        Viz.drawWaveform('waveform-canvas', data.audio_features || [], state.audioType, duration);

        // Transcript
        renderTranscript(data.transcript || []);
    }

    function redrawVisualizations() {
        if (!state.analysisData) return;
        const data = state.analysisData;
        const duration = data.duration || data.overall_stats?.total_duration || 120;

        Viz.drawHeatmap('heatmap-canvas', data.attention_timeline || [], data.segments, duration);
        Viz.drawWaveform('waveform-canvas', data.audio_features || [], state.audioType, duration);
    }

    function renderTranscript(transcript) {
        const container = document.getElementById('transcript-container');
        if (!container) return;

        container.innerHTML = transcript.map(seg => `
            <div class="transcript-segment" data-start="${seg.start}" data-end="${seg.end}">
                <span class="transcript-time">${Viz.formatTime(seg.start)}</span>
                <span class="transcript-text">${escapeHtml(seg.text)}</span>
            </div>
        `).join('');

        // Click to highlight
        container.querySelectorAll('.transcript-segment').forEach(el => {
            el.addEventListener('click', () => {
                container.querySelectorAll('.transcript-segment').forEach(s => s.classList.remove('highlight'));
                el.classList.add('highlight');
            });
        });
    }

    // ═══ AUDIO TOGGLES ═══════════════════════════════════════

    function setupAudioToggles() {
        document.querySelectorAll('.toggle-btn[data-audio]').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.toggle-btn[data-audio]').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                state.audioType = btn.dataset.audio;

                if (state.analysisData) {
                    const data = state.analysisData;
                    const duration = data.duration || data.overall_stats?.total_duration || 120;
                    Viz.drawWaveform('waveform-canvas', data.audio_features || [], state.audioType, duration);
                }
            });
        });
    }

    // ═══ CLIPS RENDERING ═════════════════════════════════════

    function renderClips(data) {
        const grid = document.getElementById('clips-grid');
        if (!grid) return;

        const segments = data.segments || [];

        grid.innerHTML = segments.map((seg, idx) => {
            const vClass = Viz.viralityClass(seg.virality_score);
            const vColor = Viz.viralityColor(seg.virality_score);
            const vGradient = Viz.viralityGradient(seg.virality_score);

            return `
                <div class="clip-card" data-segment-id="${seg.id}" data-index="${idx}">
                    <div class="clip-card-header">
                        <span class="clip-card-time">${Viz.formatTime(seg.start)} → ${Viz.formatTime(seg.end)}</span>
                        <div class="virality-badge ${vClass}">
                            ${seg.virality_score >= 70 ? '🔥' : seg.virality_score >= 45 ? '📈' : '📊'}
                            ${seg.virality_score}
                        </div>
                    </div>
                    <div class="clip-card-body">
                        <div class="virality-gauge">
                            <div class="virality-gauge-fill" style="width: ${seg.virality_score}%; background: ${vGradient}"></div>
                        </div>
                        <p class="clip-card-transcript">${escapeHtml(seg.transcript)}</p>
                        ${seg.keywords && seg.keywords.length ? `
                            <div class="clip-card-keywords">
                                ${seg.keywords.map(kw => `<span class="keyword-tag">${escapeHtml(kw)}</span>`).join('')}
                            </div>
                        ` : ''}
                        <div class="clip-card-emotion">
                            ${getEmotionEmoji(seg.emotion?.dominant)} 
                            <span>${capitalize(seg.emotion?.dominant || 'neutral')}</span>
                            <span class="clip-card-duration">• ${seg.duration?.toFixed(1)}s</span>
                        </div>
                        <div class="clip-card-reasons">
                            ${(seg.reasons || []).slice(0, 2).map(r => `<span>${r}</span>`).join('')}
                        </div>
                    </div>
                    <div class="clip-card-footer">
                        <button class="btn btn-ghost btn-sm" data-action="detail" data-seg-id="${seg.id}">
                            🎬 Details
                        </button>
                        <button class="btn btn-ghost btn-sm" data-action="copy" data-seg-id="${seg.id}">
                            📋 Copy
                        </button>
                        <button class="btn btn-primary btn-sm" data-action="export" data-seg-id="${seg.id}">
                            ⬇ Export
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        // Click card to open detail
        grid.querySelectorAll('.clip-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const segId = card.dataset.segmentId;
                openSegmentDetail(segId);
            });
        });

        // Handle button clicks via delegation
        grid.querySelectorAll('[data-action]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                const segId = btn.dataset.segId;
                if (action === 'detail') openSegmentDetail(segId);
                else if (action === 'copy') {
                    const seg = (state.analysisData?.segments || []).find(s => s.id === segId);
                    if (seg) copyToClipboard(seg.transcript);
                }
                else if (action === 'export') exportClip(segId);
            });
        });
    }

    // ═══ SORT BUTTONS ════════════════════════════════════════

    function setupSortButtons() {
        document.querySelectorAll('.sort-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                if (!state.analysisData) return;

                const sortType = btn.dataset.sort;
                const segments = [...state.analysisData.segments];

                if (sortType === 'virality') {
                    segments.sort((a, b) => b.virality_score - a.virality_score);
                } else {
                    segments.sort((a, b) => a.start - b.start);
                }

                state.analysisData.segments = segments;
                renderClips(state.analysisData);
            });
        });
    }

    // ═══ SEGMENT DETAIL ══════════════════════════════════════

    function setupDetailOverlay() {
        const overlay = document.getElementById('segment-detail-overlay');
        const closeBtn = document.getElementById('detail-close');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => overlay.classList.add('hidden'));
        }

        if (overlay) {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) overlay.classList.add('hidden');
            });
        }
    }

    window.openSegmentDetail = function (segId) {
        if (!state.analysisData) return;

        const seg = state.analysisData.segments.find(s => s.id === segId);
        if (!seg) return;

        state.selectedSegment = seg;

        const content = document.getElementById('detail-content');
        const overlay = document.getElementById('segment-detail-overlay');

        const vClass = Viz.viralityClass(seg.virality_score);

        content.innerHTML = `
            <div style="display:flex;align-items:center;gap:16px;margin-bottom:24px">
                <div style="position:relative;width:70px;height:70px">
                    ${Viz.createGaugeSVG(seg.virality_score, 70)}
                </div>
                <div>
                    <h2 style="font-size:20px;margin-bottom:4px">Virality Score: ${seg.virality_score}/100</h2>
                    <p style="font-size:13px;color:var(--text-muted)">
                        ${Viz.formatTime(seg.start)} → ${Viz.formatTime(seg.end)} • ${seg.duration?.toFixed(1)}s
                    </p>
                </div>
            </div>

            <div class="detail-section">
                <h3>📝 Transcript</h3>
                <p style="font-size:14px;line-height:1.8;color:var(--text-secondary)">${escapeHtml(seg.transcript)}</p>
            </div>

            <div class="detail-section">
                <h3>🎯 Why This Segment</h3>
                <div style="display:flex;flex-direction:column;gap:6px">
                    ${(seg.reasons || []).map(r => `
                        <span style="font-size:13px;color:var(--text-secondary)">${r}</span>
                    `).join('')}
                </div>
            </div>

            <div class="detail-section">
                <h3>🎬 Viral Hooks</h3>
                <div class="detail-hooks" id="detail-hooks-list">
                    ${(seg.hooks || []).map((h, i) => `
                        <div class="hook-item" data-hook-idx="${i}">&ldquo;${escapeHtml(h)}&rdquo;</div>
                    `).join('')}
                </div>
                <div style="display:flex;gap:8px;margin-top:12px;flex-wrap:wrap">
                    ${['curiosity', 'shock', 'challenge', 'story', 'value'].map(style => `
                        <button class="btn btn-ghost btn-sm" data-hook-style="${style}" data-hook-seg="${seg.id}">
                            ${style === 'curiosity' ? '🤔' : style === 'shock' ? '😱' : style === 'challenge' ? '💪' : style === 'story' ? '📖' : '💎'} 
                            ${capitalize(style)}
                        </button>
                    `).join('')}
                </div>
            </div>

            ${seg.emotion ? `
                <div class="detail-section">
                    <h3>😊 Emotion Analysis</h3>
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">
                        ${Object.entries(seg.emotion).filter(([k]) => k !== 'dominant').map(([key, val]) => `
                            <div style="padding:8px;background:var(--bg-tertiary);border-radius:8px;text-align:center">
                                <div style="font-size:12px;color:var(--text-muted);margin-bottom:4px">${capitalize(key)}</div>
                                <div style="font-size:16px;font-weight:700;font-family:var(--font-mono);color:${val > 0.5 ? 'var(--accent-orange)' : 'var(--text-secondary)'}">
                                    ${(val * 100).toFixed(0)}%
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <p style="margin-top:8px;font-size:12px;color:var(--text-muted)">
                        Dominant emotion: <strong>${getEmotionEmoji(seg.emotion.dominant)} ${capitalize(seg.emotion.dominant)}</strong>
                    </p>
                </div>
            ` : ''}

            ${seg.keywords && seg.keywords.length ? `
                <div class="detail-section">
                    <h3>🔑 Viral Keywords</h3>
                    <div style="display:flex;flex-wrap:wrap;gap:6px">
                        ${seg.keywords.map(kw => `<span class="keyword-tag" style="font-size:12px;padding:4px 12px">${escapeHtml(kw)}</span>`).join('')}
                    </div>
                </div>
            ` : ''}
        `;

        overlay.classList.remove('hidden');

        // Bind hook copy clicks
        document.querySelectorAll('#detail-hooks-list .hook-item').forEach(item => {
            item.addEventListener('click', () => {
                const idx = parseInt(item.dataset.hookIdx);
                const hooks = seg.hooks || [];
                if (hooks[idx]) copyToClipboard(hooks[idx]);
            });
        });

        // Bind hook style buttons
        document.querySelectorAll('[data-hook-style]').forEach(btn => {
            btn.addEventListener('click', () => {
                generateHooksForSegment(btn.dataset.hookSeg, btn.dataset.hookStyle);
            });
        });
    };

    window.generateHooksForSegment = async function (segId, style) {
        showToast(`Generating ${style} hooks...`, 'info');

        try {
            const result = await api.generateHooks(state.jobId || 'demo', segId, style, 3);
            
            // Update hooks in state
            if (state.selectedSegment && result.hooks) {
                state.selectedSegment.hooks = result.hooks;
            }

            // Update the hooks display in the detail panel
            const hooksContainer = document.getElementById('detail-hooks-list');
            if (hooksContainer && result.hooks) {
                hooksContainer.innerHTML = result.hooks.map((h, i) => `
                    <div class="hook-item" data-hook-idx="${i}">&ldquo;${escapeHtml(h)}&rdquo;</div>
                `).join('');

                // Rebind click handlers
                hooksContainer.querySelectorAll('.hook-item').forEach(item => {
                    item.addEventListener('click', () => {
                        const idx = parseInt(item.dataset.hookIdx);
                        if (result.hooks[idx]) copyToClipboard(result.hooks[idx]);
                    });
                });

                showToast(`Generated ${result.hooks.length} ${style} hooks!`, 'success');
            }
        } catch (err) {
            showToast(`Hook generation failed: ${err.message}`, 'error');
        }
    };

    window.exportClip = async function (segId) {
        showToast('Preparing clip for export...', 'info');

        try {
            const result = await api.exportClip(state.jobId || 'demo', segId);
            if (result && result.success) {
                showToast('Clip downloaded!', 'success');
            } else {
                // Generate a text file with the segment content as fallback
                const seg = (state.analysisData?.segments || []).find(s => s.id === segId);
                if (seg) {
                    const content = [
                        `AttentionX — Clip Export`,
                        `========================`,
                        ``,
                        `Virality Score: ${seg.virality_score}/100`,
                        `Time: ${Viz.formatTime(seg.start)} → ${Viz.formatTime(seg.end)}`,
                        `Duration: ${seg.duration?.toFixed(1)}s`,
                        `Emotion: ${seg.emotion?.dominant || 'neutral'}`,
                        ``,
                        `Transcript:`,
                        seg.transcript,
                        ``,
                        `Hooks:`,
                        ...(seg.hooks || []).map((h, i) => `  ${i + 1}. ${h}`),
                        ``,
                        `Keywords: ${(seg.keywords || []).join(', ')}`,
                        ``,
                        `Reasons:`,
                        ...(seg.reasons || []).map(r => `  - ${r}`),
                    ].join('\n');

                    const blob = new Blob([content], { type: 'text/plain' });
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `attentionx_clip_${segId}.txt`;
                    a.click();
                    URL.revokeObjectURL(url);
                    showToast('Clip data exported as text file!', 'success');
                } else {
                    showToast(result?.message || 'Clip export ready!', 'success');
                }
            }
        } catch (err) {
            showToast(`Export error: ${err.message}`, 'error');
        }
    };

    // ═══ STORY BUILDER ═══════════════════════════════════════

    function setupStoryBuilder() {
        const btn = document.getElementById('btn-build-story');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            if (!state.analysisData || !state.jobId) {
                showToast('No analysis data available', 'error');
                return;
            }

            const style = document.getElementById('story-style')?.value || 'problem_insight_solution';
            const segments = state.analysisData.segments || [];
            const topSegIds = segments.slice(0, 5).map(s => s.id);

            btn.disabled = true;
            btn.textContent = '⏳ Building...';

            try {
                const story = await api.buildStory(state.jobId, topSegIds, style);
                renderStoryResult(story, segments);
                showToast('Story built successfully!', 'success');
            } catch (err) {
                showToast(`Story building failed: ${err.message}`, 'error');
                // Fallback: build client-side
                renderFallbackStory(segments, style);
            }

            btn.disabled = false;
            btn.innerHTML = '<span>🧩</span> Build Story';
        });
    }

    function renderStoryResult(story, segments) {
        const container = document.getElementById('story-result');
        if (!container) return;

        container.classList.remove('hidden');
        container.innerHTML = `
            <h4>${escapeHtml(story.title)}</h4>
            <p class="story-arc">${escapeHtml(story.story_arc)}</p>
            <p style="font-size:14px;color:var(--text-secondary);margin-bottom:16px">${escapeHtml(story.narrative)}</p>
            ${story.suggested_hook ? `
                <div style="background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.3);border-radius:12px;padding:12px 16px;margin-bottom:16px">
                    <span style="font-size:12px;color:var(--accent-purple-light);font-weight:600">🎯 AI Suggested Hook</span>
                    <p style="font-size:14px;color:var(--text-primary);margin-top:4px">${escapeHtml(story.suggested_hook)}</p>
                </div>
            ` : ''}
            <div>
                ${(story.transitions || []).map((t, i) => {
                    const segId = story.segments_order?.[i];
                    const seg = segments.find(s => s.id === segId);
                    return `
                        <div class="story-transition">${escapeHtml(t)}</div>
                        ${seg ? `<p style="padding:8px 16px;font-size:13px;color:var(--text-muted);border-left:3px solid var(--border-subtle);margin:4px 0">
                            ${escapeHtml(seg.transcript?.substring(0, 150))}${seg.transcript?.length > 150 ? '...' : ''}
                        </p>` : ''}
                    `;
                }).join('')}
            </div>
            <p style="margin-top:16px;font-size:12px;color:var(--text-muted)">
                Total duration: ${Viz.formatTime(story.total_duration || 0)} • 
                ${story.segments_order?.length || 0} segments
                ${story.estimated_engagement ? ` • 📊 ${escapeHtml(story.estimated_engagement)}` : ''}
            </p>
        `;
    }

    function renderFallbackStory(segments, style) {
        const topSegs = segments.slice(0, 3);
        const templates = {
            problem_insight_solution: ['The Problem', 'The Key Insight', 'The Solution'],
            hook_build_payoff: ['The Hook', 'Building Context', 'The Payoff'],
            before_after: ['Before', 'Transformation', 'After'],
            myth_reality: ['The Myth', 'Reality Check', 'The Truth'],
        };

        const labels = templates[style] || templates.problem_insight_solution;
        const story = {
            title: `Story: ${capitalize(style.replace(/_/g, ' '))}`,
            story_arc: `A ${style.replace(/_/g, ' ')} narrative built from top moments`,
            narrative: 'Auto-generated story from your most viral segments.',
            transitions: labels,
            segments_order: topSegs.map(s => s.id),
            total_duration: topSegs.reduce((sum, s) => sum + (s.duration || 0), 0),
        };

        renderStoryResult(story, segments);
    }

    // ═══ PERSONA ADAPTER ═════════════════════════════════════

    function setupPersonaCards() {
        document.querySelectorAll('.persona-card').forEach(card => {
            card.addEventListener('click', async () => {
                const persona = card.dataset.persona;
                if (!state.analysisData) {
                    showToast('Please analyze a video first', 'error');
                    return;
                }

                // Highlight active
                document.querySelectorAll('.persona-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');

                // Get selected segment text
                const seg = state.selectedSegmentForRemix || state.analysisData.segments[0];
                if (!seg) return;

                showToast(`Adapting for ${capitalize(persona)}...`, 'info');

                try {
                    const result = await api.adaptPersona(
                        state.jobId, seg.id, persona, seg.transcript
                    );
                    renderPersonaResult(result);
                } catch (err) {
                    showToast(`Persona adaptation failed: ${err.message}`, 'error');
                    // Fallback
                    renderPersonaFallback(seg.transcript, persona);
                }
            });
        });
    }

    function renderPersonaResult(result) {
        const container = document.getElementById('persona-result');
        if (!container) return;

        container.classList.remove('hidden');
        container.innerHTML = `
            <div class="result-header">🎯 Adapted for: ${capitalize(result.persona)}</div>
            
            <div class="result-block">
                <h4>Tone</h4>
                <p>${escapeHtml(result.tone_description)}</p>
            </div>

            <div class="result-block">
                <h4>Adapted Content</h4>
                <div class="result-text">${escapeHtml(result.adapted_text)}</div>
            </div>

            <div class="result-block">
                <h4>Caption</h4>
                <div class="result-text">${escapeHtml(result.adapted_caption)}</div>
                <button class="btn btn-ghost btn-sm" style="margin-top:8px" id="btn-copy-persona-caption">
                    📋 Copy Caption
                </button>
            </div>

            ${result.adapted_hooks && result.adapted_hooks.length ? `
                <div class="result-block">
                    <h4>Hooks</h4>
                    <div class="detail-hooks">
                        ${result.adapted_hooks.map((h, i) => `
                            <div class="hook-item" data-persona-hook="${i}">&ldquo;${escapeHtml(h)}&rdquo;</div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;

        // Bind events safely
        const copyBtn = document.getElementById('btn-copy-persona-caption');
        if (copyBtn) copyBtn.addEventListener('click', () => copyToClipboard(result.adapted_caption));

        container.querySelectorAll('[data-persona-hook]').forEach(item => {
            item.addEventListener('click', () => {
                const idx = parseInt(item.dataset.personaHook);
                if (result.adapted_hooks[idx]) copyToClipboard(result.adapted_hooks[idx]);
            });
        });
    }

    function renderPersonaFallback(text, persona) {
        const personaEmoji = {
            students: '🎓', entrepreneurs: '💼', developers: '💻',
            marketers: '📊', general: '🌐'
        };

        const container = document.getElementById('persona-result');
        if (!container) return;

        container.classList.remove('hidden');
        container.innerHTML = `
            <div class="result-header">${personaEmoji[persona] || '🎯'} Adapted for: ${capitalize(persona)}</div>
            <div class="result-block">
                <h4>Adapted Content</h4>
                <div class="result-text">${escapeHtml(text)}</div>
            </div>
            <p style="font-size:12px;color:var(--text-muted);margin-top:8px">
                Note: Connect your Gemini API key for AI-powered persona adaptation
            </p>
        `;
    }

    // ═══ PLATFORM REMIX ══════════════════════════════════════

    function setupPlatformCards() {
        document.querySelectorAll('.platform-card').forEach(card => {
            card.addEventListener('click', async () => {
                const platform = card.dataset.platform;
                if (!state.analysisData) {
                    showToast('Please analyze a video first', 'error');
                    return;
                }

                document.querySelectorAll('.platform-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');

                const seg = state.selectedSegmentForRemix || state.analysisData.segments[0];
                if (!seg) return;

                showToast(`Remixing for ${platform.replace(/_/g, ' ')}...`, 'info');

                try {
                    const result = await api.remixContent(
                        state.jobId, seg.id, platform, seg.transcript
                    );
                    renderPlatformResult(result);
                } catch (err) {
                    showToast(`Remix failed: ${err.message}`, 'error');
                    renderPlatformFallback(seg.transcript, platform);
                }
            });
        });
    }

    function renderPlatformResult(result) {
        const container = document.getElementById('platform-result');
        if (!container) return;

        const platformNames = {
            instagram_reel: '📸 Instagram Reel',
            youtube_short: '▶️ YouTube Short',
            linkedin_post: '💼 LinkedIn Post',
            tiktok: '🎵 TikTok',
        };

        container.classList.remove('hidden');
        container.innerHTML = `
            <div class="result-header">${platformNames[result.platform] || result.platform}</div>
            
            <div class="result-block">
                <h4>Optimized Content</h4>
                <div class="result-text">${escapeHtml(result.content)}</div>
            </div>

            <div class="result-block">
                <h4>Caption (${result.character_count} chars)</h4>
                <div class="result-text">${escapeHtml(result.caption)}</div>
                <button class="btn btn-ghost btn-sm" style="margin-top:8px" id="btn-copy-platform-caption">
                    📋 Copy Caption
                </button>
            </div>

            ${result.hashtags && result.hashtags.length ? `
                <div class="result-block">
                    <h4>Hashtags</h4>
                    <div class="result-hashtags">
                        ${result.hashtags.map(h => `<span class="hashtag">#${escapeHtml(h.replace('#', ''))}</span>`).join('')}
                    </div>
                    <button class="btn btn-ghost btn-sm" style="margin-top:8px" id="btn-copy-platform-hashtags">
                        📋 Copy All Hashtags
                    </button>
                </div>
            ` : ''}

            ${result.format_specs ? `
                <div class="result-block">
                    <h4>Format Guidelines</h4>
                    ${Object.entries(result.format_specs).map(([k, v]) => `
                        <p style="font-size:13px;color:var(--text-muted);margin-bottom:4px">
                            <strong>${capitalize(k.replace(/_/g, ' '))}:</strong> ${escapeHtml(String(v))}
                        </p>
                    `).join('')}
                </div>
            ` : ''}
        `;

        // Bind copy buttons
        const captionBtn = document.getElementById('btn-copy-platform-caption');
        if (captionBtn) captionBtn.addEventListener('click', () => copyToClipboard(result.caption));

        const hashtagBtn = document.getElementById('btn-copy-platform-hashtags');
        if (hashtagBtn) hashtagBtn.addEventListener('click', () => copyToClipboard(result.hashtags.map(h => '#' + h.replace('#', '')).join(' ')));
    }

    function renderPlatformFallback(text, platform) {
        const container = document.getElementById('platform-result');
        if (!container) return;

        container.classList.remove('hidden');
        container.innerHTML = `
            <div class="result-header">📱 ${capitalize(platform.replace(/_/g, ' '))}</div>
            <div class="result-block">
                <h4>Content</h4>
                <div class="result-text">${escapeHtml(text)}</div>
            </div>
            <p style="font-size:12px;color:var(--text-muted);margin-top:8px">
                Note: Connect your Gemini API key for AI-powered platform optimization
            </p>
        `;
    }

    // ═══ REMIX SEGMENT SELECTOR ══════════════════════════════

    function setupRemixSegments(data) {
        const selectContainer = document.getElementById('remix-segment-select');
        const listContainer = document.getElementById('remix-segments-list');
        if (!selectContainer || !listContainer) return;

        const segments = data.segments || [];
        if (!segments.length) return;

        // Set default
        state.selectedSegmentForRemix = segments[0];

        selectContainer.classList.remove('hidden');

        listContainer.innerHTML = segments.map((seg, i) => `
            <div class="remix-segment-item ${i === 0 ? 'selected' : ''}" data-segment-id="${seg.id}">
                <span class="remix-segment-text">
                    <strong>[${Viz.formatTime(seg.start)}]</strong> 
                    ${escapeHtml(seg.transcript.substring(0, 80))}${seg.transcript.length > 80 ? '...' : ''}
                </span>
                <span class="virality-badge ${Viz.viralityClass(seg.virality_score)}" style="font-size:12px;padding:3px 8px">
                    ${seg.virality_score}
                </span>
            </div>
        `).join('');

        listContainer.querySelectorAll('.remix-segment-item').forEach(item => {
            item.addEventListener('click', () => {
                listContainer.querySelectorAll('.remix-segment-item').forEach(i => i.classList.remove('selected'));
                item.classList.add('selected');

                const segId = item.dataset.segmentId;
                state.selectedSegmentForRemix = segments.find(s => s.id === segId);

                // Reset results
                document.getElementById('persona-result')?.classList.add('hidden');
                document.getElementById('platform-result')?.classList.add('hidden');
                document.querySelectorAll('.persona-card').forEach(c => c.classList.remove('active'));
                document.querySelectorAll('.platform-card').forEach(c => c.classList.remove('active'));
            });
        });
    }

    // ═══ DEMO MODE ═══════════════════════════════════════════

    function setupDemoButton() {
        const btn = document.getElementById('btn-demo');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            btn.disabled = true;
            btn.innerHTML = '<span>⏳</span> Loading...';
            showToast('Loading demo data...', 'info');

            try {
                // Try server demo first
                const data = await api.getDemo();
                state.analysisData = data;
                state.jobId = data.job_id;

                renderDashboard(data);
                renderClips(data);
                setupRemixSegments(data);
                enableNavButtons();
                switchView('dashboard');

                showToast('Demo loaded! Explore the dashboard.', 'success');
            } catch {
                // Generate client-side demo data
                const data = generateClientDemoData();
                state.analysisData = data;
                state.jobId = data.job_id;

                renderDashboard(data);
                renderClips(data);
                setupRemixSegments(data);
                enableNavButtons();
                switchView('dashboard');

                showToast('Demo loaded (client-side)! Explore the dashboard.', 'success');
            }

            btn.disabled = false;
            btn.innerHTML = '<span>🎮</span> Try Demo';
        });
    }

    function generateClientDemoData() {
        const sentences = [
            "Welcome to this masterclass on building products that people actually want.",
            "The biggest mistake I see founders make is building something nobody asked for.",
            "Let me tell you a secret that changed how I think about product development.",
            "Most people think you need a perfect product to launch. That's completely wrong.",
            "The truth is, your first version should be embarrassingly simple.",
            "I spent three years building the wrong thing. Here's what I learned.",
            "Stop focusing on features. Start focusing on the one problem you solve.",
            "The game-changer was when I realized users don't care about your technology.",
            "They care about whether you solve their problem faster than the alternative.",
            "If you're building a startup right now, stop and listen to this carefully.",
            "The number one reason startups fail isn't money. It's building the wrong thing.",
            "Here's the framework I use: Problem, Solution, Validation. In that order.",
            "Never skip validation. I made this mistake and it cost me everything.",
            "The best products I've built started with a conversation, not a codebase.",
            "Talk to 50 users before writing a single line of code. This is non-negotiable.",
            "Here's the shocking truth: your idea doesn't matter. Execution is everything.",
            "The difference between a successful startup and a failed one is speed.",
            "Move fast, break things, but always listen to your users.",
        ];

        let currentTime = 0;
        const transcript = sentences.map(text => {
            const dur = 7 + Math.random() * 5;
            const seg = { start: +currentTime.toFixed(2), end: +(currentTime + dur).toFixed(2), text, confidence: +(0.85 + Math.random() * 0.13).toFixed(2) };
            currentTime += dur;
            return seg;
        });

        const duration = currentTime;
        const viralIndices = [2, 3, 5, 7, 10, 12, 15];

        const segments = [];
        for (let idx = 0; idx < sentences.length - 1; idx += 2) {
            const start = transcript[idx].start;
            const end = transcript[Math.min(idx + 1, transcript.length - 1)].end;
            const text = sentences.slice(idx, idx + 2).join(' ');
            const isViral = viralIndices.includes(idx);
            const score = isViral ? 65 + Math.floor(Math.random() * 30) : 25 + Math.floor(Math.random() * 35);

            const keywords = [];
            ['secret', 'mistake', 'truth', 'game-changer', 'shocking', 'never', 'stop'].forEach(kw => {
                if (text.toLowerCase().includes(kw)) keywords.push(kw);
            });

            const reasons = [];
            if (score > 70) { reasons.push('🔥 High emotional intensity detected'); reasons.push('⚡ Peak audio energy'); }
            if (keywords.length) reasons.push('🎯 Contains viral triggers: ' + keywords.join(', '));
            if (score > 60) reasons.push('🗣️ Dynamic speech pacing');
            if (!reasons.length) reasons.push('📊 Moderate viral potential');

            const dominant = isViral ? (Math.random() > 0.5 ? 'excitement' : 'surprise') : 'neutral';

            segments.push({
                id: Math.random().toString(36).substr(2, 8),
                start, end, duration: +(end - start).toFixed(2),
                virality_score: score,
                transcript: text,
                emotion: {
                    joy: +(Math.random() * 0.8).toFixed(2),
                    surprise: +(isViral ? 0.4 + Math.random() * 0.5 : Math.random() * 0.3).toFixed(2),
                    anger: +(Math.random() * 0.2).toFixed(2),
                    sadness: +(Math.random() * 0.15).toFixed(2),
                    fear: +(Math.random() * 0.1).toFixed(2),
                    excitement: +(isViral ? 0.5 + Math.random() * 0.45 : Math.random() * 0.4).toFixed(2),
                    dominant,
                },
                keywords,
                hooks: [
                    "Nobody tells you this about building products…",
                    "This mistake cost me 3 years of wasted effort",
                    "If you're building a startup, STOP and watch this",
                ],
                reasons,
            });
        }

        segments.sort((a, b) => b.virality_score - a.virality_score);

        const attention_timeline = [];
        for (let t = 0; t < duration; t++) {
            let base = 0.3;
            segments.forEach(seg => { if (seg.start <= t && t <= seg.end) base = seg.virality_score / 120 + 0.2; });
            const noise = (Math.random() - 0.5) * 0.16;
            const wave = Math.sin(t * 0.15) * 0.1;
            const score = Math.max(0.05, Math.min(0.98, base + noise + wave));
            let reason = 'Baseline';
            if (score > 0.7) reason = '🔥 High virality zone';
            else if (score > 0.5) reason = '📈 Rising engagement';
            else if (score < 0.25) reason = '📉 Drop-off zone';
            attention_timeline.push({ timestamp: t, score: +score.toFixed(3), reason });
        }

        const audio_features = [];
        for (let t = 0; t < duration; t++) {
            const p1 = Math.sin(t * 0.12) * 0.3 + 0.45;
            const p2 = Math.sin(t * 0.08 + 1.5) * 0.25 + 0.5;
            const p3 = Math.sin(t * 0.1 + 0.7) * 0.2 + 0.5;
            const n = Math.random() * 0.12;
            let boost = 0;
            segments.forEach(seg => { if (seg.start <= t && t <= seg.end && seg.virality_score > 65) boost = 0.2; });
            audio_features.push({
                timestamp: t,
                energy: +Math.max(0, Math.min(1, p1 + n + boost)).toFixed(4),
                pitch: +Math.max(0, Math.min(1, p2 + n * 0.5 + boost * 0.5)).toFixed(4),
                speech_rate: +Math.max(0, Math.min(1, p3 + n * 0.3)).toFixed(4),
                intensity: +Math.max(0, Math.min(1, (p1 + p2) / 2 + n + boost)).toFixed(4),
            });
        }

        return {
            job_id: 'demo-client',
            filename: 'startup_masterclass.mp4',
            duration,
            transcript,
            segments,
            attention_timeline,
            audio_features,
            face_regions: [],
            overall_stats: {
                total_duration: +duration.toFixed(2),
                segments_found: segments.length,
                avg_virality_score: +(segments.reduce((s, x) => s + x.virality_score, 0) / segments.length).toFixed(1),
                top_score: Math.max(...segments.map(s => s.virality_score)),
                high_virality_count: segments.filter(s => s.virality_score >= 70).length,
                transcript_word_count: transcript.reduce((s, t) => s + t.text.split(' ').length, 0),
            },
            processed_at: new Date().toISOString(),
        };
    }

    // ═══ UTILITIES ═══════════════════════════════════════════

    function setText(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    function escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    function escapeAttr(str) {
        if (!str) return '';
        return str.replace(/'/g, "\\'").replace(/"/g, '\\"').replace(/\n/g, '\\n');
    }

    function capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function getEmotionEmoji(emotion) {
        const map = {
            joy: '😊', surprise: '😲', anger: '😠',
            sadness: '😢', fear: '😰', excitement: '🤩',
            neutral: '😐',
        };
        return map[emotion] || '😐';
    }

    window.copyToClipboard = function (text) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Copied to clipboard!', 'success');
        }).catch(() => {
            // Fallback
            const ta = document.createElement('textarea');
            ta.value = text;
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            showToast('Copied to clipboard!', 'success');
        });
    };

    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
            <span>${message}</span>
        `;

        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

})();
