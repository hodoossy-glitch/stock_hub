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
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 및 그래프 엔진
@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns: df['Chg_Fix'] = df[col]; break
        
        # 지수 그래프용 20일 데이터
        kospi_h = fdr.DataReader('KS11').tail(20)['Close']
        kosdaq_h = fdr.DataReader('KQ11').tail(20)['Close']
        nas_h = fdr.DataReader('NQ=F').tail(20)['Close']
        
        trends = {
            "KOSPI": {"대금": "16.3조", "개인": -1245, "외인": 1560, "기관": -315, "hist": kospi_h},
            "KOSDAQ": {"대금": "12.4조", "개인": 2130, "외인": -840, "기관": -1290, "hist": kosdaq_h},
            "NAS": {"hist": nas_h}
        }
        return df, trends
    except:
        return pd.DataFrame(), {}

live_df, mkt_data = fetch_data()

# 3. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

def make_mini_chart(series, color):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color=color, width=2)))
    fig.update_layout(height=50, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

def show_market_with_charts():
    st.markdown(f"### 📡 실시간 시장 지표 ({now.strftime('%H:%M:%S')})")
    c1, c2, c3 = st.columns(3)
    t1, t2,
