"""Check the retained rate table against CRA. Rate changes require an effective date."""
from decimal import Decimal
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


class RateTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.table = False
        self.active = False
        self.field = None
        self.text = []
        self.row = []
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.table = True
            self.active = False
        if not self.table:
            return
        if tag == 'tr':
            self.row = []
        elif tag in ('caption', 'td'):
            self.field, self.text = tag, []

    def handle_data(self, data):
        if self.field:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == self.field:
            value = ' '.join(''.join(self.text).split())
            if tag == 'caption':
                self.active = value == 'GST/HST and PST rates'
            else:
                self.row.append(value)
            self.field = None
        elif tag == 'tr' and self.table and self.active and self.row:
            self.rows.append(self.row)
        elif tag == 'table':
            self.table = self.active = False


def validate(html, data, today):
    parser = RateTable()
    parser.feed(html)
    found = {}
    for name, federal, provincial in parser.rows:
        if name.casefold() in found:
            raise ValueError('Duplicate jurisdiction in CRA table')
        rates = [federal, provincial]
        found[name.casefold()] = [Decimal(r.removesuffix('%')) if r.endswith('%') else
                                  Decimal(0) if r == 'N/A' else Decimal(r) for r in rates]
    if len(found) != len(data['regions']):
        raise ValueError('CRA jurisdiction coverage changed')
    for region in data['regions'].values():
        rates = [period['rates'] for period in region['periods'] if period['from'] <= today][-1]
        expected = [Decimal(str(rates.get('GST', rates.get('HST', 0)))),
                    Decimal(str(sum(rates.get(part, 0) for part in ['PST', 'QST', 'RST'])))]
        if found.get(region['name'].casefold()) != expected:
            raise ValueError(f"Review changed official rates and effective dates for {region['name']}")


def main():
    path = ROOT / 'web/data/rates.json'
    data = json.loads(path.read_text())
    with urlopen(Request(data['source'], headers={'User-Agent': 'CoolCode sales tax calculator (+https://coolcode.ca/salestax/)'}), timeout=45) as reply:
        page = reply.read(2_000_001)
    if len(page) > 2_000_000:
        raise ValueError('Unexpected CRA page size')
    checked = datetime.now(timezone.utc).isoformat(timespec='seconds')
    validate(page.decode(), data, checked[:10])
    data.update(checked_at=checked, record_count=len(data['regions']))
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)
    print(f"Verified rates for {data['record_count']} jurisdictions.")


if __name__ == '__main__':
    main()
