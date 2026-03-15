import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.risk_scorer import RiskScorer


class TestRiskScorer:
    def setup_method(self):
        self.scorer = RiskScorer()

    def test_open_network_scored(self):
        result = self.scorer.score_wifi({'security': 'OPEN', 'mac': 'AA:BB:CC:11:22:33'})
        assert result['score'] >= 30
        assert 'OPEN_NETWORK' in result['flags']

    def test_hidden_ssid_scored(self):
        result = self.scorer.score_wifi({'hidden': True, 'security': 'WPA2', 'mac': 'AA:BB:CC:11:22:33'})
        assert 'HIDDEN_SSID' in result['flags']

    def test_camera_ssid_keyword(self):
        result = self.scorer.score_wifi({'ssid': 'MyHikvision', 'security': 'WPA2', 'mac': 'AA:BB:CC:11:22:33'})
        assert 'CAMERA_SSID_KEYWORD' in result['flags']

    def test_camera_oui(self):
        result = self.scorer.score_wifi({'mac': '24:0A:C4:11:22:33', 'security': 'WPA2'})
        assert 'CAMERA_VENDOR_OUI' in result['flags']

    def test_safe_network_low_score(self):
        result = self.scorer.score_wifi({'ssid': 'HomeWifi', 'security': 'WPA3', 'mac': 'AA:BB:CC:11:22:33', 'rssi': -70})
        assert result['score'] < 30

    def test_airtag_scored(self):
        result = self.scorer.score_ble({'is_airtag': True, 'mac': 'AA:BB:CC:11:22:33'})
        assert result['score'] >= 70
        assert 'AIRTAG_DETECTED' in result['flags']

    def test_ble_anonymous(self):
        result = self.scorer.score_ble({'name': '', 'is_apple': False, 'mac': 'AA:BB:CC:11:22:33'})
        assert 'ANONYMOUS_DEVICE' in result['flags']

    def test_network_rtsp_port(self):
        result = self.scorer.score_network({'open_ports': [554], 'mac': 'AA:BB:CC:11:22:33'})
        assert 'RTSP_PORT_OPEN' in result['flags']

    def test_score_capped_at_100(self):
        result = self.scorer.score_wifi({
            'ssid': 'hikvision-cam',
            'security': 'OPEN',
            'hidden': True,
            'mac': '24:0A:C4:11:22:33',
            'rssi': -30
        })
        assert result['score'] <= 100

    def test_wep_flagged(self):
        result = self.scorer.score_wifi({'security': 'WEP', 'mac': 'AA:BB:CC:11:22:33'})
        assert 'WEAK_ENCRYPTION_WEP' in result['flags']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
