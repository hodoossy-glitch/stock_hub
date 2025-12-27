import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 페이지 설정
st.set_page_config(page_title="황금키 프로: 올인원", layout="wide")

# 🔄 자동 새로고침 시각화
st.title("🔑 황금키 프로: 실시간 자동 스캐너")
st.caption(f"최근 업데이트 시간: {datetime.now().strftime('%H:%M:%S')} (1분마다 자동 갱신)")

# 사이드바 메뉴
with st.sidebar:
    st.header("🎯 스캔 조건")
    mode = st.selectbox("검색 모드", ["실시간 주도주", "순간 거래대금 급증", "신고가 돌파", "신규상장주 스캔", "거래급증 종배"])
    min_marcap = st.number_input("최소 시총(억)", value=3000)

# 데이터 분석 로직
try:
    # 종목 리스트 가져오기 (실패 시 재시도)
    with st.spinner("종목 리스트를 불러오는 중..."):
        df_krx = fdr.StockListing('KRX')
    
    if df_krx is not None:
        df_krx = df_krx[df_krx['Marcap'] >= (min_marcap * 100000000)]
        
        results = []
        # 속도와 안정성을 위해 상위 80개 종목으로 집중 분석
        for _, row in df_krx.head(80).iterrows():
            try:
                # 개별 종목 데이터 호출 시 에러 방지 처리
                df = fdr.DataReader(row['Code'], (datetime.now() - timedelta(days=40)).strftime('%Y-%m-%d'))
                if df is None or len(df) < 2: continue
                
                last = df.iloc[-1]
                prev = df.iloc[-2]
                curr_amt = int(last['Amount'] / 1e8)
                prev_amt = int(prev['Amount'] / 1e8)
                
                if mode == "실시간 주도주":
                    ma5 = df['Close'].rolling(5).mean().iloc[-1]
                    if last['Close'] >= ma5 and curr_amt >= 300:
                        results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': curr_amt, '특징': '5일선 위'})
                
                elif mode == "순간 거래대금 급증":
                    amt_increase = ((curr_amt - prev_amt) / prev_amt) * 100 if prev_amt > 0 else 0
                    if amt_increase >= 50 and curr_amt >= 500:
                        results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': curr_amt, '증가율': f"+{amt_increase:.1f}%"})
                
                elif mode == "신고가 돌파":
                    max_high = df['High'].iloc[:-1].max()
                    if last['Close'] >= max_high:
                        results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': curr_amt, '특징': '신고가'})
                
                elif mode == "신규상장주 스캔":
                    listing_date = pd.to_datetime(row['ListingDate'])
                    if listing_date > (datetime.now() - timedelta(days=365)):
                        results.append({'종목명': row['Name'], '현재가': last['Close'], '상장일': listing_date.strftime('%Y-%m-%d')})
                
                elif mode == "거래급증 종배":
                    vol_ratio = last['Volume'] / prev['Volume']
                    if vol_ratio >= 2.0 and curr_amt >= 500:
                        results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': curr_amt, '거래폭발': f"{vol_ratio:.1f}배"})
            except:
                # 특정 종목 데이터 에러 시 무시하고 다음 종목으로 패스
                continue
        
        if results:
            st.success(f"✅ {mode} 검색 결과 (총 {len(results)}개)")
            st.table(pd.DataFrame(results))
        else:
            st.warning("조건에 맞는 종목이 없습니다. 잠시 후 자동 재스캔합니다.")
    else:
        st.error("데이터 서버 응답이 원활하지 않습니다. 잠시만 기다려주세요.")

except Exception as e:
    st.info("데이터 서버 연결 대기 중... (1분 후 자동 재시도)")

# 🔄 60초 대기 후 강제 새로고침
time.sleep(60)
st.rerun()
