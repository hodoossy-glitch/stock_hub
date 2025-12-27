import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime

st.set_page_config(page_title="황금키 프로", layout="wide")
st.title("🔑 황금키 프로: 주도주 & 종배 스캐너")

# 사이드바에서 모드 선택
mode = st.sidebar.radio("🔍 스캔 모드 선택", ["실시간 주도주 스캔", "종가배팅(종배) 스캔"])

if mode == "실시간 주도주 스캔":
    st.subheader("🚀 실시간 주도주 (거래대금 + 이평선)")
    desc = "시총 5천억 이상, 5일/20일선 위에서 돈이 몰리는 종목을 찾습니다."
else:
    st.subheader("📈 종가배팅 (고가권 유지 + 거래폭발)")
    desc = "오늘 힘이 가장 강했던 종목 중, 내일 갭 상승 확률이 높은 종목을 찾습니다."

st.info(desc)

if st.button('🔎 스캔 시작'):
    with st.spinner("데이터 분석 중..."):
        try:
            df_krx = fdr.StockListing('KRX')
            # 기본 필터: 시총 5천억 이상
            df_krx = df_krx[df_krx['Marcap'] >= 500000000000]
            
            results = []
            # 상위 100개 종목 정밀 분석
            for _, row in df_krx.head(100).iterrows():
                try:
                    df = fdr.DataReader(row['Code'], '2025-11-01')
                    if len(df) < 20: continue
                    
                    last = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    # 공통 지표 계산
                    ma5 = df['Close'].rolling(5).mean().iloc[-1]
                    ma20 = df['Close'].rolling(20).mean().iloc[-1]
                    high_price = last['High']
                    curr_price = last['Close']
                    amt_billion = int(last['Amount'] / 1e8)
                    
                    if mode == "실시간 주도주 스캔":
                        # 조건: 5일선 & 20일선 위 + 거래대금 300억 이상
                        if curr_price >= ma5 and curr_price > ma20 and amt_billion >= 300:
                            results.append({'종목명': row['Name'], '현재가': f"{int(curr_price):,}", '거래대금(억)': amt_billion, '상태': '추세강세'})
                    
                    else: # 종가배팅 모드
                        # 조건: 당일 고가 대비 -2% 이내 유지 (힘이 안 빠짐) + 전일 대비 거래량 증가
                        high_diff = (high_price - curr_price) / high_price
                        vol_ratio = last['Volume'] / prev['Volume']
                        
                        if high_diff <= 0.02 and vol_ratio > 1.2 and amt_billion >= 500:
                            results.append({'종목명': row['Name'], '현재가': f"{int(curr_price):,}", '거래대금(억)': amt_billion, '고가대비': f"-{high_diff*100:.1f}%", '상태': '종배유망'})
                except: continue
            
            if results:
                st.write(f"### ✅ 검색 결과: {len(results)}건")
                st.table(pd.DataFrame(results))
            else:
                st.warning("조건에 부합하는 종목이 없습니다.")
        except Exception as e:
            st.error(f"오류 발생: {e}")
