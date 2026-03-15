'use strict';
// static/js/alerts.js

async function loadAlerts() {
  try {
    const data = await OrionAPI.getAlerts(100);
    const alerts = data.alerts || [];
    renderAlerts(alerts);
  } catch (err) {
    console.error('Alerts load error:', err);
  }
}

function renderAlerts(alerts) {
  const container = document.getElementById('alerts-list');
  if (!container) return;

  if (alerts.length === 0) {
    container.innerHTML = '<div class="card text-center p-40"><span class="dim">No alerts</span></div>';
    return;
  }

  container.innerHTML = alerts.map(a => `
    <div class="alert-card ${a.severity} ${a.acknowledged ? 'acked' : ''}">
      <div class="alert-icon ${a.severity}">!</div>
      <div class="alert-body">
        <div class="alert-title">${escHtml(a.title)}</div>
        <div class="alert-detail">${escHtml(a.detail || '')}</div>
        <div class="alert-time">${escHtml(a.event_time)} | ${escHtml(a.device_mac || '')}</div>
      </div>
      <div class="alert-actions">
        ${!a.acknowledged ? `<button type="button" class="btn" onclick="ackSingleAlert(${a.id})">ACK</button>` : '<span class="dim mono text-xs">ACKED</span>'}
      </div>
    </div>
  `).join('');
}

async function ackSingleAlert(id) {
  await OrionAPI.ackAlert(id);
  loadAlerts();
}

async function ackAllAlerts() {
  await OrionAPI.ackAllAlerts();
  loadAlerts();
}

async function loadAlertRules() {
  try {
    const data = await OrionAPI.getAlertRules();
    const rules = data.rules || [];
    const container = document.getElementById('alert-rules');
    if (!container) return;
    container.innerHTML = `
      <table class="data-table">
        <thead><tr><th>Rule</th><th>Severity</th><th>Description</th></tr></thead>
        <tbody>
          ${rules.map(r => `<tr>
            <td class="alert-rule-name">${escHtml(r.name)}</td>
            <td><span class="risk-badge risk-${r.severity === 'critical' ? 'critical' : r.severity === 'high' ? 'high' : 'medium'}">${r.severity}</span></td>
            <td>${escHtml(r.title)}</td>
          </tr>`).join('')}
        </tbody>
      </table>
    `;
  } catch (err) {
    console.error('Rules load error:', err);
  }
}
