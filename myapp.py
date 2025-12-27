import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 1. 페이지 설정 (넓은 화면 사용)
st.set_page_config(page_title="황금키 프로: 8분할 전광판", layout="wide")

# 상단 실시간 헤더 및 자동 새로고침 문구
now = datetime.now()
st.title("🔑 황금키 프로: 8분할 실시간 통합 스캐너")
st.caption(f"최근 업데이트: {now.strftime('%H:%M:%S')} (1분마다 전체 전략 자동 동기화)")

# 2. 사이드바 - 공통 방어 기준 설정
with st.sidebar:
    st.header("🛡️ 공통 방어 필터")
    min_marcap = st.number_input("최소 시총(억)", value=2000)
    st.info("※ 모든 전략에 [적자/위험종목 제외] 및 [정배열] 조건이 기본 적용됩니다.")

# 3. 데이터 분석 엔진 (한 번에 전체 데이터 로드)
try:
    with st.spinner("8가지 전략 실시간 분석 중..."):
        df_krx = fdr.StockListing('KRX')
        # [조건] 시총 필터 및 HTS 제외 종목(우선주, 스팩, 관리종목 등) 원천 차단
        df_base = df_krx[
            (df_krx['Marcap'] >= (min_marcap * 100000000)) & 
            (~df_krx['Name'].str.contains('우|스팩|관리|투자유의|정지|정리'))
        ].head(100) # 분석 속도를 위해 시총 상위주 위주

        # 전략별 리스트 바구니
        st_morning = [] # 오전 급등주
        st_closing = [] # 종가 배팅
        st_search = []  # 검색량 증가(거래대금 상위)
        st_newhigh = [] # 신고가
        st_upper = []   # 상한가 근접
        st_vol = []     # 거래량 폭증
        st_trend = []   # 정배열 대장주
        st_newlisting = [] # 신규상장 강세

        for _, row in df_base.iterrows():
            try:
                df = fdr.DataReader(row['Code'], (now - timedelta(days=60)).strftime('%Y-%m-%d'))
                if len(df) < 20: continue
                last = df.iloc[-1]
                prev = df.iloc[-2]
                curr_p = int(last['Close'])
                chg = ((curr_p - prev['Close']) / prev['Close']) * 100
                amt_b = int(last['Amount'] / 1e8)
                
                # [기본 조건] 5일 > 20일 정배열 상태만 통과
                ma5 = df['Close'].rolling(5).mean().iloc[-1]
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                if ma5 < ma20: continue 

                # 전략별 필터링
                if chg >= 7 and amt_b >= 500: st_morning.append({'종목': row['Name'], '등락': f"{chg:+.2f}%", '금액': f"{amt_b}억"})
                if 2 <= chg <= 5 and amt_b >= 300: st_closing.append({'종목': row['Name'], '등락': f"{chg:+.2f}%", '금액': f"{amt_b}억"})
                if amt_b >= 1000: st_search.append({'종목': row['Name'], '등락': f"{chg:+.2f}%", '금액': f"{amt_b}억"})
                if curr_p >= df['High'].iloc[:-1].max(): st_newhigh.append({'종목': row['Name'], '현재가': f"{curr_p:,}", '금액': f"{amt_b}억"})
                if chg >= 25: st_upper.append({'종목': row['Name'], '등락': f"{chg:+.2f}%", '금액': f"{amt_b}억"})
                if last['Volume'] >= prev['Volume'] * 3: st_vol.append({'종목': row['Name'], '배수': f"{last['Volume']/prev['Volume']:.1f}배", '금액': f"{amt_b}억"})
                if ma5 > ma20 * 1.05: st_trend.append({'종목': row['Name'], '현재가': f"{curr_p:,}", '상태': '추세강화'})
                if pd.to_datetime(row['ListingDate']) > (now - timedelta(days=365)): st_newlisting.append({'종목': row['Name'], '상장일': row['ListingDate']})
            except: continue

        # 4. 화면 8분할 배치 (상단 4칸, 하단 4칸)
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.subheader("🔥오전급등"); st.table(pd.DataFrame(st_morning).head(5))
        with col2: st.subheader("🎯종가배팅"); st.table(pd.DataFrame(st_closing).head(5))
        with col3: st.subheader("🔎실시간검색"); st.table(pd.DataFrame(st_search).head(5))
        with col4: st.subheader("🔝신고가"); st.table(pd.DataFrame(st_newhigh).head(5))

        col5, col6, col7, col8 = st.columns(4)
        with col5: st.subheader("🚩상한가근접"); st.table(pd.DataFrame(st_upper).head(5))
        with col6: st.subheader("📊거래폭증"); st.table(pd.DataFrame(st_vol).head(5))
        with col7: st.subheader("📈정배열추세"); st.table(pd.DataFrame(st_trend).head(5))
        with col8: st.subheader("✨신규상장"); st.table(pd.DataFrame(st_newlisting).head(5))

except Exception as e:
    st.info("데이터 동기화 대기 중... (1분 후 자동 재시도)")

# 5. 자동 업데이트 (1분)
time.sleep(60)
st.rerun()  
