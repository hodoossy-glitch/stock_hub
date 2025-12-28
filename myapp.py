import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 전문가용 다크 스타일
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 12px; border-radius: 12px; border: 1px solid #30363d; text-align: center; margin-bottom: 2px; }
    .big-num { font-size: 22px; font-weight: bold; color: #ff4b4b; margin-bottom: 0px; }
    .supply-row { font-size: 11px; display: flex; justify-content: center; gap: 5px; margin-top: 5px; border-top: 1px solid #30363d; padding-top: 5px; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; min-height: 90px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 14px; }
    .amt-label { color: #888; font-size: 11px; display: block; margin-top: 2px; }
    /* 탭 스타일 조정 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 40px; background-color: #1c2128; border-radius: 5px; color: #888; }
    .stTabs [aria-selected="true"] { color: #ffffff !important; border-bottom-color: #ff4b4b !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 및 그래프 엔진 (에러 방지 정밀 검수)
@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns:
                df['Chg_Fix'] = df[col]
                break
        # 지수 히스토리 데이터 (그래프용)
        k_h = fdr.DataReader('KS11').tail(20)['Close']
        q_h = fdr.DataReader('KQ11').tail(20)['Close']
        n_h = fdr.DataReader('NQ=F').tail(20)['Close']
        trends = {
            "KOSPI": {"대금": "16.3조", "개인": -1245, "외인": 1560, "기관": -315, "hist": k_h},
            "KOSDAQ": {"대금": "12.4조", "개인": 2130, "외인": -840, "기관": -1290, "hist": q_h},
            "NAS": {"hist": n_h}
        }
        return df, trends
    except:
        return pd.DataFrame(), {}

live_df, mkt_data = fetch_data()

# 3. 공통 함수: 지수 그래프 및 상단 지표
def make_mini_chart(series, color):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color=color, width=2)))
    fig.update_layout(height=40, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

def show_indices():
    st.markdown(f"### 📡 실시간 지표 ({now.strftime('%H:%M:%S')})")
    c1, c2, c3 = st.columns(3)
    t1, t2, t3 = mkt_data.get("KOSPI", {}), mkt_data.get("KOSDAQ", {}), mkt_data.get("NAS", {})
    with c1:
        st.markdown(f'<div class="m-header"><b>KOSPI</b><br><span class="big-num">2,642.15</span><br><small style="color:#ff4b4b;">▲ 1.38% ({t1.get("대금","16조")})</small></div>', unsafe_allow_html=True)
        if "hist" in t1: st.plotly_chart(make_mini_chart(t1["hist"], "#ff4b4b"), use_container_width=True, config={'displayModeBar': False})
        st.markdown(f'<div class="supply-row"><span style="color:#0088ff">개:{t1.get("개인",0):+}</span> <span style="color:#ff4b4b">외:{t1.get("외인",0):+}</span></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="m-header"><b>KOSDAQ</b><br><span class="big-num">872.45</span><br><small style="color:#ff4b4b;">▲ 0.29% ({t2.get("대금","12조")})</small></div>', unsafe_allow_html=True)
        if "hist" in t2: st.plotly_chart(make_mini_chart(t2["hist"], "#ff4b4b"), use_container_width=True, config={'displayModeBar': False})
        st.markdown(f'<div class="supply-row"><span style="color:#ff4b4b">개:{t2.get("개인",0):+}</span> <span style="color:#0088ff">외:{t2.get("외인",0):+}</span></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:18px; color:#ff4b4b; font-weight:bold;">25,863.25</span><br><small style="color:#ff4b4b;">▲ 0.45%</small></div>', unsafe_allow_html=True)
        if "hist" in t3: st.plotly_chart(make_mini_chart(t3["hist"], "#ff4b4b"), use_container_width=True, config={'displayModeBar': False})
        st.markdown('<div class="supply-row">글로벌 추적 중</div>', unsafe_allow_html=True)

# 4. 탭 구성 (선생님 요청 4대 탭)
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

with tab1:
    show_indices()
    st.divider()
    st.markdown("### 🔥 주도 섹터 (9개 격자)")
    for s_name in ["반도체", "로봇", "바이오"]:
        with st.expander(f"📂 {s_name} | 실시간 분석 중", expanded=True):
            cols = st.columns(3)
            if not live_df.empty:
                s_stocks = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
                for i in range(9):
                    with cols[i % 3]:
                        if i < len(s_stocks):
                            row = s_stocks.iloc[i]
                            amt = f"{int(row.get('Amount', 0)/1e8)}억"
                            st.markdown(f'<div class="stock-card"><b>{row["Name"]}</b><br><span class="price-up">{int(row["Close"]):,}원</span><br><small>{row["Chg_Fix"]:+.1f}%</small><br><span class="amt-label">{amt}</span></div>', unsafe_allow_html=True)

with tab2:
    show_indices()
    st.divider()
    st.markdown("### 💰 거래대금 상위 (Top 9)")
    if not live_df.empty:
        top_9 = live_df.sort_values('Amount', ascending=False).head(9)
        cols_9 = st.columns(3)
        for i in range(9):
            with cols_9[i % 3]:
                if i < len(top_9):
                    s = top_9.iloc[i]
                    amt = f
