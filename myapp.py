import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

# CSS: 블랙 HTS 디자인
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border-left: 5px solid #ff4b4b; margin-bottom: 12px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    .info-box { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. 시장 지표 자동 크롤링 엔진
@st.cache_data(ttl=60)
def get_market_indices():
    try:
        # 환율, 유가, 금, 선물 등을 자동으로 가져옴
        usd = fdr.DataReader('USD/KRW', now - timedelta(days=7)).iloc[-1]['Close']
        wti = fdr.DataReader('CL=F', now - timedelta(days=7)).iloc[-1]['Close']
        gold = fdr.DataReader('GC=F', now - timedelta(days=7)).iloc[-1]['Close']
        return {"usd": usd, "wti": wti, "gold": gold}
    except:
        return {"usd": 1445.0, "wti": 56.74, "gold": 4552.7} # 오류 시 캡처본 데이터 유지

# 3. 실시간 주도주 자동 검색 엔진
@st.cache_data(ttl=60)
def get_realtime_leaders():
    try:
        df = fdr.StockListing('KRX')
        # 캡처본처럼 4% 이상 상승 중인 거래대금 상위주 자동 선별
        leaders = df[
            (df['ChangesRatio'] >= 4.0) & 
            (~df['Name'].str.contains('우|스팩|관리'))
        ].sort_values(by='Amount', ascending=False).head(12)
        return leaders
    except:
        return pd.DataFrame()

# --- 화면 출력 시작 ---
indices = get_market_indices()
st.markdown(f"### 📡 실시간 통합 상황판 ({now.strftime('%H:%M:%S')})")

# 지표 섹션
c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='info-box'>💵 USD 환율<br><b style='color:#0088ff;'>{indices['usd']:,}</b></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='info-box'>🛢️ WTI 유가<br><b style='color:#0088ff;'>{indices['wti']:,}</b></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='info-box'>💰 국제 금<br><b style='color:#ff4b4b;'>{indices['gold']:,}</b></div>", unsafe_allow_html=True)

st.divider()

# 주도주 섹션
st.markdown("### 🔥 거래대금 상위 주도주 (4%↑)")
leaders = get_realtime_leaders()

if not leaders.empty:
    cols = st.columns(3)
    for idx, (i, row) in enumerate(leaders.iterrows()):
        with cols[idx % 3]:
            amt = row['Amount'] / 1e8
            amt_txt = f"{amt/10000:.1f}조" if amt >= 10000 else f"{int(amt)}억"
            st.markdown(f"""
                <div class="stock-card">
                    <div style="font-size:18px; font-weight:bold;">{row['Name']}</div>
                    <div class="price-up">{int(row['Close']):,}원</div>
                    <div style="display:flex; justify-content:space-between; font-size:14px;">
                        <span style="color:#ff4b4b;">▲ {row['ChangesRatio']}%</span>
                        <span style="color:#888;">{amt_txt}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
else:
    st.info("장 시작 후 실시간 데이터를 자동으로 수신합니다.")

time.sleep(60)
st.rerun()
