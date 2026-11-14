# **OVERALL DATASET DESCRIPTION**

All the raw and calclulated values. Calculated variables have the calculation used underneath it.

## UNIT

* All monetary trade values are reported in **millions of U.S. dollars (USD)**.
* Import values are in CIF
* Export values are in FOB
* `GPR` values are **index values** based on their respective index base periods.
* `GPR_RUS` and `GPR_CHN` are reported as **percentages of articles**.
* `CPI` values are reported as **percentage changes**.

## SOURCES

* **International Monetary Fund (IMF)**
    * Global/bilateral trade data
    * Inflation data
    * Commodity price index
* **Caldara, Dario and Matteo Iacoviello, Geopolitical Risk (GPR) Index dataset**
    * Geopolitical risk data 
* **Federal Reserve Economic Data (FRED)**
    * Exchange rate data
* **General Administration of Customs China (GACC)**
    * Commodity trade values and concentrations (separate dataset)
* **Organisation for Economic Co-operation and Development (OECD)**
    * Transport/Insurance cost
* **Global Sanctions Data Base**
    * Sanctions
* **UN Trade and Development (UNCTAD)**
    * Liner Shipping Connectivity 

## TIME PERIOD

**January 2006 - August 2026**

Some values are missing for May - Aug 2026

---

# **COLUMN DESCRIPTIONS**

## **Trade Risk Data**

### `Month`

Month and year associated with the data.

### `China Global Imports (CIF)` (`CHN_IMP`)

China's total monthly imports of goods in millions of dollars, valued using the **Cost, Insurance, and Freight (CIF)** method.

### `China Global Exports (FOB)` (`CHN_EXP`)

China's total monthly exports of goods in millions of dollars, valued using the **Free on Board (FOB)** method.

### `China Global Trade Balance` (`CHN_TB`)

China's total monthly trade balance in millions of dollars, representing **exports minus imports**.

### `Russia Global Imports (CIF)` (`RUS_IMP`)

Russia's total monthly imports of goods in millions of dollars, valued using the **CIF** method.

### `Russia Global Exports (FOB)` (`RUS_EXP`)

Russia's total monthly exports of goods in millions of dollars, valued using the **FOB** method.

### `Russia Global Trade Balance` (`RUS_TB`)

Russia's total monthly trade balance in millions of dollars, representing **exports minus imports**.

### `Russia Imports from China (CIF)` (`RUS_IMP_CHN`)

The value of goods Russia imports from China each month in millions of dollars, valued using the **CIF** method.

### `Russia Exports to China (FOB)` (`RUS_EXP_CHN`)

The value of goods Russia exports to China each month in millions of dollars, valued using the **FOB** method.

### `Russia's Trade Balance with China` (`RUS_TB_CHN`)

Russia's monthly bilateral trade balance with China in millions of dollars, representing **exports to China minus imports from China**.

### `China Imports from Russia (CIF)` (`CHN_IMP_RUS`)

The value of goods China imports from Russia each month in millions of dollars, valued using the **CIF** method.

### `China Exports to Russia (FOB)` (`CHN_EXP_RUS`)

The value of goods China exports to Russia each month in millions of dollars, valued using the **FOB** method.

### `China's Trade Balance with Russia` (`CHN_TB_RUS`)

China's monthly bilateral trade balance with Russia in millions of dollars, representing **exports to Russia minus imports from Russia**.

### `Global Imports (CIF)` (`G_IMP`)

Total monthly world imports of goods in millions of dollars, valued using the **CIF** method.

### `Global Exports (FOB)` (`G_EXP`)

Total monthly world exports of goods in millions of dollars, valued using the **FOB** method.

### `Russia-China Trade Intensity Index` (`RUS_CHN_TII`)

Measures the trade intensity idnex of Russia's exports to China relative to China's share of global imports. A TII greater than 1 indicates that China represents a larger share of Russia's exports than China's share of global imports.

***Calculation:*** Russia-China TII = (Russia Exports to China / Russia Global Exports) / (China Global Imports / Global Imports)

