import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 모바일 최적화 페이지 설정
st.set_page_config(page_title="황금키 모바일", layout="wide", initial_sidebar_state="collapsed")

# 한국 시간(KST) 설정
now = datetime.now(timezone(timedelta(hours=9)))

# CSS: 모바일 전용 폰트 크기 및 카드 디자인
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; padding: 10px; }
    /* 모바일에서 글자가 잘 보이도록 폰트 크기 상향 */
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; }
    .m-title { font-size: 20px; font-weight: bold; color: #ff4b4b; margin-bottom: 10px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    .sector-tag { font-size: 12px; padding: 3px 8px; border-radius: 5px; color: white; display: inline-block; margin-top: 5px; }
    .market-box { background-color: #1e1e1e; padding: 10px; border-radius: 8px; text-align: center; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단: 시장 요약 (모바일은 세로로 배치하거나 좁게)
st.markdown(f"<div class='m-title'>📡 실시간 시장 전광판</div>", unsafe_allow_html=True)
st.caption(f"최종 업데이트: {now.strftime('%H:%M:%S')}")

col_m1, col_m2 = st.columns(2)
with col_m1:
    st.markdown(f"<div class='market-box'><small>KOSPI 거래대금</small><br><b style='font-size:20px;'>8.4조</b></div>", unsafe_allow_html=True)
with col_m2:
    st.markdown(f"<div class='market-box'><small>KOSDAQ 거래대금</small><br><b style='font-size:20px;'>6.8조</b></div>", unsafe_allow_html=True)

st.markdown(f"🌐 **나스닥 선물:** <span style='color:#ff4b4b;'>20,452.25 (+0.45%)</span>", unsafe_allow_html=True)
st.divider()

# 3. 메인: 주도 섹터 (모바일에서는 '아코디언' 방식이 최고입니다)
st.markdown("### 🔥 주도 섹터 & 뉴스")
sectors = ["로봇", "반도체", "2차전지", "AI/SW"]
news = ["삼성 로봇 팔 출시 임박", "HBM 공급 부족 지속", "리튬 가격 반등 신호", "정부 AI 예산 증액"]

for s_name, s_news in zip(sectors, news):
    with st.expander(f"📂 {s_name} | {s_news}"):
        # 모바일 가독성을 위해 한 줄에 하나씩 크게 표시
        for i in range(3):
            st.markdown(f"""
                <div class="stock-card" style="border-left: 5px solid #ff4b4b;">
                    <div style="font-size:18px; font-weight:bold;">{s_name} 대장주 {i+1}</div>
                    <div class="price-up">데이터 분석 중...</div>
                </div>
                """, unsafe_allow_html=True)

st.divider()

# 4. 하단: 거래대금 상위 (모바일 최적화 리스트)
st.markdown("### 💰 거래대금 상위 (4%↑)")

sample_data = [
    {"name": "삼성전자", "sector": "반도체", "price": "75,200", "chg": "+4.2%", "amt": "1.25조", "color": "#4b0082"},
    {"name": "SK하이닉스", "sector": "반도체", "price": "185,000", "chg": "+6.3%", "amt": "1.10조", "color": "#4b0082"},
    {"name": "레인보우", "sector": "로봇", "price": "165,200", "chg": "+12.5%", "amt": "5200억", "color": "#8b0000"}
]

for s in sample_data:
    st.markdown(f"""
        <div class="stock-card" style="border-right: 4px solid {s['color']};">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:18px; font-weight:bold;">{s['name']}</div>
                    <div class="sector-tag" style="background-color:{s['color']};">{s['sector']}</div>
                </div>
                <div style="text-align:right;">
                    <div class="price-up">{s['price']}</div>
                    <div style="font-size:14px; color:#ff4b4b;">{s['chg']} <span style="color:#888; margin-left:5px;">{s['amt']}</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# 5. 자동 새로고침
time.sleep(60)
st.rerun()
