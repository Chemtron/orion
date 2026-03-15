import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scanners.ble_scanner import BLEScanner


class MockConfig:
    platform = 'unknown'


class TestBLEScanner:
    def setup_method(self):
        self.scanner = BLEScanner(MockConfig())

    def test_scan_mock_returns_list(self):
        results = self.scanner._scan_mock_ble()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_mock_has_required_fields(self):
        results = self.scanner._scan_mock_ble()
        for r in results:
            assert 'mac' in r
            assert 'rssi' in r
            assert 'source' in r

    def test_is_airtag_no_apple(self):
        assert self.scanner._is_airtag({}) is False

    def test_is_airtag_with_marker(self):
        data = {0x004C: bytes([0x12, 0x19, 0x00, 0x00])}
        assert self.scanner._is_airtag(data) is True

    def test_fingerprint_apple(self):
        data = {0x004C: bytes([0x12, 0x19])}
        hints = self.scanner._fingerprint_ble_device(data, [])
        assert 'AIRTAG_CANDIDATE' in hints

    def test_fingerprint_microsoft(self):
        data = {0x0006: bytes([0x01])}
        hints = self.scanner._fingerprint_ble_device(data, [])
        assert 'WINDOWS_DEVICE' in hints

    def test_estimate_ble_distance(self):
        d = self.scanner._estimate_ble_distance(-65)
        assert d == 1.0
        d = self.scanner._estimate_ble_distance(0)
        assert d == -1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
