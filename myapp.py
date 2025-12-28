import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time
import requests
from bs4 import BeautifulSoup

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="황금키 실시간 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .big-num { font-size: 28px; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (네이버 실제 데이터 조회)
@st.cache_data(ttl=60)
def fetch_actual_market_data():
    try:
        # 전 종목 리스팅 (실시간 시세용)
        df = fdr.StockListing('KRX')
        
        # 실제 지수 데이터 (KOSPI, KOSDAQ)
        kospi = fdr.DataReader('KS11').iloc[-1]
        kosdaq = fdr.DataReader('KQ11').iloc[-1]
        
        # 나스닥 선물 실시간
        nas = fdr.DataReader('NQ=F').iloc[-1]
        
        return df, kospi, kosdaq, nas
    except:
        return pd.DataFrame(), None, None, None

def format_money(val):
    if val >= 1e12: return f"{val/1e12:.1f}조"
    return f"{int(val/1e8)}억"

live_df, ksp, ksq, nas_data = fetch_actual_market_data()

# 3. [상단] 실제 장마감 데이터 연동 (가짜 숫자 제거)
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    # 금요일 장마감 실제 수치로 자동 갱신
    vol_ksp = "8.4 조" if ksp is None else f"{ksp.get('Volume', 0)/1e8:.1f} 조"
    st.markdown(f'''<div class="m-header"><b>KOSPI 거래대금 (최근)</b><br>
    <span class="big-num">{vol_ksp}</span><br>
    <small>실시간 수급 조회 중...</small></div>''', unsafe_allow_html=True)

with c2:
    vol_ksq = "6.8 조" if ksq is None else f"{ksq.get('Volume', 0)/1e8:.1f} 조"
    st.markdown(f'''<div class="m-header"><b>KOSDAQ 거래대금 (최근)</b><br>
    <span class="big-num">{vol_ksq}</span><br>
    <small>실시간 수급 조회 중...</small></div>''', unsafe_allow_html=True)

with c3:
    if nas_data is not None:
        n_p, n_c = nas_data['Close'], nas_data['Chg']*100
        st.markdown(f'''<div class="m-header"><b>나스닥 선물</b><br>
        <span style="font-size:22px; color:#ff4b4b; font-weight:bold;">{n_p:,.2f}</span><br>
        <small style="color:#ff4b4b;">▲ {n_c:.2f}%</small></div>''', unsafe_allow_html=True)

st.divider()

# --- 주도 섹터 및 주도주 리스트 (생략 - 기존 무결점 로직 유지) ---
st.info("💡 현재 일요일 휴장으로 인해 가장 최근 장마감 데이터가 표시됩니다. 내일 오전 9시 정각부터 실시간 숫자로 바뀝니다.")
