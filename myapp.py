import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 테마 전환 로직 (기존 다크 틀 보존)
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# 색상 변수 설정 (선생님의 기존 다크 모드 값 우선)
bg_color = "#0e1117" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#333333"
header_bg = "#1c2128" if st.session_state.dark_mode else "#f0f2f6"
card_bg = "#161b22" if st.session_state.dark_mode else "#ffffff"
border_color = "#30363d" if st.session_state.dark_mode else "#dddddd"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    /* 전체 배경 및 글자색 제어 */
    .stApp {{ background-color: {bg_color}; color: {text_color}; }}
    .main {{ background-color: {bg_color}; }}
    
    /* 선생님의 기존 헤더 스타일 보존 */
    .m-header {{ background-color: {header_bg}; padding: 12px; border-radius: 12px; border: 1px solid {border_color}; text-align: center; margin-bottom: 5px; color: {text_color}; }}
    .big-num {{ font-size: 22px; font-weight: bold; color: #ff4b4b; margin-bottom: 2px; }}
    .supply-row {{ font-size: 11px; display: flex; justify-content: center; gap: 5px; margin-top: 5px; border-top: 1px solid {border_color}; padding-top: 5px; }}
    
    /* 종목 카드 스타일 보존 및 대금 라벨 추가 */
    .stock-card {{ background-color: {card_bg}; padding: 10px; border-radius: 8px; border: 1px solid {border_color}; margin-bottom: 5px; text-align: center; min-height: 95px; color: {text_color}; }}
    .price-up {{ color: #ff4b4b; font-weight: bold; }}
    .amt-label {{ color: #888888; font-size: 10px; display: block; margin-top: 3px; }}
    
    /* 탭 메뉴 글자색 보정 */
    .stTabs [data-baseweb="tab"] {{ color: {text_color}; }}
    </style>
    """, unsafe_allow_html=True)

# 상단 모드 전환 스위치 (프레임 밖으로 배치)
c_m, _ = st.columns([1, 10])
with c_m:
    if st.button("🌓 모드전환"):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

# 2. 데이터 및 그래프 엔진
@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns: df['ChangesRatio'] = df[col]; break
        
        # 지수 히스토리 데이터
        k_h = fdr.DataReader('KS11').tail(20)['Close']
        q_h = fdr.DataReader('KQ11').tail(20)['Close']
        n_h = fdr.DataReader('NQ=F').tail(20)['Close']
        
        trends = {
            "KOSPI": {"대금": "16.3조", "개인": -1245, "외인": 1560, "hist": k_h},
            "KOSDAQ": {"대금": "12.4조", "개인": 2130, "외인": -840, "hist": q_h},
            "NAS": {"hist": n_h}
        }
        return df, trends
    except:
        return pd.DataFrame(), {}

live_df, mkt_data = fetch_data()

def make_mini_chart(series):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color='#ff4b4b', width=2)))
    fig.update_layout(height=45, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

# 3. 탭 구성 (기존 4대 탭 유지)
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

with tab1:
    st.markdown(f"### 📡 실시간 지표 ({now.strftime('%H:%M:%S')})")
    c1, c2, c3 = st.columns(3)
    t1, t2, t3 = mkt_data.get("KOSPI", {}), mkt_data.get("KOSDAQ", {}), mkt_data.get("NAS", {})
    
    with c1:
        st.markdown(f'<div class="m-header"><b>KOSPI</b><br><span class="big-num">2,642.15</span><br><small style="color:#ff4b4b;">▲ 1.38% ({t1.get("대금")})</small></div>', unsafe_allow_html=True)
        if "hist" in t1: st.plotly_chart(make_mini_chart(t1["hist"]), use_container_width=True, config={'displayModeBar': False})
        st.markdown(f'<div class="supply-row"><span style="color:#0088ff">
