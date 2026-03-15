import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanners.network_scanner import NetworkScanner


class MockConfig:
    platform = 'unknown'


class TestNetworkScanner:
    def setup_method(self):
        self.scanner = NetworkScanner(MockConfig())

    def test_parse_arp_empty(self):
        result = self.scanner._parse_arp_output('')
        assert result == []

    def test_parse_arp_linux_format(self):
        output = "router (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on eth0\n"
        result = self.scanner._parse_arp_output(output)
        assert len(result) == 1
        assert result[0]['ip'] == '192.168.1.1'
        assert result[0]['mac'] == 'AA:BB:CC:DD:EE:FF'

    def test_parse_nmap_empty(self):
        result = self.scanner._parse_nmap_output('')
        assert result == []

    def test_extract_open_ports(self):
        output = "80/tcp open  http\n443/tcp open  https\n"
        ports = self.scanner._extract_open_ports(output)
        assert 80 in ports
        assert 443 in ports

    def test_extract_open_ports_empty(self):
        ports = self.scanner._extract_open_ports('')
        assert ports == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
