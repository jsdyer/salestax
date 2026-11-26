import assert from 'node:assert/strict';
import test from 'node:test';
import {readFileSync} from 'node:fs';
import {cents, ratesFor, calculate} from '../web/model.mjs';
const {regions} = JSON.parse(readFileSync(new URL('../web/data/rates.json', import.meta.url)));
test('provincial changes take effect on the stated dates', () => {
  assert.equal(ratesFor(regions.NS,'2025-03-31').HST, 15);
  assert.equal(ratesFor(regions.NS,'2025-04-01').HST, 14);
  assert.equal(ratesFor(regions.NB,'2016-07-01').HST, 15);
  assert.equal(ratesFor(regions.MB,'2019-06-30').RST, 8);
  assert.equal(ratesFor(regions.MB,'2019-07-01').RST, 7);
  assert.throws(() => ratesFor(regions.MB,'2012-01-01'));
});
test('receipt figures balance in both directions in each jurisdiction', () => {
  for (const region of Object.values(regions)) {
    const rates = ratesFor(region, '2026-01-01');
    for (const amount of [1, 2, 3, 9, 10, 99, 100, 11400, 9999999999]) {
      const forward = calculate(amount, rates);
      assert.equal(calculate(forward.total, rates, true).base, amount);
      const reverse = calculate(amount, rates, true);
      assert.equal(reverse.base + reverse.parts.reduce((n,x)=>n+x.value,0) + reverse.adjustment, amount);
    }
  }
});
test('Quebec rounds each tax and reverse calculates Nova Scotia included tax', () => {
  const qc = calculate(cents('100.00'), ratesFor(regions.QC, '2026-11-25'));
  assert.deepEqual(qc.parts.map(p => p.value), [500,998]);
  assert.equal(qc.total,11498);
  assert.equal(calculate(11400, {HST:14}, true).base,10000);
  assert.throws(() => cents('1.234')); assert.throws(() => cents('-1')); assert.equal(cents('0.01'),1);
});
