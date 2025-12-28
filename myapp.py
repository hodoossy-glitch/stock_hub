import streamlit as st
from datetime import datetime, timezone, timedelta

# 1. 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="딱-뉴스 황금키 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    .trend-box { background-color: #1c2128; padding: 10px; border-radius: 8px; border: 1px solid #30363d; font-size: 13px; margin-top: 10px; text-align: center; }
    .big-num { font-size: 28px; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# --- [상단] 📡 실시간 시장 전광판 (디자인 레이아웃) ---
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    st.markdown('<div class="m-header"><b>KOSPI 거래대금</b><br><span class="big-num">8.4 조</span><br><small>최종 마감 데이터</small></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="m-header"><b>KOSDAQ 거래대금</b><br><span class="big-num">6.8 조</span><br><small>최종 마감 데이터</small></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:20px; font-weight:bold; color:#ff4b4b;">20,452.25</span><br><span style="color:#ff4b4b; font-size:12px;">▲ 0.45%</span></div>', unsafe_allow_html=True)

# --- [수급] 개인, 외국인, 기관 매매동향 ---
st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <div class="trend-box" style="flex: 1;"><b>KOSPI 수급(억):</b> <span style="color:#0088ff">개인(-1,245)</span> | <span style="color:#ff4b4b">외인(+1,560)</span> | 기관(-315)</div>
        <div class="trend-box" style="flex: 1;"><b>KOSDAQ 수급(억):</b> <span style="color:#ff4b4b">개인(+2,130)</span> | <span style="color:#0088ff">외인(-840)</span> | 기관(-1,290)</div>
    </div>
""", unsafe_allow_html=True)

st.divider()

# --- [중단] 🔥 실시간 주도 섹터 & 뉴스 (9개 종목 격자) ---
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
sectors = [("반도체", "HBM 5세대 공급 부족 및 삼성전자 강세"), ("로봇", "삼성 로봇 출시 임박 및 수급 집중")]

for s_name, s_news in sectors:
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
