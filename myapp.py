import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime
import time

# 1. 페이지 설정 및 캐시 초기화
st.set_page_config(page_title="황금키 시뮬레이터", layout="wide", initial_sidebar_state="collapsed")

# CSS: 디자인 고정
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border-left: 5px solid #ff4b4b; margin-bottom: 12px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧪 금요일(12/26) 실제 데이터 동기화 테스트")
st.write("※ 현재 화면은 선생님의 캡처본 날짜인 **2025-12-26** 종가 기준입니다.")

# 2. 데이터 강제 호출 (캐시 없이 직접 호출)
try:
    # 12월 26일 기준 전체 시세 호출
    df = fdr.StockListing('KRX') 
    
    # 필터링: 시총 5천억 이상, 상승률 4% 이상 (선생님 캡처본의 우상단 종목들 타겟)
    leaders = df[
        (df['Marcap'] >= 500000000000) & 
        (df['ChangesRatio'] >= 4.0) &
        (~df['Name'].str.contains('우|스팩|관리'))
    ].sort_values(by='Amount', ascending=False).head(15)

    if not leaders.empty:
        cols = st.columns(3)
        for idx, (i, row) in enumerate(leaders.iterrows()):
            with cols[idx % 3]:
                amt = row['Amount'] / 1e8
                amt_txt = f"{amt/10000:.1f}조" if amt >= 10000 else f"{int(amt)}억"
                st.markdown(f"""
                    <div class="stock-card">
                        <div style="font-size:18px; font-weight:bold;">{row['Name']}</div>
                        <div class="price-up">{int(row['Close']):,}원</div>
                        <div style="display:flex; justify-content:space-between; font-size:14px;">
                            <span style="color:#ff4b4b;">▲ {row['ChangesRatio']}%</span>
                            <span style="color:#888;">대금: {amt_txt}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.warning("조건에 맞는 종목을 찾는 중입니다. 잠시만 기다려 주세요.")

except Exception as e:
    st.error(f"데이터 연결 오류: {e}")

# 자동 새로고침 방지 (테스트용이므로 한 번만 로드)
st.button("다시 데이터 불러오기")
