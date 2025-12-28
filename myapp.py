import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 실시간 레이더", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

# CSS 디자인
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 5px solid #ff4b4b; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    .m-title { font-size: 20px; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<div class='m-title'>📡 실시간 주도주 레이더 (정밀 모드)</div>", unsafe_allow_html=True)
st.caption(f"최종 데이터 동기화: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# 2. 정밀 데이터 엔진 (리스트가 아닌 개별 시세 확인)
@st.cache_data(ttl=60)
def fetch_exact_data():
    try:
        # 먼저 시총 상위 리스트를 가져옵니다.
        df_list = fdr.StockListing('KRX')
        # 시총 5,000억 이상 상위 30개만 추려서 개별 정밀 검사
        target_list = df_list[df_list['Marcap'] >= 500000000000].head(30)
        
        results = []
        for _, row in target_list.iterrows():
            try:
                # 데이터리더로 해당 종목의 최근 3일치 시세를 직접 가져옵니다 (가장 확실한 방법)
                df_detail = fdr.DataReader(row['Code'], (now - timedelta(days=7)).strftime('%Y-%m-%d'))
                if df_detail.empty: continue
                
                last_price = int(df_detail.iloc[-1]['Close'])
                prev_price = int(df_detail.iloc[-2]['Close'])
                chg_ratio = ((last_price - prev_price) / prev_price) * 100
                amount = int(df_detail.iloc[-1]['Amount'] / 1e8) # 억 단위

                # 4% 이상 상승 종목만 선별
                if chg_ratio >= 4.0:
                    results.append({
                        'Name': row['Name'],
                        'Close': last_price,
                        'ChangesRatio': chg_ratio,
                        'Amount': amount,
                        'Sector': row['Sector']
                    })
            except: continue
        
        return pd.DataFrame(results).sort_values(by='Amount', ascending=False)
    except:
        return pd.DataFrame()

# 3. 화면 출력
leaders_df = fetch_exact_data()

if not leaders_df.empty:
    for _, row in leaders_df.iterrows():
        amt_display = f"{row['Amount']/10000:.1f}조" if row['Amount'] >= 10000 else f"{row['Amount']}억"
        
        st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:18px; font-weight:bold;">{row['Name']}</div>
                        <div style="font-size:12px; color:#888;">{row['Sector'] if row['Sector'] else '주도주'}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="price-up">{row['Close']:,}원</div>
                        <div style="font-size:14px; color:#ff4b4b;">{row['ChangesRatio']:+.2f}% <span style="color:#888; margin-left:5px;">{amt_display}</span></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("현재 시장에서 4% 이상 상승 중인 우량주를 정밀 탐색 중입니다.")

st.divider()
time.sleep(60)
st.rerun()
