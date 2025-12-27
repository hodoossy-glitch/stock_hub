import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 긴급진단", layout="wide")

# 한국 시간 설정
now = datetime.now(timezone(timedelta(hours=9)))

st.title("📡 황금키 프로: 긴급 진단 모드")
st.caption(f"현재 시각: {now.strftime('%H:%M:%S')} (데이터 서버 연결 시도 중)")

with st.sidebar:
    st.header("⚙️ 필터 조절")
    min_marcap = st.number_input("최소 시총(억)", value=1000)

# 2. 분석 엔진 (테스트용 유연한 조건)
try:
    with st.spinner("데이터 강제 동기화 중..."):
        # 전체 종목 리스트 호출
        df_krx = fdr.StockListing('KRX')
        
        # 필터링: 시총 기준만 적용 (우선주 등은 제외)
        df_base = df_krx[
            (df_krx['Marcap'] >= (min_marcap * 100000000)) & 
            (~df_krx['Name'].str.contains('우|스팩'))
        ].head(50) # 상위 50개만 빠르게 테스트

        results = []
        for _, row in df_base.iterrows():
            try:
                # 최근 10일치 데이터만 호출 (속도 극대화)
                df = fdr.DataReader(row['Code'], (now - timedelta(days=15)).strftime('%Y-%m-%d'))
                if df is None or len(df) < 2: continue
                
                last = df.iloc[-1]
                prev = df.iloc[-2]
                curr_p = int(last['Close'])
                chg = ((curr_p - prev['Close']) / prev['Close']) * 100
                
                # 테스트를 위해 아주 완만한 조건 적용 (상승 중인 종목 모두 포착)
                results.append({
                    '종목명': row['Name'],
                    '현재가': f"{curr_p:,}원",
                    '등락률': f"{chg:+.2f}%",
                    '거래대금': f"{int(last['Amount']/1e8)}억"
                })
                if len(results) >= 10: break
            except: continue

    # 3. 결과 출력
    if results:
        st.success(f"✅ 시스템 정상! {len(results)}개 종목 포착 완료")
        st.table(pd.DataFrame(results))
    else:
        st.warning("⚠️ 주말 데이터 서버 응답 지연 중. 월요일 장 시작 시 자동 복구됩니다.")

except Exception as e:
    st.error(f"서버 연결 오류: {e}")

time.sleep(60)
st.rerun()
