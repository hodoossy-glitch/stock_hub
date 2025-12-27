import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="황금키 프로", layout="wide")
st.title("🔑 황금키 프로: 주도주 대시보드")
st.markdown("### [시총 5천억↑ / 20일선 위 / 5일선 사수 / 정배열]")

if st.button('🔄 데이터 새로고침'):
    st.rerun()

try:
    if os.path.exists('stock_scanner_result.html'):
        df = pd.read_html('stock_scanner_result.html')[0]
        
        # 요약 카드
        c1, c2, c3 = st.columns(3)
        c1.metric("포착 종목수", f"{len(df)}개")
        c2.metric("최고 거래대금", f"{df['거래대금(억)'].max()}억")
        c3.metric("최대 시총", f"{df['시가총액(억)'].max()}억")
        
        # 결과 표
        st.dataframe(df, use_container_width=True, height=500)
    else:
        st.warning("먼저 'python mystock.py'를 실행해 주세요.")
except Exception as e:
    st.error(f"오류 발생: {e}")