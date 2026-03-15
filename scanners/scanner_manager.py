import threading
import logging
import schedule
from typing import Callable

logger = logging.getLogger(__name__)


class ScannerManager:
    def __init__(self, config, db):
        self.config = config
        self.db = db
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._last_wifi_results = []
        self._last_ble_results = []
        self._last_network_results = []
        self._scan_in_progress = {'wifi': False, 'ble': False, 'network': False}

        # Import scanners
        from scanners.wifi_scanner import WiFiScanner
        from scanners.ble_scanner import BLEScanner
        from scanners.network_scanner import NetworkScanner
        from analysis.device_classifier import DeviceClassifier
        from analysis.risk_scorer import RiskScorer
        from enrichment.oui_lookup import OUILookup
        from intel.alert_manager import AlertManager

        self.wifi_scanner = WiFiScanner(config)
        self.ble_scanner = BLEScanner(config)
        self.network_scanner = NetworkScanner(config)
        self.classifier = DeviceClassifier(db)
        self.risk_scorer = RiskScorer(config)
        self.oui_lookup = OUILookup(config.oui_path)
        self.alert_manager = AlertManager(db)

    def start(self):
        self._stop_event.clear()
        if self.config.enable_wifi_scan:
            schedule.every(self.config.wifi_scan_interval).seconds.do(self._run_wifi_scan)
        if self.config.enable_ble_scan:
            schedule.every(self.config.ble_scan_interval).seconds.do(self._run_ble_scan)
        if self.config.enable_network_scan:
            schedule.every(self.config.network_scan_interval).seconds.do(self._run_network_scan)

        schedule.every(1).hours.do(self._run_cleanup)

        # Run initial scans immediately
        threading.Thread(target=self._run_wifi_scan, daemon=True).start()
        threading.Thread(target=self._run_ble_scan, daemon=True).start()

        self._thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        schedule.clear()
        if self._thread:
            self._thread.join(timeout=5)

    def _scheduler_loop(self):
        while not self._stop_event.is_set():
            schedule.run_pending()
            self._stop_event.wait(1)

    def _run_wifi_scan(self):
        with self._lock:
            if self._scan_in_progress['wifi']:
                return
            self._scan_in_progress['wifi'] = True
        try:
            devices = self.wifi_scanner.scan()
            for device in devices:
                mac = device.get('mac')
                if not mac:
                    continue
                vendor = self.oui_lookup.lookup(mac)
                device['vendor'] = vendor
                risk = self.risk_scorer.score_wifi(device)
                device['risk_score'] = risk['score']
                device['risk_flags'] = risk['flags']
                classification = self.classifier.classify(mac, 'wifi', device)
                device['classification'] = classification
                self.db.upsert_device(mac, 'wifi', device)
                self.db.log_scan_event('wifi', mac, device)
                self.alert_manager.evaluate_wifi(device)
            with self._lock:
                self._last_wifi_results = devices
        except Exception as e:
            logger.error("Scan error (wifi): %s", e, exc_info=True)
        finally:
            with self._lock:
                self._scan_in_progress['wifi'] = False

    def _run_ble_scan(self):
        with self._lock:
            if self._scan_in_progress['ble']:
                return
            self._scan_in_progress['ble'] = True
        try:
            devices = self.ble_scanner.scan()
            for device in devices:
                mac = device.get('mac')
                if not mac:
                    continue
                vendor = self.oui_lookup.lookup(mac)
                device['vendor'] = vendor
                risk = self.risk_scorer.score_ble(device)
                device['risk_score'] = risk['score']
                device['risk_flags'] = risk['flags']
                classification = self.classifier.classify(mac, 'ble', device)
                device['classification'] = classification
                self.db.upsert_device(mac, 'ble', device)
                self.db.log_scan_event('ble', mac, device)
                self.alert_manager.evaluate_ble(device)
            if not devices:
                logger.info("BLE scan returned 0 devices — scanner may not be available on this platform")
            with self._lock:
                self._last_ble_results = devices
        except Exception as e:
            logger.error("Scan error (ble): %s", e, exc_info=True)
        finally:
            with self._lock:
                self._scan_in_progress['ble'] = False

    def _run_network_scan(self):
        with self._lock:
            if self._scan_in_progress['network']:
                return
            self._scan_in_progress['network'] = True
        try:
            devices = self.network_scanner.scan_arp()
            for device in devices:
                mac = device.get('mac')
                if not mac:
                    continue
                vendor = self.oui_lookup.lookup(mac)
                device['vendor'] = vendor
                device['device_type'] = 'network'
                risk = self.risk_scorer.score_network(device)
                device['risk_score'] = risk['score']
                device['risk_flags'] = risk['flags']
                self.db.upsert_device(mac, 'network', device)
                self.db.log_scan_event('network', mac, device)
            with self._lock:
                self._last_network_results = devices
        except Exception as e:
            logger.error("Scan error (network): %s", e, exc_info=True)
        finally:
            with self._lock:
                self._scan_in_progress['network'] = False

    def _run_cleanup(self):
        try:
            self.db.cleanup_old_data(days=7)
        except Exception as e:
            logger.error("Data cleanup error: %s", e)

    def run_wifi_scan(self):
        """Public method to trigger a WiFi scan."""
        self._run_wifi_scan()

    def run_ble_scan(self):
        """Public method to trigger a BLE scan."""
        self._run_ble_scan()

    def run_network_scan(self):
        """Public method to trigger a network scan."""
        self._run_network_scan()

    def get_current_state(self) -> dict:
        with self._lock:
            return {
                'wifi': self._last_wifi_results,
                'ble': self._last_ble_results,
                'network': self._last_network_results,
                'wifi_count': len(self._last_wifi_results),
                'ble_count': len(self._last_ble_results),
                'network_count': len(self._last_network_results)
            }


if __name__ == '__main__':
    print("ScannerManager module loaded")
