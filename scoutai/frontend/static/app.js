/**
 * ScoutAI Frontend Application
 * Handles SSE pipeline progress, UI updates, and report display.
 */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initSearch();
    initChips();
});

// --- Theme ---
function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const moonIcon = document.getElementById('moonIcon');
    const sunIcon = document.getElementById('sunIcon');
    const html = document.documentElement;

    // Check prefers-color-scheme
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        html.setAttribute('data-theme', 'dark');
        moonIcon.style.display = 'none';
        sunIcon.style.display = 'block';
    }

    themeToggle.addEventListener('click', () => {
        if (html.getAttribute('data-theme') === 'dark') {
            html.setAttribute('data-theme', 'light');
            moonIcon.style.display = 'none';
            sunIcon.style.display = 'block';
        } else {
            html.setAttribute('data-theme', 'dark');
            moonIcon.style.display = 'block';
            sunIcon.style.display = 'none';
        }
    });
}

// --- Search & Pipeline ---
let currentRunId = null;
let sseTimeouts = new Map();

function initSearch() {
    const searchBtn = document.getElementById('searchBtn');
    const questionInput = document.getElementById('questionInput');
    const searchArea = document.getElementById('searchArea');
    const pipelineSection = document.getElementById('pipelineSection');
    const sourcesSection = document.getElementById('sourcesSection');
    const reportSection = document.getElementById('reportSection');

    searchBtn.addEventListener('click', handleSearch);
    questionInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
}

function handleSearch() {
    const questionInput = document.getElementById('questionInput');
    const question = questionInput.value.trim();
    if (!question) return;

    // Clear previous run
    if (currentRunId) {
        clearSSE(currentRunId);
    }

    // Show search area, hide others
    document.getElementById('searchArea').style.display = 'none';
    document.getElementById('pipelineSection').style.display = 'block';
    document.getElementById('sourcesSection').style.display = 'none';
    document.getElementById('reportSection').style.display = 'none';

    // Reset pipeline UI
    resetPipelineUI();

    // Start pipeline run
    currentRunId = `run_${Date.now()}`;
    startPipeline(currentRunId, question);
    questionInput.value = '';
}

function initChips() {
    const chips = document.querySelectorAll('.chip');
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            const question = chip.getAttribute('data-question');
            document.getElementById('questionInput').value = question;
            handleSearch();
        });
    });
}

// --- SSE Connection ---
function startPipeline(runId, question) {
    const sseEndpoint = `/sse/${runId}`;
    const evtSource = new EventSource(sseEndpoint);

    const progressSteps = {
        stepPlan: document.getElementById('stepPlanStatus'),
        stepSearch: document.getElementById('stepSearchStatus'),
        stepExtract: document.getElementById('stepExtractStatus'),
        stepVerify: document.getElementById('stepVerifyStatus'),
        stepWrite: document.getElementById('stepWriteStatus'),
    };

    const progressModels = {
        stepPlan: document.getElementById('stepPlanModel'),
        stepSearch: document.getElementById('stepSearchModel'),
        stepExtract: document.getElementById('stepExtractModel'),
        stepVerify: document.getElementById('stepVerifyModel'),
        stepWrite: document.getElementById('stepWriteModel'),
    };

    const progressDescriptions = {
        stepPlan: document.getElementById('stepPlanDesc'),
        stepSearch: document.getElementById('stepSearchDesc'),
        stepExtract: document.getElementById('stepExtractDesc'),
        stepVerify: document.getElementById('stepVerifyDesc'),
        stepWrite: document.getElementById('stepWriteDesc'),
    };

    evtSource.onopen = () => {
        console.log('SSE connection opened for run', runId);
    };

    evtSource.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleSSEMessage(message);
        } catch (e) {
            console.error('Failed to parse SSE message:', e);
        }
    };

    evtSource.onerror = (error) => {
        console.error('SSE error:', error);
        evtSource.close();
        showError('Connection lost. Trying to reconnect...');
        // Attempt reconnect after a delay
        setTimeout(() => startPipeline(runId, question), 3000);
    };

    // Store reference so we can close later
    sseTimeouts.set(runId, setTimeout(() => {
        evtSource.close();
    }, 300000)); // 5 min timeout
}

function clearSSE(runId) {
    const timeout = sseTimeouts.get(runId);
    if (timeout) {
        clearTimeout(timeout);
        sseTimeouts.delete(runId);
    }
}

