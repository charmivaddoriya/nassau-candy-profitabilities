# Product Line Profitability & Margin Performance Analysis for Nassau Candy Distributor

**Unified Mentor Project · Research Paper**

## Abstract
Sales volume alone can mislead a distributor. This paper analyses 9,881 validated order lines (Jan 2024 – Dec 2025) from Nassau Candy Distributor to show which products and divisions really create gross profit. The business earned $138,284 in sales and $91,076 in gross profit (65.9% margin). Profit is extremely concentrated: five chocolate products deliver 92.7% of revenue and 94.9% of profit, while seven Sugar products together contribute 0.3%. Two margin risks stand out: Kazookles (7.7% margin) and the Other division (44.8% margin versus 67.4% for Chocolate). We close with a ranked action list: reprice, renegotiate cost, review for discontinuation, and protect the chocolate core.

## 1. Introduction and objectives
The brief asks four questions: which product lines deliver the highest gross margin; whether high-sales products are actually profitable; how profitability varies by division; and which products are margin risks. We answer them with product, division, Pareto and cost-structure analysis, and deliver the results as a Streamlit dashboard.

## 2. Data and cleaning
The dataset has 10,194 rows and 18 fields (order, customer, geography, division, product, sales, units, gross profit, cost). Cleaning steps and outcomes:

| Check | Result |
|---|---|
| Invalid dates | 0 |
| Zero/negative sales, missing cost or profit | 0 rows removed |
| Missing or zero units | 0 (imputation rule built in for future data) |
| Gross Profit = Sales − Cost | Holds on every row |
| Negative-profit rows / cost > sales | 0 |
| Duplicate order lines (same order, product, customer, date, values; different Row ID) | 313 removed |
| Labels | Trimmed and standardised; products mapped to their factories |

The analysis uses 9,881 rows covering 15 products, 3 divisions, 4 regions and 5 factories. One caveat: Ship Date values run well beyond Order Date (some into 2026), so shipping timelines were not used here; they do not affect profitability metrics.

## 3. Metrics
- Gross Margin % = Gross Profit ÷ Sales
- Profit per Unit = Gross Profit ÷ Units
- Revenue / Profit Contribution = product value ÷ portfolio total
- Margin Volatility = standard deviation of monthly margin, in percentage points
- Herfindahl index (HHI) for concentration

## 4. Findings

### 4.1 Portfolio overview
Sales rose from $56,577 in 2024 to $81,707 in 2025 (+44%). Portfolio margin stayed within 64.5%–66.7% each month (std. dev. 0.53 pp). Margins are almost identical across regions (65.4%–66.4%), so geography is not a margin driver. Order-level cost and sales are highly correlated (r = 0.96), meaning cost scales with order size and margin is set mainly by product, not by order.

### 4.2 Product-level profitability (Fig 1)
- **Stars:** Wonka Bar Scrumdiddlyumptious ($18,770 profit, 20.6% of total, 69.4% margin), Nutty Crunch Surprise (71.4% margin, highest among large products) and Fudge Mallows (66.7%).
- **Slightly below average, high volume:** Triple Dazzle Caramel (65.3%) and Milk Chocolate (64.9%). Milk Chocolate sells the most units (8,079) but earns the least profit per unit among the bars ($2.11). The gap to the portfolio average is under 1 pp, so this is a mild pricing opportunity rather than a problem.
- **High-profit per unit, low volume:** Lickable Wallpaper earns $10.00 per unit at 50% margin but sold only 393 units (4.3% of profit).
- **Margin risks:** Kazookles sells at about $3.25 against a unit cost of about $3.00, a 7.7% margin. It generated $1,206 of sales but only $93 of profit (0.10%). SweeTARTS and Nerds (46.7%) and Fun Dip (40.0%) also sit well below the portfolio margin with very low sales.
- **Best margins, tiny volume:** Everlasting Gobstopper (80%) and Hair Toffee (77.8%) sell only 13 and 17 units, so they cannot move the total.

