'use strict';
// static/js/radar.js
// Canvas-based tactical radar renderer

const RadarCanvas = {
  canvas: null,
  ctx: null,
  centerX: 250,
  centerY: 250,
  radius: 240,
  sweepAngle: 0,
  devices: [],
  dots: [],

  init(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.centerX = this.canvas.width / 2;
    this.centerY = this.canvas.height / 2;
    this.radius = (this.canvas.width / 2) - 10;
    this._startSweep();
  },

  setDevices(devices) {
    this.devices = devices;
    this._buildDots();
  },

  _buildDots() {
    this.dots = this.devices.map(d => {
      const dist = d.distance_m || 15;
      const maxDist = 60;
      const r = Math.min((dist / maxDist) * this.radius, this.radius - 10);
      const angle = this._macToAngle(d.mac || '');
      const jitter = ((d.rssi || -70) % 10) * 2;
      return {
        x: this.centerX + r * Math.cos(angle + jitter * 0.01),
        y: this.centerY + r * Math.sin(angle + jitter * 0.01),
        color: this._riskColor(d.risk_score || 0, d.device_type || 'wifi'),
        label: (d.ssid || d.name || d.mac || '').substring(0, 16),
        risk_score: d.risk_score || 0,
        type: d.device_type || 'wifi'
      };
    });
  },

  _macToAngle(mac) {
    let hash = 0;
    for (let i = 0; i < mac.length; i++) {
      hash = mac.charCodeAt(i) + ((hash << 5) - hash);
    }
    return (hash % 628) / 100;
  },

  _riskColor(score, type) {
    if (score >= 70) return '#ff4444';
    if (score >= 40) return '#ffaa00';
    if (type === 'ble') return '#00ffee';
    if (type === 'network') return '#00cc66';
    return '#66ddff';
  },

  _startSweep() {
    const draw = () => {
      this._drawFrame();
      this.sweepAngle = (this.sweepAngle + 0.015) % (Math.PI * 2);
      requestAnimationFrame(draw);
    };
    draw();
  },

  _drawFrame() {
    const ctx = this.ctx;
    const cx = this.centerX;
    const cy = this.centerY;
    const r = this.radius;

    // Background
    ctx.fillStyle = '#050a0f';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Clip to circle
    ctx.save();
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.clip();

    // Grid rings
    [0.25, 0.5, 0.75, 1.0].forEach(frac => {
      ctx.beginPath();
      ctx.arc(cx, cy, r * frac, 0, Math.PI * 2);
      ctx.strokeStyle = '#1a3a5a';
      ctx.lineWidth = 1;
      ctx.stroke();
    });

    // Crosshairs
    ctx.strokeStyle = '#1a3a5a';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(cx - r, cy); ctx.lineTo(cx + r, cy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(cx, cy - r); ctx.lineTo(cx, cy + r); ctx.stroke();

    // Sweep gradient
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.sweepAngle);
    const grad = ctx.createLinearGradient(0, 0, r, 0);
    grad.addColorStop(0, 'rgba(102, 221, 255, 0.4)');
    grad.addColorStop(0.3, 'rgba(102, 221, 255, 0.1)');
    grad.addColorStop(1, 'rgba(102, 221, 255, 0)');
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, r, -0.3, 0);
    ctx.closePath();
    ctx.fillStyle = grad;
    ctx.fill();
    ctx.restore();

    // Sweep line
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(this.sweepAngle);
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(r, 0);
    ctx.strokeStyle = 'rgba(102, 221, 255, 0.8)';
    ctx.lineWidth = 1.5;
    ctx.stroke();
    ctx.restore();

    // Device dots
    this.dots.forEach(dot => {
      // Glow
      const glow = ctx.createRadialGradient(dot.x, dot.y, 0, dot.x, dot.y, 12);
      glow.addColorStop(0, dot.color + '88');
      glow.addColorStop(1, 'transparent');
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, 12, 0, Math.PI * 2);
      ctx.fillStyle = glow;
      ctx.fill();

      // Core dot
      ctx.beginPath();
      ctx.arc(dot.x, dot.y, dot.risk_score >= 60 ? 5 : 3, 0, Math.PI * 2);
      ctx.fillStyle = dot.color;
      ctx.fill();

      // Label
      ctx.fillStyle = dot.color;
      ctx.font = '11px JetBrains Mono, monospace';
      ctx.fillText(dot.label, dot.x + 7, dot.y - 4);
    });

    // Center dot (scanner)
    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#00ffee';
    ctx.fill();
    ctx.beginPath();
    ctx.arc(cx, cy, 10, 0, Math.PI * 2);
    ctx.strokeStyle = '#00ffee44';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.restore();
  }
};
