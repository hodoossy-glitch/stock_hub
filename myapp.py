import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time
import requests
from bs4 import BeautifulSoup
import plotly.graph_objects as go

# 1. 페이지 설정 (모바일 최적화 및 다크모드)
st.set_page_config(page_title="황금키 전문가 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    .trend-box { background-color: #1c2128; padding: 10px; border-radius: 8px; border: 1px solid #30363d; font-size: 13px; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 엔진 (데이터 & 뉴스 조회)
def format_money(val):
    if val >= 1e12: return f"{val/1e12:.1f}조"
    return f"{int(val/1e8)}억"

def get_live_news(keyword):
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={keyword}+주식"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=2)
        soup = BeautifulSoup(res.text, 'html.parser')
        return soup.select_one('a.news_tit').get_text()[:40] + "..."
    except:
        return f"{keyword} 섹터 수급 집중 분석 중"

@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        nas = fdr.DataReader('NQ=F').iloc[-1]
        # 장중 실시간 수급 (샘플값 유지, 장중 크롤링 연동 가능)
        trends = {"KOSPI": {"개인": -1245, "외인": 1560, "기관": -315},
                  "KOSDAQ": {"개인": 2130, "외인": -840, "기관": -1290}}
        return df, nas, trends
    except:
        return pd.DataFrame(), None, {}

live_df, nas_data, mkt_trends = fetch_data()

# --- [1단계] 주도 섹터 레이더 (9개 종목 & 뉴스 한 줄) ---
st.markdown(f"### 🔥 실시간 주도 섹터 레이더 ({now.strftime('%H:%M:%S')})")
sectors = ["반도체", "로봇", "바이오", "비철금속"]

for s_name in sectors:
    headline = get_live_news(s_name)
    with st.expander(f"📂 {s_name} | {headline}", expanded=True):
        cols = st.columns(3)
        if not live_df.empty:
            s_df = live_df[live_df['Sector'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_df):
                        row = s_df.iloc[i]
                        st.markdown(f"""<div class="stock-card">
                            <div style="font-size:14px; font-weight:bold;">{row['Name']}</div>
                            <div class="price-up">{int(row['Close']):,}원 ({row['ChangesRatio']:+.1f}%)</div>
                            <div style="font-size:11px; color:#888;">{format_money(row['Amount'])}</div>
                        </div>""", unsafe_allow_html=True)

st.divider()

# --- [2단계] 거래대금 상위 주도주 (8개, 섹터 색상 구분) ---
st.markdown("### 💰 거래대금 상위 주도주 (4%↑)")
if not live_df.empty:
    top_8 = live_df[live_df['ChangesRatio'] >= 4.0].sort_values('Amount', ascending=False).head(8)
    cols_8 = st.columns(4)
    cmap = {"반도체": "#4b0082", "로봇": "#8b0000", "바이오": "#006400", "자동차": "#00008b"}
    for idx, (i, s) in enumerate(top_8.iterrows()):
        s_type = s['Sector'] if pd.notna(s['Sector']) else "주도주"
        bg = "#161b22"
        for k, v in cmap.items():
            if k in str(s_type): bg = v
        with cols_8[idx % 4]:
            st.markdown(f"""<div class="stock-card" style="border-top: 4px solid {bg};">
                <div style="font-size:15px; font-weight:bold;">{s['Name']}</div>
                <div class="sector-tag" style="background-color:{bg};">{s_type}</div>
                <div class="price-up">{int(s['Close']):,}원 ({s['ChangesRatio']:+.1f}%)</div>
                <div style="font-size:11px; color:#888;">{format_money(s['Amount'])}</div>
            </div>""", unsafe_allow_html=True)

st.divider()

# --- [3단계] 하단 지표 및 매매동향 (개인/외인/기관) ---
cl, cr = st.columns(2)
with cl:
    st.markdown("<p style='font-size:14px; color:#888;'>📉 KOSPI 거래대금 (조)</p>", unsafe_allow_html=True)
    st.plotly_chart(go.Figure(go.Indicator(mode="number", value=8.4, number={'suffix':"조", 'font':{'size':30, 'color':'#ff4b4b'}})).update_layout(height=80, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117"), use_container_width=True)
    t = mkt_trends.get("KOSPI", {})
    st.markdown(f"""<div class="trend-box"><b>KOSPI 수급(억):</b> <span style="color:#0088ff">개인({t['개인']:+})</span> | <span style="color:#ff4b4b">외인({t['외인']:+})</span> | 기관({t['기관']:+})</div>""", unsafe_allow_html=True)
with cr:
    st.markdown("<p style='font-size:14px; color:#888;'>📈 KOSDAQ 거래대금 (조)</p>", unsafe_allow_html=True)
    st.plotly_chart(go.Figure(go.Indicator(mode="number", value=6.8, number={'suffix':"조", 'font':{'size':30, 'color':'#ff4b4b'}})).update_layout(height=80, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117"), use_container_width=True)
    t2 = mkt_trends.get("KOSDAQ", {})
    st.markdown(f"""<div class="trend-box"><b>KOSDAQ 수급(억):</b> <span style="color:#ff4b4b">개인({t2['개인']:+})</span> | 외인({t2['외인']:+}) | 기관({t2['기관']:+})</div>""", unsafe_allow_html=True)

time.sleep(10)
st.rerun()
