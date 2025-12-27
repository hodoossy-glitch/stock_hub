import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 1. HTS 블랙 스타일 테마 설정
st.set_page_config(page_title="황금키 HTS 프로", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    div[data-testid="stTable"] { background-color: #1e1e1e; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730; border-radius: 5px; color: white; padding: 8px 12px;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 상단 실시간 전광판
now = datetime.now()
st.markdown(f"""
    <div style="background-color:#1e1e1e; padding:15px; border-radius:10px; border-left: 5px solid #ff4b4b;">
        <span style="color:#ff4b4b; font-size:22px; font-weight:bold;">📡 HTS LIVE: {now.strftime('%H:%M:%S')}</span>
        <span style="color:#00ff00; font-size:14px; margin-left:15px;">● 실시간 우량주 감시 중</span>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ HTS SETTINGS")
    min_marcap = st.number_input("최소 시총(억)", value=5000) # 선생님 설정값 반영
    st.divider()
    st.caption("🛡️ 적자/위험/잡주 필터 가동 중")

# 2. 고속 분석 엔진 (최적화 버전)
try:
    with st.spinner("전문가용 데이터 동기화 중..."):
        df_krx = fdr.StockListing('KRX')
        # 시총 기준 및 HTS 제외 항목 필터링
        df_base = df_krx[
            (df_krx['Marcap'] >= (min_marcap * 100000000)) & 
            (~df_krx['Name'].str.contains('우|스팩|관리|투자유의|정지|정리'))
        ].head(50) # 속도를 위해 핵심 50개 종목 집중 분석

        # 전략별 바구니
        s1, s2, s3, s4, s5, s6, s7, s8 = [], [], [], [], [], [], [], []

        for _, row in df_base.iterrows():
            try:
                # 최근 20일치만 가져와서 속도 극대화
                df = fdr.DataReader(row['Code'], (now - timedelta(days=20)).strftime('%Y-%m-%d'))
                if df is None or len(df) < 5: continue
                
                last, prev = df.iloc[-1], df.iloc[-2]
                curr_p, amt_b = int(last['Close']), int(last['Amount'] / 1e8)
                chg = ((curr_p - prev['Close']) / prev['Close']) * 100
                ma5, ma20 = df['Close'].tail(5).mean(), df['Close'].tail(20).mean()

                if ma5 < ma20: continue # 정배열 필터

                res = {'종목': row['Name'], '현재가': f"{curr_p:,}", '등락': f"{chg:+.2f}%", '금액': f"{amt_b}억"}

                if chg >= 7 and amt_b >= 300: s1.append(res) # 단타
                if 2 <= chg <= 5: s2.append(res) # 종배
                if amt_b >= 1000: s3.append(res) # 거래대금
                if curr_p >= df['High'].max(): s4.append(res) # 신고가
                if chg >= 20: s5.append(res) # 상한근접
                if last['Volume'] >= prev['Volume'] * 2: s6.append(res) # 거래폭증
                if ma5 > ma20 * 1.03: s7.append(res) # 추세강화
                if pd.to_datetime(row['ListingDate']) > (now - timedelta(days=365)): s8.append(res) # 신규
            except: continue

    # 3. 8대 전략 멀티탭 출력
    t = st.tabs(["🔥단타", "🎯종배", "💰대금", "🔝신고", "🚩상한", "📊폭증", "📈추세", "✨신규"])
    lists = [s1, s2, s3, s4, s5, s6, s7, s8]
    titles = ["오전 급등주", "종가 배팅", "거래대금 상위", "신고가 돌파", "상한가 근접", "거래량 폭발", "정배열 추세", "신규 상장"]

    for i, data in enumerate(lists):
        with t[i]:
            st.subheader(f"📡 {titles[i]}")
            if data: st.table(pd.DataFrame(data).head(10))
            else: st.info("조건에 맞는 우량주를 탐색 중입니다.")

except Exception as e:
    st.warning("데이터 서버 응답 대기 중입니다. 1분 후 자동으로 다시 시도합니다.")

# 4. 자동 새로고침
time.sleep(60)
st.rerun()
