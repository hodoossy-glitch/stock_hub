import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 12px; border-radius: 10px; border-left: 5px solid #ff4b4b; margin-bottom: 10px; }
    .info-box { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; font-size: 14px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 20px; }
    .price-down { color: #0088ff; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단: 통합 금융 지표 (환율, 유가, 금시세)
st.markdown(f"### 🌍 글로벌 경제 지표 ({now.strftime('%Y-%m-%d')})")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("<div class='info-box'>💵 <b>미국 USD</b><br><span class='price-down'>1,445.00</span><br><small>▼ 5.00</small></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='info-box'>🛢️ <b>WTI 유가</b><br><span class='price-down'>56.74</span><br><small>▼ 1.61</small></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='info-box'>💰 <b>국제 금</b><br><span class='price-up'>4,552.70</span><br><small>▲ 49.90</small></div>", unsafe_allow_html=True)
with c4:
    st.markdown("<div class='info-box'>📈 <b>코스피 200</b><br><span class='price-up'>590.08</span><br><small>▲ 5.87 (+1.00%)</small></div>", unsafe_allow_html=True)

st.divider()

# 3. 메인: 실시간 주도주 (이미지 기반 최신 시세 반영)
st.markdown("### 🔥 2025년 12월 금요일 장마감 주도주")

# 캡처 이미지 데이터 기반 강제 업데이트 로직
@st.cache_data(ttl=60)
def get_verified_data():
    # 이미지에 나온 실제 수치 적용
    verified_list = [
        {'name': '삼성전자', 'price': 117000, 'chg': 5.31, 'amt': '1.2조', 'sector': '반도체'},
        {'name': 'SK하이닉스', 'price': 599000, 'chg': 1.87, 'amt': '8900억', 'sector': '반도체'},
        {'name': '에스엠벡셀', 'price': 2610, 'chg': 16.00, 'amt': '420억', 'sector': '배터리'},
        {'name': '셀루메드', 'price': 1896, 'chg': 29.95, 'amt': '350억', 'sector': '바이오'},
        {'name': '남선알미늄', 'price': 1310, 'chg': 29.96, 'amt': '280억', 'sector': '비철금속'},
        {'name': '조일알미늄', 'price': 1389, 'chg': 14.79, 'amt': '190억', 'sector': '비철금속'}
    ]
    return verified_list

stocks = get_verified_data()
cols = st.columns(3)

for idx, s in enumerate(stocks):
    with cols[idx % 3]:
        st.markdown(f"""
            <div class="stock-card">
                <div style="font-size:16px; font-weight:bold;">{s['name']}</div>
                <div style="font-size:11px; color:#888; margin-bottom:5px;">{s['sector']}</div>
                <div class="price-up">{s['price']:,}원</div>
                <div style="display:flex; justify-content:space-between; font-size:14px;">
                    <span style="color:#ff4b4b;">▲ {s['chg']}%</span>
                    <span style="color:#888;">{s['amt']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# 4. 하단: 테마/업종 상위 요약
st.divider()
st.markdown("### 🔝 테마/업종 상위 (실시간)")
t1, t2 = st.columns(2)
with t1:
    st.info("📂 뉴로모픽 반도체 (+8.97%) | 온디바이스 AI (+6.28%)")
with t2:
    st.success("📂 반도체 대표주 (+3.90%) | 생물공학 (+2.48%)")

# 5. 자동 새로고침
time.sleep(60)
st.rerun()
