'use strict';
// static/js/devices.js
let allDevicesData = [];
let currentTypeFilter = 'all';
let currentSearch = '';

async function loadDevices() {
  try {
    const data = await OrionAPI.getDevices();
    allDevicesData = data.devices || [];
    renderDeviceTable(getFilteredDevices());
  } catch (err) {
    console.error('Devices load error:', err);
  }
}

function getFilteredDevices() {
  let devices = allDevicesData;
  if (currentTypeFilter !== 'all') {
    devices = devices.filter(d => d.device_type === currentTypeFilter);
  }
  if (currentSearch) {
    const q = currentSearch.toLowerCase();
    devices = devices.filter(d =>
      (d.mac || '').toLowerCase().includes(q) ||
      (d.ssid || '').toLowerCase().includes(q) ||
      (d.vendor || '').toLowerCase().includes(q) ||
      (d.name || '').toLowerCase().includes(q)
    );
  }
  return devices;
}

function setTypeFilter(type, btn) {
  currentTypeFilter = type;
  document.querySelectorAll('.type-tab').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderDeviceTable(getFilteredDevices());
}

function filterDevices() {
  currentSearch = document.getElementById('device-search').value;
  renderDeviceTable(getFilteredDevices());
}

function renderDeviceTable(devices) {
  const tbody = document.getElementById('device-tbody');
  const countEl = document.getElementById('device-count');
  if (!tbody) return;
  if (countEl) countEl.textContent = `${devices.length} devices`;

  // Sort by risk score descending
  const sorted = [...devices].sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0));

  tbody.innerHTML = sorted.map(d => {
    const score = d.risk_score || 0;
    const riskClass = score >= 70 ? 'risk-critical' : score >= 50 ? 'risk-high' :
                      score >= 30 ? 'risk-medium' : 'risk-low';
    const classLabel = d.classification || 'unknown';
    const classCSS = {
      'new': 'device-class-new',
      'transient': 'device-class-transient',
      'static': 'device-class-static',
      'baseline': 'device-class-baseline',
      'mobile': 'device-class-mobile',
      'recurring': 'device-class-recurring'
    }[classLabel] || 'device-class-unknown';

    return `<tr>
      <td><span class="risk-badge ${riskClass}">${score}</span></td>
      <td class="device-type-cell">${d.device_type}</td>
      <td class="mac-cell">${escHtml(d.mac || '')}</td>
      <td>${escHtml(d.ssid || d.name || '')}</td>
      <td class="vendor-cell">${escHtml(d.vendor || 'Unknown')}</td>
      <td class="${classCSS}">${classLabel}</td>
      <td class="rssi-cell">${d.rssi || '—'}</td>
      <td class="device-security-cell">${escHtml(d.security || '—')}</td>
      <td class="device-lastseen-cell">${formatTime(d.last_seen)}</td>
      <td class="device-scans-cell">${d.scan_count || 1}</td>
    </tr>`;
  }).join('');
}

document.addEventListener('DOMContentLoaded', () => {
  loadDevices();
  setInterval(loadDevices, 10000);
});