### `China-Russia Trade Intensity Index` (`CHN_RUS_TII`)

The Trade Intensity Index measuring the intensity of China's exports to Russia relative to Russia's share of global imports. A value greater than 1 indicates that China's exports to Russia represent a larger share of China's exports than would be expected based on Russia's share of world imports.

***Calculation:*** China-Russia TII = (China Exports to Russia / China Global Exports) / (Russia Global Imports / Global Imports)

---
## **Dependency Risk Data**

### `Russia Import Dependency on China` (`RUS_IMP_DEP`)

Measures the proportion of Russia's total imports that originate from China.

***Calculation:*** Russia Import Dependency on China = Russia Imports from China / Russia Global Imports

### `Russia Export Dependency on China` (`RUS_EXP_DEP`)

Measures the proportion of Russia's total exports that are destined for China.

***Calculation:*** Russia Export Dependency on China = Russia Exports to China / Russia Global Exports

### `China Import Dependency on Russia` (`CHN_IMP_DEP`)

The proportion of China's total imports that originate from Russia. This is calculated as China's imports from Russia divided by China's global imports.

***Calculation:*** China Import Dependency on Russia = China Imports from Russia / China Global Imports

### `China Export Dependency on Russia` (`CHN_EXP_DEP`)

The proportion of China's total exports that are destined for Russia. This is calculated as China's exports to Russia divided by China's global exports.

***Calculation:*** China Export Dependency on Russia = China Exports to Russia / China Global Exports

---
## **Transportation Risk**

### `China Transport Costs from Russia` (`CHN_TRANS_FROM_RUS`)

Measures China’s estimated transport and insurance costs for imports from Russia using the OECD International Transport and Insurance Costs (ITIC) dataset. The annual cost ratio is applied to each month within the corresponding year to align with the monthly trade dataset. The 2024 value is carried forward for 2025 and 2026 where annual estimates are unavailable.

***Calculation:*** ITIC Margin = (CIF-FOB)/CIF

### `Russia Transport Costs from China` (`RUS_TRANS_FROM_CHN`)

Measures Russia’s estimated transport and insurance costs for imports from China using the OECD International Transport and Insurance Costs (ITIC) dataset. The annual cost ratio is applied to each month within the corresponding year to align with the monthly trade dataset. The 2024 value is carried forward for 2025 and 2026 where annual estimates are unavailable. The margin is calculated as:

***Calculation:*** ITIC Margin = (CIF-FOB)/CIF

### `China Liner Shipping Connectivity Index` (`LSCI_CHN`)

Measures **China's connectivity to the global liner shipping network**. The LSCI reflects factors related to the availability and connectivity of container shipping services linking a country to international markets. Higher values indicate stronger liner shipping connectivity.

### `Russia Liner Shipping Connectivity Index` (`LSCI_RUS`)

Measures **Russia's connectivity to the global liner shipping network**. Higher values indicate stronger liner shipping connectivity and greater integration into the international liner shipping network.


***LSCI Data Note:***
The available LSCI data contained quaterly observations for earlier years and monthly observations beginning in 2023. To integrate the data into the monthly dataset, missing monthly values between available observations were estimated using linear interpolation. Therefore, not all monthly LSCI values represent directly observed values. The interpolated values should be treated as estimates rather than observed measurements.

### `Liner Shipping Connectivity Index` (`LSBCI`)

Measures liner shipping connectivity and the degree to which a country's shipping network is integrated into the global liner shipping network. Higher values indicate stronger connectivity and greater integration into international shipping networks.


***LSBCI Data Note:***
The available LSBCI data contained annual values reported for the first quarter (Q1) of each year. To integrate the data into the monthly dataset, each year's available LSBCI value was applied uniformly to all 12 months of that year. Therefore, monthly LSBCI values do not represent independent monthly observations; they repeat the corresponding annual value. These values should be interpreted as annual connectivity measurements carried forward across the months, rather than as observed monthly changes.



---

## **Economic Risk Data**

