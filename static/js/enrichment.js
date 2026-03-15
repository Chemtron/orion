'use strict';
// static/js/enrichment.js

async function lookupOUI() {
  const mac = document.getElementById('oui-mac').value.trim();
  if (!mac) return;
  const result = document.getElementById('oui-result');
  result.classList.remove('hidden');
  result.innerHTML = '<span class="dim">Looking up...</span>';
  try {
    const data = await OrionAPI.lookupOUI(mac);
    result.innerHTML = `
      <div class="enrich-field"><span class="enrich-field-label">MAC</span><span class="enrich-field-value">${escHtml(data.mac)}</span></div>
      <div class="enrich-field"><span class="enrich-field-label">Vendor</span><span class="enrich-field-value">${escHtml(data.vendor)}</span></div>
      <div class="enrich-field"><span class="enrich-field-label">Camera Vendor</span><span class="enrich-field-value ${data.is_camera ? 'color-alert' : 'color-ok'}">${data.is_camera ? 'YES' : 'No'}</span></div>
      <div class="enrich-field"><span class="enrich-field-label">Espressif</span><span class="enrich-field-value">${data.is_espressif ? 'YES' : 'No'}</span></div>
    `;
  } catch (err) {
    result.innerHTML = `<span class="enrich-error">Error: ${escHtml(err.message)}</span>`;
  }
}

async function analyzeSSID() {
  const ssid = document.getElementById('ssid-input').value.trim();
  if (!ssid) return;
  const result = document.getElementById('ssid-result');
  result.classList.remove('hidden');
  result.innerHTML = '<span class="dim">Analyzing...</span>';
  try {
    const data = await OrionAPI.analyzeSSID(ssid);
    let html = `
      <div class="enrich-field"><span class="enrich-field-label">SSID</span><span class="enrich-field-value">${escHtml(data.ssid)}</span></div>
      <div class="enrich-field"><span class="enrich-field-label">Hotspot</span><span class="enrich-field-value">${data.is_hotspot ? 'YES' : 'No'}</span></div>
    `;
    if (data.extracted_name) {
      html += `<div class="enrich-field"><span class="enrich-field-label">Extracted Name</span><span class="enrich-field-value color-warn">${escHtml(data.extracted_name)}</span></div>`;
    }
    if (data.isp) {
      html += `<div class="enrich-field"><span class="enrich-field-label">ISP</span><span class="enrich-field-value">${escHtml(data.isp)}</span></div>`;
    }
    if (data.flags.length) {
      html += `<div class="enrich-field"><span class="enrich-field-label">Flags</span><span class="enrich-field-value">${escHtml(data.flags.join(', '))}</span></div>`;
    }
    if (data.risk_intel.length) {
      html += `<div class="enrich-intel-section"><span class="enrich-field-label">Intel</span>`;
      data.risk_intel.forEach(r => { html += `<div class="enrich-intel-item">${escHtml(r)}</div>`; });
      html += '</div>';
    }
    result.innerHTML = html;
  } catch (err) {
    result.innerHTML = `<span class="enrich-error">Error: ${escHtml(err.message)}</span>`;
  }
}

async function lookupWiGLE() {
  const bssid = document.getElementById('wigle-bssid').value.trim();
  if (!bssid) return;
  const result = document.getElementById('wigle-result');
  result.classList.remove('hidden');
  result.innerHTML = '<span class="dim">Querying WiGLE...</span>';
  try {
    const data = await OrionAPI.lookupWiGLE(bssid);
    if (data.error) {
      result.innerHTML = `<span class="dim">${escHtml(data.error)}</span>`;
    } else {
      result.innerHTML = `<pre>${escHtml(JSON.stringify(data, null, 2))}</pre>`;
    }
  } catch (err) {
    result.innerHTML = `<span class="enrich-error">Error: ${escHtml(err.message)}</span>`;
  }
}

async function lookupCVE() {
  const vendor = document.getElementById('cve-vendor').value.trim();
  if (!vendor) return;
  const result = document.getElementById('cve-result');
  result.classList.remove('hidden');
  result.innerHTML = '<span class="dim">Searching NVD...</span>';
  try {
    const data = await OrionAPI.lookupCVE(vendor);
    if (!data.cves || data.cves.length === 0) {
      result.innerHTML = '<span class="dim">No CVEs found for this vendor</span>';
    } else {
      result.innerHTML = data.cves.map(c => `
        <div class="cve-item">
          <div class="cve-id">${escHtml(c.cve_id)}</div>
          <div class="cve-score-row">
            <span class="risk-badge ${c.severity === 'HIGH' || c.severity === 'CRITICAL' ? 'risk-critical' : 'risk-medium'}">${escHtml(c.severity)} ${escHtml(String(c.score))}</span>
          </div>
          <div class="cve-description">${escHtml(c.description)}</div>
        </div>
      `).join('');
    }
  } catch (err) {
    result.innerHTML = `<span class="enrich-error">Error: ${escHtml(err.message)}</span>`;
  }
}
