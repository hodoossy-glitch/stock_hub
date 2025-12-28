import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time
import plotly.graph_objects as go

# 1. 페이지 설정 및 스타일 정의
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .sector-header { background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b; margin-bottom: 10px; display: flex; justify-content: space-between; align-items: center; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    .market-label { font-size: 14px; font-weight: bold; color: #888; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (4%↑ & 거래대금 정렬)
@st.cache_data(ttl=10)
def get_verified_data():
    try:
        df = fdr.StockListing('KRX')
        nasdaq = fdr.DataReader('NQ=F').iloc[-1]
        return df, float(nasdaq['Close']), float(nasdaq['Chg']) * 100
    except:
        return pd.DataFrame(), 20452.25, 0.45

live_df, nas_p, nas_c = get_verified_data()

# --- [상단] 1. 주도 섹터별 종목 나열 & 관련 뉴스 ---
st.markdown(f"### 🔥 주도 섹터 실시간 레이더 ({now.strftime('%H:%M:%S')})")
sectors_news = {
    "반도체": "HBM 5세대 공급 부족 및 삼성전자 11만 돌파",
    "비철금속": "알루미늄 가격 급등에 따른 수급 집중",
    "바이오": "신약 임상 결과 발표 임박 소식",
    "로봇": "삼성 로봇 팔 출시 임박 소식"
}

for s_name, s_news in sectors_news.items():
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
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
                                <div style="font-size:11px; color:#888;">{int(row['Amount']/1e8)}억</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='stock-card' style='color:#444;'>데이터 대기</div>", unsafe_allow_html=True)

st.divider()

# --- [중단] 2. 거래대금 상위 4% 이상 상승 종목 (8개) ---
st.markdown("### 💰 거래대금 상위 주도주 (4%↑)")
if not live_df.empty:
    top_8 = live_df[live_df['ChangesRatio'] >= 4.0].sort_values('Amount', ascending=False).head(8)
    cols_8 = st.columns(4)
    for idx, (i, s) in enumerate(top_8.iterrows()):
        amt_txt = f"{s['Amount']/1e12:.1f}조" if s['Amount'] >= 1e12 else f"{int(s['Amount']/1e8)}억"
        # 섹터별 바탕색 다르게 처리 (예시: 반도체-보라, 자동차-남색, 로봇-빨강 등)
        bg_color = "#4b0082" if "반도체" in str(s['Sector']) else "#00008b" if "자동차" in str(s['Sector']) else "#8b0000"
        with cols_8[idx % 4]:
            st.markdown(f"""
                <div class="stock-card" style="border-top: 4px solid {bg_color};">
                    <div style="font-size:15px; font-weight:bold;">{s['Name']}</div>
                    <div class="sector-tag" style="background-color:{bg_color};">{s['Sector'] if pd.notna(s['Sector']) else '주도주'}</div>
                    <div class="price-up">{
