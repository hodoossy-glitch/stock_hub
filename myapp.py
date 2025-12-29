import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 기본 설정
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide")
now = datetime.now(timezone(timedelta(hours=9)))

# 디자인 스타일 (최소화)
st.markdown("""
    <style>
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 10px; border: 1px solid #30363d; text-align: center; margin-bottom: 10px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 18px; }
    .amt-label { color: #888888; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 수집 함수 (가장 안전한 방식)
@st.cache_data(ttl=2)
def get_data():
    try:
        # 전종목 시세 긁기
        df = fdr.StockListing('KRX')
        # 지수 데이터 긁기
        ks = fdr.DataReader('KS11').tail(1)
        kq = fdr.DataReader('KQ11').tail(1)
        return df, ks, kq
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

st.title(f"📡 황금키 실시간 상황판 ({now.strftime('%H:%M:%S')})")

df, ks, kq = get_data()

# 3. 상단 지수 표시
c1, c2 = st.columns(2)
with c1:
    if not ks.empty:
        st.metric("KOSPI", f"{ks['Close'].iloc[-1]:,.2f}")
with c2:
    if not kq.empty:
        st.metric("KOSDAQ", f"{kq['Close'].iloc[-1]:,.2f}")

# 4. 주도주 포착 (거래대금 순)
st.divider()
st.subheader("🔥 실시간 거래대금 상위 종목")

if not df.empty:
    # 거래대금(Amount) 상위 12개 추출
    top_df = df.sort_values('Amount', ascending=False).head(12)
    
    cols = st.columns(4)
    for i in range(12):
        with cols[i % 4]:
            row = top_df.iloc[i]
            amt = f"{int(row['Amount']/1e8):,}억"
            st.markdown(f"""
                <div class="stock-card">
                    <div style="font-weight:bold; font-size:16px;">{row['Name']}</div>
                    <div class="price-up">{int(row['Close']):,}원</div>
                    <div class="amt-label">대금: {amt}</div>
                </div>
            """, unsafe_allow_html=True)
else:
    st.error("데이터를 긁어오지 못했습니다. 잠시 후 자동 재시도합니다.")

# 2초마다 강제 새로고침
time.sleep(2)
st.rerun()
