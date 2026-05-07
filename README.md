# NDX Monte Carlo Simulator

A single-file, client-side Monte Carlo simulator for Nasdaq-100 (NDX) portfolios with support for leveraged ETFs, rebalancing strategies, DCA, withdrawals, and margin loans.

> **風險聲明 · Risk Disclaimer**
> 本工具僅供學術研究與教育用途，不構成任何投資建議。槓桿投資涉及高度風險，可能導致損失超過本金。
> For educational and research purposes only. Not investment advice. Past performance does not guarantee future results.

---

## Features

- **Bootstrap sampling** — daily (i.i.d.) or annual block resampling from historical NDX data (1985–present)
- **Leveraged ETFs** — synthetic NDX 2× and 3× with daily compounding, embedded borrowing cost, and expense ratio
- **7 rebalancing strategies** — none, fixed interval, beta threshold, smart, defensive/aggressive flexible, and glide path
- **DCA** — periodic investment at monthly / quarterly / annual intervals
- **Withdrawals** — fixed-rate (% p.a.) or fixed-amount periodic withdrawals
- **Margin loan** — LTV-based monthly withdrawals with margin call liquidation
- **Initial debt** — models mortgage / securities lending with optional forced liquidation
- **Historical data tab** — annual NDX returns, USD M2 supply, risk-free rate, and rolling Kelly fraction charts
- **Comparison tab** — fan chart, box plots, and side-by-side stats for multiple configurations
- **Export** — all tabs exportable as PNG or PDF with embedded risk disclaimer
- **No server required** — pure static HTML/JS, open `index.html` directly in any browser
- **Mobile responsive** — slide-in sidebar layout for small screens

---

## Quick Start

```
# Clone
git clone https://github.com/petahung/monte_carlo_sim.git
cd monte_carlo_sim

# Open in browser — no build step needed
open index.html        # macOS
start index.html       # Windows
```

---

## Repository Structure

```
index.html                          Main simulator (self-contained)

Nasdaq 100 Historical Data (*.csv)  NDX daily price & return data (Investing.com export)
QLD.csv                             ProShares Ultra QQQ (2×) historical data
TQQQ.csv                            ProShares UltraPro QQQ (3×) historical data
ndx_leveraged.csv                   Synthetic NDX 2× / 3× series (1985–present)
ndx_leveraged_1999.csv              Synthetic series starting 1999
compare_NDX2L_vs_QLD.csv            Synthetic vs actual QLD comparison
compare_NDX3L_vs_TQQQ.csv           Synthetic vs actual TQQQ comparison
美元貨幣市場基金利率趨勢.csv           USD money market / risk-free rate history

build_leveraged_etf.py              Builds ndx_leveraged.csv from raw NDX CSVs
build_leveraged_etf.ps1             PowerShell wrapper for build script
compare_leverage.ps1                Compares synthetic ETF series against actual QLD/TQQQ
download_etf.ps1                    Downloads QLD / TQQQ data from Yahoo Finance
```

---

## Data Sources

| Dataset | Source |
|---------|--------|
| NDX daily prices | [Investing.com](https://www.investing.com/indices/nasdaq-100-historical-data) |
| QLD / TQQQ | Yahoo Finance (via `download_etf.ps1`) |
| USD M2 supply | [FRED M2SL](https://fred.stlouisfed.org/series/M2SL) (hardcoded annual, updated manually) |
| Risk-free rate | USD money market fund rate (embedded in `index.html`) |

---

## Rebuilding Leveraged ETF Data

When new NDX CSV exports are added, regenerate the synthetic series:

```powershell
# PowerShell
.\build_leveraged_etf.ps1

# or Python directly
python build_leveraged_etf.py
```

The script merges all `Nasdaq 100 Historical Data*.csv` files, deduplicates by date, and outputs `ndx_leveraged.csv` with synthetic 2× / 3× columns using daily compounding (expense ratio and borrowing cost applied).

---

## Simulation Methodology

### Returns model
Each simulation draws `N × T` daily log-returns from the historical NDX series using bootstrap resampling. Leveraged returns apply daily multiplicative leverage with:

```
r_2x = 2 × r_ndx − c_borrow / 252 − er_2x / 252
r_3x = 3 × r_ndx − c_borrow / 252 − er_3x / 252
```

Where `c_borrow` is the daily risk-free rate and `er` is the product expense ratio.

### Kelly Fraction
The rolling optimal leverage is estimated from the trailing 5-year window using the continuous Kelly criterion:

```
f* = μ / σ²
```

where μ and σ² are the annualised mean and variance of NDX daily log-returns.

---

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| [Chart.js](https://www.chartjs.org/) | 4.4.0 | All charts |
| [@sgratzl/chartjs-chart-boxplot](https://github.com/sgratzl/chartjs-chart-boxplot) | 4.4.0 | Box plots |
| [html2canvas](https://html2canvas.hertzen.com/) | 1.4.1 | Report screenshot |
| [jsPDF](https://github.com/parallax/jsPDF) | 2.5.1 | PDF export |

All dependencies loaded from CDN; no npm or build tooling required.

---

## License

© 2026 Peta Hung · All rights reserved.

本工具由 Claude (Anthropic) 協作開發，僅供個人教育與學術研究使用，不得用於商業目的。
