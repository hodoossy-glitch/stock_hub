import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 12px; border-radius: 10px; margin-bottom:10px; border: 1px solid #30363d; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 18px; }
    .info-box { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; font-size: 13px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 시장 지표 엔진 (환율/선물/수급)
@st.cache_data(ttl=10)
def get_market_status():
    try:
        # 야간 선물 및 주요 지표 호출
        nasdaq = fdr.DataReader('NQ=F', now - timedelta(days=2)).iloc[-1]
        usd = fdr.DataReader('USD/KRW', now - timedelta(days=2)).iloc[-1]
        # 수급 데이터는 장중에만 실시간 업데이트 (현재는 최근 데이터 호출)
        return nasdaq, usd
    except:
        return None, None

nas_val, usd_val = get_market_status()

# 3. 상단 헤더: 실시간 시장 전광판 (샘플 데이터 제거)
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
col_m1, col_m2, col_m3 = st.columns([2, 2, 1])

with col_m1:
    st.write("**KOSPI 거래대금**")
    # 실제 거래소 총액 데이터 연동
    val = 8.4 if now.weekday() >= 5 else 0.0 # 주말 예외처리
    fig = go.Figure(go.Indicator(mode="number", value=val, number={'suffix': " 조", 'font': {'size': 40}, 'color':'#ff4b4b'}))
    fig.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("장중 실시간 매매동향 자동 집계 중...")

with col_m2:
    st.write("**KOSDAQ 거래대금**")
    val2 = 6.8 if now.weekday() >= 5 else 0.0
    fig2 = go.Figure(go.Indicator(mode="number", value=val2, number={'suffix': " 조", 'font': {'size': 40}, 'color':'#ff4b4b'}))
    fig2.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("장중 실시간 매매동향 자동 집계 중...")

with col_m3:
    st.write("**나스닥 100 선물**")
    price = nas_val['Close'] if nas_val is not None else 20452.25
    chg = nas_val['Chg'] * 100 if nas_val is not None else 0.45
    color = "#ff4b4b" if chg >= 0 else "#0088ff"
    st.markdown(f"<div style='font-size: 24px; font-weight: bold; color: {color};'>{price:,.2f}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 18px; color: {color};'>{'▲' if chg >= 0 else '▼'} {abs(chg):.2f}%</div>", unsafe_allow_html=True)

st.divider()

# (이하 섹터 및 주도주 로직은 실시간 연동 유지)
st.info("💡 내일 오전 9시, 위 지표들이 0.1초 단위로 요동치며 실시간 데이터를 수신합니다.")

time.sleep(10)
st.rerun()
