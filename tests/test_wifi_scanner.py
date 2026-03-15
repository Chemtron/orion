import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanners.wifi_scanner import WiFiScanner
from core.config import Config


class MockConfig:
    platform = 'unknown'


class TestWiFiScanner:
    def setup_method(self):
        self.scanner = WiFiScanner(MockConfig())

    def test_scan_mock_returns_list(self):
        results = self.scanner._scan_mock()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_scan_mock_has_required_fields(self):
        results = self.scanner._scan_mock()
        for r in results:
            assert 'mac' in r
            assert 'ssid' in r
            assert 'rssi' in r
            assert 'source' in r

    def test_freq_to_channel(self):
        assert self.scanner._freq_to_channel(2412) == 1
        assert self.scanner._freq_to_channel(2437) == 6
        assert self.scanner._freq_to_channel(2462) == 11

    def test_estimate_distance(self):
        d = self.scanner._estimate_distance(-59)
        assert d == 1.0
        d = self.scanner._estimate_distance(0)
        assert d == -1.0

    def test_scan_returns_list(self):
        results = self.scanner.scan()
        assert isinstance(results, list)

    def test_parse_netsh_output_empty(self):
        results = self.scanner._parse_netsh_output('')
        assert results == []

    def test_parse_iwlist_output_empty(self):
        results = self.scanner._parse_iwlist_output('')
        assert results == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
