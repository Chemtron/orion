import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from enrichment.oui_lookup import OUILookup


class TestOUILookup:
    def setup_method(self):
        self.oui = OUILookup('')

    def test_known_camera_oui(self):
        result = self.oui.lookup('24:0A:C4:11:22:33')
        assert 'Espressif' in result

    def test_hikvision_detected(self):
        result = self.oui.lookup('D4:5D:64:AA:BB:CC')
        assert 'Hikvision' in result

    def test_unknown_mac(self):
        result = self.oui.lookup('FF:FF:FF:00:00:00')
        assert result == 'Unknown'

    def test_empty_mac(self):
        result = self.oui.lookup('')
        assert result == 'Unknown'

    def test_is_camera_vendor(self):
        assert self.oui.is_camera_vendor('24:0A:C4:11:22:33') is True
        assert self.oui.is_camera_vendor('AA:BB:CC:11:22:33') is False

    def test_is_espressif(self):
        assert self.oui.is_espressif('24:0A:C4:11:22:33') is True
        assert self.oui.is_espressif('AA:BB:CC:11:22:33') is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
