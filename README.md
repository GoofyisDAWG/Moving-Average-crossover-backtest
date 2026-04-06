# Moving Average Crossover Backtest Study
### A beginner quant research project — by [Your Name]

---

## What This Project Is

A systematic backtest of Moving Average (MA) crossover trading strategies across 6 assets over 10 years, built entirely in Python. The goal was to learn quantitative research methodology from scratch — not just to build a profitable strategy, but to understand *how to properly test* whether a strategy is real or just lucky.

This project covers:
- Multi-asset backtesting (stocks, ETFs, and crypto)
- Multi-parameter sensitivity analysis
- Proper out-of-sample (train/test split) validation
- Performance metrics: Sharpe ratio, Max Drawdown, Win Rate, Annualised Return

---

## Assets Tested

| Ticker | Type |
|--------|------|
| AAPL | US Stock |
| SPY | S&P 500 ETF |
| TSLA | US Stock (high volatility) |
| WM | US Stock (defensive) |
| BTC-USD | Cryptocurrency |
| ETH-USD | Cryptocurrency |

**Data period:** January 2016 – April 2026 (10 years)
**Data source:** Yahoo Finance via `yfinance`

---

## MA Pairs Tested

`(5,20)` `(10,30)` `(15,40)` `(20,50)` `(25,60)` `(30,70)` `(50,200)` `(100,200)`

The fast MA crossing above the slow MA = Buy signal. Crossing below = Exit to cash.

---

## Key Findings

**1. Crypto responded best to MA strategies**
ETH and BTC showed consistent outperformance over Buy & Hold in risk-adjusted terms (Sharpe > 1.0 in-sample). The strategy effectively avoided the major 80%+ crypto crashes while staying invested during bull runs.

**2. Stable stocks favoured Buy & Hold**
AAPL, SPY, and WM were better left as Buy & Hold. Their corrections are short and sharp — the MA strategy exits near the bottom and misses the recovery, consistently underperforming.

**3. Sensitivity analysis confirmed BTC robustness**
BTC's Sharpe ratio stayed consistently high (0.73–1.08) across all MA pairs, a sign the strategy works broadly on BTC and is not tuned to one specific parameter.

**4. Out-of-sample testing revealed the reality**
Training on 2016–2020 and testing on 2021–2026:
- BTC Sharpe: 2.03 → 0.11 (−94.6%)
- ETH Sharpe: 1.38 → 0.26 (−81.2%)
- TSLA Sharpe: 1.33 → 0.44 (−66.9%) — only asset to beat Buy & Hold out-of-sample

The 2021–2026 period was choppy and mean-reverting, the worst possible environment for trend-following. This degradation is expected and is exactly why out-of-sample testing matters.

**5. The main lesson**
A simple MA crossover strategy that looks excellent in a 10-year bull market will degrade significantly when market conditions change. The gap between in-sample and out-of-sample performance is where real quantitative research begins.

---

## Files

| File | Description |
|------|-------------|
| `ma_multi_backtest.py` | Full multi-asset, multi-MA-pair backtest with heatmap and equity curves |
| `out_of_sample_test.py` | Train/test split validation — 2016–2020 training, 2021–2026 testing |

---

## How to Run

**Requirements:**
```
pip install yfinance pandas numpy matplotlib
```

**Run the main backtest:**
```
python ma_multi_backtest.py
```

**Run the out-of-sample test:**
```
python out_of_sample_test.py
```

Both scripts download data automatically from Yahoo Finance. No API key required.

---

## Output

Running the scripts produces:
- Full comparison tables printed to console
- Sharpe ratio heatmap (MA pair vs Ticker)
- Equity curves (strategy vs Buy & Hold)
- In-sample vs out-of-sample Sharpe bar chart
- PNG files saved to working directory

---

## What's Next

- [ ] Add transaction cost modelling
- [ ] Walk-forward analysis (rolling train/test windows)
- [ ] Test additional strategies (RSI, Bollinger Bands, momentum)
- [ ] Explore position sizing and risk management

---

## Disclaimer

This project is for educational purposes only. Nothing here is financial advice. Past performance does not indicate future results.

---

*Built as part of a self-directed quant trading learning journey during final year of university.*
