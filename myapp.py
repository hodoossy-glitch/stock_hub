import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="황금키 프로: 올인원", layout="wide")

# 🔄 자동 새로고침 설정 (1분마다 실행, 최대 100번)
count = st_autorefresh(interval=60000, limit=100, key="fscounter")

st.title("🔑 황금키 프로: 실시간 자동 스캐너")
st.caption(f"최근 업데이트 시간: {datetime.now().strftime('%H:%M:%S')} (1분마다 자동 갱신)")

# 사이드바 메뉴
with st.sidebar:
    st.header("🎯 스캔 조건")
    mode = st.selectbox("검색 모드", ["실시간 주도주", "신고가 돌파", "신규상장주 스캔", "거래급증 종배"])
    min_marcap = st.number_input("최소 시총(억)", value=3000)

# 메인 설명
st.info(f"선택 모드: {mode} | 시총 {min_marcap}억 이상 종목 자동 분석 중")

# 스캔 로직 (자동 새로고침 시에도 실행되도록 바로 시작)
try:
    df_krx = fdr.StockListing('KRX')
    df_krx = df_krx[df_krx['Marcap'] >= (min_marcap * 100000000)]
    
    results = []
    # 분석 범위를 100개로 최적화 (자동 갱신 속도를 위해)
    for _, row in df_krx.head(100).iterrows():
        try:
            df = fdr.DataReader(row['Code'], (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d'))
            if len(df) < 5: continue
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            amt_billion = int(last['Amount'] / 1e8)
            
            if mode == "실시간 주도주":
                ma5 = df['Close'].rolling(5).mean().iloc[-1]
                if last['Close'] >= ma5 and amt_billion >= 300:
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': amt_billion, '특징': '5일선 사수'})

            elif mode == "신고가 돌파":
                max_60 = df['High'].iloc[:-1].max()
                if last['Close'] >= max_60:
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': amt_billion, '특징': '60일 신고가'})

            elif mode == "신규상장주 스캔":
                listing_date = pd.to_datetime(row['ListingDate'])
                if listing_date > (datetime.now() - timedelta(days=365)):
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '상장일': listing_date.strftime('%Y-%m-%d'), '특징': '신규상장'})

            elif mode == "거래급증 종배":
                vol_ratio = last['Volume'] / prev['Volume']
                if vol_ratio >= 2.0 and amt_billion >= 500:
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': amt_billion, '거래폭발': f"{vol_ratio:.1f}배"})
        except: continue
    
    if results:
        st.success(f"✅ {mode} 검색 결과 (총 {len(results)}개)")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.warning("현재 조건에 부합하는 종목이 없습니다. 잠시 후 자동으로 다시 스캔합니다.")

except Exception as e:
    st.error(f"데이터를 가져오는 중 오류 발생: {e}")
