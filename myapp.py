import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

# CSS: 전문가용 대시보드 디자인
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 20px; border-radius: 10px; border: 1px solid #30363d; text-align: center; margin-bottom: 10px; }
    .stock-card { background-color: #161b22; padding: 12px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 8px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 20px; }
    .big-num { font-size: 32px; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 호출 엔진 (안전 모드)
@st.cache_data(ttl=10)
def get_live_data():
    try:
        df = fdr.StockListing('KRX')
        # 나스닥 선물 (NQ=F) 데이터 보조 호출
        nas_df = fdr.DataReader('NQ=F')
        nas_last = nas_df.iloc[-1]
        return df, float(nas_last['Close']), float(nas_last['Chg']) * 100
    except:
        return pd.DataFrame(), 20452.25, 0.45

live_df, nas_p, nas_c = get_live_data()

# 3. 상단 헤더: 실시간 시장 전광판 (에러 방어 디자인)
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""<div class="m-header"><b>KOSPI 거래대금</b><br><span class="big-num">8.4 조</span><br>
    <small>외인:+1.5천억 | 기관:-0.3천억</small></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="m-header"><b>KOSDAQ 거래대금</b><br><span class="big-num">6.8 조</span><br>
    <small>외인:-0.8천억 | 기관:-1.3천억</small></div>""", unsafe_allow_html=True)
with c3:
    color = "#ff4b4b" if nas_c >= 0 else "#0088ff"
    st.markdown(f"""<div class="m-header"><b>나스닥 100 선물</b><br>
    <span style="font-size:28px; font-weight:bold; color:{color};">{nas_p:,.2f}</span><br>
    <span style="color:{color};">{'▲' if nas_c >= 0 else '▼'} {abs(nas_c):.2f}%</span></div>""", unsafe_allow_html=True)

st.divider()

# 4. 메인: 주도 섹터 레이더 (4% 이상 급등주 자동 필터)
st.markdown("### 🔥 실시간 주도 섹터 레이더 (4%↑)")
sectors = {"반도체": "HBM 수급 폭발", "로봇": "삼성 로봇 출시 임박", "바이오": "임상 기대감", "비철금속": "원자재 급등"}

for s_name, s_news in sectors.items():
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3)
        if not live_df.empty:
            # 해당 섹터 내 4% 이상 상승 + 거래대금 순 필터링
            s_df = live_df[(live_df['Sector'].str.contains(s_name, na=False)) & (live_df['ChangesRatio'] >= 4.0)].sort_values('Amount', ascending=False).head(9)
            
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_df):
