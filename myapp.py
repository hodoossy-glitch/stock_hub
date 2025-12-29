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
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border: 1px solid #30363d; text-align: center; min-height: 150px; }
    .price-val { font-size: 26px; font-weight: bold; margin: 5px 0; }
    .up { color: #ff4b4b; } .down { color: #0088ff; }
    .amt-label { color: #8b949e; font-size: 14px; margin-top: 10px; border-top: 1px solid #30363d; padding-top: 8px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 정밀 데이터 수집 엔진 (SK하이닉스 1.8조 오차 수정)
@st.cache_data(ttl=0) # 캐시를 0으로 설정하여 무조건 새로 긁어옵니다.
def fetch_exact_market_data():
    try:
        # 전종목 데이터 호출
        df = fdr.StockListing('KRX')
        
        # [정밀 수술] 문자열 데이터를 강제로 숫자로 변환 (1.8조원 대응)
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce').fillna(0)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        # 등락률 데이터 강제 추출
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns:
                df['Rate_Val'] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
                break
        return df
    except:
        return pd.DataFrame()

# 데이터 로드
live_df = fetch_exact_market_data()

st.title(f"📡 황금키 실시간 수급 상황판 ({now.strftime('%H:%M:%S')})")

if not live_df.empty:
    # 거래대금 상위 12개 정렬 (SK하이닉스가 1위에 와야 정상입니다)
    top_12 = live_df.sort_values('Amount', ascending=False).head(12)
    
    # 4개씩 격자 배치
    rows = [top_12.iloc[i:i+4] for i in range(0, 12, 4)]
    for row_df in rows:
        cols = st.columns(4)
        for i, (idx, row) in enumerate(row_df.iterrows()):
            with cols[i]:
                rate = row['Rate_Val']
                color_class = "up" if rate > 0 else "down" if rate < 0 else ""
                sign = "+" if rate > 0 else ""
                
                # [단위 보정] 1조 이상은 '조', 이하는 '억'으로 표시
                amt = row['Amount']
                amt_str = f"{amt/1e12:.2f}조" if amt >= 1e12 else f"{int(amt/1e8):,}억"

                st.markdown(f"""
                    <div class="stock-card">
                        <div style="font-size:18px; color:#c9d1d9;"><b>{row['Name']}</b></div>
                        <div class="price-val {color_class}">{int(row['Close']):,}원</div>
                        <div class="{color_class}" style="font-size:18px; font-weight:bold;">{sign}{rate:.2f}%</div>
                        <div class="amt-label">실시간 대금: <span style="color:white;">{amt_str}</span></div>
                    </div>
                """, unsafe_allow_html=True)
else:
    st.error("🚨 서버 연결이 지연되고 있습니다. 1초 후 강제 재시도합니다.")

# 1초마다 자동 새로고침
time.sleep(1)
st.rerun()
