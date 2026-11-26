"""Produce usable prefilled calculators with visible examples in the initial HTML."""
from decimal import Decimal, ROUND_HALF_UP
from html import escape
import json
from search_metadata import add_search_metadata

PRESETS = {'bc-gst-pst': ('BC', False, '100.00', 'BC GST and PST Calculator',
              'Add British Columbia GST and PST to a fully taxable purchase.'),
           'nova-scotia-reverse-hst': ('NS', True, '114.00', 'Nova Scotia Reverse HST Calculator',
              'Enter a tax-included Nova Scotia receipt total to find its price before HST.'),
           'ontario-hst': ('ON', False, '100.00', 'Ontario HST Calculator',
              'Calculate Ontario HST and the checkout total for a fully taxable purchase.'),
           'quebec-gst-qst': ('QC', False, '100.00', 'Quebec GST and QST Calculator',
              'Calculate GST and QST separately on the same Quebec selling price.')}


def render(data, code, reverse, amount, prefix):
    regions = data['regions']
    checked = data['checked_at'][:10]
    rates = next(p['rates'] for p in reversed(regions[code]['periods']) if p['from'] <= checked)
    base = Decimal(amount)
    penny = Decimal('.01')
    if reverse:
        base = (base / (1 + sum(Decimal(str(x)) for x in rates.values()) / 100)).quantize(penny, ROUND_HALF_UP)
    items = [(k, (base * Decimal(str(r)) / 100).quantize(penny, ROUND_HALF_UP)) for k, r in rates.items()]
    opts = ''.join(f'<option value="{k}"{" selected" if k == code else ""}>{escape(v["name"])}</option>' for k, v in regions.items())
    tax = ''.join(f'<div><dt>{key} ({rates[key]}%)</dt><dd>${value:,.2f}</dd></div>' for key, value in items)
    total = Decimal(amount) if reverse else base + sum(v for _,v in items)
    clean = ''.join(f'<a href="{prefix}{key}/">{escape(opts[3])}</a> ' for key, opts in PRESETS.items())
    return f'''<section><form id="calculator"><div class="fields"><label>Amount (CAD)<input id="amount" inputmode="decimal" value="{amount}" required></label>
<label>Province or territory<select id="region">{opts}</select></label><label>Calculation<select id="mode">
<option value="add">Add sales tax</option><option value="reverse"{' selected' if reverse else ''}>Remove included tax</option></select></label>
<label>Transaction date<input type="date" id="day" min="2013-04-01" value="{checked}" required></label></div>
</form><div role="status" aria-live="polite" id="receipt"><h2>Calculation</h2><dl><div><dt>Before tax</dt><dd>${base:,.2f}</dd></div>{tax}<div><dt>Total including tax</dt><dd>${total:,.2f}</dd></div></dl></div>
<button id="print" type="button">Print calculation</button></section><nav aria-label="Common calculations">{clean}</nav>
<p>General rates from April 1, 2013 onward. Standard tax components round separately to the nearest cent. In reverse mode any cent difference is shown explicitly.</p>
<p>Rates last verified {checked} · <a href="{escape(data['source'],quote=True)}">Canada Revenue Agency rate table</a>.</p>'''


def publish_pages(stage, template, tool):
    data = json.loads((stage / 'data/rates.json').read_text())
    pages = {'': ('BC', False, '100.00', tool['title'], tool['description']), **PRESETS}
    for slug, (code, reverse, amount, title, description) in pages.items():
        info = dict(tool, title=title, description=description, url=tool['url'] + (slug + '/' if slug else ''))
        prefix = '../' if slug else './'
        page = template
        if slug:
            page = (page.replace(escape(tool['title']), escape(title)).replace(escape(tool['description']), escape(description))
                        .replace('href="./style.css"', 'href="../style.css"').replace('src="./app.mjs"', 'src="../app.mjs"'))
        page = page.replace('<!-- CALCULATOR -->', render(data, code, reverse, amount, prefix))
        destination = stage / slug
        destination.mkdir(exist_ok=True)
        (destination / 'index.html').write_text(add_search_metadata(page, info, category='FinanceApplication'))