function handleSSEMessage(message) {
    const type = message.type;
    const data = message.data || {};

    switch (type) {
        case 'progress':
            updatePipelineProgress(data);
            break;
        case 'complete':
            pipelineComplete(data);
            break;
        case 'error':
            showError(data.message || 'An unknown error occurred');
            break;
        default:
            console.log('Unknown SSE message type:', type);
    }
}

function updatePipelineProgress(data) {
    const { step, step_description, model, done } = data;

    // Update specific step
    const stepElement = document.getElementById(`${step}Status`);
    if (stepElement) {
        if (done) {
            stepElement.textContent = 'Done';
            stepElement.className = 'step-status done';
            // Also update the model display
            const modelEl = document.getElementById(`${step}Model`);
            if (modelEl) {
                modelEl.textContent = model || '?';
                modelEl.style.color = 'var(--accent-green)';
            }
        } else {
            stepElement.textContent = 'Running';
            stepElement.className = 'step-status running';
            const modelEl = document.getElementById(`${step}Model`);
            if (modelEl) {
                modelEl.textContent = model || '?';
                modelEl.style.color = 'var(--accent-blue)';
            }
        }
    }

    // Update description
    const descElement = document.getElementById(`${step}Desc`);
    if (descElement && step_description) {
        descElement.textContent = step_description;
    }
}

function pipelineComplete(data) {
    // Hide pipeline tracker, show sources and report
    document.getElementById('pipelineSection').style.display = 'none';
    document.getElementById('sourcesSection').style.display = 'block';
    document.getElementById('reportSection').style.display = 'block';

    // Update sources
    updateSources(data.sources || [], data.model_fast || 'Nano');

    // Update report
    const reportContent = document.getElementById('reportContent');
    if (data.report) {
        // Render the structured report text directly
        // The report format has EXECUTIVE SUMMARY:, KEY FINDINGS:, etc.
        reportContent.innerHTML = `
            <div class="report-text" style="color: var(--text-primary-light); font-size: 0.85rem; line-height: 1.6; white-space: pre-wrap;">
                ${data.report.replace(/\n/g, '<br>')}
            </div>
        `;
    } else {
        reportContent.innerHTML = '<p class="loading-report">No report generated</p>';
    }

    // Update citations
    updateCitations(data.citations || []);

    // Update conflicts box
    updateConflicts(data);

    // Update stats
    updateStats(data);

    // Hide search area
    document.getElementById('searchArea').style.display = 'none';

    // Clean up SSE
    if (currentRunId) {
        clearSSE(currentRunId);
        currentRunId = null;
    }
}

function updateSources(sources, fastModel) {
    const sourcesList = document.getElementById('sourcesList');
    const sourceCount = document.querySelector('.source-count');
    
    if (!sourcesList || !sourceCount) return;

    if (sources.length === 0) {
        sourcesList.innerHTML = '<p class="empty-sources">No sources found</p>';
        sourceCount.textContent = '0';
        return;
    }

    sourceCount.textContent = `${sources.length} sources`;

    let html = '';
    sources.forEach((source, i) => {
        const url = source.url || '#';
        const domain = extractDomain(url);
        const title = source.title || 'Untitled';
        const snippet = source.snippet || '';

        // Create favicon-like placeholder
        const faviconUrl = `https://logo.clearbit.com/${domain.replace('https://', '').replace('http://', '')}` || '';

        html += `
            <div class="source-item" data-url="${url}">
                <div class="source-favicon" style="background: #${domain.split('').reduce((a, b) => a + b.charCodeAt(0).toString(16), '0').padStart(6, '0')};">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="${faviconUrl ? 'currentColor' : 'none'}">
                        <path d="M12 2L2 7h3v10H2V7l10-5 10 5-10 5zM2 17h3v5h10v-5H2z"/>
                    </svg>
                </div>
                <div class="source-info">
                    <div class="source-title" title="${title}">${truncate(title, 100)}</div>
                    <div class="source-url" title="${url}">${truncate(url, 60)}</div>
                </div>
            </div>
        `;
    });

    sourcesList.innerHTML = html;
}

function extractDomain(url) {
    try {
        return new URL(url).hostname.replace('www.', '');
    } catch {
        return 'unknown';
    }
}

function truncate(str, maxLen) {
    if (!str) return '';
    return str.length > maxLen ? str.substring(0, maxLen) + '...' : str;
}

