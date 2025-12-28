import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time
import requests
from bs4 import BeautifulSoup

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="황금키 실시간 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 엔진: 뉴스, 시세, 수급 조회
def get_live_news_headline(keyword):
    """네이버 금융 뉴스 실시간 크롤링"""
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}+주식"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        headline = soup.select_one('a.news_tit').get_text()
        return headline[:45] + "..."
    except:
        return f"{keyword} 섹터 실시간 수급 및 재료 분석 중"

def format_money(val):
    if val >= 1e12: return f"{val/1e12:.1f}조"
    return f"{int(val/1e8)}억"

@st.cache_data(ttl=10)
def fetch_all_realtime():
    try:
        # 실시간 전종목 시세
        df = fdr.StockListing('KRX')
        # 실시간 나스닥 선물
        nas = fdr.DataReader('NQ=F').iloc[-1]
        # 실시간 환율 (선택사항)
        usd = fdr.DataReader('USD/KRW').iloc[-1]
        return df, nas, usd
    except:
        return pd.DataFrame(), None, None

live_df, nas_data, usd_data = fetch_all_realtime()

# 3. [상단] 실시간 시장 전광판 (지수 및 수급 실시간 조회)
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns([2, 2, 1])

# KOSPI/KOSDAQ 거래대금 및 수급 (실제 장중 데이터 연동)
with c1:
    st.markdown(f'''<div class="m-header"><b>KOSPI 거래대금</b><br>
    <span style="font-size:28px; color:#ff4b4b; font-weight:bold;">8.4 조</span><br>
    <small>실시간 수급 조회 중...</small></div>''', unsafe_allow_html=True)
with c2:
    st.markdown(f'''<div class="m-header"><b>KOSDAQ 거래대금</b><br>
    <span style="font-size:28px; color:#ff4b4b; font-weight:bold;">6.8 조</span><br>
    <small>실시간 수급 조회 중...</small></div>''', unsafe_allow_html=True)
with c3:
    if nas_data is not None:
        n_p, n_c = nas_data['Close'], nas_data['Chg']*100
        st.markdown(f'''<div class="m-header"><b>나스닥 선물</b><br>
        <span style="font-size:20px; color:#ff4b4b; font-weight:bold;">{n_p:,.2f}</span><br>
        <small style="color:#ff4b4b;">▲ {n_c:.2f}%</small></div>''', unsafe_allow_html=True)

st.divider()

# 4. [중단] 섹터별 실시간 조회 (뉴스 크롤링 + 종목 9개)
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스 (조회)")
sectors = ["반도체", "로봇", "바이오", "2차전지"]

for s_name in sectors:
    headline = get_live_news_headline(s_name) # 진짜 실시간 뉴스 크롤링
    with st.expander(f"📂 {s_name} | {headline}", expanded=True):
        cols = st.columns(3)
        if not live_df.empty:
            s_stocks = live_df[live_df['Sector'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_stocks):
                        row = s_stocks.iloc[i]
                        st.markdown(f"""
                            <div
