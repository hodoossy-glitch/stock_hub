import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 페이지 설정 및 한국 시간
st.set_page_config(page_title="황금키 통합 상황판", layout="wide")
now = datetime.now(timezone(timedelta(hours=9)))

# CSS: 직관적인 디자인 (글자색, 배경색, 카드 스타일)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .sector-header { background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b; margin-bottom: 5px; display: flex; justify-content: space-between; align-items: center; }
    .news-text { font-size: 13px; color: #888; margin-left: 15px; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 5px; border: 1px solid #30363d; margin-bottom: 5px; }
    .sector-tag { font-size: 10px; padding: 2px 5px; border-radius: 3px; color: white; }
    .price-up { color: #ff4b4b; font-weight: bold; }
    .price-down { color: #0088ff; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단: 시장별 거래대금 및 매매동향 (좌:코스피 / 우:코스닥)
st.markdown("### 📊 국내 시장 실시간 수급 현황")
col_m1, col_m2 = st.columns(2)

with col_m1:
    st.write("**KOSPI 거래대금 (조)**")
    # 예시 그래프 데이터 (실제 데이터 연동 가능)
    fig_kospi = go.Figure(go.Indicator(mode = "number+delta", value = 8.4, delta = {'reference': 7.2}, number = {'suffix': " 조"}))
    fig_kospi.update_layout(height=150, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="#1e1e1e")
    st.plotly_chart(fig_kospi, use_container_width=True)
    st.caption("개인: -1,200억 | 외국인: +1,500억 | 기관: -300억")

with col_m2:
    st.write("**KOSDAQ 거래대금 (조)**")
    fig_kosdaq = go.Figure(go.Indicator(mode = "number+delta", value = 6.8, delta = {'reference': 7.5}, number = {'suffix': " 조"}))
    fig_kosdaq.update_layout(height=150, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor="#1e1e1e")
    st.plotly_chart(fig_kosdaq, use_container_width=True)
    st.caption("개인: +2,100억 | 외국인: -800억 | 기관: -1,300억")

st.markdown(f"**🌐 나스닥 100 선물:** 20,452.25 <span class='price-up'>+0.45%</span>", unsafe_allow_html=True)
st.divider()

# 3. 메인: 주도 섹터 레이더 (로봇, 반도체 등)
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")

# 실시간 데이터 분석 (약식 구현)
try:
    df_krx = fdr.StockListing('KRX')
    sectors = ["로봇", "반도체", "2차전지", "AI/SW"]
    news = ["삼성 로봇 팔 출시 임박 소식에 수급 집중", "HBM 공급 부족 현상 지속 전망", "리튬 가격 반등 시그널 포착", "정부 AI 예산 대폭 증액 발표"]

    for s_name, s_news in zip(sectors, news):
        with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
            cols = st.columns(3)
            # 해당 섹터 종목 9개 가상 출력 (로직 연동)
            for i in range(9):
                with cols[i % 3]:
                    st.markdown(f"""
                        <div class="stock-card">
                            <div style="font-size:14px; font-weight:bold;">{s_name}대장_{i+1}</div>
                            <div style="font-size:12px;"><span class="price-up">12,500</span> <span class="price-up">+5.2%</span></div>
                            <div style="font-size:11px; color:#888;">대금: 1,240억</div>
                        </div>
                        """, unsafe_allow_html=True)

except:
    st.warning("데이터 동기화 중...")

st.divider()

# 4. 하단: 거래대금 상위 (4% 이상 상승 종목)
st.markdown("### 💰 거래대금 상위 주도주 (4%↑)")
col_stocks = st.columns(4)

# 거래대금 직관적 표기 함수 (조, 억)
def format_amt(amt):
    if amt >= 10000: return f"{amt/10000:.2f}조"
    return f"{amt}억"

# 예시 데이터 8개
sample_stocks = [
    {"name": "삼성전자", "sector": "반도체", "price": "75,200", "chg": "+4.2%", "amt": 12500, "color": "#4b0082"},
    {"name": "현대차", "sector": "자동차", "price": "245,000", "chg": "+5.1%", "amt": 8400, "color": "#00008b"},
    {"name": "레인보우", "sector": "로봇", "price": "165,200", "chg": "+12.5%", "amt": 5200, "color": "#8b0000"},
    {"name": "에코프로", "sector": "2차전지", "price": "105,000", "chg": "+4.8%", "amt": 9800, "color": "#006400"},
    {"name": "SK하이닉스", "sector": "반도체", "price": "185,000", "chg": "+6.3%", "amt": 11000, "color": "#4b0082"},
    {"name": "두산로보", "sector": "로봇", "price": "85,000", "chg": "+8.2%", "amt": 3400, "color": "#8b0000"},
    {"name": "카카오", "sector": "플랫폼", "price": "48,000", "chg": "+4.1%", "amt": 2100, "color": "#8b8b00"},
    {"name": "NAVER", "sector": "플랫폼", "price": "195,000", "chg": "+4.5%", "amt": 2500, "color": "#8b8b00"},
]

for idx, s in enumerate(sample_stocks):
    with col_stocks[idx % 4]:
        st.markdown(f"""
            <div style="background-color:#1c2128; padding:12px; border-radius:10px; border-top: 4px solid {s['color']}; margin-bottom:10px;">
                <div style="font-size:16px; font-weight:bold;">{s['name']}</div>
                <div style="background-color:{s['color']}; color:white; font-size:10px; padding:2px 5px; border-radius:3px; display:inline-block; margin-bottom:5px;">{s['sector']}</div>
                <div style="font-size:18px; color:#ff4b4b; font-weight:bold;">{s['price']}</div>
                <div style="display:flex; justify-content:space-between; font-size:13px;">
                    <span style="color:#ff4b4b;">{s['chg']}</span>
                    <span style="color:#888;">{format_amt(s['amt'])}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 5. 자동 새로고침
time.sleep(60)
st.rerun()
