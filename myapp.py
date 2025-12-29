import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide")
now = datetime.now(timezone(timedelta(hours=9)))

# 2. 데이터 수집 엔진 (데이터 누락 방지 로직)
@st.cache_data(ttl=1) # 1초 주기로 강제 갱신
def get_safe_data():
    try:
        # [핵심] KRX 데이터를 먼저 긁고, 값이 비어있는지 즉시 체크
        df = fdr.StockListing('KRX')
        
        # 만약 Close(종가)나 Amount(대금)가 비어있다면, 다른 서버 경로 시도
        if df['Close'].sum() == 0:
            df = fdr.StockListing('KOSPI') # 코스피만이라도 우선 확보
            
        # 등락률 컬럼 이름 자동 매칭 (에러 방지)
        target_col = 'Chg'
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns:
                target_col = col
                break
        df['Rate_Fix'] = df[target_col]
        return df
    except:
        return pd.DataFrame()

# 디자인 설정
st.markdown("""
    <style>
    .stock-box { background-color: #161b22; padding: 15px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }
    .price-red { color: #ff4b4b; font-size: 22px; font-weight: bold; }
    .amt-gray { color: #888888; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

st.title(f"🚀 황금키 실시간 상황판 ({now.strftime('%H:%M:%S')})")

# 데이터 가져오기
main_df = get_safe_data()

if main_df.empty or main_df['Close'].sum() == 0:
    st.error("🚨 현재 거래소 서버 응답이 지연되고 있습니다. 2초 후 강제 재접속합니다.")
    time.sleep(2)
    st.rerun()

# 3. 거래대금 상위 12개 화면 배치
st.subheader("🔥 실시간 거래대금 폭발 종목 (Top 12)")
top_stocks = main_df.sort_values('Amount', ascending=False).head(12)

cols = st.columns(4)
for i in range(12):
    with cols[i % 4]:
        row = top_stocks.iloc[i]
        # 금액이 0일 경우 '데이터 수신 중' 표시
        price = f"{int(row['Close']):,}원" if row['Close'] > 0 else "수신 중..."
        amt = f"{int(row['Amount']/1e8):,}억" if row['Amount'] > 0 else "집계 중..."
        rate = f"{row['Rate_Fix']:+.2f}%" if 'Rate_Fix' in row else ""

        st.markdown(f"""
            <div class="stock-box">
                <div style="font-size:18px; color:white;"><b>{row['Name']}</b></div>
                <div class="price-red">{price}</div>
                <div style="color:#ff4b4b;">{rate}</div>
                <div class="amt-gray">거래대금: {amt}</div>
            </div>
        """, unsafe_allow_html=True)

# 2초마다 화면 강제 갱신
time.sleep(2)
st.rerun()
