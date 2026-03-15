'use strict';
// static/js/app.js
const POLL_INTERVAL = 5000;

async function loadHUD() {
  try {
    const state = await OrionAPI.getCurrentScan();
    const allDevices = await OrionAPI.getDevices();
    const intel = await OrionAPI.getIntelEvents(10);

    // Counts
    document.getElementById('wifi-count').textContent = state.wifi_count || 0;
    document.getElementById('ble-count').textContent = state.ble_count || 0;
    document.getElementById('net-count').textContent = state.network_count || 0;

    // Stats
    const allDevList = allDevices.devices || [];
    const alertDevs = allDevList.filter(d => d.risk_score >= 60);
    const newDevs = allDevList.filter(d => d.classification === 'new');
    const staticDevs = allDevList.filter(d => d.classification === 'static');

    document.getElementById('stat-total').textContent = allDevList.length;
    document.getElementById('stat-alerts').textContent = alertDevs.length;
    document.getElementById('stat-new').textContent = newDevs.length;
    document.getElementById('stat-static').textContent = staticDevs.length;

    // Radar
    const radarDevs = [
      ...state.wifi.map(d => ({ ...d, device_type: 'wifi' })),
      ...state.ble.map(d => ({ ...d, device_type: 'ble' })),
      ...state.network.map(d => ({ ...d, device_type: 'network' }))
    ];
    if (window.RadarCanvas) RadarCanvas.setDevices(radarDevs);

    // Live device list
    renderLiveDevices(allDevList.slice(0, 30));

    // Intel feed
    renderIntelFeed(intel.events || []);

    // Alert banners
    const criticalAlerts = (intel.events || []).filter(
      e => e.severity === 'critical' && !e.acknowledged
    );
    if (criticalAlerts.length > 0) {
      showAlertBanner(criticalAlerts[0]);
    }

    document.getElementById('last-scan-time').textContent =
      new Date().toLocaleTimeString();

  } catch (err) {
    const indicator = document.getElementById('scan-indicator');
    if (indicator) indicator.classList.add('offline');
    console.error('HUD load error:', err);
  }
}

function renderLiveDevices(devices) {
  const container = document.getElementById('live-device-list');
  if (!container) return;
  container.innerHTML = devices.map(d => {
    const score = d.risk_score || 0;
    const riskClass = score >= 70 ? 'risk-high' : score >= 40 ? 'risk-medium' :
                      d.classification === 'new' ? 'risk-new' : '';
    const scoreClass = score >= 70 ? 'score-alert' : score >= 40 ? 'score-warn' : 'score-ok';
    const typeLabel = { wifi: 'WF', ble: 'BT', network: 'LAN' }[d.device_type] || 'UK';
    const name = d.ssid || d.name || d.mac || 'Unknown';
    return `
      <div class="device-row ${riskClass}" onclick="window.location='/devices'">
        <div class="device-row-icon">${typeLabel}</div>
        <div class="device-row-info">
          <div class="device-row-ssid">${escHtml(name)}</div>
          <div class="device-row-meta">
            <span>${escHtml(d.vendor || 'Unknown')}</span>
            <span>${d.rssi ? d.rssi + 'dBm' : ''}</span>
            <span class="mono">${escHtml((d.mac || '').substring(0, 8))}</span>
          </div>
        </div>
        <div class="device-row-score ${scoreClass}">${score}</div>
      </div>`;
  }).join('');
}

function renderIntelFeed(events) {
  const container = document.getElementById('intel-feed');
  if (!container) return;
  container.innerHTML = events.slice(0, 10).map(e => `
    <div class="intel-event">
      <span class="intel-sev sev-${e.severity}">${e.severity}</span>
      <span class="intel-title">${escHtml(e.title)}</span>
      <span class="intel-time">${formatTime(e.event_time)}</span>
    </div>`).join('');
}

function showAlertBanner(event) {
  const container = document.getElementById('alert-container');
  if (!container) return;
  container.innerHTML = `
    <div class="alert-banner">
      WARNING: ${escHtml(event.title)}
      <button type="button" class="btn btn-danger ml-auto" onclick="ackAlert(${event.id})">
        Acknowledge
      </button>
    </div>`;
}

async function ackAlert(id) {
  await OrionAPI.ackIntelEvent(id);
  document.getElementById('alert-container').innerHTML = '';
}

async function triggerScan(type) {
  await OrionAPI.triggerScan(type);
  setTimeout(loadHUD, 2000);
}

// Init
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('radar-canvas')) {
    RadarCanvas.init('radar-canvas');
  }
  loadHUD();
  setInterval(loadHUD, POLL_INTERVAL);
});
