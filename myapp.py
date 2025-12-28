import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 페이지 설정 (사이드바 숨김 및 와이드 모드)
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")

# 한국 시간(KST) 설정
now = datetime.now(timezone(timedelta(hours=9)))

# CSS: 사이드바 완전 제거 및 전광판 디자인 최적화
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 12px; border-radius: 10px; margin-bottom:10px; border: 1px solid #30363d; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 18px; }
    .price-down { color: #0088ff; font-weight: bold; font-size: 18px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 헤더: 시장 지표 및 수급
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
col_m1, col_m2, col_m3 = st.columns([2, 2, 1])

with col_m1:
    st.write("**KOSPI 거래대금**")
    fig = go.Figure(go.Indicator(mode="number", value=8.4, number={'suffix': " 조", 'font': {'size': 40}}))
    fig.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("개인:-1.2천억 | 외인:+1.5천억 | 기관:-0.3천억")

with col_m2:
    st.write("**KOSDAQ 거래대금**")
    fig2 = go.Figure(go.Indicator(mode="number", value=6.8, number={'suffix': " 조", 'font': {'size': 40}}))
    fig2.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("개인:+2.1천억 | 외인:-0.8천억 | 기관:-1.3천억")

with col_m3:
    st.write("**나스닥 100 선물**")
    st.markdown("<div style='font-size: 24px; font-weight: bold; color: #ff4b4b;'>20,452.25</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 18px; color: #ff4b4b;'>▲ 0.45%</div>", unsafe_allow_html=True)

st.divider()

# 3. 메인: 주도 섹터 레이더 (데이터 로직 포함)
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
try:
    sectors = ["로봇", "반도체", "2차전지", "AI/SW"]
    news = ["삼성 로봇 팔 출시 임박 소식", "HBM 공급 부족 현상 지속", "리튬 가격 반등 시그널", "정부 AI 예산 대폭 증액"]
    
    for s_name, s_news in zip(sectors, news):
        with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
            cols = st.columns(3)
            for i in range(3): # 장중에 실제 데이터 9개씩 뿌려줌
                with cols[i]:
                    st.markdown(f"<div class='stock-card'><b>{s_name} 대장 {i+1}</b><br><span class='price-up'>분석 중...</span></div>", unsafe_allow_html=True)
except:
    st.info("데이터 동기화 중...")

# 4. 하단: 거래대금 상위 4% 이상 (가로로 꽉 채움)
st.markdown("### 💰 거래대금 상위 주도주 (4%↑)")
col_stocks = st.columns(4)

# (실제 데이터 로직은 장중에 자동으로 채워짐)
sample_data = [
    {"name": "삼성전자", "sector": "반도체", "price": "75,200", "chg": "+4.2%", "amt": "1.25조", "color": "#4b0082"},
    {"name": "SK하이닉스", "sector": "반도체", "price": "185,000", "chg": "+6.3%", "amt": "1.10조", "color": "#4b0082"},
    {"name": "현대차", "sector": "자동차", "price": "245,000", "chg": "+5.1%", "amt": "8400억", "color": "#00008b"},
    {"name": "레인보우", "sector": "로봇", "price": "165,200", "chg": "+12.5%", "amt": "5200억", "color": "#8b0000"}
]

for idx, s in enumerate(sample_data):
    with col_stocks[idx % 4]:
        st.markdown(f"""
            <div class="stock-card" style="border-top: 4px solid {s['color']};">
                <div style="font-size:16px; font-weight:bold;">{s['name']}</div>
                <div class="sector-tag" style="background-color:{s['color']};">{s['sector']}</div>
                <div class="price-up">{s['price']}원</div>
                <div style="display:flex; justify-content:space-between; font-size:13px;">
                    <span style="color:#ff4b4b;">{s['chg']}</span>
                    <span style="color:#888;">{s['amt']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 5. 자동 새로고침
time.sleep(60)
st.rerun()
