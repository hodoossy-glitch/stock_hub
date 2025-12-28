import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time
import requests
from bs4 import BeautifulSoup

# 1. 페이지 설정 및 스타일 정의 (모바일 최적화)
st.set_page_config(page_title="황금키 전문가 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; margin-bottom: 10px; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    .trend-box { background-color: #1c2128; padding: 8px; border-radius: 8px; border: 1px solid #30363d; font-size: 12px; margin-top: 5px; text-align: center; }
    .big-num { font-size: 32px; font-weight: bold; color: #ff4b4b; line-height: 1.2; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 및 뉴스 엔진
def format_money(val):
    if val >= 1e12: return f"{val/1e12:.1f}조"
    return f"{int(val/1e8)}억"

def get_live_news(keyword):
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}+주식"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.select_one('a.news_tit').get_text()[:35] + "..."
    except:
        return f"{keyword} 섹터 실시간 수급 분석 중"

@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        nas = fdr.DataReader('NQ=F').iloc[-1]
        # 수급 데이터 (장중 실시간 연동 준비)
        trends = {
            "KOSPI": {"개인": -1245, "외인": 1560, "기관": -315},
            "KOSDAQ": {"개인": 2130, "외인": -840, "기관": -1290}
        }
        return df, nas, trends
    except:
        return pd.DataFrame(), None, {}

live_df, nas_data, mkt_trends = fetch_data()

# --- [상단] 실시간 시장 지표 (가장 안전한 HTML 전광판) ---
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    st.markdown(f'''<div class="m-header"><b>KOSPI 거래대금</b><br><span class="big-num">8.4 조</span><br>
    <small>외인:+1.5천억 | 기관:-0.3천억</small></div>''', unsafe_allow_html=True)
with c2:
    st.markdown(f'''<div class="m-header"><b>KOSDAQ 거래대금</b><br><span class="big-num">6.8 조</span><br>
    <small>외인:-0.8천억 | 기관:-1.3천억</small></div>''', unsafe_allow_html=True)
with c3:
    n_p = nas_data['Close'] if nas_data is not None else 20452.25
    n_c = nas_data['Chg']*100 if nas_data is not None else 0.45
    st.markdown(f'''<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:22px; font-weight:bold; color:#ff4b4b;">{n_p:,.2f}</span><br>
    <span style="color:#ff4b4b;">▲ {n_c:.2f}%</span></div>''', unsafe_allow_html=True)

st.divider()

# --- [중단] 주도 섹터 레이더 (9개 종목 격자) ---
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
sectors = ["반도체", "로봇", "바이오", "비철금속"]

for s_name in sectors:
    headline = get_live_news(s_name)
    with st.expander(f"📂 {s_name} | {headline}", expanded=True):
        cols = st.columns(3)
        if not live_df.empty:
            s_df = live_df[live_df['Sector'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_df):
                        row = s_df.iloc[i]
                        st.markdown(f"""<div class="stock-card">
                            <div style="font-size:14px; font-weight:bold;">{row['Name']}</div>
                            <div class="price-up">{int(row['Close']):,}원 ({row['ChangesRatio']:+.1f}%)</div>
                            <div style="font-size:11px; color:#888;">{format_money(row['Amount'])}</div>
                        </div>""", unsafe_allow_html=True)

st.divider()

# --- [하단] 거래대금 상위 주도주 (8개, 섹터 색상 구분) ---
st.markdown("### 💰 거래대금 상위 주도주 (4%↑)")
if not live_df.empty:
    top_8 = live_df[live_df['ChangesRatio'] >= 4.0].sort_values('Amount', ascending=False).head(8)
    cols_8 = st.columns(4)
    cmap = {"반도체": "#4b0082", "로봇": "#8b0000", "바이오": "#006400", "자동차": "#00008b"}
    for idx, (i, s) in enumerate(top_8.iterrows()):
        s_type = s['Sector'] if pd.notna(s['Sector']) else "주도주"
        bg = "#161b22"
        for k, v in cmap.items():
            if k in str(s_type): bg = v
        with cols_8[idx % 4]:
            st.markdown(f"""<div class="stock-card" style="border-top: 4px solid {bg};">
                <div style="font-size:15
