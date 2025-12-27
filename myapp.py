import streamlit as st
import pandas as pd
import FinanceDataReader as fdr

st.set_page_config(page_title="황금키 프로", layout="wide")
st.title("🔑 황금키 프로: 실시간 주도주 스캐너")

# 버튼이 있어야 실행됩니다!
if st.button('🚀 실시간 주도주 스캔 시작'):
    with st.spinner("데이터 분석 중..."):
        # 12월 26일 금요일 데이터 기준 테스트
        target_date = '2025-12-26' 
        df_krx = fdr.StockListing('KRX')
        df_krx = df_krx[df_krx['Marcap'] >= 500000000000] # 시총 5천억 이상
        
        results = []
        for _, row in df_krx.head(50).iterrows(): # 우선 50개만 테스트
            try:
                df = fdr.DataReader(row['Code'], '2025-11-01', target_date)
                df['MA5'] = df['Close'].rolling(5).mean()
                df['MA20'] = df['Close'].rolling(20).mean()
                last = df.iloc[-1]
                # 5일선 위 & 20일선 위 조건
                if last['Close'] >= last['MA5'] and last['Close'] > last['MA20']:
                    results.append({'종목명': row['Name'], '현재가': int(last['Close']), '거래대금(억)': int(last['Amount']/1e8)})
            except: continue
        
        if results:
            st.dataframe(pd.DataFrame(results), use_container_width=True)
        else:
            st.warning("조건에 맞는 종목이 없습니다. 잠시 후 다시 시도하세요.")
