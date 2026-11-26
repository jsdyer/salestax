import {cents, ratesFor, calculate} from './model.mjs';
const get = id => document.getElementById(id);
const money = new Intl.NumberFormat('en-CA', {style:'currency', currency:'CAD'});
const now = new Date();
const today = [now.getFullYear(), String(now.getMonth()+1).padStart(2, '0'), String(now.getDate()).padStart(2,'0')].join('-');
get('day').value = today;
get('day').max = today;
function line(label, value) {
  const row = document.createElement('div');
  const dt = document.createElement('dt');
  dt.textContent = label;
  const dd = document.createElement('dd');
  dd.textContent = money.format(value / 100);
  row.append(dt, dd);
  return row;
}
function render(data) {
  const output = get('receipt');
  try {
    const region = data.regions[get('region').value];
    if (get('day').value > today) throw new Error('Choose today or an earlier transaction date.');
    const rates = ratesFor(region, get('day').value);
    const result = calculate(cents(get('amount').value.trim()), rates, get('mode').value === 'reverse');
    const heading = document.createElement('h2');
    heading.textContent = region.name + ' calculation';
    const list = document.createElement('dl');
    list.append(line('Before tax', result.base));
    for (const p of result.parts) list.append(line(p.name + ' (' + p.rate + '%)', p.value));
    if (result.adjustment) list.append(line('Reverse rounding adjustment', result.adjustment));
    list.append(line('Total including tax', result.total));
    output.replaceChildren(heading, list);
    get('print').disabled = false;
  } catch (error) {
    output.textContent = error.message;
    get('print').disabled = true;
  }
}
try {
  const response = await fetch(new URL('./data/rates.json', import.meta.url));
  if (!response.ok) throw new Error('Could not load the rate table.');
  const rates = await response.json();
  get('calculator').addEventListener('input', () => render(rates));
  get('calculator').addEventListener('submit', e => e.preventDefault());
  get('print').addEventListener('click', () => window.print());
  render(rates);
} catch {
  get('receipt').textContent = 'Rates could not be loaded. Reload the page to calculate.';
  get('print').disabled = true;
}
