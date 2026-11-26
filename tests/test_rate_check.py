from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from refresh import validate


class OfficialCheckTests(unittest.TestCase):
    def test_unexpected_or_missing_official_rate_cannot_be_published(self):
        data = {'regions': {'TEST': {'name': 'Example', 'periods': [{'from': '2020-01-01', 'rates': {'GST': 5, 'QST': 9.975}}]}}}
        document = '<table><caption>GST/HST and PST rates</caption><tr><td>Example</td><td>5%</td><td>9.975%</td></tr></table>'
        validate(document, data, '2026-01-02')
        with self.assertRaises(ValueError):
            validate(document.replace('9.975%', '10%'), data, '2026-01-02')
        with self.assertRaises(ValueError):
            validate('<html>unavailable</html>', data, '2026-01-02')
