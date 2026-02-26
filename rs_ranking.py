#!/usr/bin/env python
# rs_ranking.py — Fixed version
# Changes vs original:
#   1. pandas 2.x compatibility (pd.qcut behaviour)
#   2. Minor robustness improvements (safer iloc access)
#   3. Logic and output unchanged

import sys
import pandas as pd
import numpy as np
import json
import os
from datetime import date
from scipy.stats import linregress
import yaml
from rs_data import TD_API, cfg, read_json
from functools import reduce
import datetime

DIR = os.path.dirname(os.path.realpath(__file__))

pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_columns', None)

try:
    with open('config.yaml', 'r') as stream:
        config = yaml.safe_load(stream)
except FileNotFoundError:
    config = None
except yaml.YAMLError as exc:
    print(exc)

PRICE_DATA = os.path.join(DIR, "data", "price_history.json")
MIN_PERCENTILE = cfg("MIN_PERCENTILE")
POS_COUNT_TARGET = cfg("POSITIONS_COUNT_TARGET")
REFERENCE_TICKER = cfg("REFERENCE_TICKER")
ALL_STOCKS = cfg("USE_ALL_LISTED_STOCKS")
TICKER_INFO_FILE = os.path.join(DIR, "data_persist", "ticker_info.json")
TICKER_INFO_DICT = read_json(TICKER_INFO_FILE)

TITLE_RANK = "Rank"
TITLE_TICKER = "Ticker"
TITLE_TICKERS = "Tickers"
TITLE_SECTOR = "Sector"
TITLE_INDUSTRY = "Industry"
TITLE_UNIVERSE = "Universe" if not ALL_STOCKS else "Exchange"
TITLE_PERCENTILE = "Percentile"
TITLE_1M = "1 Month Ago"
TITLE_3M = "3 Months Ago"
TITLE_6M = "6 Months Ago"
TITLE_RS = "Relative Strength"

if not os.path.exists('output'):
    os.makedirs('output')

# ── RS calculation ────────────────────────────────────────────────────────────

def relative_strength(closes: pd.Series, closes_ref: pd.Series):
    rs_stock = strength(closes)
    rs_ref = strength(closes_ref)
    rs = (1 + rs_stock) / (1 + rs_ref) * 100
    rs = int(rs * 100) / 100  # round to 2 decimals
    return rs

def strength(closes: pd.Series):
    """Calculates the performance of the last year (most recent quarter is weighted double)"""
    try:
        quarters1 = quarters_perf(closes, 1)
        quarters2 = quarters_perf(closes, 2)
        quarters3 = quarters_perf(closes, 3)
        quarters4 = quarters_perf(closes, 4)
        return 0.4 * quarters1 + 0.2 * quarters2 + 0.2 * quarters3 + 0.2 * quarters4
    except:
        return 0

def quarters_perf(closes: pd.Series, n):
    length = min(len(closes), n * int(252 / 4))
    prices = closes.tail(length)
    pct_chg = prices.pct_change().dropna()
    perf_cum = (pct_chg + 1).cumprod() - 1
    return perf_cum.tail(1).item()

# ── TradingView CSV generation ────────────────────────────────────────────────

def generate_tradingview_csv(percentile_values, first_rs_values):
    lines = []
    trading_days = 0
    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    for percentile in sorted(percentile_values):
        rs_value = first_rs_values[percentile]
        for _ in range(5):
            trading_date = yesterday - datetime.timedelta(days=trading_days)
            date_str = trading_date.strftime("%Y%m%dT")
            csv_row = f"{date_str},0,1000,0,{rs_value},0\n"
            lines.append(csv_row)
            trading_days += 1

    reversed_lines = reversed(lines)
    return ''.join(reversed_lines)

# ── Rankings ──────────────────────────────────────────────────────────────────

