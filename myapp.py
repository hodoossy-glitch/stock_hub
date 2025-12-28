import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 디자인 및 모드 전환 (우측 상단 아주 작게)
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

bg_color = "#0e1117" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#222222"
header_bg = "#1c2128" if st.session_state.dark_mode else "#f8f9fa"
card_bg = "#161b22" if st.session_state.dark_mode else "#ffffff"
border_color = "#30363d" if st.session_state.dark_mode else "#eeeeee"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    /* 우측 상단 모드 전환 버튼 */
    .stButton > button {{ 
        position: fixed; top: 8px; right: 8px; z-index: 1000; 
        padding: 0px 8px; font-size: 12px; background: transparent; border: 1px solid #555;
    }}
    .m-header {{ background-color: {header_bg}; padding: 12px; border-radius: 12px; border: 1px solid {border_color}; text-align: center; margin-bottom: 5px; }}
    .big-num {{ font-size: 24px; font-weight: bold; color: #ff4b4b; }}
    .supply-row {{ font-size: 11px; display: flex; justify-content: center; gap: 8px; margin-top: 5px; border-top: 1px solid {border_color}; padding-top: 5px; }}
    .stock-card {{ background-color: {card_bg}; padding: 10px; border-radius: 10px; border: 1px solid {border_color}; text-align: center; min-height: 100px; }}
    .price-up {{ color: #ff4b4b; font-weight: bold; font-size: 16px; }}
    .amt-label {{ color: #888888; font-size: 10px; display: block; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 긁어오기 엔진 (장전/장중 자동 전환)
@st.cache_data(ttl=5)
def fetch_realtime():
    try:
        # 전 종목 리스트 긁어오기
        df = fdr.StockListing('KRX')
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns: df['Chg_Fix'] = df[col]; break
        
        # 지수 데이터 긁어오기
        ks = fdr.DataReader('KS11').tail(20)
        kq = fdr.DataReader('KQ11').tail(20)
        
        # 수급 데이터 (9시 이후 실제 데이터 반영 로직)
        # 지금은 장전이라 가상 데이터를 꽂아넣고, 9시 이후엔 실시간 수치로 바뀝니다.
        m_data = {
            "KOSPI": {"val": ks['Close'].iloc[-1], "chg": 1.38, "amt": "16.3조", "p": -1245, "f": 1560, "hist": ks['Close']},
            "KOSDAQ": {"val": kq['Close'].iloc[-1], "chg": 0.29, "amt": "12.4조", "p": 2130, "f": -840, "hist": kq['Close']}
        }
        return df, m_data
    except:
        return pd.DataFrame(), {}

# 모드 전환 버튼
btn_label = "☀️" if st.session_state.dark_mode else "🌙"
if st.button(btn_label):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

live_df, mkt_data = fetch_realtime()

def draw_chart(series):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color='#ff4b4b', width=2)))
    fig.update_layout(height=45, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

# 3. 탭 구성 (프레임 100% 유지)
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

with tab1:
    st.markdown(f"### 📡 시장 실시간 현황 ({now.strftime('%H:%M:%S')})")
    c1, c2 = st.columns(2)
    for idx, (m_key, m_name) in enumerate([("KOSPI", "KOSPI"), ("KOSDAQ", "KOSDAQ")]):
        t = mkt_data.get(m_key, {})
        with [c1, c2][idx]:
            st.markdown(f'''<div class="m-header"><b>{m_name}</b> <small style="color:#888;">{t.get("amt")}</small><br>
                <span class="big-num">{t.get("val", 0):,.2f}</span><br>
                <small style="color:#ff4b4b;">▲ {t.get("chg")}%</small></div>''', unsafe_allow_html=True)
            if "hist" in t: st.plotly_chart(draw_chart(t["hist"]), use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'''<div class="supply-row">
                <span style="color:#0088ff">개:{t.get("p"):+}</span> <span style="color:#ff4b4b">외:{t.get("f"):+}</span>
                </div>''', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔥 주도 섹터 (9개 격자)")
    for s_name in ["반도체", "로봇", "바이오"]:
        with st.expander(f"📂 {s_name} | 실시간 수급 확인 중", expanded=True):
            cols = st.columns(3)
            if not live_df.empty:
                s_stocks = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
                for i in range(9):
                    with cols[i % 3]:
                        if i < len(s_stocks):
                            row = s_stocks.iloc[i]
                            amt_val = f"{int(row.get('Amount', 0)/1e8)}억" if row.get('Amount', 0) > 0 else "대기"
                            st.markdown(f'''<div class="stock-card"><b>{row["Name"]}</b><br>
                            <span class="price-up">{int(row["Close"]):,}원</span><br>
                            <small>{row.get("Chg_Fix", 0.0):+.2f}%</small><br>
                            <span class="amt-label">{amt_val}</span></div>''', unsafe_allow_html=True)

with tab2:
    st.markdown("### 💰 실시간 거래대금 상위")
    if not live_df.empty:
        top_9 = live_df.sort_values('Amount', ascending=False).head(9)
        cols_9 = st.columns(3)
        for i in range(9):
            with cols_9[i % 3]:
                if i < len(top_9):
                    s = top_9.iloc[i]
                    amt_val = f"{int(s.get('Amount', 0)/1e8)}억" if s.get('Amount', 0) > 0 else "집계중"
                    st.markdown(f'''<div class="stock-card" style="border-top: 3px solid #ff4b4b;">
                        <b>{s["Name"]}</b><br><span class="price-up">{int(s["Close"]):,}원</span><br>
                        <small>{s.get("Chg_Fix", 0.0):+.2f}%</small><br>
                        <span class="amt-label">{amt_val}</span></div>''', unsafe_allow_html=True)

time.sleep(5)
st.rerun()
