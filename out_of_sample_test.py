import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt

# ── Configuration ──────────────────────────────────────────────────────────────
FULL_START   = dt.datetime(2016, 1, 1)
SPLIT_DATE   = dt.datetime(2021, 1, 1)   # train = before this, test = after this
FULL_END     = dt.datetime.now()

stocks   = ["BTC-USD", "ETH-USD", "TSLA"]
ma_pairs = [(5, 20), (10, 30), (15, 40), (20, 50), (25, 60), (30, 70)]

PERIODS_PER_YEAR = 252


# ── Helpers ────────────────────────────────────────────────────────────────────
def run_backtest(price_series, fast, slow):
    df = pd.DataFrame({'price': price_series})
    df[f'MA{fast}'] = df['price'].rolling(window=fast).mean()
    df[f'MA{slow}'] = df['price'].rolling(window=slow).mean()
    df['signal']   = (df[f'MA{fast}'] > df[f'MA{slow}']).astype(int)
    df['position'] = df['signal'].shift(1)
    df['log_returns']          = np.log(df['price'] / df['price'].shift(1))
    df['strategy_log_returns'] = df['position'] * df['log_returns']
    df['cum_market']   = np.exp(df['log_returns'].cumsum())
    df['cum_strategy'] = np.exp(df['strategy_log_returns'].cumsum())
    return df

def max_drawdown(cum_series):
    running_max = cum_series.cummax()
    return ((cum_series - running_max) / running_max).min()

def get_metrics(df):
    market_lr   = df['log_returns'].dropna()
    strategy_lr = df['strategy_log_returns'].dropna()
    total_mkt    = df['cum_market'].dropna().iloc[-1]   - 1
    total_strat  = df['cum_strategy'].dropna().iloc[-1] - 1
    ann_mkt      = np.exp(market_lr.mean()   * PERIODS_PER_YEAR) - 1
    ann_strat    = np.exp(strategy_lr.mean() * PERIODS_PER_YEAR) - 1
    vol_mkt      = market_lr.std()   * np.sqrt(PERIODS_PER_YEAR)
    vol_strat    = strategy_lr.std() * np.sqrt(PERIODS_PER_YEAR)
    sharpe_mkt   = ann_mkt   / vol_mkt   if vol_mkt   != 0 else np.nan
    sharpe_strat = ann_strat / vol_strat if vol_strat != 0 else np.nan
    mdd_strat    = max_drawdown(df['cum_strategy'].dropna())
    return {
        'B&H Total Return %':    round(total_mkt   * 100, 2),
        'Strat Total Return %':  round(total_strat * 100, 2),
        'Strat Annual Return %': round(ann_strat   * 100, 2),
        'B&H Sharpe':            round(sharpe_mkt,   2),
        'Strat Sharpe':          round(sharpe_strat, 2),
        'Strat Max DD %':        round(mdd_strat   * 100, 2),
    }


# ── Step 1: Download full price data ──────────────────────────────────────────
print("Downloading data...\n")
price_data = {}
for stock in stocks:
    raw = yf.download(stock, start=FULL_START, end=FULL_END,
                      auto_adjust=True, progress=False)
    price_data[stock] = raw['Close'].squeeze()
    print(f"  {stock}: {len(raw)} rows")


# ── Step 2: Split into in-sample and out-of-sample ────────────────────────────
in_sample  = {s: price_data[s][price_data[s].index < SPLIT_DATE]  for s in stocks}
out_sample = {s: price_data[s][price_data[s].index >= SPLIT_DATE] for s in stocks}

print(f"\n  In-sample  period: {FULL_START.date()} → {SPLIT_DATE.date()}")
print(f"  Out-of-sample period: {SPLIT_DATE.date()} → {FULL_END.date()}\n")


# ── Step 3: Find best MA pair per stock using IN-SAMPLE data ONLY ─────────────
print("=" * 70)
print("  STEP 1 — TRAINING (In-Sample: 2016–2020)")
print("  Finding best MA pair per stock on training data only...")
print("=" * 70)

best_pairs = {}   # stores chosen MA pair for each stock
in_sample_results = []

for stock in stocks:
    best_sharpe = -999
    best_pair   = None
    for fast, slow in ma_pairs:
        df      = run_backtest(in_sample[stock], fast, slow)
        metrics = get_metrics(df)
        metrics['Ticker']  = stock
        metrics['MA Pair'] = f"MA{fast}/{slow}"
        in_sample_results.append(metrics)
        if metrics['Strat Sharpe'] > best_sharpe:
            best_sharpe = metrics['Strat Sharpe']
            best_pair   = (fast, slow)
    best_pairs[stock] = best_pair
    print(f"  {stock}: best in-sample pair = MA{best_pair[0]}/{best_pair[1]} "
          f"(Sharpe: {best_sharpe:.2f})")

in_sample_df = pd.DataFrame(in_sample_results).set_index(['Ticker', 'MA Pair'])
print("\nFull in-sample results:")
print(in_sample_df.to_string())


