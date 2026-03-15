'use strict';
// static/js/api.js
const API_KEY = document.querySelector('meta[name="api-key"]')?.content || '';

const OrionAPI = {
  async _fetch(path, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
      ...(options.headers || {})
    };
    const resp = await fetch(path, { ...options, headers });
    if (!resp.ok) throw new Error(`API error: ${resp.status}`);
    return resp.json();
  },

  getCurrentScan:     ()     => OrionAPI._fetch('/api/scan/current'),
  getDevices:         (type) => OrionAPI._fetch(`/api/devices/${type ? '?type=' + encodeURIComponent(type) : ''}`),
  getDevice:          (mac, type) => OrionAPI._fetch(`/api/devices/${encodeURIComponent(mac)}?type=${encodeURIComponent(type || 'wifi')}`),
  getIntelEvents:     (limit) => OrionAPI._fetch(`/api/intel/events?limit=${limit || 50}`),
  getDebrief:         (window) => OrionAPI._fetch(`/api/intel/debrief?window=${window || 5}`),
  ackIntelEvent:      (id)   => OrionAPI._fetch(`/api/intel/events/${id}/ack`, { method: 'POST' }),
  triggerScan:        (type) => OrionAPI._fetch(`/api/scan/trigger/${type}`, { method: 'POST' }),
  lookupOUI:          (mac)  => OrionAPI._fetch(`/api/enrich/oui/${encodeURIComponent(mac)}`),
  lookupWiGLE:        (bssid) => OrionAPI._fetch(`/api/enrich/wigle/${encodeURIComponent(bssid)}`),
  lookupCVE:          (vendor) => OrionAPI._fetch(`/api/enrich/cve/${encodeURIComponent(vendor)}`),
  analyzeSSID:        (ssid) => OrionAPI._fetch('/api/enrich/ssid', { method: 'POST', body: JSON.stringify({ ssid }) }),
  getSettings:        ()     => OrionAPI._fetch('/api/settings/'),
  updateIntervals:    (data) => OrionAPI._fetch('/api/settings/scan-intervals', { method: 'POST', body: JSON.stringify(data) }),
  updateToggles:      (data) => OrionAPI._fetch('/api/settings/toggles', { method: 'POST', body: JSON.stringify(data) }),
  getAlerts:          (limit) => OrionAPI._fetch(`/api/alerts/?limit=${limit || 50}`),
  ackAlert:           (id)   => OrionAPI._fetch(`/api/alerts/${id}/ack`, { method: 'POST' }),
  ackAllAlerts:       ()     => OrionAPI._fetch('/api/alerts/ack-all', { method: 'POST' }),
  ackAllIntelEvents:  ()     => OrionAPI._fetch('/api/intel/events/ack-all', { method: 'POST' }),
  getAlertRules:      ()     => OrionAPI._fetch('/api/alerts/rules'),
};
