import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 페이지 설정
st.set_page_config(page_title="황금키 프로: 올인원", layout="wide")

# 🔄 자동 새로고침 시각화 (선생님 요청 문구 포함)
st.title("🔑 황금키 프로: 실시간 자동 스캐너")
st.caption(f"최근 업데이트 시간: {datetime.now().strftime('%H:%M:%S')} (1분마다 자동 갱신)")

# 사이드바 메뉴
with st.sidebar:
    st.header("🎯 스캔 조건")
    mode = st.selectbox("검색 모드", ["실시간 주도주", "순간 거래대금 급증", "신고가 돌파", "신규상장주 스캔", "거래급증 종배"])
    min_marcap = st.number_input("최소 시총(억)", value=3000)

# 데이터 분석 로직
try:
    df_krx = fdr.StockListing('KRX')
    df_krx = df_krx[df_krx['Marcap'] >= (min_marcap * 100000000)]
    
    results = []
    # 분석 범위 최적화
    for _, row in df_krx.head(100).iterrows():
        try:
            df = fdr.DataReader(row['Code'], (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            if len(df) < 2: continue
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            curr_amt = int(last['Amount'] / 1e8) # 현재 거래대금(억)
            prev_amt = int(prev['Amount'] / 1e8) # 직전일 거래대금(억)
            
            if mode == "실시간 주도주":
                ma5 = df['Close'].rolling(5).mean().iloc[-1]
                if last['Close'] >= ma5 and curr_amt >= 300:
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': curr_amt, '특징': '5일선 사수'})
            
            elif mode == "순간 거래대금 급증":
                # 직전 거래일 대비 오늘 거래대금이 50% 이상 급증한 경우
                amt_increase = ((curr_amt - prev_amt) / prev_amt) * 100 if prev_amt > 0 else 0
                if amt_increase >= 50 and curr_amt >= 500:
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': curr_amt, '증가율': f"+{amt_increase:.1f}%", '특징': '돈이 몰림'})
            
            elif mode == "신고가 돌파":
                max_high = df['High'].iloc[:-1].max()
                if last['Close'] >= max_high:
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': curr_amt, '특징': '신고가'})
            
            elif mode == "신규상장주 스캔":
                listing_date = pd.to_datetime(row['ListingDate'])
                if listing_date > (datetime.now() - timedelta(days=365)):
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '상장일': listing_date.strftime('%Y-%m-%d'), '특징': '신입생'})
            
            elif mode == "거래급증 종배":
                vol_ratio = last['Volume'] / prev['Volume']
                if vol_ratio >= 2.0 and curr_amt >= 500:
                    results.append({'종목명': row['Name'], '현재가': last['Close'], '거래대금(억)': curr_amt, '거래폭발': f"{vol_ratio:.1f}배"})
        except: continue
    
    if results:
        st.success(f"✅ {mode} 검색 결과 (총 {len(results)}개)")
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.warning("현재 조건에 맞는 종목이 없습니다. 1분 후 자동으로 다시 스캔합니다.")

except Exception as e:
    st.error(f"데이터 분석 중 오류: {e}")

# 🔄 60초 대기 후 강제 새로고침 (에러 없는 순정 방식)
time.sleep(60)
st.rerun()
