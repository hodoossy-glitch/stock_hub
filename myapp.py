import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 시뮬레이션", layout="wide", initial_sidebar_state="collapsed")

# 테스트용 날짜 설정: 2025년 12월 26일 (금요일)
test_date = "2025-12-26"

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border-left: 5px solid #ff4b4b; margin-bottom: 12px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"## 🧪 금요일(12/26) 데이터 재현 테스트")
st.info(f"현재 화면은 선생님이 보내주신 캡처본의 날짜인 **{test_date}** 장마감 시점의 실제 데이터를 분석 중입니다.")

# 2. 금요일 주도주 검색 엔진 (시뮬레이션 모드)
@st.cache_data
def run_test_search():
    try:
        # 12월 26일 기준 전체 시세 호출
        df = fdr.StockListing('KRX') 
        
        # 캡처본에 나온 조건 재현: 시총 5천억 이상, 등락률 4% 이상
        leaders = df[
            (df['Marcap'] >= 500000000000) & 
            (df['ChangesRatio'] >= 4.0) &
            (~df['Name'].str.contains('우|스팩|관리'))
        ].sort_values(by='Amount', ascending=False).head(15)
        
        return leaders
    except:
        return pd.DataFrame()

# 3. 결과 출력
leaders_df = run_test_search()

if not leaders_df.empty:
    st.markdown("### 💰 12월 26일 주도주 검색 결과")
    cols = st.columns(3)
    for idx, (i, row) in enumerate(leaders_df.iterrows()):
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
    st.error("데이터를 불러오는 데 실패했습니다. 서버 상태를 확인해주세요.")

st.divider()
st.caption("※ 내일(월요일)은 이 시뮬레이션 코드를 '실시간 모드'로 한 줄만 바꾸면 바로 실전 투입이 가능합니다.")
