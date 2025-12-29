import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 다크 테마 유지
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

# 2. 강철 데이터 엔진 (KeyError 방어형)
@st.cache_data(ttl=1)
def fetch_robust_data():
    try:
        df = fdr.StockListing('KRX')
        # 데이터가 숫자가 아닐 경우를 대비한 강제 변환
        df['Close'] = pd.to_numeric(df['Close'], errors='coerce').fillna(0)
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        
        # [에러 해결] Rate_Val 칸이 없으면 0으로 가득 채운 칸을 즉시 생성
        if 'ChangesRatio' in df.columns:
            df['Rate_Val'] = pd.to_numeric(df['ChangesRatio'], errors='coerce').fillna(0.0)
        else:
            df['Rate_Val'] = 0.0 # 에러 방지용 기본값
            
        return df
    except:
        return pd.DataFrame()

live_df = fetch_robust_data()

# 3. 탭 다시 살리기 (사라졌던 탭 복구)
tab1, tab2 = st.tabs(["🔥 실시간 주도주", "💰 거래대금 상위"])

with tab1:
    st.title(f"📡 황금키 수급 상황판 ({now.strftime('%H:%M:%S')})")
    
    if not live_df.empty:
        # 주도섹터 키워드 매칭
        for s_name in ["반도체", "로봇", "바이오"]:
            with st.expander(f"📂 {s_name} 실시간 수급", expanded=True):
                s_df = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(4)
                cols = st.columns(4)
                for i in range(len(s_df)):
                    row = s_df.iloc[i]
                    # [KeyError 방어] 안전하게 데이터 가져오기
                    rate = row.get('Rate_Val', 0.0)
                    color = "up" if rate > 0 else "down" if rate < 0 else ""
                    amt = row['Amount']
                    amt_str = f"{amt/1e12:.2f}조" if amt >= 1e12 else f"{int(amt/1e8):,}억"
                    
                    with cols[i]:
                        st.markdown(f"""
                            <div class="stock-card">
                                <div style="font-size:16px;">{row['Name']}</div>
                                <div class="price-val {color}">{int(row['Close']):,}원</div>
                                <div class="{color}">{rate:+.2f}%</div>
                                <div class="amt-label">대금: {amt_str}</div>
                            </div>
                        """, unsafe_allow_html=True)
    else:
        st.warning("데이터 연결 대기 중...")

with tab2:
    st.subheader("💰 전 종목 거래대금 TOP 12")
    if not live_df.empty:
        top_12 = live_df.sort_values('Amount', ascending=False).head(12)
        grid_rows = [top_12.iloc[i:i+4] for i in range(0, 12, 4)]
        for r_df in grid_rows:
            grid_cols = st.columns(4)
            for i, (idx, row) in enumerate(r_df.iterrows()):
                rate = row.get('Rate_Val
