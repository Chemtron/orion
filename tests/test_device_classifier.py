import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.device_classifier import DeviceClassifier
from core.database import Database


class TestDeviceClassifier:
    def setup_method(self):
        self.db = Database(':memory:')
        self.classifier = DeviceClassifier(self.db)

    def test_new_device(self):
        result = self.classifier.classify('AA:BB:CC:DD:EE:FF', 'wifi', {})
        assert result == 'new'

    def test_baseline_device(self):
        self.db.upsert_device('AA:BB:CC:DD:EE:FF', 'wifi', {
            'ssid': 'Test', 'classification': 'baseline'
        })
        with self.db.get_conn() as conn:
            conn.execute("UPDATE devices SET is_baseline=1 WHERE mac='AA:BB:CC:DD:EE:FF'")
        result = self.classifier.classify('AA:BB:CC:DD:EE:FF', 'wifi', {})
        assert result == 'baseline'

    def test_transient_device(self):
        self.db.upsert_device('AA:BB:CC:DD:EE:FF', 'wifi', {
            'ssid': 'Test', 'classification': 'unknown'
        })
        result = self.classifier.classify('AA:BB:CC:DD:EE:FF', 'wifi', {})
        assert result == 'transient'

    def test_static_device(self):
        self.db.upsert_device('AA:BB:CC:DD:EE:FF', 'wifi', {
            'ssid': 'Test', 'classification': 'unknown'
        })
        with self.db.get_conn() as conn:
            conn.execute("UPDATE devices SET scan_count=10 WHERE mac='AA:BB:CC:DD:EE:FF'")
        result = self.classifier.classify('AA:BB:CC:DD:EE:FF', 'wifi', {})
        assert result == 'static'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
