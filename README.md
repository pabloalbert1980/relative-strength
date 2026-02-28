# RS Rating — IBD Style Relative Strength

> Fork of [Skyte](https://github.com/skyte/relative-strength)'s project, modified by [maximbelyayev](https://github.com/maximbelyayev/relative-strength), maintained by [Fred6725](https://github.com/Fred6725).  
> Maintenance assistance provided by [Claude](https://claude.ai) (Anthropic).

IBD Style Relative Strength Percentile Ranking of Stocks (0-99 score).  
TradingView indicator using this data: **https://www.tradingview.com/script/pziQwiT2/**

---
# Buy Me A Coffee
<a href="https://www.buymeacoffee.com/fred6725" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
---

## Daily Generated Outputs

Updated every weekday automatically via GitHub Actions (~16 min run, ~6100 tickers).

### Browsable on GitHub (rendered as table)

| File | Content |
|------|---------|
| [rs_stocks_1.csv](https://github.com/Fred6725/rs-log/blob/main/output/rs_stocks_1.csv) | Stocks — Percentile 50 to 99 (strongest) |
| [rs_stocks_2.csv](https://github.com/Fred6725/rs-log/blob/main/output/rs_stocks_2.csv) | Stocks — Percentile 0 to 49 |
| [rs_industries.csv](https://github.com/Fred6725/rs-log/blob/main/output/rs_industries.csv) | Industry rankings |

### Full dataset (download / Google Sheets)

| File | Content |
|------|---------|
| [rs_stocks.csv](https://github.com/Fred6725/rs-log/blob/main/output/rs_stocks.csv) | All ~6100 stocks in one file |

---

## Using with Google Sheets

The easiest way to filter, sort, and scan the full dataset.  
Use the **raw** GitHub URLs with `IMPORTDATA()` — no login required, auto-refreshes on open.

### Full dataset in one sheet (recommended)

Paste this in cell `A1`:
```
=IMPORTDATA("https://raw.githubusercontent.com/Fred6725/rs-log/main/output/rs_stocks.csv",",",0)
```

### What you can filter on

Once imported, use standard Google Sheets filters or `QUERY()` to slice by:
- **Sector / Industry** — find the strongest stocks in a given sector
- **Percentile** — focus on RS ≥ 90 for IBD-style momentum screens
- **MarketCap** — filter by large/mid/small cap
- **Float** — identify low-float momentum candidates
- **AvgVol50** — filter by liquidity (IBD standard: 50-day average volume)
- **ShortFloatPct** — spot heavily shorted stocks (note: updated 2x/month by Yahoo)
- **PctFrom52WkHigh** — find stocks near their highs vs. extended ones

---

## Output Columns

| Column | Description | Source |
|--------|-------------|--------|
| Rank | Overall rank (1 = strongest) | Calculated |
| Ticker | Stock symbol | NASDAQ list |
| Sector | GICS Sector | Yahoo Finance |
| Industry | GICS Sub-Industry | Yahoo Finance |
| Exchange | NYSE / NASDAQ / etc. | NASDAQ list |
| Relative Strength | Raw RS score | Calculated |
| Percentile | 0–99 percentile rank | Calculated |
| 1M/3M/6M_RS_Percentile | RS percentile 1, 3, 6 months ago | Calculated |
| Price | Last closing price | Yahoo Finance |
| MarketCap | Market capitalisation | Yahoo Finance |
| Float | Float shares | Yahoo Finance |
| ShortFloatPct | Short % of float (2x/month) | Yahoo Finance |
| 52WkHigh / 52WkLow | 52-week high and low | Yahoo Finance |
| PctFrom52WkHigh | % distance from 52-week high | Calculated |
| AvgVol10/30/50/60 | Average volume over 10/30/50/60 days | Calculated |

---

## Calculation

```
RS Score (stock) = 40% × P3 + 20% × P6 + 20% × P9 + 20% × P12
RS Score (SPY)   = 40% × P3 + 20% × P6 + 20% × P9 + 20% × P12
Final RS = (1 + RS Score stock) / (1 + RS Score SPY)
```

Where P3 = performance over the last 3 months (63 trading days), etc.  
All stocks are then ranked and assigned a percentile from 99 (strongest) to 0 (weakest).

---

## Considered Stocks

All tickers from [nasdaqtrader.com](https://www.nasdaqtrader.com/dynamic/symdir/nasdaqtraded.txt), excluding ETFs and test issues (~6100 stocks across NYSE, NASDAQ, NYSE ARCA, BATS).

---

## Known Issues

- Close prices from Yahoo Finance are not always split-adjusted. If a stock had a recent split, its RS value may be temporarily off.
- Short interest (`ShortFloatPct`) is updated by Yahoo Finance twice a month — may lag other sources like Finviz.
- `Float` may be missing for some small-cap stocks.
- Occasionally 1–2 tickers per run are skipped due to Yahoo rate limiting. No meaningful impact on percentile distribution.

---

## How To Run (Python Script)

### Requirements
- Python 3.10 or higher (3.11 recommended)

```bash
git clone https://github.com/Fred6725/relative-strength.git
cd relative-strength
pip install -r requirements.txt
python relative-strength.py true
```

Output files will be in the `output/` folder.

---

## Support the Project

If this is useful to you, consider buying me a coffee ☕

<a href="https://www.buymeacoffee.com/fred6725" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
