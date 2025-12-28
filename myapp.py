import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 실시간 레이더", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border-left: 5px solid #ff4b4b; margin-bottom: 12px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 황금키 실시간 주도주 레이더")

# 2. 오류 발생 시 '빈 데이터' 대신 '안내 메시지'를 돌려주는 함수
def get_data_safely():
    try:
        # 데이터 서버 호출 시도
        df = fdr.StockListing('KRX')
        if df is not None and not df.empty:
            # 시총 5,000억 이상 + 4% 이상 상승주 필터링
            leaders = df[(df['Marcap'] >= 500000000000) & (df['ChangesRatio'] >= 4.0)]
            return leaders.sort_values(by='Amount', ascending=False).head(15)
        return pd.DataFrame() # 데이터가 비어있으면 빈 표 반환
    except Exception:
        # 서버 점검 중일 때 발생하는 모든 오류를 무시함
        return "CHECKING"

# 3. 화면 표시
result = get_data_safely()

if isinstance(result, pd.DataFrame):
    if not result.empty:
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
    else:
        st.info("⌛ 현재 조건에 맞는 주도주를 탐색 중입니다.")
else:
    # 서버 오류(일요일 점검) 시 출력되는 메시지
    st.warning("⚠️ 데이터 서버(KRX) 점검 중으로 실시간 조회가 지연되고 있습니다.")
    st.info("내일(월요일) 오전 9시, 장 시작과 함께 자동으로 가격이 동기화됩니다.")

# 자동 새로고침
time.sleep(60)
st.rerun()
