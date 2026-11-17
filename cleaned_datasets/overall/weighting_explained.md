# How the Overall index is weighted, and why

There are two layers of weights.

## Layer 1: indicators inside each basket
Each basket is a weighted average of its indicators' 0-100 scores. In the config every indicator has a `weight` (1 if not written) and a `why` line.

- **Weight 1** = a standard indicator.
- **Weight 2 or 3** = an indicator the team judged more important for this country's corridor risk. The reason is in the last column of the table below. These weights are judgement, not fitted to the data.
- The sensitivity test at the end shows how much these weights change the index. Nothing was tuned to the 2014 or 2022 shocks.

## Layer 2: the baskets into one index
- **Main index = equal basket weights.** Reasons: (1) there is no theory that says one component matters more; (2) with only two big shocks in the data, any 'optimal' weights would be fitted to two events; (3) it is the easiest to explain and audit.
- **PCA weights** (alternative): first principal component explains 48% of component variance, so it is only a weak single factor, and the weights depend heavily on the training window. Weights: dependency 22%, economic 0%, geopolitical 20%, transportation 28%, sanctions 30%.
- **Learned weights** (alternative): ridge regression predicting a later trade shortfall, refitted every January using only past data. Latest learned weights: dependency 21%, economic 79%, geopolitical 0%, transportation 0%, sanctions 0%.

## What each indicator is and how much it counts (equal-weight index)

| Basket | Indicator | Weight inside basket | Share of final index | Why it is in the index |
|---|---|---|---|---|
| dependency | rus_export_dep | 33% | 6.7% |  |
| dependency | chn_export_dep | 33% | 6.7% |  |
| dependency | chn_import_dep | 11% | 2.2% |  |
| dependency | rus_import_dep | 11% | 2.2% |  |
| dependency | tii_rus | 11% | 2.2% |  |
| economic | rub_depr_12m | 20% | 4.0% |  |
| economic | cny_depr_12m | 20% | 4.0% |  |
| economic | rub_vol_6m | 10% | 2.0% |  |
| economic | cny_vol_6m | 10% | 2.0% |  |
| economic | rus_cpi_yoy | 10% | 2.0% |  |
| economic | chn_cpi_yoy | 10% | 2.0% |  |
| economic | rus_price_index | 10% | 2.0% |  |
| economic | chn_price_index | 10% | 2.0% |  |
| geopolitical | gpr_global | 8% | 1.5% |  |
| geopolitical | gpr_rus | 46% | 9.2% |  |
| geopolitical | gpr_chn | 46% | 9.2% |  |
| transportation | chn_trans_cost | 20% | 4.0% |  |
| transportation | rus_trans_cost | 20% | 4.0% |  |
| transportation | lsci_chn | 20% | 4.0% |  |
| transportation | lsci_rus | 20% | 4.0% |  |
| transportation | lsbci | 20% | 4.0% |  |
| sanctions | rus_sanc | 50% | 10.0% |  |
| sanctions | chn_sanc | 50% | 10.0% |  |

## Does the weighting choice change the answer? (sensitivity test)

| Variant | Correlation with main | Avg difference (pts) | Same alert status | Latest |
|---|---|---|---|---|
| MAIN: equal baskets, configured indicator weights | 1.00 | 0.0 | 100% | 68.1 |
| All indicators weighted the same (ignore configured weights) | 0.99 | 1.5 | 99% | 69.3 |
| Configured weights flattened (square root of each weight) | 1.00 | 0.6 | 100% | 68.7 |
| PCA basket weights | 0.98 | 3.7 | 91% | 74.8 |
| Learned basket weights (walk-forward) | 0.42 | 8.5 | 80% | 45.6 |
| Without the dependency basket | 0.97 | 3.9 | 93% | 62.0 |
| Without the economic basket | 0.98 | 3.8 | 90% | 76.4 |
| Without the geopolitical basket | 0.94 | 4.0 | 94% | 62.5 |
| Without the transportation basket | 0.98 | 9.0 | 77% | 75.8 |
| Without the sanctions basket | 0.98 | 4.7 | 92% | 62.4 |

Reading the table: a correlation near 1 and a small average difference mean the result does not depend on the weights. Large differences (usually PCA and learned) are why those two are shown only as alternatives.
