/**
 * AttentionX — API Client
 * Handles all communication with the FastAPI backend
 */

const API_BASE = window.location.origin + '/api';

const api = {
    /**
     * Upload a video file for processing
     */
    async uploadVideo(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            throw new Error(err.detail || `Upload failed: ${response.status}`);
        }

        return response.json();
    },

    /**
     * Check processing status
     */
    async getStatus(jobId) {
        const response = await fetch(`${API_BASE}/status/${jobId}`);
        if (!response.ok) throw new Error('Failed to get status');
        return response.json();
    },

    /**
     * Get full analysis results
     */
    async getAnalysis(jobId) {
        const response = await fetch(`${API_BASE}/analysis/${jobId}`);
        if (!response.ok && response.status !== 202) {
            throw new Error('Failed to get analysis');
        }
        return response.json();
    },

    /**
     * Generate hooks for a segment
     */
    async generateHooks(jobId, segmentId, style = 'curiosity', count = 3) {
        const response = await fetch(`${API_BASE}/generate-hooks`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: jobId,
                segment_id: segmentId,
                style,
                count,
            }),
        });

        if (!response.ok) throw new Error('Failed to generate hooks');
        return response.json();
    },

    /**
     * Adapt content for a persona
     */
    async adaptPersona(jobId, segmentId, persona, text) {
        const response = await fetch(`${API_BASE}/adapt-persona`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: jobId,
                segment_id: segmentId,
                persona,
                text,
            }),
        });

        if (!response.ok) throw new Error('Failed to adapt persona');
        return response.json();
    },

    /**
     * Remix content for a platform
     */
    async remixContent(jobId, segmentId, platform, text) {
        const response = await fetch(`${API_BASE}/remix`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: jobId,
                segment_id: segmentId,
                platform,
                text,
            }),
        });

        if (!response.ok) throw new Error('Failed to remix content');
        return response.json();
    },

    /**
     * Build a story from segments
     */
    async buildStory(jobId, segmentIds, narrativeStyle = 'problem_insight_solution') {
        const response = await fetch(`${API_BASE}/story-builder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: jobId,
                segment_ids: segmentIds,
                narrative_style: narrativeStyle,
            }),
        });

        if (!response.ok) throw new Error('Failed to build story');
        return response.json();
    },

    /**
     * Export a clip
     */
    async exportClip(jobId, segmentId, format = 'vertical', addCaptions = true) {
        const response = await fetch(`${API_BASE}/export-clip`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                job_id: jobId,
                segment_id: segmentId,
                format,
                add_captions: addCaptions,
            }),
        });

        if (!response.ok) throw new Error('Failed to export clip');

        // If response is a file, download it
        const contentType = response.headers.get('Content-Type') || '';
        if (contentType.includes('video') || contentType.includes('octet-stream')) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `attentionx_clip_${segmentId}.mp4`;
            a.click();
            URL.revokeObjectURL(url);
            return { success: true };
        }

        // JSON response (demo mode)
        return await response.json();
    },

    /**
     * Get demo data (no upload needed)
     */
    async getDemo() {
        const response = await fetch(`${API_BASE}/demo`);
        if (!response.ok) throw new Error('Failed to load demo');
        return response.json();
    },

    /**
     * Health check
     */
    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE}/health`);
            return response.ok;
        } catch {
            return false;
        }
    },
};
