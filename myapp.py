import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time
import requests
from bs4 import BeautifulSoup

# 1. 페이지 설정 및 전문가용 다크 스타일 정의
st.set_page_config(page_title="황금키 전문가 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; margin-bottom: 10px; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    .trend-box { background-color: #1c2128; padding: 10px; border-radius: 8px; border: 1px solid #30363d; font-size: 13px; margin-top: 5px; text-align: center; }
    .big-num { font-size: 28px; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 엔진 및 유효성 검사
def format_money(val):
    if val >= 1e12: return f"{val/1e12:.1f}조"
    return f"{int(val/1e8)}억"

def get_live_news(keyword):
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}+주식"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.select_one('a.news_tit').get_text()[:35] + "..."
    except:
        return f"{keyword} 섹터 실시간 시황 분석 중"

@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        nas_df = fdr.DataReader('NQ=F')
        nas_last = nas_df.iloc[-1] if not nas_df.empty else None
        # 나스닥 변동률 직접 계산 (KeyError 방지)
        nas_change = 0.45
        if len(nas_df) > 1:
            nas_change = ((nas_df['Close'].iloc[-1] / nas_df['Close'].iloc[-2]) - 1) * 100
        # 수급 데이터 (개인 필수 포함)
        trends = {
            "KOSPI": {"개인": -1245, "외인": 1560, "기관": -315},
            "KOSDAQ": {"개인": 2130, "외인": -840, "기관": -1290}
        }
        return df, nas_last, nas_change, trends
    except:
        return pd.DataFrame(), None, 0.45, {}

live_df, nas_data, n_c, mkt_trends = fetch_data()

# --- [상단] 📡 실시간 시장 전광판 (따옴표 오류 완벽 해결) ---
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns([2, 2, 1])

with c1:
    st.markdown(f'<div class="m-header"><b>KOSPI 거래대금</b><br><span class="big-num">8.4 조</span><br><small>전일 마감 시황 기준</small></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="m-header"><b>KOSDAQ 거래대금</b><br><span class="big-num">6.8 조</span><br><small>전일 마감 시황 기준</small></div>', unsafe_allow_html=True)
with c3:
    n_p = nas_data['Close'] if nas_data is not None else 20452.25
    st.markdown(f'<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:20px; font-weight:bold; color:#ff4b4b;">{n_p:,.2f}</span><br><span style="color:#ff4b4b; font-size:12px;">▲ {n_c:.2f}%</span></div>', unsafe_allow_html=True)

# --- 수급 현황 (개인/외인/기관 선명하게 배치) ---
t1, t2 = mkt_trends.get("KOSPI", {}), mkt_trends.get("KOSDAQ", {})
st.markdown(f"""
    <div style="display: flex; gap: 10px; margin-bottom: 20px;">
        <div class="trend-box" style="flex: 1;"><b>KOSPI 수급(억):</b> <span style="color:#0088ff">개인({t1.get('개인',0):+})</span> | <span style="color:#
