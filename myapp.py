import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta

# 1. 페이지 설정 및 전문가용 다크 스타일 (모바일 최적화)
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .nav-bar { display: flex; justify-content: space-around; padding: 10px; background: #1c2128; border-bottom: 1px solid #30363d; margin-bottom: 15px; font-size: 14px; font-weight: bold; color: #888; }
    .nav-active { color: #ffffff; border-bottom: 2px solid #ff4b4b; padding-bottom: 5px; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }
    .big-num { font-size: 24px; font-weight: bold; color: #ff4b4b; margin: 5px 0; }
    .leader-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #000; }
    .tag-bio { background-color: #d1f7d1; } .tag-robot { background-color: #fff4cc; } .tag-aero { background-color: #ffdce0; } .tag-atomic { background-color: #e8dff5; }
    .stock-grid-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .trend-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; margin-top: 10px; }
    .trend-table th { color: #888; padding: 8px; border-bottom: 1px solid #30363d; }
    .trend-table td { padding: 10px; border-bottom: 1px solid #1c2128; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 네비게이션
st.markdown('<div class="nav-bar"><span class="nav-active">주도섹터</span><span>대금상위</span><span>캘린더</span><span>공지</span></div>', unsafe_allow_html=True)

# 3. 실시간 시장 지표
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="m-header"><b>KOSPI</b><br><span class="big-num">2,642.15</span><br><small>▲ 1.38% (16.3조)</small></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="m-header"><b>KOSDAQ</b><br><span class="big-num">872.45</span><br><small>▲ 0.29% (12.4조)</small></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:18px; font-weight:bold; color:#ff4b4b;">25,185.80</span><br><small>▼ 1.95%</small></div>', unsafe_allow_html=True)

st.divider()

# 4. 주도 섹터 및 뉴스 상세 (이미지 2의 '로봇' 섹터 구현)
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
sectors = [("로봇", "4대 그룹 다 뛰어든 로봇 관절 전쟁... K-휴머노이드 성패 달렸다")]

for s_name, s_news in sectors:
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3)
        stocks = [("클로봇", "65,200", "+26.8%"), ("씨메스", "39,700", "+14.5%"), ("유진로봇", "16,920", "+14.0%")]
        for i, (name, price, chg) in enumerate(stocks):
            with cols[i % 3]:
                st.markdown(f'<div class="stock-grid-card"><b>{name}</b><br><span style="color:#ff4b4b;">{price}</span><br><small>{chg}</small></div>', unsafe_allow_html=True)

st.divider()

# 5. 거래대금 상위 4% 이상 (이미지 1의 컬러 리스트)
st.markdown("### 💰 거래대금 상위 4%↑ 주도주")
top_stocks = [
    ("삼성에피스", "바이오", "661,000", "+16.17%", "1.59조", "tag-bio"),
    ("클로봇", "로봇", "65,200", "+26.85%", "9673억", "tag-robot"),
    ("한화시스템", "우주항공", "53,100", "+10.51%", "39