Margin volatility at product level is zero: each product has fixed unit economics (stable price and cost). Volatility exists only through product mix, at division level (Chocolate 0.24 pp; Other 10.2 pp; Sugar 11.1 pp, on very small volumes).

### 4.3 Division performance (Fig 2)
| Division | Sales | Profit | Margin | Revenue share | Profit share |
|---|---|---|---|---|---|
| Chocolate | $128,193 | $86,458 | 67.4% | 92.7% | 94.9% |
| Other | $9,663 | $4,333 | 44.8% | 7.0% | 4.8% |
| Sugar | $427 | $285 | 66.6% | 0.3% | 0.3% |

Chocolate is financially efficient: its profit share exceeds its revenue share by 2.2 pp. The Other division has a structural margin problem, losing 2.2 pp of share between revenue and profit, driven by Kazookles and the 50–52% margins on Lickable Wallpaper and Wonka Gum. Sugar has healthy average margins but is commercially negligible: seven products, 137 units.

### 4.4 Profit concentration (Fig 3)
Five of 15 products (33%) are needed to reach 80% of revenue and the same five for 80% of profit; together they provide 92.7% of revenue and 94.9% of profit. HHI is 1,760 for revenue and 1,827 for profit (moderate concentration across the five bars, but extreme between divisions). Geographically, California supplies 19.7% of profit, New York 10.9% and Texas 9.5% (top three = 40%). The key dependency risks are therefore the chocolate division and two factories: Lot's O' Nuts (69.1% margin, $74.3k sales) and Wicked Choccy's (65.1%, $53.9k).

### 4.5 Cost structure diagnostics (Fig 4)
On a cost-versus-sales view, the five chocolate bars sit on a clean, low cost-to-sales line (cost ≈ 29–35% of sales). Kazookles is the outlier: cost is 92% of sales. By factory, The Other Factory earns only 11.9% margin (Kazookles and Hair Toffee), versus 50.6% at Secret Factory and 54.9% at Sugar Shack. Flags generated by the dashboard (threshold = 90% of portfolio margin):

| Product | Margin | Flag |
|---|---|---|
| Kazookles | 7.7% | Cost renegotiation |
| Lickable Wallpaper, Wonka Gum | 50%, 52% | Repricing |
| SweeTARTS, Nerds, Fun Dip | 46.7%, 46.7%, 40% | Discontinuation review |

## 5. Recommendations
1. **Fix Kazookles first.** Raise the price, or cut unit cost by about 20% (from about $3.00 to about $2.40, which gives a margin near 26%); otherwise review it for discontinuation.
2. **Test small price increases on chocolate.** A 1% rise across the five bars adds about $1.3k gross profit (about 1.4%) if volume holds; start with Milk Chocolate and Triple Dazzle Caramel.
3. **Reprice Lickable Wallpaper and Wonka Gum**, and renegotiate costs at Secret Factory.
4. **Rationalise the Sugar long tail.** Review SweeTARTS, Nerds and Fun Dip; decide whether to grow Gobstopper and Hair Toffee (80% and 78% margins) through promotion or keep them as niche items.
5. **Reduce dependency.** Protect supply at Lot's O' Nuts and Wicked Choccy's (backup capacity, long-term contracts) and grow outside California, New York and Texas.
6. **Monitor monthly** using the dashboard's margin-threshold slider and risk flags.

## 6. Limitations
Only gross profit is available (no marketing, freight or overhead). Two years of data, with product prices fixed, mean margin volatility cannot show price elasticity. Dedupe assumes repeated order lines are data errors. Recommendations are directional and should be tested before scaling.

## 7. Conclusion
Nassau Candy's profit engine is the chocolate division. Sales volume is a reasonable proxy for profit among the bars, but not in the Other and Sugar divisions, where low-margin products consume attention without adding profit. Targeted repricing, cost renegotiation and portfolio rationalisation can raise overall margin while protecting the chocolate core.

*Figures 1–5 are in the repository's `figures/` folder. Code: `analysis.py`, `app.py`.*
