# How the Russia index is weighted, and why

There are two layers of weights.

## Layer 1: indicators inside each basket
Each basket is a weighted average of its indicators' 0-100 scores. In the config every indicator has a `weight` (1 if not written) and a `why` line.

- **Weight 1** = a standard indicator.
- **Weight 2 or 3** = an indicator the team judged more important for this country's corridor risk. The reason is in the last column of the table below. These weights are judgement, not fitted to the data.
- The sensitivity test at the end shows how much these weights change the index. Nothing was tuned to the 2014 or 2022 shocks.

## Layer 2: the baskets into one index
- **Main index = equal basket weights.** Reasons: (1) there is no theory that says one component matters more; (2) with only two big shocks in the data, any 'optimal' weights would be fitted to two events; (3) it is the easiest to explain and audit.
- **PCA weights** (alternative): first principal component explains 40% of component variance, so it is only a weak single factor, and the weights depend heavily on the training window. Weights: dependency 22%, transportation 25%, economic 0%, geopolitical 25%, sanctions 28%.
- **Learned weights** (alternative): ridge regression predicting a later trade shortfall, refitted every January using only past data. Latest learned weights: dependency 1%, transportation 0%, economic 99%, geopolitical 0%, sanctions 0%.

## What each indicator is and how much it counts (equal-weight index)

| Basket | Indicator | Weight inside basket | Share of final index | Why it is in the index |
|---|---|---|---|---|
| dependency | rus_export_dep | 38% | 7.5% | Share of Russia's exports that go to China. The more of its sales rest on one buyer, the more a disruption hurts. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| dependency | rus_import_dep | 38% | 7.5% | Share of Russia's imports that come from China (China-reported, see note). The more it relies on one supplier, the harder it is to replace goods. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| dependency | tii_rus | 12% | 2.5% | Trade intensity of Russia's exports to China: dependency relative to China's normal weight in world trade. Separates real dependence from China simply being big. |
| dependency | tii_rus_imp | 12% | 2.5% | Same idea for Russia's imports from China. |
| transportation | rus_trans_cost | 33% | 6.7% | Transport and insurance cost on Russia's imports from China (CIF minus FOB gap, yearly value spread over months). Higher cost = harder to move goods. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| transportation | lsci_chn | 22% | 4.4% | China's liner shipping connectivity (UNCTAD). Higher = better connected, so lower risk. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| transportation | lsci_rus | 11% | 2.2% | Russia's liner shipping connectivity (UNCTAD). Higher = better connected, so lower risk. |
| transportation | lsbci | 33% | 6.7% | Bilateral shipping connectivity between China and Russia (yearly value repeated across months). Higher = lower risk. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| economic | rub_depr_12m | 20% | 4.0% | Ruble weakening vs USD over 12 months: makes imports and debt service more expensive for Russia. |
| economic | rub_vol_6m | 20% | 4.0% | How jumpy the ruble has been: unstable prices make contracts and payments riskier. |
| economic | cny_vol_6m | 20% | 4.0% | How jumpy the yuan has been: unstable prices make contracts and payments riskier. |
| economic | rus_cpi_yoy | 20% | 4.0% | Russian inflation: a sign of supply and price stress inside Russia. |
| economic | rus_price_index | 20% | 4.0% | Russia's commodity net export price index. Higher = better terms of trade, so lower risk (direction -1). |
| geopolitical | gpr_global | 20% | 4.0% | Global geopolitical risk (GPR) news index: world-wide tension that affects every route and counterparty. |
| geopolitical | gpr_rus | 20% | 4.0% | Geopolitical risk (GPR) news index for Russia. |
| geopolitical | gpr_chn | 60% | 12.0% | Geopolitical risk (GPR) news index for China. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| sanctions | rus_sanc_start | 14% | 2.9% | New sanction cases against Russia that started this month (GSDB). Scored with a rolling z-score because the series is mostly zeros. |
| sanctions | chn_sanc_start | 43% | 8.6% | New sanction cases against China that started this month (GSDB). Rolling z-score because the series is mostly zeros. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |
| sanctions | rus_sanc | 14% | 2.9% | Active sanction cases against Russia (GSDB). Rolling z-score. |
| sanctions | chn_sanc | 29% | 5.7% | Active sanction cases against China (GSDB). Rolling z-score. Weight above 1 set by Takia: judged more important for this corridor. REASON TO CONFIRM. |

## Does the weighting choice change the answer? (sensitivity test)

| Variant | Correlation with main | Avg difference (pts) | Same alert status | Latest |
|---|---|---|---|---|
| MAIN: equal baskets, configured indicator weights | 1.00 | 0.0 | 100% | 65.5 |
| All indicators weighted the same (ignore configured weights) | 0.99 | 1.4 | 99% | 65.8 |
| Configured weights flattened (square root of each weight) | 1.00 | 0.7 | 99% | 65.7 |
| PCA basket weights | 0.97 | 3.3 | 97% | 69.8 |
| Learned basket weights (walk-forward) | 0.24 | 11.2 | 72% | 46.0 |
| Without the dependency basket | 0.96 | 5.8 | 91% | 59.3 |
| Without the transportation basket | 0.97 | 8.5 | 81% | 72.1 |
| Without the economic basket | 0.97 | 3.4 | 96% | 70.5 |
| Without the geopolitical basket | 0.93 | 4.0 | 92% | 58.2 |
| Without the sanctions basket | 0.99 | 1.9 | 95% | 67.0 |

Reading the table: a correlation near 1 and a small average difference mean the result does not depend on the weights. Large differences (usually PCA and learned) are why those two are shown only as alternatives.
