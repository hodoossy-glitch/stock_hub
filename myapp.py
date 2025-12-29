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
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border: 1px solid #30363d; text-align: center; }
    .price-val { font-size: 24px; font-weight: bold; }
    .up { color: #ff4b4b; } .down { color: #0088ff; }
    .amt-label { color: #8b949e; font-size: 13px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 정밀 데이터 엔진 (형변환 오류 해결)
@st.cache_data(ttl=1)
def fetch_exact_data():
    try:
        # 전종목 데이터 호출
        df = fdr.StockListing('KRX')
        
        # [정밀 보정] 문자열로 들어온 데이터를 강제로 숫자로 변환 (SK하이닉스 1조대 응답용)
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce').fillna(0)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        # 등락률 계산 보정
        if 'ChangesRatio' in df.columns:
            df['Rate_Fix'] = pd.to_numeric(df['ChangesRatio'], errors='coerce').fillna(0.0)
        else:
            df['Rate_Fix'] = 0.0
            
        return df
    except:
        return pd.DataFrame()

# 데이터 로드
live_df = fetch_exact_data()

st.title(f"📡 황금키 실시간 정밀 상황판 ({now.strftime('%H:%M:%S')})")

if not live_df.empty:
    # 3. 거래대금 상위 12개 정밀 배치
    st.subheader("🔥 현재 시장 거래대금 TOP 12 (실시간 집계)")
    top_12 = live_df.sort_values('Amount', ascending=False).head(12)
    
    rows = [top_12.iloc[i:i+4] for i in range(0, 12, 4)]
    for row_df in rows:
        cols = st.columns(4)
        for i, (idx, row) in enumerate(row_df.iterrows()):
            with cols[i]:
                # 등락률에 따른 색상 결정
                color_class = "up" if row['Rate_Fix'] > 0 else "down" if row['Rate_Fix'] < 0 else ""
                sign = "+" if row['Rate_Fix'] > 0 else ""
                
                # 금액 단위 변환 (조 단위 대응)
                amt_val = row['Amount']
                if amt_val >= 1e12:
                    amt_str = f"{amt_val/1e12:.2f}조"
                else:
                    amt_str = f"{int(amt_val/1e8):,}억"

                st.markdown(f"""
                    <div class="stock-card">
                        <div style="font-size:18px; margin-bottom:8px;">{row['Name']}</div>
                        <div class="price-val {color_class}">{int(row['Close']):,}원</div>
                        <div class="{color_class}" style="font-size:16px;">{sign}{row['Rate_Fix']:.2f}%</div>
                        <div class="amt-label">거래대금: <b>{amt_str}</b></div>
                    </div>
                """, unsafe_allow_html=True)
else:
    st.warning("🔄 데이터 동기화 중입니다. 잠시만 기다려주세요.")

# 4. 강제 갱신 주기를 1초로 단축
time.sleep(1)
st.rerun()