### **Inflation Data**

### `China Month-Over-Month CPI` (`CHN_CPI_MoM`)

**China's month-over-month Consumer Price Index (CPI)**, representing the percentage change in consumer prices compared with the previous month.

### `China Year-Over-Year CPI` (`CHN_CPI_YoY`)

**China's year-over-year Consumer Price Index (CPI)**, representing the percentage change in consumer prices compared with the same month of the previous year.

### `Russia Month-Over-Month CPI` (`RUS_CPI_MoM`)

**Russia's month-over-month Consumer Price Index (CPI)**, representing the percentage change in consumer prices compared with the previous month.

### `Russia Year-Over-Year CPI` (`RUS_CPI_YoY`)

**Russia's year-over-year Consumer Price Index (CPI)**, representing the percentage change in consumer prices compared with the same month of the previous year.

### **Exchange Rate Data**

### `USD to RUB` (`USD_RUB`)

**U.S. dollar to Russian ruble exchange rate**, representing the number of Russian rubles equivalent to one U.S. dollar.

### `USD to CNY` (`USD_CNY`)

**U.S. dollar to Chinese renminbi exchange rate**, representing the number of Chinese renminbi equivalent to one U.S. dollar.

### **Prices Data**

### `Russia Commodity Net Export Price Index` `RUS_PRICE_INDEX`

Measures Russia’s **Commodity Net Export Price Index** from the commodity terms of trade dataset, which tracks price movements across individual commodities weighted by their net exports relative to total commodity trade, using recent, rolling weights, with base June 2012 = 100. 

### `China Commodity Net Export Price Index` `CHN_PRICE_INDEX`

Measures China’s **Commodity Net Export Price Index** from the commodity terms of trade dataset, which tracks price movements across individual commodities weighted by their net exports relative to total commodity trade, using recent, rolling weights, with base June 2012 = 100.

***Interpetation:***
Represents the difference in the trends of export and import price indices for commodities. It is calculated by subtracting the Commodity Import Price Index from the Commodity Export Price Index. A higher value indicates that the prices of exports are increasing at a faster rate than the prices of imports, potentially leading to a favorable trade balance and contributing to economic growth. This weighs commodities based on their net export value relative to the total value of commodity trade (exports plus imports).

---

## **Geopolitical Risk Data**

The following columns are obtained from the **Geopolitical Risk (GPR) Index dataset**. These values are included as raw measures and have not been calculated or modified as part of the trade analysis.

### `GPR`

**Recent Geopolitical Risk Index**, measuring the frequency of geopolitical risk-related terms in newspaper articles. The index is normalized to **100 for the 1985-2019 period**.

### `GPR_RUS` 

**Country-specific Geopolitical Risk measure for Russia**, representing the percentage of recent newspaper articles associated with Russia-related geopolitical risk.

### `GPR_CHN`

**Country-specific Geopolitical Risk measure for China**, representing the percentage of recent newspaper articles associated with China-related geopolitical risk.

### `Russia Sanctions Start` (`RUS_SANC_START`)

Measures the **monthly number of new sanctions cases targeting Russia** using the Global Sanctions Data Base (GSDB-R5). Each unique sanction case is counted once on the month it started.

### `China Sanctions Start` (`CHN_SANC_START`)

Measures the **monthly number of new sanctions cases targeting China** using the Global Sanctions Data Base (GSDB-R5). Each unique sanction case is counted once on the month it started. 

### `Russia Sanctions Count` (`RUS_SANC`)

Measures the **monthly number of new sanctions cases targeting China** using the Global Sanctions Data Base (GSDB-R5). Each unique sanction case is counted once on the month it started. (Note: 2026 data is not available, but February 2026 and June 2026 were estimated as one to reflect 2 known EU sanctions that started on that month.)


### `China Sanctions Count` (`CHN_SANC`)

Measures the **monthly number of active sanction cases targeting China** using the Global Sanctions Data Base (GSDB-R5). Each unique sanction case is counted once per month when its active period overlaps that month, based on its recorded start and end dates.

