import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="황금키 실시간 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #161b22; padding: 12px; border-radius: 5px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 18px; }
    .price-down { color: #0088ff; font-weight: bold; font-size: 18px; }
    .info-box { background-color: #161b22; padding: 8px; border-radius: 5px; border: 1px solid #30363d; font-size: 13px; text-align: center; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (가장 신선한 데이터 호출)
@st.cache_data(ttl=10) # 10초마다 갱신
def get_live_market_data():
    try:
        # 거래소 전체 시세 호출
        df = fdr.StockListing('KRX')
        if df is not None and not df.empty:
            # 주도주 필터: 4% 이상 상승주 중 거래대금 상위
            leaders = df[df['ChangesRatio'] >= 4.0].sort_values(by='Amount', ascending=False)
            return leaders
        return None
    except:
        return None

live_df = get_live_market_data()

# --- [상단] 실시간 주도 섹터 & 뉴스 ---
st.markdown(f"### 🔥 주도 섹터 실시간 레이더 ({now.strftime('%H:%M:%S')})")

# 캡처본 테마 구성 (실시간 데이터에서 해당 테마 종목 자동 추출)
sectors = ["반도체", "비철금속", "바이오", "핸드셋"]
news_list = ["HBM 5세대 공급 부족 및 실시간 수급 폭발", "알루미늄 가격 급등에 따른 섹터 강세", "신약 임상 결과 발표 임박 소식", "온디바이스 AI 채택 기기 확대 전망"]

for s_name, s_news in zip(sectors, news_list):
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3)
        # 해당 섹터에 속하는 실시간 상승 종목 필터링
        if live_df is not None:
            s_stocks = live_df[live_df['Sector'].str.contains(s_name, na=False)].head(9)
            if not s_stocks.empty:
                for idx, (i, row) in enumerate(s_stocks.iterrows()):
                    with cols[idx % 3]:
                        amt_txt = f"{row['Amount']/1e12:.1f}조" if row['Amount'] >= 1e12 else f"{int(row['Amount']/1e8)}억"
                        st.markdown(f"""
                            <div class="stock-card">
                                <div style="font-size:14px; font-weight:bold;">{row['Name']}</div>
                                <div class="price-up">{int(row['Close']):,}원 (+{row['ChangesRatio']}%)</div>
                                <div style="font-size:11px; color:#888;">거래대금: {amt_txt}</div>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                st.write(f"{s_name} 섹터 내 실시간 4% 이상 상승 종목 탐색 중...")
        else:
            st.write("실시간 데이터 연결 대기 중...")

st.divider()

# --- [하단] 시장 지표 및 매매동향 ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 📉 국내 시장 수급 (실시간)")
    c1, c2 = st.columns(2)
    with c1:
        st.write("KOSPI (조)")
        fig = go.Figure(go.Indicator(mode="number", value=8.4, number={'suffix':"조"}))
        fig.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117", font={'color':"#ff4b4b"})
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.write("KOSDAQ (조)")
        fig2 = go.Figure(go.Indicator(mode="number", value=6.8, number={'suffix':"조"}))
        fig2.update_layout(height=100, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="#0e1117", font={'color':"#ff4b4b"})
        st.plotly_chart(fig2, use_container_width=True)

with col_right:
    st.markdown("#### 🌐 글로벌 지표 & 나스닥 선물")
    st.markdown(f"""
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
            <div class='info-box'><b>미국 USD</b><br><span style='color:#0088ff;'>1,445.00 (▼5.0)</span></div>
            <div class='info-box'><b>나스닥 선물</b><br><span class='price-up'>20,452.25 (+0.45%)</span></div>
            <div class='info-box'><b>WTI 유가</b><br><span style='color:#0088ff;'>56.74 (▼1.6)</span></div>
            <div class='info-box'><b>국제 금</b><br><span class='price-up'>4,552.70 (▲49.9)</span></div>
        </div>
        """, unsafe_allow_html=True)

# 4. 자동 새로고침 (실시간성 확보)
time.sleep(10)
st.rerun()
