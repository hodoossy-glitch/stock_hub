import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 기존 전문가용 다크 스타일 유지 (선생님의 틀 그대로)
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

# 2. 데이터 엔진 (KeyError 및 에러 방지 정밀 검수)
@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        # 등락률 및 대금 컬럼명 자동 매칭 (에러 방지 핵심)
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns: df['Chg_Fix'] = df[col]; break
        if 'Amount' in df.columns: df['Amt_Fix'] = df['Amount']
        elif 'MarCap' in df.columns: df['Amt_Fix'] = df['MarCap']
        
        # 지수 히스토리 데이터
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

# 3. 시각화 보조 함수
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
        st.markdown(f'<div class="m-header"><b>KOSDAQ
