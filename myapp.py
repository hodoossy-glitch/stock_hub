import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta

# 1. 페이지 설정 및 모바일 최적화 CSS
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    /* 배경 및 기본 폰트 설정 */
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; font-family: 'Pretendard', sans-serif; }
    
    /* 상단 네비게이션 바 스타일 */
    .nav-bar { display: flex; justify-content: space-around; padding: 10px; background: #1c2128; border-bottom: 1px solid #30363d; margin-bottom: 15px; font-size: 14px; font-weight: bold; color: #888; }
    .nav-active { color: #ffffff; border-bottom: 2px solid #ff4b4b; padding-bottom: 5px; }

    /* 지수/지표 카드 스타일 */
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }
    .big-num { font-size: 24px; font-weight: bold; color: #ff4b4b; margin: 5px 0; }
    
    /* 거래대금 상위 종목 리스트 (이미지 2 스타일) */
    .leader-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 15px; border-radius: 8px; margin-bottom: 8px; font-weight: bold; font-size: 14px; color: #000; }
    .tag-bio { background-color: #d1f7d1; } .tag-robot { background-color: #fff4cc; } .tag-aero { background-color: #ffdce0; } .tag-atomic { background-color: #e8dff5; }
    
    /* 주도 섹터 및 종목 카드 */
    .sector-news { font-size: 12px; color: #888; text-decoration: underline; margin-left: 10px; font-weight: normal; }
    .stock-grid-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    
    /* 시장 매매동향 테이블 */
    .trend-table { width: 100%; border-collapse: collapse; font-size: 12px; text-align: center; margin-top: 10px; }
    .trend-table th { color: #888; padding: 8px; border-bottom: 1px solid #30363d; }
    .trend-table td { padding: 10px; border-bottom: 1px solid #1c2128; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 네비게이션
st.markdown("""
    <div class="nav-bar">
        <span class="nav-active">주도섹터</span>
        <span>대금상위</span>
        <span>캘린더</span>
        <span>공지</span>
    </div>
    """, unsafe_allow_html=True)

# 3. 실시간 시장 지수 & 선물 (이미지 1 + 2 혼합)
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns(3)

# 지수 그래프 예시 데이터 생성
def get_mini_chart(color):
    fig = go.Figure(data=go.Scatter(y=[10, 12, 11, 14, 15, 14, 16], mode='lines', line=dict(color=color, width=2)))
    fig.update_layout(height=60, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

with c1:
    st.markdown('<div class="m-header"><b>KOSPI</b><br><span class="big-num">2,642.15</span><br><small>▲ 1.38% (16.3조)</small></div>', unsafe_allow_html=True)
    st.plotly_chart(get_mini_chart('#ff4b4b'), use_container_width=True, config={'displayModeBar': False})
with c2:
    st.markdown('<div class="m-header"><b>KOSDAQ</b><br><span class="big-num">872.45</span><br><small>▲ 0.29% (12.4조)</small></div>', unsafe_allow_html=True)
    st.plotly_chart(get_mini_chart('#ff4b4b'), use_container_width=True, config={'displayModeBar': False})
with c3:
    st.markdown('<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:18px; font-weight:bold; color:#ff4b4b;">25,185.80</span><br><small>▼ 1.95%</small></div>', unsafe_allow_html=True)

st.divider()

# 4. 거래대금 상위 4% 이상 (이미지 2 스타일)
st.markdown("### 💰 거래대금 상위 4%↑ 주도주")
top_stocks = [
    ("삼성에피스", "바이오", "661,000", "+16.17%", "1.59조", "tag-bio"),
    ("클로봇", "로봇", "65,200", "+26.85%", "9673억", "tag-robot"),
    ("에임드바이오", "바이오", "55,900", "+19.70%", "5657억", "tag-bio"),
    ("한화시스템", "우주항공", "53,100", "+10.51%", "3909억", "tag-aero"),
    ("비에이치아이", "원전", "64,200", "+21.82%", "4882억", "tag-atomic")
]

for name, sector, price, change, amount, tag in top_stocks:
    st.markdown(f"""
        <div class="leader-item {tag}">
            <div style="flex:1;">{name} <small style="font-weight:normal; opacity:0.7;">{sector}</small></div>
            <div style="flex:1; text-align:center;">{price} <small>{change}</small></div>
            <div style="flex:1; text-align:right;">{amount}</div>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# 5. 주도 섹터 상세 (이미지 3 스타일: 뉴스 한 줄 매칭)
st.markdown("### 🔥 주도 섹터 & 뉴스")
with st.expander("📂 로봇 | '4대 그룹 다 뛰어든 로봇 관절 전쟁...'", expanded=True):
    grid_cols = st.columns(3)
    robot_stocks = [("클로봇", "65,200", "26.8%"), ("씨메스", "39,700", "14.5%"), ("유진로봇", "16,920", "14.0%")]
    for i, (name, price, chg) in enumerate(robot_stocks):
        with grid_cols[i % 3]:
            st.markdown(f"""<div class="stock-grid-card"><b>{name}</b><br><span class="price-up">{price}</span><br><small>{chg}</small></div>""", unsafe_allow_html=True)

st.divider()

# 6. 시장별 매매동향 (이미지 2 하단 스타일)
st.markdown("### 📊 시장별 매매동향 (단위: 억)")
st.markdown("""
    <table class="trend-table">
        <tr><th>시장</th><th>개인</th><th>외국인</th><th>기관</th></tr>
        <tr><td>코스피</td><td style="color:#0088ff">-1245</td><td style="color:#ff4b4b">+1560</td><td>-315</td></tr>
        <tr><td>코스닥</td><td style="color:#ff4b4b">+2130</td><td style="color:#0088ff">-840</td><td>-1290</td></tr>
    </table>
    """, unsafe_allow_html=True)
