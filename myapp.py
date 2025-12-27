import streamlit as st
import pandas as pd
import FinanceDataReader as fdr

st.set_page_config(page_title="황금키 프로", layout="wide")
st.title("🔑 황금키 프로: 실시간 주도주 스캐너")

# 이 버튼이 화면에 보여야 합니다!
if st.button('🚀 실시간 주도주 스캔 시작'):
    with st.spinner("5일선을 지키는 강력한 종목 분석 중..."):
        df_krx = fdr.StockListing('KRX')
        # 시총 5천억 이상 종목만 필터링
        df_krx = df_krx[df_krx['Marcap'] >= 500000000000]
        
        results = []
        # 속도를 위해 상위 100개만 먼저 스캔
        for _, row in df_krx.head(100).iterrows():
            try:
                # 최근 데이터 가져오기
                df = fdr.DataReader(row['Code'], '2025-11-01')
                df['MA5'] = df['Close'].rolling(5).mean()
                df['MA20'] = df['Close'].rolling(20).mean()
                last = df.iloc[-1]
                
                # 5일선 사수 & 20일선 위 조건
                if last['Close'] >= last['MA5'] and last['Close'] > last['MA20']:
                    results.append({
                        '종목명': row['Name'], 
                        '현재가': f"{int(last['Close']):,}", 
                        '거래대금(억)': int(last['Amount']/1e8)
                    })
            except: continue
        
        if results:
            st.write(f"### ✅ 스캔 완료: {len(results)}개 종목 발견")
            st.table(pd.DataFrame(results))
        else:
            st.warning("조건에 맞는 종목이 없습니다.")
