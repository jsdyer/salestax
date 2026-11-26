# Canadian Sales Tax Calculator

[Open the calculator](https://coolcode.ca/salestax/).

<!-- coolcode:guide -->
Enter a receipt total and choose **Remove included tax**, or enter a pre-tax price and choose **Add sales tax**. Select the transaction date and province or territory to see each component in Canadian dollars. Try the [Nova Scotia reverse HST example](https://coolcode.ca/salestax/nova-scotia-reverse-hst/) to see the effect of the April 2025 rate change.
<!-- /coolcode:guide -->

General rates cover all 13 jurisdictions from April 1, 2013. Each component rounds to the nearest cent using integer cents and thousandths of one percentage point. In reverse mode the display lists any cent adjustment needed to reconcile a tax-included receipt with component rounding. The selected jurisdiction and date are supplied by the visitor. This tool assumes a fully taxable ordinary purchase. It does not determine place-of-supply, exemptions, rebates or special product rates. Amounts stay local. The standard CoolCode counter receives the tool ID.

## Sources

- [CRA current GST, HST and provincial rates](https://www.canada.ca/en/revenue-agency/services/tax/businesses/topics/gst-hst-businesses/charge-collect-which-rate/calculator.html)
- [CRA historical rates, including July 2016 changes for NB and NL](https://www.canada.ca/en/revenue-agency/programs/about-canada-revenue-agency-cra/income-statistics-gst-hst-statistics/gst-hst-statistics/gst-hst-statistics-tables-2012-2016-calendar-years.html)
- [Québec historical GST and QST rates](https://www.revenuquebec.ca/en/businesses/consumption-taxes/gsthst-and-qst/basic-rules-for-applying-the-gsthst-and-qst/tables-of-gst-and-qst-rates/)
- [Manitoba rate increase and subsequent decrease](https://news.gov.mb.ca/news/index.html?item=45109&posted=2019-03-07)
- [Saskatchewan 2017 PST rate change](https://sets.saskatchewan.ca/rptp/wcm/connect/0f6cfa6b-ca97-4e87-9b89-6e282b159b53/IN%2B2017-01%2BPST%2BRate%2BTransition%2BRules.pdf?CACHE=NONE&CONTENTCACHE=NONE&MOD=AJPERES&attachment=true)
- [BC budget describing PST reinstatement](https://www.bcbudget.gov.bc.ca/2012/bfp/2012_budget_fiscal_plan.pdf)

## Expand or customize

Add a dated period with its component names and percentages in `web/data/rates.json`. Keep periods sorted, source every change and test the day before and after. Add common calculations to `PRESETS` in `scripts/pages.py` and declare their routes in the CoolCode sitemap. Monthly Actions compare the retained current rules with the official CRA table. A changed rate requires editorial confirmation of the effective date before deployment. Failed validation preserves the previous Pages deployment and snapshot. A manual workflow run repeats the check.

## Build and publish

Run `python3 scripts/refresh.py` to verify current general rates. Run `node --test tests/*.test.mjs`, `python3 -m unittest discover -s tests -v`, and `python3 scripts/build.py`. Serve `dist/` locally or run `python3 tests/browser_smoke.py` with Playwright Chromium installed. GitHub Pages uses the Actions source. Successful default-branch changes publish the offline build. No API credentials are required.
