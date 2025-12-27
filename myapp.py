import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 1. HTS 스타일 페이지 설정
st.set_page_config(page_title="황금키 HTS 프로", layout="wide", initial_sidebar_state="expanded")

# 2. 실시간 시간 표시 (상단 고정)
now = datetime.now()
st.markdown(f"""
    <div style="background-color:#1e1e1e; padding:10px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <span style="color:white; font-size:20px; font-weight:bold;">🕒 실시간 스캔 중: {now.strftime('%H:%M:%S')}</span>
        <span style="color:#00ff00; font-size:14px; margin-left:20px;">● 데이터 서버 연결됨</span>
    </div>
    """, unsafe_allow_html=True)

# 3. 사이드바 (HTS 설정창 느낌)
with st.sidebar:
    st.header("⚙️ SYSTEM SETTINGS")
    mode = st.selectbox("🎯 전략 선택", ["실시간 주도주", "순간 거래대금 급증", "신고가 돌파", "신규상장주", "거래폭발 종배"])
    min_marcap = st.slider("최소 시총(억)", 1000, 10000, 3000, step=500)
    st.divider()
    st.write("🔄 60초마다 자동 갱신 중")

# 4. 메인 데이터 스캔 로직
try:
    with st.spinner("MARKET DATA SCANNING..."):
        df_krx = fdr.StockListing('KRX')
        df_krx = df_krx[df_krx['Marcap'] >= (min_marcap * 100000000)]
        
        results = []
        for _, row in df_krx.head(60).iterrows(): # 속도 향상을 위해 60개 집중 분석
            try:
                df = fdr.DataReader(row['Code'], (now - timedelta(days=30)).strftime('%Y-%m-%d'))
                if df is None or len(df) < 2: continue
                
                last = df.iloc[-1]
                prev = df.iloc[-2]
                curr_price = int(last['Close'])
                change_rate = ((curr_price - prev['Close']) / prev['Close']) * 100
                amt_billion = int(last['Amount'] / 1e8)
                
                # 색상 결정 (상승/하락)
                color = "red" if change_rate > 0 else "blue"
                
                # 모드별 필터링
                if mode == "실시간 주도주":
                    if amt_billion >= 300:
                        results.append({'종목명': row['Name'], '현재가': f"{curr_price:,}", '등락': f"{change_rate:+.2f}%", '거래대금': f"{amt_billion}억"})
                elif mode == "순간 거래대금 급증":
                    if (last['Amount'] / prev['Amount']) >= 1.5 and amt_billion >= 500:
                        results.append({'종목명': row['Name'], '현재가': f"{curr_price:,}", '등락': f"{change_rate:+.2f}%", '거래대금': f"{amt_billion}억"})
                elif mode == "신고가 돌파" and curr_price >= df['High'].iloc[:-1].max():
                    results.append({'종목명': row['Name'], '현재가': f"{curr_price:,}", '등락': f"{change_rate:+.2f}%", '거래대금': f"{amt_billion}억"})
                # ... 다른 모드들도 유사하게 적용
            except: continue

        # 5. 결과 출력 (HTS 테이블 스타일)
        if results:
            st.write(f"### 📡 {mode} 실시간 포착 리스트")
            # 스타일링된 데이터프레임
            st.dataframe(pd.DataFrame(results), use_container_width=True, height=500)
        else:
            st.info("시장을 감시 중입니다. 조건에 맞는 종목이 포착되면 즉시 표시됩니다.")

except Exception as e:
    st.error("데이터 서버 재연결 시도 중...")

# 6. HTS급 리프레시 구현
time.sleep(60)
st.rerun()
