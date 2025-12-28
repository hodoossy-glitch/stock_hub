import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border-left: 5px solid #ff4b4b; margin-bottom: 12px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 황금키 실시간 주도주 레이더")

# 2. 오류 방어형 데이터 엔진
def get_safe_data():
    try:
        # 서버에 데이터를 요청합니다.
        df = fdr.StockListing('KRX')
        
        # 데이터가 정상적으로 왔는지 확인
        if df is not None and not df.empty:
            # 시총 5,000억 이상 + 4% 이상 상승주 필터링
            leaders = df[
                (df['Marcap'] >= 500000000000) & 
                (df['ChangesRatio'] >= 4.0)
            ].sort_values(by='Amount', ascending=False).head(15)
            return leaders
        return None
    except Exception as e:
        # 서버 점검 중일 때 발생하는 오류를 잡아냅니다.
        return "CHECKING"

# 3. 화면 출력 로직
result = get_safe_data()

if isinstance(result, pd.DataFrame) and not result.empty:
    cols = st.columns(3)
    for idx, (i, row) in enumerate(result.iterrows()):
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
elif result == "CHECKING":
    st.warning("⚠️ 현재 거래소 데이터 서버가 정기 점검 중입니다 (일요일).")
    st.info("내일(월요일) 오전 9시, 장 시작과 동시에 실시간 시세가 자동으로 활성화됩니다.")
else:
    st.info("조건에 맞는 주도주를 탐색 중입니다.")

# 4. 자동 새로고침
time.sleep(60)
st.rerun()