def rankings():
    """Returns a dataframe with percentile rankings for relative strength"""
    price_data = read_json(PRICE_DATA)
    relative_strengths = []
    ranks = []
    industries = {}
    ind_ranks = []
    stock_rs = {}
    ref = price_data[REFERENCE_TICKER]

    for ticker in price_data:
        if not cfg("SP500") and price_data[ticker].get("universe") == "S&P 500":
            continue
        if not cfg("SP400") and price_data[ticker].get("universe") == "S&P 400":
            continue
        if not cfg("SP600") and price_data[ticker].get("universe") == "S&P 600":
            continue
        if not cfg("NQ100") and price_data[ticker].get("universe") == "Nasdaq 100":
            continue
        try:
            closes = list(map(lambda candle: candle["close"], price_data[ticker]["candles"]))
            closes_ref = list(map(lambda candle: candle["close"], ref["candles"]))

            # Use cached ticker_info for industry/sector when not available directly
            industry = (
                TICKER_INFO_DICT[ticker]["info"]["industry"]
                if price_data[ticker].get("industry") == "unknown"
                else price_data[ticker].get("industry", "unknown")
            )
            sector = (
                TICKER_INFO_DICT[ticker]["info"]["sector"]
                if price_data[ticker].get("sector") == "unknown"
                else price_data[ticker].get("sector", "unknown")
            )

            if len(closes) >= 6 * 20:
                closes_series = pd.Series(closes)
                closes_ref_series = pd.Series(closes_ref)
                rs = relative_strength(closes_series, closes_ref_series)
                month = 20
                tmp_percentile = 100
                rs1m = relative_strength(closes_series.head(-1 * month), closes_ref_series.head(-1 * month))
                rs3m = relative_strength(closes_series.head(-3 * month), closes_ref_series.head(-3 * month))
                rs6m = relative_strength(closes_series.head(-6 * month), closes_ref_series.head(-6 * month))

                # Guard against obviously corrupt price data
                if rs < 590:
                    ranks.append(len(ranks) + 1)
                    relative_strengths.append((
                        0, ticker, sector, industry,
                        price_data[ticker].get("universe", ""),
                        rs, tmp_percentile, rs1m, rs3m, rs6m
                    ))
                    stock_rs[ticker] = rs

                    # Aggregate by industry
                    if industry not in industries:
                        industries[industry] = {
                            "info": (0, industry, sector, 0, 99, 1, 3, 6),
                            TITLE_RS: [],
                            TITLE_1M: [],
                            TITLE_3M: [],
                            TITLE_6M: [],
                            TITLE_TICKERS: []
                        }
                        ind_ranks.append(len(ind_ranks) + 1)
                    industries[industry][TITLE_RS].append(rs)
                    industries[industry][TITLE_1M].append(rs1m)
                    industries[industry][TITLE_3M].append(rs3m)
                    industries[industry][TITLE_6M].append(rs6m)
                    industries[industry][TITLE_TICKERS].append(ticker)

        except KeyError:
            print(f'Ticker {ticker} has corrupted data.')

    dfs = []

    # ── Stocks DataFrame ──────────────────────────────────────────────────────
    df = pd.DataFrame(
        relative_strengths,
        columns=[TITLE_RANK, TITLE_TICKER, TITLE_SECTOR, TITLE_INDUSTRY, TITLE_UNIVERSE,
                 TITLE_RS, TITLE_PERCENTILE, TITLE_1M, TITLE_3M, TITLE_6M]
    )

    # pandas 2.x: pd.qcut is more strict — use retbins=False, duplicates="drop"
    df[TITLE_PERCENTILE] = pd.qcut(df[TITLE_RS], 100, labels=False, duplicates="drop")
    df[TITLE_1M]         = pd.qcut(df[TITLE_1M], 100, labels=False, duplicates="drop")
    df[TITLE_3M]         = pd.qcut(df[TITLE_3M], 100, labels=False, duplicates="drop")
    df[TITLE_6M]         = pd.qcut(df[TITLE_6M], 100, labels=False, duplicates="drop")

    df = df.sort_values([TITLE_RS], ascending=False)
    df[TITLE_RANK] = list(range(1, len(df) + 1))

    # Filter by MIN_PERCENTILE
    out_tickers_count = int((df[TITLE_PERCENTILE] >= MIN_PERCENTILE).sum())
    df = df.head(out_tickers_count)

    # ── TradingView RSRATING.csv ──────────────────────────────────────────────
    percentile_values = [98, 89, 69, 49, 29, 9, 1]
    first_rs_values = {}

    for percentile in percentile_values:
        matching = df[df[TITLE_PERCENTILE] == percentile]
        if matching.empty:
            # Fallback: find nearest available percentile value
            available = df[TITLE_PERCENTILE].dropna().unique()
            if len(available) == 0:
                continue
            nearest = min(available, key=lambda x: abs(x - percentile))
            matching = df[df[TITLE_PERCENTILE] == nearest]
        if not matching.empty:
            first_rs_values[percentile] = matching.iloc[0][TITLE_RS]

    # Only generate if we have all values
    if len(first_rs_values) == len(percentile_values):
        tradingview_csv_content = generate_tradingview_csv(percentile_values, first_rs_values)
        with open(os.path.join(DIR, "output", "RSRATING.csv"), "w") as csv_file:
            csv_file.write(tradingview_csv_content)
        print("✓ RSRATING.csv generated for TradingView.")
    else:
        print("⚠ Could not generate RSRATING.csv — not enough percentile data points.")

    df.to_csv(os.path.join(DIR, "output", 'rs_stocks.csv'), index=False)
    dfs.append(df)

    # ── Industries DataFrame ──────────────────────────────────────────────────
    def getDfView(entry):
        return entry["info"]

    def rs_sum(a, b):
        return a + b

    def getRsAverage(ind_dict, industry, column):
        rs = reduce(rs_sum, ind_dict[industry][column]) / len(ind_dict[industry][column])
        return int(rs * 100) / 100

    def rs_for_stock(ticker):
        return stock_rs.get(ticker, 0)

    def getTickers(ind_dict, industry):
        return ",".join(sorted(ind_dict[industry][TITLE_TICKERS], key=rs_for_stock, reverse=True))

    filtered_industries = list(filter(lambda i: len(i[TITLE_TICKERS]) > 1, list(industries.values())))
    df_industries = pd.DataFrame(
        map(getDfView, filtered_industries),
        columns=[TITLE_RANK, TITLE_INDUSTRY, TITLE_SECTOR, TITLE_RS, TITLE_PERCENTILE,
                 TITLE_1M, TITLE_3M, TITLE_6M]
    )

    df_industries[TITLE_RS]  = df_industries.apply(lambda row: getRsAverage(industries, row[TITLE_INDUSTRY], TITLE_RS), axis=1)
    df_industries[TITLE_1M]  = df_industries.apply(lambda row: getRsAverage(industries, row[TITLE_INDUSTRY], TITLE_1M), axis=1)
    df_industries[TITLE_3M]  = df_industries.apply(lambda row: getRsAverage(industries, row[TITLE_INDUSTRY], TITLE_3M), axis=1)
    df_industries[TITLE_6M]  = df_industries.apply(lambda row: getRsAverage(industries, row[TITLE_INDUSTRY], TITLE_6M), axis=1)

    df_industries[TITLE_PERCENTILE] = pd.qcut(df_industries[TITLE_RS], 100, labels=False, duplicates="drop")
    df_industries[TITLE_1M]         = pd.qcut(df_industries[TITLE_1M], 100, labels=False, duplicates="drop")
    df_industries[TITLE_3M]         = pd.qcut(df_industries[TITLE_3M], 100, labels=False, duplicates="drop")
    df_industries[TITLE_6M]         = pd.qcut(df_industries[TITLE_6M], 100, labels=False, duplicates="drop")

    df_industries[TITLE_TICKERS] = df_industries.apply(
        lambda row: getTickers(industries, row[TITLE_INDUSTRY]), axis=1
    )
    df_industries = df_industries.sort_values([TITLE_RS], ascending=False)
    df_industries[TITLE_RANK] = list(range(1, len(df_industries) + 1))

    df_industries.to_csv(os.path.join(DIR, "output", 'rs_industries.csv'), index=False)
    dfs.append(df_industries)

    return dfs


def main(skipEnter=False):
    ranks = rankings()
    print(ranks[0])
    print("***\nYour 'rs_stocks.csv' is in the output folder.\n***")
    if not skipEnter and cfg("EXIT_WAIT_FOR_ENTER"):
        input("Press Enter key to exit...")

if __name__ == "__main__":
    main()
