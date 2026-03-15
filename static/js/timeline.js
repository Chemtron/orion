'use strict';
// static/js/timeline.js
let currentFilter = 'all';
let allEvents = [];

async function loadTimeline() {
  try {
    const data = await OrionAPI.getIntelEvents(200);
    allEvents = data.events || [];
    renderTimeline(filterEvents(allEvents));
  } catch (err) {
    console.error('Timeline load error:', err);
  }
}

function filterEvents(events) {
  if (currentFilter === 'all') return events;
  return events.filter(e => e.severity === currentFilter);
}

function filterTimeline(severity, btn) {
  currentFilter = severity;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  renderTimeline(filterEvents(allEvents));
}

function renderTimeline(events) {
  const container = document.getElementById('timeline-list');
  if (!container) return;

  if (events.length === 0) {
    container.innerHTML = '<div class="card text-center p-40"><span class="dim">No intel events recorded yet</span></div>';
    return;
  }

  container.innerHTML = events.map(e => `
    <div class="timeline-event ${e.acknowledged ? 'acked' : ''}">
      <div class="timeline-sev-bar ${e.severity}"></div>
      <div class="timeline-content">
        <div class="timeline-title">${escHtml(e.title)}</div>
        <div class="timeline-detail">${escHtml(e.detail || '')}</div>
        <div class="timeline-meta">
          <span>${e.severity.toUpperCase()}</span>
          <span>${e.event_type}</span>
          ${e.device_mac ? '<span>' + escHtml(e.device_mac) + '</span>' : ''}
          ${e.ssid ? '<span>' + escHtml(e.ssid) + '</span>' : ''}
          <span>${formatTime(e.event_time)}</span>
        </div>
      </div>
      <div class="timeline-actions">
        ${!e.acknowledged ? `<button type="button" class="btn" onclick="ackEvent(${e.id})">ACK</button>` : '<span class="dim mono text-xs">ACKED</span>'}
      </div>
    </div>
  `).join('');
}

async function ackEvent(id) {
  await OrionAPI.ackIntelEvent(id);
  loadTimeline();
}

async function ackAllEvents() {
  await OrionAPI.ackAllIntelEvents();
  loadTimeline();
}

document.addEventListener('DOMContentLoaded', () => {
  loadTimeline();
  setInterval(loadTimeline, 10000);
});
