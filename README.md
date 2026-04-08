# Moving Average Crossover Backtest Study

**A beginner quant research project — by Hiroki Kunu**

---

## What This Project Is

A systematic backtest of Moving Average (MA) crossover trading strategies across 6 assets over 10 years, built entirely in Python. This is Part 1 of an ongoing strategy library being built toward an automated asset screener.

The goal was not just to find a profitable strategy, but to understand *how to properly test whether a strategy is real or just lucky.*

---

## Assets Tested

| Asset | Market | Type |
|-------|--------|------|
| AAPL | US | Large-cap tech |
| SPY | US | S&P 500 index ETF |
| TSLA | US | High-volatility growth |
| WM | US | Defensive / utility-like |
| BTC-USD | Crypto | Bitcoin |
| ETH-USD | Crypto | Ethereum |

---

## How MA Crossover Works

Two moving averages are calculated — a fast MA (short window) and a slow MA (long window). When the fast MA crosses above the slow MA, the trend is turning up — buy. When it crosses below — exit. It's a trend-following strategy that rides momentum rather than fighting it.

**MA pairs tested:** 5/20, 10/30, 15/40, 20/50, 25/60, 30/70, 50/200, 100/200

---

## Validation Method

To check whether results are real or just lucky:

1. **Parameter robustness** — tested multiple MA pairs per asset to check if results are consistent across parameters, not dependent on one lucky setting
2. **Out-of-sample validation** — trained on 2016–2020 data only, then tested on unseen 2021–2026 data

---

## Key Findings

**ETH was the standout.**
The MA strategy didn't just reduce risk — it massively outperformed Buy & Hold in total return (5,424% vs 564%). The strategy successfully dodged the 80%+ crypto crashes while staying in during the big bull runs.

**BTC showed strong risk-adjusted performance (Sharpe > 1.0) across multiple MA pairs** — a sign of robustness, not just one lucky parameter.

**For stable stocks like AAPL and SPY, Buy & Hold was actually better.**
The MA strategy kept stepping out of the market during short corrections and missing the rebounds. Trend-following works best on volatile, momentum-driven assets.

**The out-of-sample test was the reality check.**
When trained on 2016–2020 and tested on 2021–2026, Sharpe ratios dropped 80–95% for crypto. The 2021–2026 period was choppy and mean-reverting — exactly the worst environment for MA crossover strategies.

**TSLA was the surprise.**
The most suspicious asset going in — only one MA pair seemed to work — but it was the only one to beat Buy & Hold out-of-sample. Goes to show: out-of-sample results can surprise you in both directions.

---

## The Core Lesson

A strategy that looks perfect on historical data often breaks down on new data. That gap — between in-sample and out-of-sample — is where real quant research lives. The goal isn't to find a strategy that worked in the past. It's to find one robust enough to survive conditions it hasn't seen yet.

---

## Part of a Larger Project

This is Strategy 1 of 5 in a strategy library being built toward an automated screener:

- ✅ Strategy 1 — Moving Average Crossover (this repo)
- ✅ Strategy 2 — RSI
- ⬜ Strategy 3 — Bollinger Bands
- ⬜ Strategy 4 — MACD
- ⬜ Strategy 5 — Mean Reversion
- ⬜ Phase 2 — Automated Screener

---

## How to Run

```bash
pip install yfinance numpy pandas matplotlib
```

Open `Goofy MA for 6 assets.ipynb` in Jupyter Notebook or Anaconda and run cells top to bottom.

- **Cell 4** — Full backtest: all 6 assets × all MA parameter combinations
- **Cell 5** — All MA pairs overlaid per stock
- **Cell 6** — In-sample vs out-of-sample validation (2016–2020 train, 2021–2026 test)

---

## Author

**Hiroki Kunu**
UQ Brisbane | Quantitative Research
[LinkedIn](https://www.linkedin.com/in/hiroki-kunu-ba4218401) | [GitHub](https://github.com/GoofyisDAWG)
