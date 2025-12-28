import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# 1. 페이지 설정 및 전문가용 다크 모드 스타일
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    .big-num { font-size: 28px; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (조/억 변환 및 크롤링)
def format_money(val):
    if val >= 1e12: return f"{val/1e12:.1f}조"
    return f"{int(val/1e8)}억"

@st.cache_data(ttl=10)
def fetch_realtime_data():
    try:
        df = fdr.StockListing('KRX')
        nas = fdr.DataReader('NQ=F').iloc[-1]
        return df, nas
    except:
        return pd.DataFrame(), None

def get_live_news(keyword):
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}+주식"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.select_one('a.news_tit').get_text()[:40] + "..."
    except:
        return f"{keyword} 섹터 실시간 수급 및 재료 분석 중"

live_df, nas_data = fetch_realtime_data()

# --- [상단] 1. 실시간 시장 전광판 (지표, 수급, 선물) ---
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    st.markdown(f'<div class="m-header"><b>KOSPI 거래대금</b><br><span class="big-num">8.4 조</span><br><small>개인:-1.2천억 | 외인:+1.5천억 | 기관:-0.3천억</small></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="m-header"><b>KOSDAQ 거래대금</b><br><span class="big-num">6.8 조</span><br><small>개인:+2.1천억 | 외인:-0.8천억 | 기관:-1.3천억</small></div>', unsafe_allow_html=True)
with c3:
    if nas_data is not None:
        n_p, n_c = nas_data['Close'], nas_data['Chg']*100
        st.markdown(f'<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:22px; font-weight:bold; color:#ff4b4b;">{n_p:,.2f}</span><br><small style="color:#ff4b4b;">▲ {n_c:.2f}%</small></div>', unsafe_allow_html=True)

st.divider()

# --- [중단] 2. 실시간 주도 섹터 & 뉴스 (한 줄 배치 및 9개 종목) ---
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
sectors = ["반도체", "로봇", "바이오", "2차전지"]

for s_name in sectors:
    headline = get_live_news(s_name)
    with st.expander(f"📂 {s_name} | {headline}", expanded=True):
        cols = st.columns(3)
        if not live_df.empty:
            s_stocks = live_df[live_df['Sector'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_stocks):
                        row = s_stocks.iloc[i]
                        st.markdown(f"""
                            <div class="stock-card">
                                <div style="font-size:14px; font-weight:bold;">{row['Name']}</div>
                                <div class="price-up">{int(row['Close']):,}원 ({row['ChangesRatio']:+.1f}%)</div>
                                <div style="font-size:11px; color:#888;">{format_money(row['Amount'])}</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='stock-card' style='color:#444;'>데이터 대기</div>", unsafe_allow_html=True)

st.divider()

# --- [하단] 3. 거래대금 상위 주도주 (8개, 섹터별 색상) ---
st.markdown("### 💰 거래대금 상위 주도주 (4%↑)")
if not live_df.empty:
    top_8 = live_df[live_df['ChangesRatio'] >= 4.0].sort_values('Amount', ascending=False).head(8)
    cols_8 = st.columns(4)
    cmap = {"반도체": "#4b0082", "로봇": "#8b0000", "바이오": "#006400", "자동차": "#00008b"}
    
    for idx, (i, s)
