import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인 (사이드바 제거)
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .sector-header { background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b; margin-bottom: 10px; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 5px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .info-box { background-color: #161b22; padding: 8px; border-radius: 5px; border: 1px solid #30363d; font-size: 13px; text-align: center; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- [상단] 실시간 주도 섹터 & 뉴스 ---
st.markdown(f"### 🔥 주도 섹터 실시간 레이더 ({now.strftime('%H:%M:%S')})")

# 캡처본 기반 데이터 구성 (실제 데이터 엔진과 연동 준비)
sectors = ["반도체", "비철금속", "바이오", "핸드셋"]
news_list = ["HBM 5세대 공급 부족 및 삼성전자 11만 돌파", "알루미늄 가격 급등에 따른 수급 집중", "신약 임상 결과 발표 임박 소식", "온디바이스 AI 채택 기기 확대 전망"]

for s_name, s_news in zip(sectors, news_list):
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3) # 한 줄에 3개씩, 총 3줄로 9개 종목 배치
        for i in range(3): 
            with cols[i]:
                # 실제 데이터 연동 시 이 부분이 실시간 값으로 대체됩니다
                st.markdown(f"""
                    <div class="stock-card">
                        <div style="font-size:14px; font-weight:bold;">{s_name}대장_{i+1}</div>
                        <div class="price-up">117,000원 (+5.31%)</div>
                        <div style="font-size:11px; color:#888;">거래대금: 1.2조</div>
                    </div>
                    """, unsafe_allow_html=True)

st.divider()

# --- [하단] 시장 지표 및 매매동향 (좌/우 분할) ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 📉 국내 시장 거래대금")
    c1, c2 = st.columns(2)
    with c1:
        st.write("KOSPI (조)")
        fig = go.Figure(go.Indicator(mode="number", value=8.4, number={'suffix':"조"}))
        fig.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117", font={'color':"#ff4b4b"})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.write("KOSDAQ (조)")
        fig2 = go.Figure(go.Indicator(mode="number", value=6.8, number={'suffix':"조"}))
        fig2.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117", font={'color':"#ff4b4b"})
        st.plotly_chart(fig2, use_container_width=True)
    
    st.markdown("""
        <div class='info-box'>
        <b>시장 매매동향 (억)</b><br>
        코스피: 개인(-1200) 외인(+1500) 기관(-300)<br>
        코스닥: 개인(+2100) 외인(-800) 기관(-1300)
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("#### 🌐 글로벌 지표 & 환율")
    st.markdown(f"""
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
            <div class='info-box'><b>미국 USD</b><br><span style='color:#0088ff;'>1,445.00 (▼5.0)</span></div>
            <div class='info-box'><b>나스닥 선물</b><br><span class='price-up'>20,452.25 (+0.45%)</span></div>
            <div class='info-box'><b>WTI 유가</b><br><span style='color:#0088ff;'>56.74 (▼1.6)</span></div>
            <div class='info-box'><b>국제 금</b><br><span class='price-up'>4,552.70 (▲49.9)</span></div>
        </div>
        """, unsafe_allow_html=True)

# 4. 자동 새로고침 (60초)
time.sleep(60)
st.rerun()
