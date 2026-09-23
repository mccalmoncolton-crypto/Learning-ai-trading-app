
import streamlit as st
import sqlite3
import json
from datetime import datetime
from pathlib import Path

APP_DIR = Path("trading_ai_data")
APP_DIR.mkdir(exist_ok=True)
DB = APP_DIR / "trading_ai.db"
IMG_DIR = APP_DIR / "charts"
IMG_DIR.mkdir(exist_ok=True)

def db():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS charts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT, timeframe TEXT, date TEXT, notes TEXT,
        setup TEXT, trend TEXT, vwap TEXT, volume TEXT,
        news TEXT, news_impact TEXT, created_at TEXT
    )""")
    return c

def save_record(row):
    c = db()
    c.execute("""INSERT INTO charts
        (ticker,timeframe,date,notes,setup,trend,vwap,volume,news,news_impact,created_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", row)
    c.commit()
    c.close()

st.set_page_config(page_title="Learning AI Trading Lab", page_icon="📈", layout="wide")

st.title("📈 Learning AI Trading Lab")
st.caption("SPY • QQQ • IWM | Screenshot-based pattern learning + economic-news context")

with st.sidebar:
    st.header("Market")
    ticker = st.selectbox("Ticker", ["SPY", "QQQ", "IWM"])
    timeframe = st.selectbox("Timeframe", ["1D", "1H", "15m", "5m", "1m"])
    st.divider()
    st.info("This V1 stores chart observations and outcomes. It does not automatically place trades.")

tabs = st.tabs(["📊 Analyze Chart", "🧠 Pattern Database", "📰 Economic News", "📓 Journal"])

with tabs[0]:
    st.subheader("Upload chart screenshots")
    files = st.file_uploader(
        "Upload one or more screenshots",
        type=["png","jpg","jpeg","webp"],
        accept_multiple_files=True
    )

    col1, col2 = st.columns(2)
    with col1:
        date = st.date_input("Chart date")
        trend = st.selectbox("Market structure", ["Unknown","Bullish","Bearish","Range","Breakout","Breakdown"])
        vwap = st.selectbox("VWAP", ["Unknown","Above","Below","Reclaiming","Rejecting"])
        volume = st.selectbox("Volume", ["Unknown","Low","Normal","High","Breakout confirmation"])

    with col2:
        setup = st.selectbox("Observed setup", [
            "None / unclear","Opening Range Breakout","Opening Range Breakdown",
            "VWAP Reclaim","VWAP Rejection","Premarket High Break",
            "Premarket Low Break","Previous Day High Break",
            "Previous Day Low Break","Support/Resistance Reaction",
            "Consolidation","Failed Breakout","Failed Breakdown"
        ])
        news = st.text_input("Economic/news event (if any)", placeholder="Example: CPI, FOMC, jobs report")
        news_impact = st.selectbox("News impact", ["None / unknown","Low","Medium","High"])
        notes = st.text_area("Notes / what happened next")

    if st.button("💾 Save chart observation", type="primary"):
        if not files:
            st.warning("Upload at least one chart screenshot first.")
        else:
            for i, f in enumerate(files):
                out = IMG_DIR / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}_{f.name}"
                out.write_bytes(f.getbuffer())
            save_record((ticker,str(timeframe),str(date),notes,setup,trend,vwap,volume,news,news_impact,datetime.now().isoformat()))
            st.success(f"Saved {len(files)} screenshot(s) and the structured observation.")

    st.divider()
    st.subheader("What the future AI layer will analyze")
    st.markdown("""
- Trend and market structure
- VWAP and key levels
- Premarket high/low
- Previous-day high/low
- Opening-range behavior
- Volume confirmation
- SPY/QQQ/IWM agreement or divergence
- Economic-news environment
- What happened after the setup
""")

with tabs[1]:
    st.subheader("🧠 Pattern Database")
    c = db()
    rows = c.execute("""SELECT ticker,timeframe,date,setup,trend,vwap,volume,news,news_impact
                        FROM charts ORDER BY id DESC""").fetchall()
    c.close()
    if not rows:
        st.info("No patterns saved yet. Upload charts in Analyze Chart.")
    else:
        st.dataframe(
            rows,
            use_container_width=True,
            column_config={
                0:"Ticker",1:"Timeframe",2:"Date",3:"Setup",4:"Trend",
                5:"VWAP",6:"Volume",7:"News",8:"News Impact"
            }
        )
        st.caption("As more examples are collected, this database becomes the foundation for historical pattern matching.")

with tabs[2]:
    st.subheader("📰 Economic News")
    st.warning("Live economic-calendar/news integration is the next upgrade. V1 lets you label the news environment so the learning database can account for it.")
    st.markdown("""
**Events the final version should track:**
- CPI / PPI
- Jobs report / unemployment
- FOMC rate decisions and minutes
- Fed speeches
- GDP
- Retail sales
- ISM manufacturing/services
- Major unexpected market-moving headlines

The final scanner should flag high-impact events before interpreting a technical setup.
""")

with tabs[3]:
    st.subheader("📓 Trade / Setup Journal")
    st.info("Journal fields and automatic outcome tracking will be added in the next version.")
    st.markdown("""
Planned fields:
- Entry
- Stop / invalidation
- Target
- Result
- R multiple
- Screenshot before entry
- Screenshot after outcome
- Setup type
- Economic-news environment
- Time of day
""")

st.divider()
st.caption("V1 foundation: collect consistent chart + news observations first. The learning engine can then measure which patterns actually worked historically.")
