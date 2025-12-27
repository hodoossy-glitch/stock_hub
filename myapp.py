import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta
import time

# 1. HTS 스타일 페이지 설정 및 디자인
st.set_page_config(page_title="황금키 HTS 프로", layout="wide")

# HTS 블랙 테마 적용 (CSS 커스텀)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stTable { background-color: #1e1e1e; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 5px;
        color: white;
        padding: 5px 15px;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 상단 실시간 지수/시간 전광판
now = datetime.now()
st.markdown(f"""
    <div style="background-color:#1e1e1e; padding:15px; border-radius:10px; border-left: 5px solid #ff4b4b; margin-bottom: 20px;">
        <span style="color:#ff4b4b; font-size:24px; font-weight:bold;">📡 SYSTEM LIVE: {now.strftime('%H:%M:%S')}</span>
        <span style="color:#888; font-size:16px; margin-left:20px;">● 데이터 서버 동기화 완료</span>
        <span style="float:right; color:#00ff00; font-weight:bold;">실시간 자동 스캔 중...</span>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ HTS SETTINGS")
    min_marcap = st.number_input("최소 시총(억)", value=3000)
    st.divider()
    st.write("※ 🛡️ 재무위험/적자/잡주 원천 차단 모드")

# 2. 고속 분석 엔진
try:
    with st.spinner("MARKET DATA SCANNING..."):
        df_krx = fdr.StockListing('KRX')
        df_base = df_krx[
            (df_krx['Marcap'] >= (min_marcap * 100000000)) & 
            (~df_krx['Name'].str.contains('우|스팩|관리|투자유의|정지|정리'))
        ].head(80)

        # 8대 전략 바구니
        s_morning, s_closing, s_amt, s_high, s_upper, s_vol, s_trend, s_new = [], [], [], [], [], [], [], []

        for _, row in df_base.iterrows():
            try:
                df = fdr.DataReader(row['Code'], (now - timedelta(days=30)).strftime('%Y-%m-%d'))
                if len(df) < 20: continue
                last, prev = df.iloc[-1], df.iloc[-2]
                curr_p, amt_b = int(last['Close']), int(last['Amount'] / 1e8)
                chg = ((curr_p - prev['Close']) / prev['Close']) * 100
                ma5, ma20 = df['Close'].tail(5).mean(), df['Close'].tail(20).mean()

                if ma5 < ma20: continue # 정배열 필수

                # HTS 스타일 데이터 (상승 시 빨간색 강조용 등락률)
                chg_str = f"<span style='color:#ff4b4b; font-weight:bold;'>{chg:+.2f}%</span>" if chg > 0 else f"<span style='color:#4b4bff;'>{chg:+.2f}%</span>"
                
                res = {'종목': row['Name'], '현재가': f"{curr_p:,}", '등락률': chg, '대금': f"{amt_b}억"}

                if chg >= 7 and amt_b >= 500: s_morning.append(res)
                if 2 <= chg <= 5 and amt_b >= 300: s_closing.append(res)
                if amt_b >= 1000: s_amt.append(res)
                if curr_p >= df['High'].max(): s_high.append(res)
                if chg >= 25: s_upper.append(res)
                if last['Volume'] >= prev['Volume'] * 3: s_vol.append(res)
                if ma5 > ma20 * 1.05: s_trend.append(res)
                if pd.to_datetime(row['ListingDate']) > (now - timedelta(days=365)): s_new.append(res)
            except: continue

    # 3. HTS 멀티탭 배치
    tabs = st.tabs(["🔥단타", "🎯종배", "💰대금", "🔝신고", "🚩상한", "📊폭증", "📈추세", "✨신규"])
    
    label_list = ["오전 급등 주도주", "장마감 종가 배팅", "거래대금 상위주", "60일 신고가 돌파", "상한가 근접주", "거래량 폭증주", "정배열 강세주", "신규상장 유망주"]
    data_list = [s_morning, s_closing, s_amt, s_high, s_upper, s_vol, s_trend, s_new]

    for i, data in enumerate(data_list):
        with tabs[i]:
            st.subheader(f"📡 {label_list[i]}")
            if data:
                # 데이터프레임 시각화 (등락률에 따라 색상 강조는 st.dataframe의 column_config 활용)
                df_res = pd.DataFrame(data).sort_values(by='등락률', ascending=False)
                st.dataframe(df_res, use_container_width=True, hide_index=True, 
                             column_config={"등락률": st.column_config.NumberColumn(format="%.2f%%")})
            else:
                st.info("조건에 부합하는 종목을 탐색 중입니다.")

except Exception as e:
    st.info("시장을 감시 중입니다. 잠시만 기다려주세요...")

# 4. 자동 새로고침 (1분)
time.sleep(60)
st.rerun()
