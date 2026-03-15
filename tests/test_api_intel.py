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


class TestIntelAPI:
    def test_get_intel_events(self, client):
        resp = client.get('/api/intel/events')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'events' in data
        assert 'count' in data

    def test_get_debrief(self, client):
        resp = client.get('/api/intel/debrief')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'summary' in data
        assert 'ai_prompt' in data

    def test_get_settings(self, client):
        resp = client.get('/api/settings/')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'platform' in data

    def test_get_alerts(self, client):
        resp = client.get('/api/alerts/')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'alerts' in data

    def test_oui_lookup(self, client):
        resp = client.get('/api/enrich/oui/24:0A:C4:11:22:33')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'vendor' in data
        assert 'Espressif' in data['vendor']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
