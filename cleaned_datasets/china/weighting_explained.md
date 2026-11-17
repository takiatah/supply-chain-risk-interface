# How the China index is weighted, and why

There are two layers of weights.

## Layer 1: indicators inside each basket
Each basket is a weighted average of its indicators' 0-100 scores. In the config every indicator has a `weight` (1 if not written) and a `why` line.

- **Weight 1** = a standard indicator.
- **Weight 2 or 3** = an indicator the team judged more important for this country's corridor risk. The reason is in the last column of the table below. These weights are judgement, not fitted to the data.
- The sensitivity test at the end shows how much these weights change the index. Nothing was tuned to the 2014 or 2022 shocks.

## Layer 2: the baskets into one index
- **Main index = equal basket weights.** Reasons: (1) there is no theory that says one component matters more; (2) with only two big shocks in the data, any 'optimal' weights would be fitted to two events; (3) it is the easiest to explain and audit.
- **PCA weights** (alternative): first principal component explains 42% of component variance, so it is only a weak single factor, and the weights depend heavily on the training window. Weights: dependency 20%, transportation 34%, economic 0%, geopolitical 21%, sanctions 25%.
- **Learned weights** (alternative): ridge regression predicting a later trade shortfall, refitted every January using only past data. Latest learned weights: dependency 0%, transportation 0%, economic 100%, geopolitical 0%, sanctions 0%.

## What each indicator is and how much it counts (equal-weight index)

| Basket | Indicator | Weight inside basket | Share of final index | Why it is in the index |
|---|---|---|---|---|
| dependency | chn_import_dep | 43% | 8.6% | Share of China's imports that come from Russia (energy, metals, timber). More reliance on one supplier means a disruption is harder to replace. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| dependency | chn_export_dep | 43% | 8.6% | Share of China's exports that go to Russia. More sales resting on one buyer means a disruption costs more. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| dependency | tii_chn | 14% | 2.9% | Trade intensity of China's exports to Russia: dependency relative to Russia's normal weight in world imports. |
| transportation | chn_trans_cost | 33% | 6.7% | Transport and insurance cost on China's imports from Russia (CIF minus FOB gap, yearly value spread over months). Higher cost = harder to move goods. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| transportation | lsci_chn | 11% | 2.2% | China's liner shipping connectivity (UNCTAD). Higher = better connected, so lower risk. |
| transportation | lsci_rus | 22% | 4.4% | Russia's liner shipping connectivity (UNCTAD). Higher = better connected, so lower risk. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| transportation | lsbci | 33% | 6.7% | Bilateral shipping connectivity between China and Russia (yearly value repeated across months). Higher = lower risk. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| economic | rub_depr_12m | 17% | 3.3% | Ruble weakening vs USD over 12 months: makes imports and debt service more expensive for Russia. |
| economic | rub_vol_6m | 17% | 3.3% | How jumpy the ruble has been: unstable prices make contracts and payments riskier. |
| economic | cny_vol_6m | 17% | 3.3% | How jumpy the yuan has been: unstable prices make contracts and payments riskier. |
| economic | rus_cpi_yoy | 17% | 3.3% | Russian inflation: a sign of supply and price stress inside Russia. |
| economic | chn_cpi_yoy | 17% | 3.3% | Chinese inflation: a sign of price stress inside China. |
| economic | chn_price_index | 17% | 3.3% | China's commodity net export price index. Higher = better terms of trade, so lower risk (direction -1). |
| geopolitical | gpr_global | 17% | 3.3% | Global geopolitical risk (GPR) news index: world-wide tension that affects every route and counterparty. |
| geopolitical | gpr_rus | 50% | 10.0% | Geopolitical risk (GPR) news index for Russia. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| geopolitical | gpr_chn | 33% | 6.7% | Geopolitical risk (GPR) news index for China. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| sanctions | rus_sanc_start | 43% | 8.6% | New sanction cases against Russia that started this month (GSDB). Scored with a rolling z-score because the series is mostly zeros. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| sanctions | chn_sanc_start | 14% | 2.9% | New sanction cases against China that started this month (GSDB). Rolling z-score because the series is mostly zeros. |
| sanctions | rus_sanc | 29% | 5.7% | Active sanction cases against Russia (GSDB). Rolling z-score. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| sanctions | chn_sanc | 14% | 2.9% | Active sanction cases against China (GSDB). Rolling z-score. |

## Does the weighting choice change the answer? (sensitivity test)

| Variant | Correlation with main | Avg difference (pts) | Same alert status | Latest |
|---|---|---|---|---|
| MAIN: equal baskets, configured indicator weights | 1.00 | 0.0 | 100% | 64.1 |
| All indicators weighted the same (ignore configured weights) | 0.99 | 1.3 | 98% | 63.8 |
| Configured weights flattened (square root of each weight) | 1.00 | 0.6 | 99% | 64.1 |
| PCA basket weights | 0.98 | 4.7 | 98% | 64.9 |
| Learned basket weights (walk-forward) | 0.66 | 11.7 | 91% | 41.6 |
| Without the dependency basket | 0.95 | 3.7 | 94% | 56.6 |
| Without the transportation basket | 0.97 | 7.3 | 92% | 70.8 |
| Without the economic basket | 0.98 | 3.6 | 93% | 69.7 |
| Without the geopolitical basket | 0.92 | 4.8 | 95% | 57.6 |
| Without the sanctions basket | 0.99 | 2.4 | 96% | 63.9 |

Reading the table: a correlation near 1 and a small average difference mean the result does not depend on the weights. Large differences (usually PCA and learned) are why those two are shown only as alternatives.
