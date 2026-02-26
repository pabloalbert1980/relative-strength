# RS Rating — IBD Style Relative Strength for Everyone

> Fork of [Skyte](https://github.com/skyte/relative-strength)'s project, modified by [maximbelyayev](https://github.com/maximbelyayev/relative-strength), maintained by [Fred6725](https://github.com/Fred6725).

IBD Style Relative Strength Percentile Ranking of Stocks (0-99 score).  
I also made a TradingView indicator that uses the data generated here: **https://www.tradingview.com/script/pziQwiT2/**

---
# Buy Me A Coffee
<a href="https://www.buymeacoffee.com/fred6725" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
---

## Daily Generated Outputs

| File | Link |
|------|------|
| Stocks | https://github.com/Fred6725/rs-log/blob/main/output/rs_stocks.csv |
| Industries | https://github.com/Fred6725/rs-log/blob/main/output/rs_industries.csv |

Updated every weekday automatically via GitHub Actions (~30 min run, ~6800 tickers).

---

## Calculation

Yearly performance of a stock divided by SPY performance over the same period.

```
RS Score (stock) = 40% × P3 + 20% × P6 + 20% × P9 + 20% × P12
RS Score (SPY)   = 40% × P3 + 20% × P6 + 20% × P9 + 20% × P12

Final RS = (1 + RS Score stock) / (1 + RS Score SPY)
```

Where P3 = performance over the last 3 months (63 trading days), etc.  
All stocks are then ranked and assigned a percentile from 99 (strongest) to 0 (weakest).

---

## Considered Stocks

All tickers from [nasdaqtrader.com](https://www.nasdaqtrader.com/dynamic/symdir/nasdaqtraded.txt), excluding ETFs and test issues (~6800 stocks across NYSE, NASDAQ, NYSE ARCA, BATS).

---

## Known Issues

- Close prices from Yahoo Finance are not always split-adjusted. If a stock had a recent split, its RS value may be temporarily off until the data normalizes.
- Occasionally 1-2 tickers per run may be skipped due to Yahoo rate limiting. This has no meaningful impact on the overall percentile distribution.

---

## How To Run (Python Script)

### Requirements
- Python 3.10 or higher (3.11 recommended)

### Steps

```bash
# 1. Clone the repo
git clone https://github.com/Fred6725/relative-strength.git
cd relative-strength

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure (optional)
#    Edit config.yaml to change reference ticker, universe, etc.

# 4. Run
python relative-strength.py true
```

Output files will be in the `output/` folder:
- `rs_stocks.csv` — ranked stocks with RS percentile
- `rs_industries.csv` — ranked industries
- `RSRATING.csv` — formatted data for the TradingView indicator

### Separate Steps

You can also run the two stages independently:
```bash
python rs_data.py      # Step 1: download price data from Yahoo Finance
python rs_ranking.py   # Step 2: calculate RS rankings and generate CSVs
```

---

## Config

Edit `config.yaml` to customize behavior. You can also create a `config_private.yaml` next to it to override parameters like `API_KEY` without creating git conflicts.

Key settings:

| Parameter | Description |
|-----------|-------------|
| `REFERENCE_TICKER` | Benchmark ticker (default: `SPY`) |
| `USE_ALL_LISTED_STOCKS` | `true` = all NASDAQ-listed stocks, `false` = S&P/NQ100 only |
| `SP500` / `SP400` / `SP600` / `NQ100` | Enable/disable individual index universes |
| `MIN_PERCENTILE` | Minimum percentile to include in output |
| `DATA_SOURCE` | `YAHOO` (default) or `TD_AMERITRADE` |

---

## Technical Notes

The daily workflow runs on GitHub Actions and:
1. Downloads price history for ~6800 tickers in batches of 100 via `yfinance`
2. Calculates RS scores and percentile rankings
3. Pushes the output CSVs to [Fred6725/rs-log](https://github.com/Fred6725/rs-log)

Dependencies use `curl_cffi` to reliably bypass Yahoo Finance's anti-bot measures.  
Maintenance assistance provided by [Claude](https://claude.ai) (Anthropic).

---

## Support the Project

If this is useful to you, consider buying me a coffee ☕
<a href="https://www.buymeacoffee.com/fred6725" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>
