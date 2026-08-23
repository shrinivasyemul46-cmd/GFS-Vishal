
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="AI Market Decision System — Nifty 200 V2", page_icon="🧠", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#080d18}
.block-container{max-width:1500px;padding-top:1rem}
.card{background:#111a2b;border:1px solid #293752;border-radius:16px;padding:15px}
</style>
""",unsafe_allow_html=True)

# ---------------- Universe ----------------
# Representative liquid Nifty-200 seed universe for the prototype.
# Production: replace this dictionary with the latest official NSE Nifty 200 constituent CSV.
STOCKS={
"ABB.NS":"ABB India","ADANIENT.NS":"Adani Enterprises","ADANIPORTS.NS":"Adani Ports",
"APOLLOHOSP.NS":"Apollo Hospitals","ASIANPAINT.NS":"Asian Paints","AXISBANK.NS":"Axis Bank",
"BAJAJ-AUTO.NS":"Bajaj Auto","BAJFINANCE.NS":"Bajaj Finance","BAJAJFINSV.NS":"Bajaj Finserv",
"BEL.NS":"Bharat Electronics","BHARTIARTL.NS":"Bharti Airtel","BPCL.NS":"BPCL",
"BRITANNIA.NS":"Britannia","CIPLA.NS":"Cipla","COFORGE.NS":"Coforge","COLPAL.NS":"Colgate-Palmolive",
"DIVISLAB.NS":"Divi's Laboratories","DLF.NS":"DLF","DMART.NS":"Avenue Supermarts",
"DRREDDY.NS":"Dr Reddy's","EICHERMOT.NS":"Eicher Motors","ETERNAL.NS":"Eternal",
"FEDERALBNK.NS":"Federal Bank","GRASIM.NS":"Grasim","HCLTECH.NS":"HCLTech","HDFCBANK.NS":"HDFC Bank",
"HDFCLIFE.NS":"HDFC Life","HEROMOTOCO.NS":"Hero MotoCorp","HINDALCO.NS":"Hindalco",
"HINDPETRO.NS":"Hindustan Petroleum","HINDUNILVR.NS":"Hindustan Unilever","ICICIBANK.NS":"ICICI Bank",
"ICICIGI.NS":"ICICI Lombard","ICICIPRULI.NS":"ICICI Prudential Life","INDHOTEL.NS":"Indian Hotels",
"INDIGO.NS":"InterGlobe Aviation","INDUSINDBK.NS":"IndusInd Bank","INFY.NS":"Infosys",
"IOC.NS":"Indian Oil","IRCTC.NS":"IRCTC","ITC.NS":"ITC","JINDALSTEL.NS":"Jindal Steel",
"JSWSTEEL.NS":"JSW Steel","KOTAKBANK.NS":"Kotak Mahindra Bank","LT.NS":"Larsen & Toubro",
"LTIM.NS":"LTIMindtree","M&M.NS":"Mahindra & Mahindra","MARUTI.NS":"Maruti Suzuki",
"MAXHEALTH.NS":"Max Healthcare","MCX.NS":"MCX","MOTHERSON.NS":"Samvardhana Motherson",
"MPHASIS.NS":"Mphasis","MUTHOOTFIN.NS":"Muthoot Finance","NAUKRI.NS":"Info Edge",
"NMDC.NS":"NMDC","NTPC.NS":"NTPC","ONGC.NS":"ONGC","PAGEIND.NS":"Page Industries",
"PEL.NS":"Piramal Enterprises","PERSISTENT.NS":"Persistent Systems","PFC.NS":"Power Finance Corp",
"PIDILITIND.NS":"Pidilite Industries","PIIND.NS":"PI Industries","POLYCAB.NS":"Polycab India",
"POWERGRID.NS":"Power Grid","PVRINOX.NS":"PVR INOX","RECLTD.NS":"REC","RELIANCE.NS":"Reliance Industries",
"SBILIFE.NS":"SBI Life","SBIN.NS":"State Bank of India","SHREECEM.NS":"Shree Cement",
"SIEMENS.NS":"Siemens","SOLARINDS.NS":"Solar Industries","SRF.NS":"SRF","SUNPHARMA.NS":"Sun Pharma",
"SUPREMEIND.NS":"Supreme Industries","TATACONSUM.NS":"Tata Consumer","TATAMOTORS.NS":"Tata Motors",
"TATASTEEL.NS":"Tata Steel","TCS.NS":"TCS","TECHM.NS":"Tech Mahindra","TITAN.NS":"Titan",
"TORNTPHARM.NS":"Torrent Pharma","TRENT.NS":"Trent","TVSMOTOR.NS":"TVS Motor","ULTRACEMCO.NS":"UltraTech Cement",
"UNOMINDA.NS":"Uno Minda","UPL.NS":"UPL","VEDL.NS":"Vedanta","VOLTAS.NS":"Voltas",
"WIPRO.NS":"Wipro","YESBANK.NS":"Yes Bank","ZYDUSLIFE.NS":"Zydus Lifesciences",
"HAL.NS":"HAL","DIXON.NS":"Dixon Technologies","BHEL.NS":"BHEL","BANKBARODA.NS":"Bank of Baroda",
"CANBK.NS":"Canara Bank","PNB.NS":"Punjab National Bank","IDFCFIRSTB.NS":"IDFC First Bank",
"INDUSTOWER.NS":"Indus Towers","LUPIN.NS":"Lupin","MANKIND.NS":"Mankind Pharma",
"AUROPHARMA.NS":"Aurobindo Pharma","BIOCON.NS":"Biocon","ASHOKLEY.NS":"Ashok Leyland",
"BHARATFORG.NS":"Bharat Forge","BOSCHLTD.NS":"Bosch","EXIDEIND.NS":"Exide Industries",
"KPITTECH.NS":"KPIT Technologies","TATAELXSI.NS":"Tata Elxsi","ZYDUSLIFE.NS":"Zydus Lifesciences"
}

SECTORS={
"Auto":"^CNXAUTO","Bank":"^NSEBANK","Financial Services":"^CNXFIN","FMCG":"^CNXFMCG",
"IT":"^CNXIT","Metal":"^CNXMETAL","Pharma":"^CNXPHARMA","Realty":"^CNXREALTY",
"PSU Bank":"^CNXPSUBANK","Private Bank":"^NIFTYPVTBANK","Energy":"^CNXENERGY",
"Media":"^CNXMEDIA","Consumer":"^CNXCONSUMER"
}
INDICES={"NIFTY 50":"^NSEI","BANK NIFTY":"^NSEBANK","NIFTY MIDCAP 100":"NIFTY_MIDCAP_100.NS","INDIA VIX":"^INDIAVIX"}

@st.cache_data(ttl=900,show_spinner=False)
def hist(symbols,period="2y"):
    return yf.download(list(symbols),period=period,interval="1d",auto_adjust=False,progress=False,threads=True,group_by="ticker")

def ser(raw,sym,field="Close"):
    try:return raw[sym][field].dropna()
    except:
        try:return raw[field][sym].dropna()
        except:return pd.Series(dtype=float)

def metrics(s):
    if len(s)<80:return None
    ema20=s.ewm(span=20,adjust=False).mean(); ema50=s.ewm(span=50,adjust=False).mean()
    ema200=s.ewm(span=200,adjust=False).mean() if len(s)>=200 else s.rolling(100).mean()
    d=s.diff(); g=d.clip(lower=0).rolling(14).mean(); l=(-d.clip(upper=0)).rolling(14).mean()
    rsi=100-100/(1+g/l.replace(0,np.nan))
    macd=s.ewm(span=12,adjust=False).mean()-s.ewm(span=26,adjust=False).mean()
    signal=macd.ewm(span=9,adjust=False).mean()
    return {
        "price":float(s.iloc[-1]),"ema20":float(ema20.iloc[-1]),"ema50":float(ema50.iloc[-1]),"ema200":float(ema200.iloc[-1]),
        "rsi":float(rsi.iloc[-1]),"macd":float(macd.iloc[-1]),"signal":float(signal.iloc[-1]),
        "r20":float(s.pct_change(20).iloc[-1]*100),"r60":float(s.pct_change(60).iloc[-1]*100),
        "high20":float(s.rolling(20).max().iloc[-1]),"low20":float(s.rolling(20).min().iloc[-1]),
        "high52":float(s.rolling(252).max().iloc[-1]),"low52":float(s.rolling(252).min().iloc[-1])
    }

def volume_metrics(raw,sym):
    try:
        v=raw[sym]["Volume"].dropna()
    except:
        try:v=raw["Volume"][sym].dropna()
        except:return np.nan,np.nan
    if len(v)<21:return np.nan,np.nan
    avg=float(v.rolling(20).mean().iloc[-1])
    return float(v.iloc[-1]), (float(v.iloc[-1])/avg if avg else np.nan)

def atr(raw,sym,n=14):
    try:
        h=raw[sym]["High"].dropna(); l=raw[sym]["Low"].dropna(); c=raw[sym]["Close"].dropna()
    except:
        try:h=raw["High"][sym].dropna(); l=raw["Low"][sym].dropna(); c=raw["Close"][sym].dropna()
        except:return np.nan
    tr=pd.concat([h-l,(h-c.shift()).abs(),(l-c.shift()).abs()],axis=1).max(axis=1)
    return float(tr.rolling(n).mean().iloc[-1])

def rel_strength(stock,bench):
    if len(stock)<60 or len(bench)<60:return np.nan
    sr=float(stock.pct_change(60).iloc[-1]); br=float(bench.pct_change(60).iloc[-1])
    return (sr-br)*100

def setup_score(x,volratio,rs):
    p=0; why=[]
    if x["price"]>x["ema20"]>x["ema50"]>x["ema200"]:p+=25;why.append("EMA alignment")
    elif x["price"]>x["ema50"]>x["ema200"]:p+=17;why.append("Long trend")
    elif x["price"]>x["ema200"]:p+=8
    if 55<=x["rsi"]<=75:p+=12;why.append("RSI 55-75")
    elif 50<=x["rsi"]<55:p+=6
    if x["macd"]>x["signal"]:p+=8;why.append("MACD positive")
    if x["price"]>=x["high20"]*.985:p+=12;why.append("Near 20D pivot")
    if np.isfinite(volratio):
        if volratio>=2:p+=15;why.append("Volume >=2x")
        elif volratio>=1.5:p+=10;why.append("Volume >=1.5x")
    if np.isfinite(rs):
        if rs>=10:p+=13;why.append("Strong relative strength")
        elif rs>=5:p+=8
        elif rs<0:p-=5
    if x["r20"]>18:p-=8;why.append("Extended")
    return int(np.clip(p,0,100)),why

def stock_scan(capital,risk_pct):
    syms=list(STOCKS)
    raw=hist(tuple(syms),"2y")
    bench=ser(hist(("^NSEI",),"2y"),"^NSEI")
    rows=[]
    for sym in syms:
        s=ser(raw,sym); x=metrics(s)
        if not x:continue
        vr,vratio=volume_metrics(raw,sym); rs=rel_strength(s,bench)
        sc,why=setup_score(x,vratio,rs)
        a=atr(raw,sym); 
        # Risk model: ATR stop plus structure stop; choose wider of the two for realism.
        structure=x["low20"]*.99
        atrstop=x["price"]-1.5*a if np.isfinite(a) else x["price"]*.95
        sl=min(structure,atrstop)
        risk=max(x["price"]-sl,x["price"]*.02)
        t1=x["price"]+2*risk;t2=x["price"]+3*risk
        qty=max(0,int((capital*risk_pct/100)/risk))
        confidence=int(np.clip(40+0.55*sc,40,95))
        rows.append([
            sym.replace(".NS",""),STOCKS[sym],sc,confidence,round(x["price"],2),round(x["rsi"],1),
            round(x["r20"],2),round(x["r60"],2),round(rs,2) if np.isfinite(rs) else np.nan,
            round(vratio,2) if np.isfinite(vratio) else np.nan,round(x["ema20"],2),round(x["ema50"],2),
            round(x["ema200"],2),round(sl,2),round(t1,2),round(t2,2),qty,"; ".join(why[:4])
        ])
    return pd.DataFrame(rows,columns=["Symbol","Company","Score","Confidence %","Price","RSI","20D %","60D %",
                                       "RS vs Nifty 200","Vol / Avg20","EMA20","EMA50","EMA200","Stop","Target 1","Target 2","Qty","Evidence"])

def sector_scan():
    raw=hist(tuple(SECTORS.values()),"1y"); rows=[]
    for name,sym in SECTORS.items():
        x=metrics(ser(raw,sym))
        if not x:continue
        sc=0
        if x["price"]>x["ema20"]>x["ema50"]>x["ema200"]:sc+=50
        elif x["price"]>x["ema50"]>x["ema200"]:sc+=35
        elif x["price"]>x["ema200"]:sc+=20
        sc+=float(np.clip(x["r20"],-20,20))+float(np.clip(x["r60"]/2,-15,15))
        rows.append([name,round(sc,1),round(x["r20"],2),round(x["r60"],2),round(x["rsi"],1)])
    return pd.DataFrame(rows,columns=["Sector","Strength","20D %","60D %","RSI"]).sort_values("Strength",ascending=False)

# ---------------- Sidebar ----------------
st.sidebar.title("🧠 NIFTY 200 V2")
page=st.sidebar.radio("Modules",[
"🏠 Command Center","🌍 Global Radar","🇮🇳 Market Regime","🔥 Top 3 Sectors",
"🚀 Nifty 200 Swing","💎 Positional","🎯 Trade Builder","📊 Validation Lab","📒 Journal","⚙️ Settings"
])
capital=st.sidebar.number_input("Capital ₹",1000,10000000,50000,5000)
risk_pct=st.sidebar.number_input("Risk / trade %",0.25,3.0,1.0,0.25)

# ---------------- Command Center ----------------
if page=="🏠 Command Center":
    st.title("🧠 AI Market Decision System — Nifty 200 V2")
    st.caption("Global → Market → Top 3 sectors → Nifty 200 leaders → Setup → Risk")
    try:
        raw=hist(tuple(INDICES.values()),"1y")
        n=metrics(ser(raw,"^NSEI")); b=metrics(ser(raw,"^NSEBANK")); v=ser(raw,"^INDIAVIX")
        regime=0
        if n and n["price"]>n["ema20"]>n["ema50"]>n["ema200"]:regime+=50
        elif n and n["price"]>n["ema50"]:regime+=28
        if b and b["price"]>b["ema50"]:regime+=20
        if n and n["rsi"]>55:regime+=15
        if len(v) and float(v.iloc[-1])<float(v.rolling(20).mean().iloc[-1]):regime+=15
        regime=int(np.clip(regime,0,100))
        a,bx,c,d=st.columns(4)
        a.metric("Market Score",f"{regime}/100")
        bx.metric("NIFTY RSI",f"{n['rsi']:.1f}" if n else "N/A")
        c.metric("BANK NIFTY RSI",f"{b['rsi']:.1f}" if b else "N/A")
        d.metric("VIX",f"{float(v.iloc[-1]):.2f}" if len(v) else "N/A")
    except: st.warning("Market data unavailable. Check data connection.")
    st.subheader("🔥 Top 3 sectors")
    try:st.dataframe(sector_scan().head(3),use_container_width=True,hide_index=True)
    except:st.info("Sector data unavailable.")
    st.subheader("🚀 Top Nifty 200 candidates")
    try:st.dataframe(stock_scan(capital,risk_pct).head(10),use_container_width=True,hide_index=True)
    except:st.info("Stock data unavailable.")
    st.warning("This is a research/decision-support prototype. Confidence % is not a guaranteed probability of profit.")

elif page=="🌍 Global Radar":
    st.title("🌍 Global & Asian Radar")
    g={"S&P 500":"^GSPC","Nasdaq":"^IXIC","Dow":"^DJI","Nikkei":"^N225","Hang Seng":"^HSI","Shanghai":"000001.SS","KOSPI":"^KS11","Taiwan":"^TWII","DAX":"^GDAXI","FTSE":"^FTSE"}
    raw=hist(tuple(g.values()),"6mo"); rows=[]
    for n,sym in g.items():
        x=metrics(ser(raw,sym))
        if x:rows.append([n,round(x["price"],2),round(x["r20"],2),round(x["r60"],2),round(x["rsi"],1)])
    st.dataframe(pd.DataFrame(rows,columns=["Index","Last","20D %","60D %","RSI"]),use_container_width=True,hide_index=True)

elif page=="🇮🇳 Market Regime":
    st.title("🇮🇳 Indian Market Regime")
    raw=hist(tuple(INDICES.values()),"1y"); rows=[]
    for n,sym in INDICES.items():
        x=metrics(ser(raw,sym))
        if x:
            regime="🟢 Strong Bullish" if x["price"]>x["ema20"]>x["ema50"]>x["ema200"] else ("🟡 Mixed" if x["price"]>x["ema200"] else "🔴 Weak")
            rows.append([n,regime,round(x["price"],2),round(x["rsi"],1),round(x["r20"],2),round(x["r60"],2)])
    st.dataframe(pd.DataFrame(rows,columns=["Index","Regime","Last","RSI","20D %","60D %"]),use_container_width=True,hide_index=True)

elif page=="🔥 Top 3 Sectors":
    st.title("🔥 Top 3 Strongest Sectors")
    df=sector_scan();st.dataframe(df,use_container_width=True,hide_index=True)
    st.success("Use only the leading sectors as the first filter for Nifty 200 stock selection.")

elif page=="🚀 Nifty 200 Swing":
    st.title("🚀 Nifty 200 Swing Hunter V2")
    df=stock_scan(capital,risk_pct)
    st.dataframe(df.head(30),use_container_width=True,hide_index=True)
    st.caption("Filters include EMA trend, RSI, MACD, 20-day pivot proximity, relative strength vs Nifty 200, volume/20D average and ATR/structure risk.")

elif page=="💎 Positional":
    st.title("💎 Nifty 200 Positional Hunter")
    df=stock_scan(capital,risk_pct)
    df=df[(df["EMA200"]<df["Price"])].sort_values(["Score","60D %"],ascending=False)
    st.dataframe(df.head(25),use_container_width=True,hide_index=True)

elif page=="🎯 Trade Builder":
    st.title("🎯 Professional Trade Builder")
    df=stock_scan(capital,risk_pct)
    sym=st.selectbox("Select stock",df["Symbol"].tolist() if len(df) else [])
    if sym:
        r=df[df["Symbol"]==sym].iloc[0]
        a,b,c,d,e=st.columns(5)
        a.metric("Score",f"{r['Score']}/100");b.metric("Entry",f"₹{r['Price']:.2f}");c.metric("Stop",f"₹{r['Stop']:.2f}");d.metric("T1",f"₹{r['Target 1']:.2f}");e.metric("Qty",int(r["Qty"]))
        st.write(f"**Confidence:** {r['Confidence %']}% (model score, not a guaranteed win probability)")
        st.write(f"**RS vs Nifty 200:** {r['RS vs Nifty 200']} | **Volume ratio:** {r['Vol / Avg20']}x | **RSI:** {r['RSI']}")
        st.write("**Evidence:**",r["Evidence"])

elif page=="📊 Validation Lab":
    st.title("📊 Backtest & Probability Validation")
    st.write("V2 intentionally separates signal scoring from statistical probability.")
    st.markdown("""
**Before using any probability percentage:**
1. Define exact entry/pivot rule.
2. Define stop, target and time stop.
3. Include slippage, brokerage, taxes and gaps.
4. Backtest every Nifty 200 stock over multiple market regimes.
5. Use walk-forward / out-of-sample validation.
6. Measure win rate, expectancy, profit factor and max drawdown.
7. Calibrate confidence to observed outcomes.
""")
    st.info("The next engineering step is a real event-driven backtester, not a cosmetic percentage.")

elif page=="📒 Journal":
    st.title("📒 Trade Journal")
    df=pd.DataFrame(columns=["Date","Symbol","Sector","Setup","Entry","Stop","Target","Qty","Risk ₹","Result","R","Notes"])
    st.download_button("⬇️ Journal CSV",df.to_csv(index=False),"nifty200_trade_journal.csv","text/csv")
    st.dataframe(df,use_container_width=True)

else:
    st.title("⚙️ Nifty 200 V2 Settings")
    st.markdown("""
### Data
Prototype uses yfinance. Production should use a reliable authorised market-data source.

### Nifty 200
This prototype contains a broad representative seed list. For production, import the latest official NSE Nifty 200 constituent CSV automatically.

### V2 scoring
- Trend: EMA20/50/200
- Momentum: RSI + MACD
- Breakout: 20-day pivot proximity
- Volume: current / 20-day average
- Relative strength: stock vs Nifty 200
- Risk: ATR + structure
- Position size: fixed capital risk

### Important
No system can guarantee profitable trades. The app should be validated on historical and out-of-sample data before real-money execution.
""")

st.divider()
st.caption("Independent educational implementation. Not affiliated with Vishal B. Malkan and not a reproduction of proprietary material.")
