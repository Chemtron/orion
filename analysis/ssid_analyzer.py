import logging
import re
from typing import Dict, List

logger = logging.getLogger(__name__)


class SSIDAnalyzer:
    """
    Extracts personally identifying information from SSID names.
    Identifies hotspot names, employer names, ISP patterns, etc.
    """

    PERSONAL_HOTSPOT_PATTERNS = [
        (r"^(.+)'s?\s+iphone$", 'person_name', 'IPHONE_HOTSPOT'),
        (r"^(.+)'s?\s+android$", 'person_name', 'ANDROID_HOTSPOT'),
        (r"^(.+)'s?\s+galaxy\b", 'person_name', 'GALAXY_HOTSPOT'),
        (r"^(.+)'s?\s+macbook\b", 'person_name', 'MACBOOK_HOTSPOT'),
        (r"^(.+)'s?\s+ipad\b", 'person_name', 'IPAD_HOTSPOT'),
        (r"^(.+)'s?\s+phone$", 'person_name', 'PHONE_HOTSPOT'),
    ]

    ISP_PATTERNS = [
        ('xfinitywifi', 'Comcast/Xfinity', 'ISP_COMCAST'),
        ('attwifi', 'AT&T', 'ISP_ATT'),
        ('spectrum', 'Charter Spectrum', 'ISP_CHARTER'),
        ('cox-', 'Cox Communications', 'ISP_COX'),
        ('verizon', 'Verizon', 'ISP_VERIZON'),
        ('tmobile', 'T-Mobile', 'ISP_TMOBILE'),
    ]

    def analyze(self, ssid: str) -> Dict:
        result = {
            'ssid': ssid,
            'flags': [],
            'extracted_name': None,
            'isp': None,
            'is_hotspot': False,
            'is_default_router': False,
            'has_address_info': False,
            'risk_intel': []
        }
        if not ssid:
            return result

        ssid_lower = ssid.lower().strip()

        for pattern, data_type, flag in self.PERSONAL_HOTSPOT_PATTERNS:
            match = re.match(pattern, ssid_lower, re.IGNORECASE)
            if match:
                name = match.group(1).strip().title()
                result['extracted_name'] = name
                result['is_hotspot'] = True
                result['flags'].append(flag)
                result['risk_intel'].append(
                    f"Personal hotspot — owner name likely: {name}"
                )

        for pattern, isp_name, flag in self.ISP_PATTERNS:
            if pattern in ssid_lower:
                result['isp'] = isp_name
                result['flags'].append(flag)

        if re.search(r'\d{3,5}\s+\w+\s+(st|ave|rd|blvd|ln|dr|ct|way)', ssid_lower):
            result['has_address_info'] = True
            result['flags'].append('ADDRESS_IN_SSID')
            result['risk_intel'].append("SSID may contain a street address")

        if re.search(r'[\w.]+@[\w.]+\.\w+', ssid):
            result['flags'].append('EMAIL_IN_SSID')
            result['risk_intel'].append("SSID appears to contain an email address")

        return result


if __name__ == '__main__':
    analyzer = SSIDAnalyzer()
    result = analyzer.analyze("John's iPhone")
    print(f"Flags: {result['flags']}")
    print(f"Name: {result['extracted_name']}")
