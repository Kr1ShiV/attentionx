/**
 * AttentionX — Visualizations
 * Canvas-based heatmap, waveform, and gauge rendering
 */

const Viz = {
    colors: {
        cold: '#3b82f6',
        cool: '#06b6d4',
        warm: '#f59e0b',
        hot: '#f97316',
        fire: '#ef4444',
        purple: '#7c3aed',
        purpleLight: '#a78bfa',
        bg: '#0d0d1a',
        grid: 'rgba(255,255,255,0.04)',
        text: 'rgba(255,255,255,0.4)',
    },

    /**
     * Get color for a 0-1 score value
     */
    scoreColor(score) {
        if (score >= 0.8) return this.colors.fire;
        if (score >= 0.6) return this.colors.hot;
        if (score >= 0.4) return this.colors.warm;
        if (score >= 0.2) return this.colors.cool;
        return this.colors.cold;
    },

    /**
     * Get color for virality score (0-100)
     */
    viralityColor(score) {
        if (score >= 80) return this.colors.fire;
        if (score >= 60) return this.colors.hot;
        if (score >= 40) return this.colors.warm;
        if (score >= 20) return this.colors.cool;
        return this.colors.cold;
    },

    /**
     * Get gradient for virality score
     */
    viralityGradient(score) {
        if (score >= 70) return 'linear-gradient(90deg, #ef4444, #f97316)';
        if (score >= 50) return 'linear-gradient(90deg, #f97316, #f59e0b)';
        if (score >= 30) return 'linear-gradient(90deg, #f59e0b, #06b6d4)';
        return 'linear-gradient(90deg, #3b82f6, #06b6d4)';
    },

    /**
     * Get badge class for virality score
     */
    viralityClass(score) {
        if (score >= 70) return 'high';
        if (score >= 45) return 'medium';
        return 'low';
    },

    /**
     * Format seconds to MM:SS
     */
    formatTime(seconds) {
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s.toString().padStart(2, '0')}`;
    },

    // ═══ ATTENTION HEATMAP ═══════════════════════════════════

    /**
     * Draw the attention heatmap on canvas
     */
    drawHeatmap(canvasId, attentionData, segments, duration) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !attentionData.length) return;

        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.parentElement.getBoundingClientRect();

        canvas.width = (rect.width - 48) * dpr;
        canvas.height = 180 * dpr;
        canvas.style.width = (rect.width - 48) + 'px';
        canvas.style.height = '180px';
        ctx.scale(dpr, dpr);

        const W = canvas.width / dpr;
        const H = canvas.height / dpr;
        const padLeft = 45;
        const padRight = 15;
        const padTop = 15;
        const padBottom = 30;
        const chartW = W - padLeft - padRight;
        const chartH = H - padTop - padBottom;

        // Clear
        ctx.clearRect(0, 0, W, H);

        // Grid lines
        ctx.strokeStyle = this.colors.grid;
        ctx.lineWidth = 0.5;
        for (let i = 0; i <= 4; i++) {
            const y = padTop + (chartH / 4) * i;
            ctx.beginPath();
            ctx.moveTo(padLeft, y);
            ctx.lineTo(W - padRight, y);
            ctx.stroke();
        }

        // Y-axis labels
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = this.colors.text;
        ctx.textAlign = 'right';
        ['1.0', '0.75', '0.5', '0.25', '0'].forEach((label, i) => {
            ctx.fillText(label, padLeft - 8, padTop + (chartH / 4) * i + 4);
        });

        // X-axis time labels
        ctx.textAlign = 'center';
        const timeSteps = Math.min(10, Math.floor(duration / 15));
        for (let i = 0; i <= timeSteps; i++) {
            const t = (duration / timeSteps) * i;
            const x = padLeft + (t / duration) * chartW;
            ctx.fillText(this.formatTime(t), x, H - 8);
        }

        // Draw heatmap bars
        const barWidth = Math.max(2, chartW / attentionData.length);

        attentionData.forEach((point, i) => {
            const x = padLeft + (point.timestamp / duration) * chartW;
            const barH = point.score * chartH;
            const y = padTop + chartH - barH;

            // Color based on score
            const color = this.scoreColor(point.score);

            // Gradient bar
            const grad = ctx.createLinearGradient(x, y, x, padTop + chartH);
            grad.addColorStop(0, color);
            grad.addColorStop(1, color + '10');
            ctx.fillStyle = grad;
            ctx.fillRect(x, y, barWidth - 0.5, barH);
        });

        // Draw segment markers
        if (segments) {
            segments.forEach(seg => {
                const x1 = padLeft + (seg.start / duration) * chartW;
                const x2 = padLeft + (seg.end / duration) * chartW;

                if (seg.virality_score >= 70) {
                    ctx.fillStyle = 'rgba(239, 68, 68, 0.08)';
                    ctx.fillRect(x1, padTop, x2 - x1, chartH);

                    // Top marker
                    ctx.fillStyle = this.colors.fire;
                    ctx.fillRect(x1, padTop - 3, x2 - x1, 3);
                }
            });
        }

        // Smooth curve overlay
        ctx.beginPath();
        ctx.strokeStyle = this.colors.purpleLight + '80';
        ctx.lineWidth = 1.5;

        attentionData.forEach((point, i) => {
            const x = padLeft + (point.timestamp / duration) * chartW;
            const y = padTop + chartH - (point.score * chartH);

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // Store data for tooltip
        canvas._heatmapData = { attentionData, duration, padLeft, padRight, padTop, chartW, chartH, W };
    },

    /**
     * Handle heatmap hover for tooltip
     */
    setupHeatmapTooltip(canvasId, tooltipId) {
        const canvas = document.getElementById(canvasId);
        const tooltip = document.getElementById(tooltipId);
        if (!canvas || !tooltip) return;

        canvas.addEventListener('mousemove', (e) => {
            const data = canvas._heatmapData;
            if (!data) return;

            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const relX = (x - data.padLeft) / data.chartW;

            if (relX < 0 || relX > 1) {
                tooltip.style.display = 'none';
                return;
            }

            const timestamp = relX * data.duration;
            const closest = data.attentionData.reduce((prev, curr) =>
                Math.abs(curr.timestamp - timestamp) < Math.abs(prev.timestamp - timestamp) ? curr : prev
            );

            tooltip.innerHTML = `
                <strong>${this.formatTime(closest.timestamp)}</strong><br>
                Score: ${(closest.score * 100).toFixed(0)}%<br>
                ${closest.reason || ''}
            `;
            tooltip.style.display = 'block';
            tooltip.style.left = (e.clientX - rect.left + 15) + 'px';
            tooltip.style.top = (e.clientY - rect.top - 30) + 'px';
        });

        canvas.addEventListener('mouseleave', () => {
            tooltip.style.display = 'none';
        });
    },

    // ═══ AUDIO WAVEFORM ══════════════════════════════════════

    /**
     * Draw audio waveform on canvas
     */
    drawWaveform(canvasId, audioFeatures, type = 'energy', duration) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || !audioFeatures.length) return;

        const ctx = canvas.getContext('2d');
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.parentElement.getBoundingClientRect();

        canvas.width = (rect.width - 48) * dpr;
        canvas.height = 130 * dpr;
        canvas.style.width = (rect.width - 48) + 'px';
        canvas.style.height = '130px';
        ctx.scale(dpr, dpr);

        const W = canvas.width / dpr;
        const H = canvas.height / dpr;
        const padLeft = 45;
        const padRight = 15;
        const padTop = 10;
        const padBottom = 25;
        const chartW = W - padLeft - padRight;
        const chartH = H - padTop - padBottom;

        ctx.clearRect(0, 0, W, H);

        // Grid
        ctx.strokeStyle = this.colors.grid;
        ctx.lineWidth = 0.5;
        for (let i = 0; i <= 3; i++) {
            const y = padTop + (chartH / 3) * i;
            ctx.beginPath();
            ctx.moveTo(padLeft, y);
            ctx.lineTo(W - padRight, y);
            ctx.stroke();
        }

        // Color map for types
        const colorMap = {
            energy: { main: '#7c3aed', fill: 'rgba(124, 58, 237, 0.2)' },
            pitch: { main: '#06b6d4', fill: 'rgba(6, 182, 212, 0.2)' },
            intensity: { main: '#f97316', fill: 'rgba(249, 115, 22, 0.2)' },
            speech_rate: { main: '#10b981', fill: 'rgba(16, 185, 129, 0.2)' },
        };

        const colors = colorMap[type] || colorMap.energy;

        // Draw filled area
        ctx.beginPath();
        ctx.moveTo(padLeft, padTop + chartH);

        audioFeatures.forEach((f) => {
            const x = padLeft + (f.timestamp / duration) * chartW;
            const val = f[type] || 0;
            const y = padTop + chartH - (val * chartH);
            ctx.lineTo(x, y);
        });

        ctx.lineTo(padLeft + chartW, padTop + chartH);
        ctx.closePath();

        const grad = ctx.createLinearGradient(0, padTop, 0, padTop + chartH);
        grad.addColorStop(0, colors.fill);
        grad.addColorStop(1, 'transparent');
        ctx.fillStyle = grad;
        ctx.fill();

        // Draw line
        ctx.beginPath();
        ctx.strokeStyle = colors.main;
        ctx.lineWidth = 2;

        audioFeatures.forEach((f, i) => {
            const x = padLeft + (f.timestamp / duration) * chartW;
            const val = f[type] || 0;
            const y = padTop + chartH - (val * chartH);

            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();

        // X-axis labels
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = this.colors.text;
        ctx.textAlign = 'center';
        const timeSteps = Math.min(8, Math.floor(duration / 20));
        for (let i = 0; i <= timeSteps; i++) {
            const t = (duration / timeSteps) * i;
            const x = padLeft + (t / duration) * chartW;
            ctx.fillText(this.formatTime(t), x, H - 5);
        }

        // Type label
        ctx.font = '11px Inter, sans-serif';
        ctx.fillStyle = colors.main;
        ctx.textAlign = 'left';
        ctx.fillText(type.replace('_', ' ').toUpperCase(), padLeft + 5, padTop + 14);
    },

    // ═══ VIRALITY GAUGE ══════════════════════════════════════

    /**
     * Create a small inline SVG gauge for virality score
     */
    createGaugeSVG(score, size = 60) {
        const radius = (size / 2) - 5;
        const circumference = 2 * Math.PI * radius;
        const progress = (score / 100) * circumference;
        const color = this.viralityColor(score);

        return `
            <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" style="transform: rotate(-90deg)">
                <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" 
                    stroke="rgba(255,255,255,0.05)" stroke-width="4"/>
                <circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" 
                    stroke="${color}" stroke-width="4" 
                    stroke-dasharray="${progress} ${circumference}"
                    stroke-linecap="round"
                    style="transition: stroke-dasharray 1s ease"/>
            </svg>
            <span style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
                font-family:'JetBrains Mono',monospace;font-size:${size/4}px;font-weight:700;
                color:${color};transform:none">${score}</span>
        `;
    },

    // ═══ RESIZE HANDLER ══════════════════════════════════════

    /**
     * Setup resize observer for canvas elements
     */
    setupResizeHandler(callback) {
        let resizeTimeout;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(callback, 200);
        });
    },
};
