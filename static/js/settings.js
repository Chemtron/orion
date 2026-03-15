'use strict';
// static/js/settings.js

async function loadSettings() {
  try {
    const data = await OrionAPI.getSettings();

    // Platform
    document.getElementById('platform-badge').textContent = data.platform;
    document.getElementById('platform-info').textContent =
      `${data.host}:${data.port} | Debug: ${data.debug}`;

    // Toggles
    document.getElementById('toggle-wifi').checked = data.enable_wifi_scan;
    document.getElementById('toggle-ble').checked = data.enable_ble_scan;
    document.getElementById('toggle-network').checked = data.enable_network_scan;
    document.getElementById('toggle-enrichment').checked = data.enable_enrichment;

    // Intervals
    document.getElementById('wifi-interval').value = data.wifi_scan_interval;
    document.getElementById('ble-interval').value = data.ble_scan_interval;
    document.getElementById('network-interval').value = data.network_scan_interval;

    // Enrichment status
    const es = data.enrichment_status || {};
    document.getElementById('enrichment-status').innerHTML = `
      <div class="enrichment-status-grid">
        ${Object.entries(es).map(([k, v]) => `
          <div class="enrichment-status-row">
            <span class="enrichment-status-key">${escHtml(k)}</span>
            <span class="${v ? 'enrichment-status-configured' : 'enrichment-status-notset'}">${v ? 'Configured' : 'Not set'}</span>
          </div>
        `).join('')}
      </div>
    `;
  } catch (err) {
    console.error('Settings load error:', err);
  }
}

async function updateToggle(key, value) {
  const data = {};
  data[key] = value;
  await OrionAPI.updateToggles(data);
}

async function saveIntervals() {
  await OrionAPI.updateIntervals({
    wifi_scan_interval: parseInt(document.getElementById('wifi-interval').value, 10),
    ble_scan_interval: parseInt(document.getElementById('ble-interval').value, 10),
    network_scan_interval: parseInt(document.getElementById('network-interval').value, 10),
  });
}

document.addEventListener('DOMContentLoaded', loadSettings);
