// Store entered money as whole cents. Rates use thousandths of one percent.
export function cents(text) {
  if (!/^\d{1,8}(?:\.\d{1,2})?$/.test(text)) throw new Error('Enter a CAD amount from $0 to $99,999,999.99 with up to two decimal places.');
  const [dollars, fraction = ''] = text.split('.');
  return Number(dollars) * 100 + Number(fraction.padEnd(2, '0'));
}
export function ratesFor(region, date) {
  const period = region?.periods.findLast(period => period.from <= date);
  if (!period || !/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error('Choose a supported transaction date on or after April 1, 2013.');
  return period.rates;
}
function roundedPart(base, rate) {
  return Math.floor((base * Math.round(rate * 1000) + 50000) / 100000);
}
export function calculate(amount, rates, reverse = false) {
  let base = amount;
  if (reverse) {
    const sum = Object.values(rates).reduce((n, r) => n + Math.round(r * 1000), 0);
    const approximate = Math.floor((amount * 100000 + (100000 + sum) / 2) / (100000 + sum));
    // With separately rounded components, an adjacent cent may reproduce the exact receipt.
    const candidates = [approximate, approximate - 1, approximate + 1].filter(n => n >= 0);
    base = candidates.find(n => n + Object.values(rates).reduce((v, r) => v + roundedPart(n, r), 0) === amount) ?? approximate;
  }
  const parts = Object.entries(rates).map(([name, rate]) => ({name, rate, value: roundedPart(base, rate)}));
  const computed = base + parts.reduce((total, part) => total + part.value, 0);
  return {base, parts, total: reverse ? amount : computed, adjustment: reverse ? amount - computed : 0};
}
