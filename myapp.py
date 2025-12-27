import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 1. 페이지 설정 및 캐시 기능 정의
st.set_page_config(page_title="황금키 초고속 레이더", layout="wide")

# 종목 리스트를 불러올 때 캐시를 사용하여 속도 향상
@st.cache_data(ttl=3600) # 1시간 동안 리스트 보관
def get_stock_list():
    return fdr.StockListing('KRX')

st.title("⚡ 황금키 프로: 초고속 통합 전광판")
st.caption(f"최근 분석: {datetime.now().strftime('%H:%M:%S')} (데이터 최적화 모드 작동 중)")

with st.sidebar:
    st.header("⚙️ 고속 필터")
    min_marcap = st.number_input("최소 시총(억)", value=3000)

try:
    with st.spinner("🚀 엔진 가동 중... (데이터 최적화 중)"):
        df_krx = get_stock_list()
        # 기본 필터링 (우선순위: 시총 상위)
        df_base = df_krx[
            (df_krx['Marcap'] >= (min_marcap * 100000000)) & 
            (~df_krx['Name'].str.contains('우|스팩|관리|투자유의|정지'))
        ].head(80) # 분석 대상을 80개로 압축하여 속도 극대화

        s1, s2, s3, s4, s5, s6, s7, s8 = [], [], [], [], [], [], [], []

        for _, row in df_base.iterrows():
            try:
                # 데이터 호출 기간을 최소화 (20일치만 호출하여 속도 개선)
                df = fdr.DataReader(row['Code'], (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
                if len(df) < 20: continue
                
                last, prev = df.iloc[-1], df.iloc[-2]
                curr_p, amt_b = int(last['Close']), int(last['Amount'] / 1e8)
                chg = ((curr_p - prev['Close']) / prev['Close']) * 100
                
                # 기술 지표 계산 최적화
                ma5 = df['Close'].tail(5).mean()
                ma20 = df['Close'].tail(20).mean()

                if ma5 < ma20: continue # 정배열 아니면 즉시 패스 (연산 절약)

                # 전략별 분류
                if chg >= 7 and amt_b >= 500: s1.append({'종목': row['Name'], '등락': f"{chg:+.1f}%", '대금': f"{amt_b}억"})
                if 2 <= chg <= 5 and amt_b >= 300: s2.append({'종목': row['Name'], '등락': f"{chg:+.1f}%"})
                if amt_b >= 1000: s3.append({'종목': row['Name'], '대금': f"{amt_b}억"})
                if curr_p >= df['High'].max(): s4.append({'종목': row['Name'], '현재가': f"{curr_p:,}"})
                if chg >= 25: s5.append({'종목': row['Name'], '등락': f"{chg:+.1f}%"})
                if last['Volume'] >= prev['Volume'] * 3: s6.append({'종목': row['Name'], '배수': f"{last['Volume']/prev['Volume']:.1f}배"})
                if ma5 > ma20 * 1.05: s7.append({'종목': row['Name'], '현재가': f"{curr_p:,}"})
                if pd.to_datetime(row['ListingDate']) > (datetime.now() - timedelta(days=365)): s8.append({'종목': row['Name'], '상장일': row['ListingDate']})
            except: continue

    # 상단 탭 배치 (휴대폰 대응)
    t = st.tabs(["🔥단타", "🎯종배", "💰대금", "🔝신고", "🚩상한", "📊폭증", "📈추세", "✨신규"])
    
    # 데이터 출력 (표 크기 최적화)
    data_lists = [s1, s2, s3, s4, s5, s6, s7, s8]
    for i, data in enumerate(data_lists):
        with t[i]:
            if data: st.table(pd.DataFrame(data).head(10))
            else: st.write("조건 부합 종목 없음")

except Exception as e:
    st.info("데이터를 동기화 중입니다...")

time.sleep(60)
st.rerun()
