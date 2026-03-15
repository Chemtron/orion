import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config
from core.app import create_app


@pytest.fixture
def client():
    config = Config()
    config.db_path = ':memory:'
    app = create_app(config)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestScanAPI:
    def test_get_current_scan(self, client):
        resp = client.get('/api/scan/current')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'wifi' in data
        assert 'ble' in data
        assert 'network' in data

    def test_trigger_wifi_scan(self, client):
        resp = client.post('/api/scan/trigger/wifi', content_type='application/json')
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['status'] == 'triggered'

    def test_get_devices(self, client):
        resp = client.get('/api/devices/')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'devices' in data
        assert 'count' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
