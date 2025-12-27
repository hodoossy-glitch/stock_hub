import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from streamlit_autorefresh import st_autorefresh

# 1분(60,000밀리초)마다 자동으로 앱을 다시 실행합니다.
# 100번까지 새로고침하고 멈추도록 설정 (숫자는 조절 가능)
count = st_autorefresh(interval=60000, limit=100, key="fscounter")

st.set_page_config(page_title="황금키 프로", layout="wide")
st.title("🔑 황금키 프로: 주도주 & 종배 스캐너")

# 1. 왼쪽 사이드바 메뉴 만들기
with st.sidebar:
    st.header("🔍 스캔 설정")
    mode = st.radio("모드를 선택하세요", ["실시간 주도주", "종가배팅(종배)"])
    st.info(f"현재 모드: {mode}")

# 2. 메인 화면 설명
if mode == "실시간 주도주":
    st.markdown("### 🚀 실시간 주도주 모드")
    st.write("시총 5천억 이상, 5일/20일선 위에서 돈이 몰리는 종목을 찾습니다.")
else:
    st.markdown("### 📈 종가배팅(종배) 모드")
    st.write("당일 고가권 유지 + 거래량 폭발! 내일 아침 갭 상승 유망주를 찾습니다.")

# 3. 스캔 실행 버튼
if st.button(f'🔎 {mode} 스캔 시작'):
    with st.spinner("데이터 분석 중... 잠시만 기다려주세요."):
        try:
            df_krx = fdr.StockListing('KRX')
            df_krx = df_krx[df_krx['Marcap'] >= 500000000000] # 시총 5천억 이상만
            
            results = []
            # 상위 100개 종목 분석 (속도를 위해)
            for _, row in df_krx.head(100).iterrows():
                try:
                    df = fdr.DataReader(row['Code'], '2025-11-01')
                    if len(df) < 20: continue
                    
                    last = df.iloc[-1]
                    prev = df.iloc[-2]
                    
                    # 공통 지표
                    ma5 = df['Close'].rolling(5).mean().iloc[-1]
                    ma20 = df['Close'].rolling(20).mean().iloc[-1]
                    amt_billion = int(last['Amount'] / 1e8)
                    
                    if mode == "실시간 주도주":
                        # 조건: 5일선 & 20일선 위 + 거래대금 300억 이상
                        if last['Close'] >= ma5 and last['Close'] > ma20 and amt_billion >= 300:
                            results.append({'종목명': row['Name'], '현재가': f"{int(last['Close']):,}", '거래대금(억)': amt_billion})
                    
                    else: # 종가배팅
                        # 조건: 당일 고가 대비 -2% 이내 + 전일대비 거래량 120% 증가 + 거래대금 500억 이상
                        high_diff = (last['High'] - last['Close']) / last['High']
                        vol_ratio = last['Volume'] / prev['Volume']
                        if high_diff <= 0.02 and vol_ratio > 1.2 and amt_billion >= 500:
                            results.append({'종목명': row['Name'], '현재가': f"{int(last['Close']):,}", '거래대금(억)': amt_billion, '고가대비': f"-{high_diff*100:.1f}%"})
                except: continue
            
            if results:
                st.success(f"총 {len(results)}개의 종목을 찾았습니다!")
                st.table(pd.DataFrame(results))
            else:
                st.warning("조건에 맞는 종목이 현재 없습니다.")
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")

