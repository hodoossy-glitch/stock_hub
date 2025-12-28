import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 디자인 스타일 (이미지 1, 2, 3 통합)
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #f8f9fa; color: #333; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #fff; padding: 5px; border-bottom: 1px solid #eee; }
    .stTabs [data-baseweb="tab"] { height: 45px; font-weight: bold; font-size: 16px; color: #888; }
    .stTabs [aria-selected="true"] { color: #000 !important; border-bottom: 3px solid #ff4b4b !important; }
    
    .color-card { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; border-radius: 10px; margin-bottom: 8px; font-weight: bold; font-size: 14px; border: 1px solid rgba(0,0,0,0.05); }
    .tag-bio { background-color: #d1f7d1; color: #006400; }
    .tag-robot { background-color: #fff4cc; color: #856404; }
    .tag-aero { background-color: #ffdce0; color: #a94442; }
    
    .m-header { background-color: #fff; padding: 15px; border-radius: 12px; border: 1px solid #eee; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .big-num { font-size: 24px; font-weight: bold; color: #ff4b4b; margin: 5px 0; }
    .supply-info { font-size: 11px; color: #666; display: flex; justify-content: center; gap: 8px; margin-top: 8px; border-top: 1px solid #f1f1f1; padding-top: 8px; }
    .stock-grid-card { background-color: #fff; padding: 10px; border-radius: 8px; border: 1px solid #eee; text-align: center; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 엔진 (에러 차단 로직)
@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        c = df.columns
        df['Chg_Fix'] = df['ChangesRatio'] if 'ChangesRatio' in c else (df['Chg'] if 'Chg' in c else 0.0)
        df['Amt_Fix'] = df['Amount'] if 'Amount' in c else (df['MarCap'] if 'MarCap' in c else 0)
        
        k_h = fdr.DataReader('KS11').tail(20)['Close']
        q_h = fdr.DataReader('KQ11').tail(20)['Close']
        
        trends = {
            "KOSPI": {"대금": "16.3조", "개인": -1245, "외인": 1560, "기관": -315, "hist": k_h, "val": 2642.15, "chg": 1.38},
            "KOSDAQ": {"대금": "12.4조", "개인": 2130, "외인": -840, "기관": -1290, "hist": q_h, "val": 872.45, "chg": 0.29}
        }
        return df, trends
    except:
        return pd.DataFrame(), {}

live_df, mkt_data = fetch_data()

def draw_chart(series):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color='#ff4b4b', width=2)))
    fig.update_layout(height=60, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

# 3. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

with tab1:
    st.markdown("### 🔥 주도 섹터 & 뉴스")
    for s_name, s_news in [("반도체", "삼성전자 HBM 공급망 확대..."), ("로봇", "대기업 로봇 투자 본격화")]:
        with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
            cols = st.columns(3)
            if not live_df.empty:
                s_stocks = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amt_Fix', ascending=False).head(9)
                for i in range(9):
                    with cols[i % 3]:
                        if i < len(s_stocks):
                            row = s_stocks.iloc[i]
                            st.markdown(f'<div class="stock-grid-card"><b>{row["Name"]}</b><br><span style="color:#ff4b4b;">{int(row["Close"]):,}</span><br><small>{row["Chg_Fix"]:+.1f}%</small></div>', unsafe_allow_html=True)

with tab2:
    st.markdown("### 💰 거래대금 상위 4%↑")
    # 에러가 났던 수동 입력 구간을 제거하고 실시간 데이터로 자동 배치
    if not live_df.empty:
        top_9 = live_df.sort_values('Amt_Fix', ascending=False).head(9)
        # 이미지 1 스타일로 구현
        for i in range(len(top_9)):
            row = top_9.iloc[i]
            tag = "tag-bio" if i % 3 == 0 else ("tag-robot" if i % 3 == 1 else "tag-aero")
            st.markdown(f'<div class="color-card {tag}"><div>{row["Name"]}</div><div>{int(row["Close"]):,}</div><div>{int(row["Amt_Fix"]/1e8)}억</div></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📊 시장 지표")
    c1, c2 = st.columns(2)
    for idx, m_key in enumerate(["KOSPI", "KOSDAQ"]):
        t = mkt_data.get(m_key, {})
        with [c1, c2][idx]:
            st.markdown(f'<div class="m-header"><b>{m_key}</b><br><span class="big-num">{t.get("val")}</span> <small style="color:#ff4b4b;">▲ {t.get("chg")}%</small></div>', unsafe_allow_html=True)
            if "hist" in t: st.plotly_chart(draw_chart(t["hist"]), use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'<div class="supply-info">개:{t.get("개인"):+} 외:{t.get("외인"):+}</div>', unsafe_allow_html=True)

with tab3: st.info("📅 일정 캘린더 준비 중")
with tab4: st.info("📢 공시 정보 대기 중")

time.sleep(10)
st.rerun()
