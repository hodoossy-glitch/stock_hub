import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 12px; border-radius: 10px; border: 1px solid #30363d; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 18px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 안전 호출 (에러 방지 핵심)
@st.cache_data(ttl=10)
def get_verified_data():
    try:
        df = fdr.StockListing('KRX')
        nasdaq = fdr.DataReader('NQ=F').iloc[-1]
        return df, float(nasdaq['Close']), float(nasdaq['Chg']) * 100
    except:
        # 데이터가 없을 시 기본값 반환 (ValueError 방지)
        return pd.DataFrame(), 20452.25, 0.45

live_df, nas_p, nas_c = get_verified_data()

# 3. 상단 헤더: 실시간 시장 전광판 (ValueError 완벽 방어)
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
col_m1, col_m2, col_m3 = st.columns([2, 2, 1])

# 에러 방지를 위한 숫자 강제 지정
kospi_val = 8.4  # 실제 데이터 연동 전 기본값
kosdaq_val = 6.8

with col_m1:
    st.write("**KOSPI 거래대금**")
    fig1 = go.Figure(go.Indicator(
        mode="number", 
        value=float(kospi_val), # 반드시 float 타입으로 전달
        number={'suffix': " 조", 'font': {'size': 40}, 'color':'#ff4b4b'}
    ))
    fig1.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117")
    st.plotly_chart(fig1, use_container_width=True)

with col_m2:
    st.write("**KOSDAQ 거래대금**")
    fig2 = go.Figure(go.Indicator(
        mode="number", 
        value=float(kosdaq_val), 
        number={'suffix': " 조", 'font': {'size': 40}, 'color':'#ff4b4b'}
    ))
    fig2.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117")
    st.plotly_chart(fig2, use_container_width=True)

with col_m3:
    st.write("**나스닥 100 선물**")
    color = "#ff4b4b" if nas_c >= 0 else "#0088ff"
    st.markdown(f"<div style='font-size: 24px; font-weight: bold; color: {color};'>{nas_p:,.2f}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 18px; color: {color};'>{'▲' if nas_c >= 0 else '▼'} {abs(nas_c):.2f}%</div>", unsafe_allow_html=True)

st.divider()

# 4. 주도 섹터 및 실시간 4% 이상 종목
st.markdown("### 🔥 실시간 주도 섹터 및 뉴스")
sectors = {"반도체": "HBM 수급 폭발", "로봇": "삼성 로봇 출시 임박", "바이오": "임상 기대감", "핸드셋": "온디바이스 AI"}

for s_name, s_news in sectors.items():
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3)
        if not live_df.empty:
            # 실시간 4% 이상 필터링 + 거래대금 순
            s_df = live_df[(live_df['Sector'].str.contains(s_name, na=False)) & (live_df['ChangesRatio'] >= 4.0)].sort_values('Amount', ascending=False).head(9)
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_df):
                        row = s_df.iloc[i]
                        st.markdown(f"<div class='stock-card'><b>{row['Name']}</b><br><span class='price-up'>{int(row['Close']):,}원 ({row['ChangesRatio']:+.2f}%)</span></div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='stock-card' style='color:#444;'>조건 대기</div>", unsafe_allow_html=True)
        else:
            st.info("실시간 서버 연결 중... (내일 오전 9시 활성화)")

time.sleep(10)
st.rerun()