# ── Step 4: Apply chosen pairs to OUT-OF-SAMPLE data ─────────────────────────
print("\n" + "=" * 70)
print("  STEP 2 — TESTING (Out-of-Sample: 2021–2026)")
print("  Applying the pairs chosen from training data to unseen data...")
print("=" * 70)

oos_results = []
oos_data    = {}   # store dataframes for plotting

for stock in stocks:
    fast, slow = best_pairs[stock]
    df         = run_backtest(out_sample[stock], fast, slow)
    metrics    = get_metrics(df)
    metrics['Ticker']  = stock
    metrics['MA Pair'] = f"MA{fast}/{slow}"
    oos_results.append(metrics)
    oos_data[stock] = df
    print(f"\n  {stock} — MA{fast}/{slow} on out-of-sample data:")
    for k, v in metrics.items():
        if k not in ['Ticker', 'MA Pair']:
            print(f"    {k}: {v}")

oos_df = pd.DataFrame(oos_results).set_index('Ticker')


# ── Step 5: Side-by-side comparison table ────────────────────────────────────
print("\n" + "=" * 70)
print("  IN-SAMPLE vs OUT-OF-SAMPLE COMPARISON")
print("=" * 70)

rows = []
for stock in stocks:
    fast, slow  = best_pairs[stock]
    pair_label  = f"MA{fast}/{slow}"
    in_s  = in_sample_df.loc[(stock, pair_label)]
    out_s = oos_df.loc[stock]
    rows.append({
        'Ticker':              stock,
        'Best Pair':           pair_label,
        'IN Strat Return %':   in_s['Strat Total Return %'],
        'OUT Strat Return %':  out_s['Strat Total Return %'],
        'IN B&H Return %':     in_s['B&H Total Return %'],
        'OUT B&H Return %':    out_s['B&H Total Return %'],
        'IN Sharpe':           in_s['Strat Sharpe'],
        'OUT Sharpe':          out_s['Strat Sharpe'],
        'IN Max DD %':         in_s['Strat Max DD %'],
        'OUT Max DD %':        out_s['Strat Max DD %'],
    })

comparison = pd.DataFrame(rows).set_index('Ticker')
print(comparison.to_string())

# Key verdict
print("\n  VERDICT:")
for stock in stocks:
    in_sharpe  = comparison.loc[stock, 'IN Sharpe']
    out_sharpe = comparison.loc[stock, 'OUT Sharpe']
    drop       = ((out_sharpe - in_sharpe) / in_sharpe) * 100
    in_ret     = comparison.loc[stock, 'IN Strat Return %']
    out_ret    = comparison.loc[stock, 'OUT Strat Return %']
    beats_bah  = out_ret > comparison.loc[stock, 'OUT B&H Return %']
    print(f"  {stock}: Sharpe changed {in_sharpe:.2f} → {out_sharpe:.2f} "
          f"({drop:+.1f}%)  |  Beats B&H out-of-sample: {beats_bah}")


# ── Step 6: Out-of-sample equity curves ───────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for i, stock in enumerate(stocks):
    ax         = axes[i]
    fast, slow = best_pairs[stock]
    df         = oos_data[stock]

    df[['cum_market', 'cum_strategy']].plot(ax=ax)
    ax.set_title(f"{stock} — MA{fast}/{slow}\nOut-of-Sample (2021–2026)", fontsize=12)
    ax.legend(['Buy & Hold', f"MA{fast}/{slow} Strategy"])
    ax.set_xlabel('')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=1, color='gray', linestyle=':', linewidth=1)  # break-even line

plt.suptitle("Out-of-Sample Equity Curves (Strategy chosen from 2016–2020 training data)",
             fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig('out_of_sample_equity_curves.png', dpi=150, bbox_inches='tight')
plt.show()
print("\nChart saved as 'out_of_sample_equity_curves.png'")


# ── Step 7: In-sample vs Out-of-sample Sharpe bar chart ──────────────────────
fig2, ax2 = plt.subplots(figsize=(10, 5))

x      = np.arange(len(stocks))
width  = 0.35
in_sh  = [comparison.loc[s, 'IN Sharpe']  for s in stocks]
out_sh = [comparison.loc[s, 'OUT Sharpe'] for s in stocks]

bars1 = ax2.bar(x - width/2, in_sh,  width, label='In-Sample (2016–2020)',  color='steelblue')
bars2 = ax2.bar(x + width/2, out_sh, width, label='Out-of-Sample (2021–2026)', color='darkorange')

ax2.set_xticks(x)
ax2.set_xticklabels([f"{s}\n({comparison.loc[s,'Best Pair']})" for s in stocks])
ax2.set_ylabel('Strategy Sharpe Ratio')
ax2.set_title('Sharpe Ratio: In-Sample vs Out-of-Sample', fontsize=13)
ax2.legend()
ax2.axhline(y=0, color='black', linewidth=0.8)
ax2.grid(True, alpha=0.3, axis='y')

# label bars
for bar in bars1 + bars2:
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
             f"{bar.get_height():.2f}", ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('sharpe_in_vs_out.png', dpi=150, bbox_inches='tight')
plt.show()
print("Chart saved as 'sharpe_in_vs_out.png'")