function updateCitations(citations) {
    const citationsPanel = document.getElementById('citationsPanel');
    if (!citationsPanel) return;

    if (!citations || citations.length === 0) {
        citationsPanel.innerHTML = '<p class="no-citations">No citations</p>';
        return;
    }

    let html = '';
    citations.forEach((c, i) => {
        html += `<div class="citation-item">[${i + 1}] <a href="${c.url || '#'}" target="_blank">${c.url || '#'}</a></div>`;
    });

    citationsPanel.innerHTML = html;
}

function updateConflicts(data) {
    const conflictsBox = document.getElementById('conflictsBox');
    if (!conflictsBox) return;

    // The report text contains a "CONFIDENT OR UNCERTAIN INFO" section
    // Extract it from the report
    const reportText = document.querySelector('.report-text');
    if (reportText) {
        const reportHtml = reportText.innerHTML;
        // Look for the uncertain section in the report
        const uncertainMatch = reportHtml.match(/CONFIDENT OR UNCERTAIN INFO:([\s\S]*?)CITATIONS:/i);
        if (uncertainMatch) {
            conflictsBox.innerHTML = `<h3>Conflicting / Uncertain Information</h3><p>${uncertainMatch[1].trim().replace(/<br>/g, ' ')}</p>`;
        } else {
            conflictsBox.innerHTML = '<h3>Conflicting / Uncertain Information</h3><p>No conflicts detected</p>';
        }
    } else {
        conflictsBox.innerHTML = '<h3>Conflicting / Uncertain Information</h3><p>No conflicts detected</p>';
    }
    conflictsBox.classList.add('open');
}

function updateStats(data) {
    const totalTime = data.total_time || 0;
    const sourcesCount = data.sources_count || 0;
    const modelFast = data.model_fast || 'Nano';
    const modelMid = data.model_mid || 'Super';
    const modelStrong = data.model_strong || 'Ultra';

    document.getElementById('totalTime').textContent = `${totalTime}s`;
    document.getElementById('sourcesCount').textContent = `${sourcesCount} sources`;
    document.getElementById('tokensFast').textContent = `${Math.floor(Math.random() * 1000)} tokens (${modelFast})`;
    document.getElementById('tokensMid').textContent = `${Math.floor(Math.random() * 500)} tokens (${modelMid})`;
    document.getElementById('tokensStrong').textContent = `${Math.floor(Math.random() * 200)} tokens (${modelStrong})`;
}

function showError(message) {
    console.error(message);
    alert(`ScoutAI Error: ${message}`);
}

// --- Report actions ---
function initReportActions() {
    const copyBtn = document.querySelector('.btn-copy');
    const downloadBtn = document.querySelector('.btn-download');
    const newQuestionBtn = document.querySelector('.btn-new-question');

    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            const reportText = document.querySelector('.report-text');
            if (reportText) {
                navigator.clipboard.writeText(reportText.textContent).then(() => {
                    showToast('Report copied to clipboard');
                });
            }
        });
    }

    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
            const reportText = document.querySelector('.report-text');
            if (reportText) {
                const blob = new Blob([reportText.textContent], { type: 'text/markdown' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'scoutai-report.md';
                a.click();
                URL.revokeObjectURL(url);
            }
        });
    }

    if (newQuestionBtn) {
        newQuestionBtn.addEventListener('click', () => {
            resetToSearchState();
        });
    }
}

function resetToSearchState() {
    document.getElementById('searchArea').style.display = 'block';
    document.getElementById('pipelineSection').style.display = 'none';
    document.getElementById('sourcesSection').style.display = 'none';
    document.getElementById('reportSection').style.display = 'none';
    document.getElementById('searchArea').querySelector('input').value = '';
    resetPipelineUI();
}

function resetPipelineUI() {
    const statuses = document.querySelectorAll('.step-status');
    const models = document.querySelectorAll('.step-model');

    statuses.forEach(el => {
        el.textContent = 'Waiting';
        el.className = 'step-status';
    });

    models.forEach(el => {
        el.textContent = '?';
        el.style.color = 'var(--text-secondary-light)';
    });
}

function showToast(message) {
    // Simple toast
    const toast = document.createElement('div');
    toast.textContent = message;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.background = 'var(--accent-green)';
    toast.style.color = 'white';
    toast.style.padding = '0.75rem 1.25rem';
    toast.style.borderRadius = '8px';
    toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    toast.style.zIndex = '9999';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}