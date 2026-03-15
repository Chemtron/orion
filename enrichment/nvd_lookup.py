import logging
import requests
from typing import List, Dict
from datetime import datetime, timezone, timedelta

from core.cache import TTLCache

logger = logging.getLogger(__name__)


class NVDLookup:
    """
    NIST National Vulnerability Database CVE lookup.
    Free, no API key required for basic use.
    Rate limit: 5 requests per 30 seconds without key, 50/30s with key.
    """
    BASE_URL = 'https://services.nvd.nist.gov/rest/json/cves/2.0'
    _cache = TTLCache(default_ttl=3600)
    _NOT_FOUND = object()

    def lookup_vendor(self, vendor_name: str, days_back: int = 90) -> List[Dict]:
        if not vendor_name or vendor_name.lower() in ('unknown', ''):
            return []

        cached = self._cache.get(f'nvd:{vendor_name}')
        if cached is self._NOT_FOUND:
            return []
        if cached is not None:
            return cached

        try:
            pub_start = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime('%Y-%m-%dT00:00:00.000')
            resp = requests.get(
                self.BASE_URL,
                params={
                    'keywordSearch': vendor_name,
                    'pubStartDate': pub_start,
                    'resultsPerPage': 10
                },
                timeout=15
            )
            if resp.status_code == 200:
                vulns = resp.json().get('vulnerabilities', [])
                result = [self._normalize_cve(v) for v in vulns]
                self._cache.set(f'nvd:{vendor_name}', result)
                return result
            else:
                logger.warning("NVD API returned status %d for vendor '%s'", resp.status_code, vendor_name)
        except Exception as e:
            logger.warning("NVD API error for vendor '%s': %s", vendor_name, e)
        self._cache.set(f'nvd:{vendor_name}', self._NOT_FOUND, ttl=600)
        return []

    def _normalize_cve(self, vuln: dict) -> dict:
        cve = vuln.get('cve', {})
        metrics = cve.get('metrics', {})
        severity = 'UNKNOWN'
        score = 0.0
        if 'cvssMetricV31' in metrics:
            cvss = metrics['cvssMetricV31'][0].get('cvssData', {})
            severity = cvss.get('baseSeverity', 'UNKNOWN')
            score = cvss.get('baseScore', 0.0)
        elif 'cvssMetricV2' in metrics:
            cvss = metrics['cvssMetricV2'][0].get('cvssData', {})
            severity = 'HIGH' if float(cvss.get('baseScore', 0)) >= 7 else 'MEDIUM'
            score = cvss.get('baseScore', 0.0)
        descs = cve.get('descriptions', [])
        description = next((d['value'] for d in descs if d['lang'] == 'en'), '')
        return {
            'cve_id': cve.get('id'),
            'severity': severity,
            'score': score,
            'description': description[:300],
            'published': cve.get('published', '')[:10],
            'source': 'nvd'
        }


if __name__ == '__main__':
    nvd = NVDLookup()
    print("NVD lookup module loaded")
