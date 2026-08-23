# AI Market Decision System — Nifty 200 V2

A professional-style prototype for a top-down Indian swing/positional workflow:

**Global → Indian Market Regime → Top 3 Sectors → Nifty 200 Leaders → Setup Score → Entry/SL/Targets → Position Size → Validation**

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## V2 additions
- Nifty-200-focused stock universe seed
- Top-3 sector ranking
- EMA20/50/200 trend
- RSI and MACD
- 20-day pivot proximity
- Volume / 20-day average
- Relative strength vs Nifty 200
- ATR + structure-based stop logic
- Capital/risk-based quantity
- Swing and positional views
- Trade Builder
- Validation Lab

## Important
The stock list is a prototype seed and must be replaced with the latest official NSE Nifty 200 constituent file for production. Market data from yfinance is suitable for a prototype/research workflow, not a guarantee of real-time execution quality.

The displayed Confidence % is a heuristic model score, NOT a statistically validated probability of profit. Build an event-driven backtest, include costs/slippage/gaps, use walk-forward validation, and calibrate probabilities before real-money use.

This is an independent educational implementation inspired by publicly described top-down trading concepts. It is not affiliated with or endorsed by Vishal B. Malkan and does not reproduce proprietary course/software content.
