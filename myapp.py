import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인 (선생님 원본 유지)
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 12px; border-radius: 10px; margin-bottom:10px; border: 1px solid #30363d; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 18px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 호출 엔진 (서버 점검 방어막 포함)
@st.cache_data(ttl=10)
def get_live_data():
    try:
        df = fdr.StockListing('KRX')
        if df is not None and not df.empty:
            return df
        return None
    except:
        return None

live_df = get_live_data()

# 3. 상단 헤더: 지표 및 수급 (디자인 유지)
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
col_m1, col_m2, col_m3 = st.columns([2, 2, 1])

with col_m1:
    st.write("**KOSPI 거래대금**")
    fig = go.Figure(go.Indicator(mode="number", value=8.4, number={'suffix': " 조", 'font': {'size': 40}, 'color':'#ff4b4b'}))
    fig.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("개인:-1.2천억 | 외인:+1.5천억 | 기관:-0.3천억")

with col_m2:
    st.write("**KOSDAQ 거래대금**")
    fig2 = go.Figure(go.Indicator(mode="number", value=6.8, number={'suffix': " 조", 'font': {'size': 40}, 'color':'#ff4b4b'}))
    fig2.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117")
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("개인:+2.1천억 | 외인:-0.8천억 | 기관:-1.3천억")

with col_m3:
    st.write("**나스닥 100 선물**")
    st.markdown("<div style='font-size: 24px; font-weight: bold; color: #ff4b4b;'>20,452.25</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 18px; color: #ff4b4b;'>▲ 0.45%</div>", unsafe_allow_html=True)

st.divider()

# 4. 메인: 주도 섹터 레이더 (실시간 종목 9개 자동 매칭)
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
sectors = ["반도체", "비철금속", "바이오", "로봇"]
news = ["HBM 5세대 공급 부족 및 실시간 수급 폭발", "알루미늄 가격 급등세 반영", "신약 임상 결과 발표 임박 소식", "삼성 로봇 팔 출시 임박 소식"]

for s_name, s_news in zip(sectors, news):
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3)
        if live_df is not None:
            # 해당 섹터 종목 중 등락률 높은 순으로 9개 추출
            s_stocks = live_df[live_df['Sector'].str.contains(s_name, na=False)].sort_values('ChangesRatio', ascending=False).head(9)
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_stocks):
                        row = s_stocks.iloc[i]
                        st.markdown(f"""
                            <div class='stock-card'>
                                <b>{row['Name']}</b><br>
                                <span class='price-up'>{int(row['Close']):,}원 ({row['ChangesRatio']:+.2f}%)</span>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='stock-card' style='color:#444;'>데이터 대기</div>", unsafe_allow_html=True)
        else:
            st.info("실시간 데이터 연결 대기 중...")

# 5. 하단: 거래대금 상위 4% 이상 (실시간 필터링 적용)
st.markdown("### 💰 거래대금 상위 주도주 (4%↑)")
if live_df is not None:
    # 실시간 4% 이상 & 거래대금 상위 4개 추출
    top_4 = live_df[live_df['ChangesRatio'] >= 4.0].sort_values('Amount', ascending=False).head(4)
    col_stocks = st.columns(4)
    for idx, (i, s) in enumerate(top_4.iterrows()):
        amt_txt = f"{s['Amount']/1e12:.1f}조" if s['Amount'] >= 1e12 else f"{int(s['Amount']/1e8)}억"
        with col_stocks[idx]:
            st.markdown(f"""
                <div class="stock-card" style="border-top: 4px solid #ff4b4b;">
                    <div style="font-size:16px; font-weight:bold;">{s['Name']}</div>
                    <div class="sector
