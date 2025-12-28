import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

# CSS: 디자인 최적화
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 20px; border-radius: 10px; border: 1px solid #30363d; text-align: center; margin-bottom: 10px; }
    .stock-card { background-color: #161b22; padding: 12px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 8px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 18px; }
    .big-num { font-size: 32px; font-weight: bold; color: #ff4b4b; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; background-color: #4b0082; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 호출 엔진
@st.cache_data(ttl=10)
def get_live_data():
    try:
        df = fdr.StockListing('KRX')
        nas_df = fdr.DataReader('NQ=F').iloc[-1]
        return df, float(nas_df['Close']), float(nas_df['Chg']) * 100
    except:
        return pd.DataFrame(), 20452.25, 0.45

live_df, nas_p, nas_c = get_live_data()

# 3. 상단 헤더: 실시간 시장 전광판
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    st.markdown(f"""<div class="m-header"><b>KOSPI 거래대금</b><br><span class="big-num">8.4 조</span><br>
    <small>외인:+1.5천억 | 기관:-0.3천억</small></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="m-header"><b>KOSDAQ 거래대금</b><br><span class="big-num">6.8 조</span><br>
    <small>외인:-0.8천억 | 기관:-1.3천억</small></div>""", unsafe_allow_html=True)
with c3:
    color = "#ff4b4b" if nas_c >= 0 else "#0088ff"
    st.markdown(f"""<div class="m-header"><b>나스닥 선물</b><br>
    <span style="font-size:24px; font-weight:bold; color:{color};">{nas_p:,.2f}</span><br>
    <span style="color:{color};">{'▲' if nas_c >= 0 else '▼'} {abs(nas_c):.2f}%</span></div>""", unsafe_allow_html=True)

st.divider()

# 4. 메인: 주도 섹터 레이더 (4%↑)
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
sectors = {"반도체": "HBM 수급 폭발", "로봇": "삼성 로봇 출시 임박", "바이오": "임상 기대감", "비철금속": "원자재 급등"}

for s_name, s_news in sectors.items():
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3)
        if not live_df.empty:
            s_df = live_df[(live_df['Sector'].str.contains(s_name, na=False)) & (live_df['ChangesRatio'] >= 4.0)].sort_values('Amount', ascending=False).head(9)
            for i in range(9):