### `Russia Sanctions Count` (`RUS_SANC`)

Measures the **monthly number of active sanction cases targeting Russia** using the Global Sanctions Data Base (GSDB-R5). Each unique sanction case is counted once per month when its active period overlaps that month, based on its recorded start and end dates.

### `China–Russia Bilateral Sanctions Count` (`CHN_RUS_SANC`)

Measures the **monthly number of active sanction cases imposed directly between China and Russia**, using the Global Sanctions Data Base (GSDB-R5). It includes both directions: sanctions imposed by China targeting Russia and sanctions imposed by Russia targeting China. Each unique case is counted once per month when its active period overlaps that month, regardless of how many sanction types are included.

**Methodological note — GSDB-R5:** 

The GSDB uses a **state-to-state case-based approach** rather than counting individual designated entities or legal measures. A single sanctions package with one objective containing asset freezes, export restrictions, and travel bans is generally recorded as **one sanction case with multiple sanction types**, rather than as three separate cases. Consequently, this column measures the number of active bilateral sanction cases, not the number of individual restrictions, legal instruments, or designated entities. Sanctions imposed by either country against third countries are excluded.

For January–August 2026, December 2025 values are carried forward because the historical sanctions data do not provide observed counts for those months. These 2026 values are imputed estimates, not observed sanction counts.


---

## **Concentration Risk Data** (separate dataset)

### `Russia's Herfindahl-Hirschman Index` (`RUS_HHI`) 

Measures the concentration of Russia’s exports across commodity categories using the Herfindahl-Hirschman Index (HHI). Higher values indicate greater reliance on a smaller number of commodity categories, while lower values indicate a more diversified export composition.

### `China's Herfindahl-Hirschman Index` (`CHN_HHI`)

Measures the concentration of China’s exports across commodity categories using the Herfindahl-Hirschman Index (HHI). Higher values indicate greater reliance on a smaller number of commodity categories, while lower values indicate a more diversified export composition.

### `Concentrations (separate dataset)`

The columns in the 2 concentration datasets are the trade values of the top 10 current HS categories exported from both countries. The columns with suffix _CON are the concentration of that commodity out of the total trade value.

The HS codes and names are given below.

## Russia — HS Commodity Codes

| HS Code | Commodity Name |
|---|---|
| 03 | Fish and crustaceans, molluscs and other aquatic invertebrates |
| 12 | Oil seeds and oleaginous fruits; miscellaneous grains, seeds and fruits; industrial or medicinal plants; straw and fodder |
| 15 | Animal or vegetable fats and oils and their cleavage products; prepared edible fats; animal or vegetable waxes |
| 26 | Ores, slag and ash |
| 27 | Mineral fuels, mineral oils and products of their distillation; bituminous substances; mineral waxes |
| 31 | Fertilizers |
| 44 | Wood and articles of wood; wood charcoal |
| 71 | Natural or cultured pearls, precious or semiprecious stones, precious metals, metals clad with precious metal, and articles thereof; imitation jewelry; coin |
| 74 | Copper and articles thereof |
| 76 | Aluminum and articles thereof |

## China — HS Commodity Codes

| HS Code | Commodity Name |
|---|---|
| 29 | Organic chemicals |
| 39 | Plastics and articles thereof |
| 40 | Rubber and articles thereof |
| 61 | Articles of apparel and clothing accessories, knitted or crocheted |
| 64 | Footwear, gaiters and the like; parts of such articles |
| 73 | Articles of iron or steel |
| 84 | Nuclear reactors, boilers, machinery and mechanical appliances; parts thereof |
| 85 | Electrical machinery and equipment and parts thereof; sound recorders and reproducers, television image and sound recorders and reproducers, and parts and accessories of such articles |
| 87 | Vehicles other than railway or tramway rolling stock, and parts and accessories thereof |
| 90 | Optical, photographic, cinematographic, measuring, checking, precision, medical or surgical instruments and apparatus; parts and accessories thereof |