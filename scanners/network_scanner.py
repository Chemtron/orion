import subprocess
import re
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

CIDR_PATTERN = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$')
IP_PATTERN = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')


class NetworkScanner:
    """
    LAN device scanner.
    Uses arp -a (passive, always available) + optional nmap ping sweep.
    No root required for basic operation.
    """

    SUSPICIOUS_PORTS = [554, 8554, 8080, 80, 443, 23, 21]
    CAMERA_PORTS = [554, 8554]

    def __init__(self, config):
        self.config = config

    def scan_arp(self) -> List[Dict]:
        """Fast passive scan using ARP cache."""
        try:
            result = subprocess.run(
                ['arp', '-a'],
                capture_output=True, text=True, timeout=10
            )
            return self._parse_arp_output(result.stdout)
        except Exception as e:
            logger.warning("Network ARP scan error: %s", e)
            return []

    def scan_subnet(self, subnet: str = None) -> List[Dict]:
        """Ping sweep using nmap. Requires nmap installed."""
        if not subnet:
            subnet = self._get_local_subnet()
        if not subnet:
            return self.scan_arp()
        if not CIDR_PATTERN.match(subnet):
            logger.warning("Invalid subnet CIDR format: %s, falling back to ARP scan", subnet)
            return self.scan_arp()
        try:
            result = subprocess.run(
                ['nmap', '-sn', '--open', subnet],
                capture_output=True, text=True, timeout=60
            )
            return self._parse_nmap_output(result.stdout)
        except FileNotFoundError:
            return self.scan_arp()

    def probe_device(self, ip: str) -> Dict:
        """Check common ports on a device to identify type."""
        if not IP_PATTERN.match(ip):
            logger.warning("Invalid IP address format: %s", ip)
            return {'ip': ip, 'open_ports': [], 'device_type': 'unknown'}
        try:
            result = subprocess.run(
                ['nmap', '-p', ','.join(str(p) for p in self.SUSPICIOUS_PORTS),
                 '--open', ip],
                capture_output=True, text=True, timeout=30
            )
            open_ports = self._extract_open_ports(result.stdout)
            device_type = 'unknown'
            if any(p in open_ports for p in self.CAMERA_PORTS):
                device_type = 'ip_camera'
            elif 23 in open_ports:
                device_type = 'telnet_device'
            return {'ip': ip, 'open_ports': open_ports, 'device_type': device_type}
        except Exception as e:
            logger.warning("Network device probe error for %s: %s", ip, e)
            return {'ip': ip, 'open_ports': [], 'device_type': 'unknown'}

    def _parse_arp_output(self, output: str) -> List[Dict]:
        devices = []
        for line in output.split('\n'):
            match = re.search(
                r'[\w.-]*\s*\(?([\d.]+)\)?\s+at\s+([0-9a-fA-F:]{17})',
                line
            )
            if match:
                ip = match.group(1)
                mac = match.group(2).upper()
                if mac not in ('<incomplete>', 'FF:FF:FF:FF:FF:FF'):
                    devices.append({
                        'ip': ip,
                        'mac': mac,
                        'hostname': self._extract_hostname(line),
                        'source': 'arp'
                    })
            else:
                # Windows arp -a format: IP  MAC  type
                win_match = re.search(
                    r'([\d.]+)\s+([0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2}-[0-9a-fA-F]{2})',
                    line
                )
                if win_match:
                    ip = win_match.group(1)
                    mac = win_match.group(2).replace('-', ':').upper()
                    if mac != 'FF:FF:FF:FF:FF:FF':
                        devices.append({
                            'ip': ip,
                            'mac': mac,
                            'hostname': '',
                            'source': 'arp'
                        })
        return devices

    def _parse_nmap_output(self, output: str) -> List[Dict]:
        devices = []
        current = {}
        for line in output.split('\n'):
            if 'Nmap scan report for' in line:
                if current.get('ip'):
                    devices.append(current)
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                hostname = line.replace('Nmap scan report for', '').strip()
                current = {
                    'ip': ip_match.group(1) if ip_match else '',
                    'hostname': hostname,
                    'mac': '',
                    'source': 'nmap'
                }
            elif 'MAC Address:' in line:
                mac_match = re.search(r'([0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})', line.upper())
                if mac_match:
                    current['mac'] = mac_match.group(1)
        if current.get('ip'):
            devices.append(current)
        return devices

    def _extract_open_ports(self, nmap_output: str) -> List[int]:
        ports = []
        for line in nmap_output.split('\n'):
            match = re.match(r'\s*(\d+)/tcp\s+open', line)
            if match:
                ports.append(int(match.group(1)))
        return ports

    def _extract_hostname(self, line: str) -> str:
        parts = line.split()
        if parts and '(' not in parts[0]:
            return parts[0]
        return ''

    def _get_local_subnet(self) -> str:
        try:
            import netifaces
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get('addr', '')
                        if ip and not ip.startswith('127.'):
                            parts = ip.split('.')
                            return f"{'.'.join(parts[:3])}.0/24"
        except Exception as e:
            logger.warning("Network interface detection error: %s", e)
        logger.warning("Could not detect local subnet, falling back to hardcoded 192.168.1.0/24")
        return '192.168.1.0/24'


if __name__ == '__main__':
    from core.config import Config
    config = Config()
    scanner = NetworkScanner(config)
    results = scanner.scan_arp()
    print(f"Found {len(results)} network devices")
    for r in results[:5]:
        print(f"  {r.get('ip', '?')} ({r.get('mac', '?')})")
