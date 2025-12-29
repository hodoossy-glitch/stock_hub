import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 다크 테마 고정
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border: 1px solid #30363d; text-align: center; min-height: 140px; }
    .price-val { font-size: 24px; font-weight: bold; margin: 5px 0; }
    .up { color: #ff4b4b; } .down { color: #0088ff; }
    .amt-label { color: #8b949e; font-size: 13px; margin-top: 5px; border-top: 1px solid #30363d; padding-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 정밀 데이터 엔진 (SK하이닉스 1.8조 대응)
@st.cache_data(ttl=1)
def fetch_exact_market_data():
    try:
        # 전종목 데이터 호출
        df = fdr.StockListing('KRX')
        
        # [핵심] 글자로 인식된 데이터를 강제로 숫자로 변환
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce').fillna(0)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        # 등락률 컬럼 정밀 매칭
        if 'ChangesRatio' in df.columns:
            df['Rate_Val'] = pd.to_numeric(df['ChangesRatio'], errors='coerce').fillna(0.0)
        else:
            df['Rate_Val'] = 0.0
            
        return df
    except:
        return pd.DataFrame()

# 데이터 호출
live_df = fetch_exact_market_data()

st.title(f"📡 황금키 실시간 수급 상황판 ({now.strftime('%H:%M:%S')})")

if not live_df.empty:
    # 거래대금 상위 정렬
    top_12 = live_df.sort_values('Amount', ascending=False).head(12)
    
    # 4개씩 격자 배치
    rows = [top_12.iloc[i:i+4] for i in range(0, 12, 4)]
    for row_df in rows:
        cols = st.columns(4)
        for i, (idx, row) in enumerate(row_df.iterrows()):
            with cols[i]:
                # 등락률 색상 및 기호
                rate = row['Rate_Val']
                color_class = "up" if rate > 0 else "down" if rate < 0 else ""
                sign = "+" if rate > 0 else ""
                
                # 거래대금 단위 변환 (SK하이닉스 1.8조 대응)
                amt = row['Amount']
                if amt >= 1e12:
                    amt_display = f"{amt/1e12:.2f}조"
                else:
                    amt_display = f"{int(amt/1e8):,}억"

                st.markdown(f"""
                    <div class="stock-card">
                        <div style="font-size:18px; color:#c9d1d9;">{row['Name']}</div>
                        <div class="price-val {color_class}">{int(row['Close']):,}원</div>
                        <div class="{color_class}" style="font-size:16px; font-weight:bold;">{sign}{rate:.2f}%</div>
                        <div class="amt-label">거래대금: <span style="color:white;">{amt_display}</span></div>
                    </div>
                """, unsafe_allow_html=True)
else:
    st.error("🚨 서버 연결이 지연되고 있습니다. 1초 후 강제 재시도합니다.")
    time.sleep(1)
    st.rerun()

# 1초마다 자동 새로고침
time.sleep(1)
st.rerun()
