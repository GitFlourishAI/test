const API_BASE = '';

let currentRunId = null;
let selectedCatalystIdx = null;

async function fetchJSON(url) {
    const res = await fetch(`${API_BASE}${url}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
}

function formatUSD(value) {
    if (!value && value !== 0) return '--';
    const abs = Math.abs(value);
    const sign = value < 0 ? '-' : '';
    if (abs >= 1e9) return `${sign}$${(abs / 1e9).toFixed(1)}B`;
    if (abs >= 1e6) return `${sign}$${(abs / 1e6).toFixed(0)}M`;
    if (abs >= 1e3) return `${sign}$${(abs / 1e3).toFixed(0)}K`;
    return `${sign}$${abs.toLocaleString()}`;
}

function formatDate(isoStr) {
    if (!isoStr) return '--';
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric',
        hour: '2-digit', minute: '2-digit'
    });
}

function formatDateShort(isoStr) {
    if (!isoStr) return '--';
    const d = new Date(isoStr);
    return d.toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
    });
}

function getConfidenceClass(pct) {
    if (pct >= 70) return 'high';
    if (pct >= 40) return 'mid';
    return 'low';
}

function getDirectionClass(dir) {
    if (!dir) return '';
    const d = dir.toLowerCase();
    if (d.includes('upside') || d.includes('up')) return 'upside';
    if (d.includes('downside') || d.includes('down')) return 'downside';
    return '';
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} active`;
    setTimeout(() => toast.classList.remove('active'), 4000);
}

function showLoading(show, text = 'Running analysis...', subtext = 'Processing through AI agents') {
    const overlay = document.getElementById('loadingOverlay');
    if (show) {
        overlay.querySelector('.loading-text').textContent = text;
        overlay.querySelector('.loading-subtext').textContent = subtext;
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}

async function loadStats() {
    try {
        const data = await fetchJSON('/api/stats');
        document.getElementById('statTotalRuns').textContent = data.total_runs || '0';
        document.getElementById('statTotalCatalysts').textContent = data.total_catalysts || '0';
        document.getElementById('statUpside').textContent = data.upside_count || '0';
        document.getElementById('statDownside').textContent = data.downside_count || '0';
        document.getElementById('statAvgConfidence').textContent =
            data.avg_confidence ? `${data.avg_confidence}%` : '--';
        document.getElementById('statTotalImpact').textContent =
            formatUSD(data.total_impact);

        document.getElementById('sideUpside').textContent = data.upside_count || '0';
        document.getElementById('sideDownside').textContent = data.downside_count || '0';
    } catch (e) {
        console.error('Failed to load stats:', e);
    }
}

async function loadLatestCatalysts() {
    try {
        const data = await fetchJSON('/api/catalysts/latest');
        currentRunId = data.run_id;

        const runTimeEl = document.getElementById('runTimestamp');
        if (data.run_time) {
            runTimeEl.textContent = `Last updated: ${formatDate(data.run_time)}`;
        } else {
            runTimeEl.textContent = 'No analysis runs yet';
        }

        renderCatalysts(data.catalysts);
    } catch (e) {
        console.error('Failed to load catalysts:', e);
        renderCatalysts([]);
    }
}

function renderCatalysts(catalysts) {
    const tbody = document.getElementById('catalystTableBody');
    const emptyState = document.getElementById('emptyState');

    if (!catalysts || catalysts.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'flex';
        return;
    }

    emptyState.style.display = 'none';

    tbody.innerHTML = catalysts.map((cat, idx) => {
        const dirClass = getDirectionClass(cat.direction);
        const confClass = getConfidenceClass(cat.confidence_pct);
        const isUp = dirClass === 'upside';
        const impactClass = isUp ? 'positive' : 'negative';
        const arrow = isUp ? '&#9650;' : '&#9660;';
        const dirLabel = isUp ? 'UPSIDE' : 'DOWNSIDE';

        return `
            <tr onclick="toggleExpand(${idx})" data-idx="${idx}">
                <td class="rank-cell">#${cat.rank}</td>
                <td class="ticker-cell">${escapeHtml(cat.ticker)}</td>
                <td>
                    <span class="direction-badge ${dirClass}">
                        <span class="direction-arrow">${arrow}</span>
                        ${dirLabel}
                    </span>
                </td>
                <td class="catalyst-text">${escapeHtml(cat.catalyst || '')}</td>
                <td class="impact-cell ${impactClass}">${formatUSD(cat.adjusted_impact_usd)}</td>
                <td class="confidence-cell">
                    <div class="confidence-bar-container">
                        <div class="confidence-bar">
                            <div class="confidence-bar-fill ${confClass}" style="width: ${cat.confidence_pct || 0}%"></div>
                        </div>
                        <span class="confidence-value">${cat.confidence_pct || 0}%</span>
                    </div>
                </td>
                <td><span class="horizon-badge">${escapeHtml(cat.time_horizon || '--')}</span></td>
            </tr>
            <tr class="expandable-row" id="expand-${idx}">
                <td colspan="7">
                    <div class="expandable-content">
                        <strong style="color: var(--text-primary); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">Summary</strong>
                        <p style="margin-top: 8px;">${escapeHtml(cat.summary || 'No summary available.')}</p>
                        <div class="detail-grid">
                            <div class="detail-item">
                                <div class="detail-item-label">Ticker</div>
                                <div class="detail-item-value">${escapeHtml(cat.ticker)}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-item-label">Direction</div>
                                <div class="detail-item-value" style="color: var(--${dirClass})">${dirLabel}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-item-label">Impact (USD)</div>
                                <div class="detail-item-value">${formatUSD(cat.adjusted_impact_usd)}</div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-item-label">Confidence</div>
                                <div class="detail-item-value">${cat.confidence_pct}%</div>
                            </div>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }).join('');

    updateDetailPanel(catalysts[0], 0);
}

function toggleExpand(idx) {
    const row = document.getElementById(`expand-${idx}`);
    const wasActive = row.classList.contains('active');

    document.querySelectorAll('.expandable-row').forEach(r => r.classList.remove('active'));

    if (!wasActive) {
        row.classList.add('active');
    }
}

function updateDetailPanel(cat, idx) {
    selectedCatalystIdx = idx;
    const panel = document.getElementById('detailPanel');
    if (!cat) {
        panel.innerHTML = '<div class="info-card-body"><p style="color: var(--text-muted); font-size: 13px;">Select a catalyst to view details.</p></div>';
        return;
    }

    const dirClass = getDirectionClass(cat.direction);
    panel.innerHTML = `
        <div class="info-card-body">
            <div class="detail-row">
                <span class="detail-label">Ticker</span>
                <span class="detail-value" style="color: var(--accent-blue)">${escapeHtml(cat.ticker)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Direction</span>
                <span class="detail-value" style="color: var(--${dirClass})">${cat.direction || '--'}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Impact</span>
                <span class="detail-value">${formatUSD(cat.adjusted_impact_usd)}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Confidence</span>
                <span class="detail-value">${cat.confidence_pct || 0}%</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Time Horizon</span>
                <span class="detail-value">${cat.time_horizon || '--'}</span>
            </div>
        </div>
        <div style="padding: 16px; border-top: 1px solid var(--border-primary);">
            <div style="font-size: 10px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;">Summary</div>
            <p style="font-size: 13px; line-height: 1.6; color: var(--text-secondary);">${escapeHtml(cat.summary || 'No summary available.')}</p>
        </div>
    `;
}

async function loadHistory() {
    try {
        const data = await fetchJSON('/api/catalysts/history');
        const list = document.getElementById('historyList');

        if (!data.runs || data.runs.length === 0) {
            list.innerHTML = '<li class="history-item" style="color: var(--text-muted); justify-content: center;">No history yet</li>';
            return;
        }

        list.innerHTML = data.runs.map(run => `
            <li class="history-item" onclick="loadRun('${run.run_id}')">
                <span class="history-time">${formatDateShort(run.run_time)}</span>
                <span class="history-count">${run.catalyst_count} catalysts</span>
            </li>
        `).join('');
    } catch (e) {
        console.error('Failed to load history:', e);
    }
}

async function loadRun(runId) {
    try {
        const data = await fetchJSON(`/api/catalysts/run/${runId}`);
        currentRunId = runId;
        renderCatalysts(data.catalysts);
        showToast(`Loaded run ${runId}`);
    } catch (e) {
        showToast('Failed to load run', 'error');
    }
}

async function runAnalysis() {
    const btn = document.getElementById('runAnalysisBtn');
    btn.disabled = true;
    showLoading(true, 'Running AI Analysis...', 'Reasoning > Verification > Calibration > Reporting');

    try {
        const res = await fetch(`${API_BASE}/api/run-analysis`, { method: 'POST' });
        const data = await res.json();

        if (res.ok) {
            showToast(`Analysis complete (Run: ${data.run_id})`);
            await Promise.all([loadLatestCatalysts(), loadStats(), loadHistory()]);
        } else {
            showToast(data.error || 'Analysis failed', 'error');
        }
    } catch (e) {
        showToast('Failed to run analysis', 'error');
    } finally {
        btn.disabled = false;
        showLoading(false);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function init() {
    await Promise.all([loadStats(), loadLatestCatalysts(), loadHistory()]);
}

document.addEventListener('DOMContentLoaded', init);
