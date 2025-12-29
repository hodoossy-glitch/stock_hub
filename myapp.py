import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 전문가용 다크 스타일 유지
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
    .stButton > button {{ position: fixed; top: 5px; right: 5px; z-index: 1000; padding: 2px 5px; font-size: 10px; background: transparent; border: 1px solid #444; }}
    .m-header {{ background-color: {header_bg}; padding: 10px; border-radius: 12px; border: 1px solid {border_color}; text-align: center; margin-bottom: 5px; }}
    .big-num {{ font-size: 24px; font-weight: bold; color: #ff4b4b; }}
    .stock-card {{ background-color: {card_bg}; padding: 10px; border-radius: 10px; border: 1px solid {border_color}; text-align: center; min-height: 100px; }}
    .price-up {{ color: #ff4b4b; font-weight: bold; font-size: 16px; }}
    .amt-label {{ color: #888888; font-size: 10px; display: block; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (강제 갱신 로직 추가)
# 캐시 시간을 1초로 줄여 거의 실시간으로 서버를 때리게 만듭니다.
@st.cache_data(ttl=1) 
def fetch_now_data_forced():
    try:
        # 전종목 실시간 스캔 (데이터가 안 변할 경우를 대비해 랜덤 시간 인자 추가 효과)
        df = fdr.StockListing('KRX')
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns:
                df['Chg_Fix'] = df[col]
                break
        
        # 지수 데이터 긁기
        ks = fdr.DataReader('KS11').tail(20)
        kq = fdr.DataReader('KQ11').tail(20)
        
        m_data = {
            "KOSPI": {"val": ks['Close'].iloc[-1], "chg": ((ks['Close'].iloc[-1]/ks['Close'].iloc[-2])-1)*100, "hist": ks['Close']},
            "KOSDAQ": {"val": kq['Close'].iloc[-1], "chg": ((kq['Close'].iloc[-1]/kq['Close'].iloc[-2])-1)*100, "hist": kq['Close']}
        }
        return df, m_data
    except Exception as e:
        # 에러 발생 시 빈 값을 보내지 않고 연결 재시도 유도
        return None, {}

# 모드 전환 버튼
btn_label = "☀️" if st.session_state.dark_mode else "🌙"
if st.button(btn_label):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

live_df, mkt_data = fetch_now_data_forced()

# 데이터가 제대로 안 긁혔을 경우 사용자 알림
if live_df is None:
    st.warning("🔄 서버 응답 지연 중입니다. 잠시만 기다려주세요...")
    time.sleep(2)
    st.rerun()

def draw_chart(series):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color='#ff4b4b', width=2)))
    fig.update_layout(height=45, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

# 3. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

with tab1:
    st.markdown(f"### 📡 실시간 지표 ({now.strftime('%H:%M:%S')})")
    c1, c2 = st.columns(2)
    for idx, (m_key, m_name) in enumerate([("KOSPI", "KOSPI"), ("KOSDAQ", "KOSDAQ")]):
        t = mkt_data.get(m_key, {})
        with [c1, c2][idx]:
            st.markdown(f'''<div class="m-header"><b>{m_name}</b><br><span class="big-num">{t.get("val", 0):,.2f}</span><br>
                <small style="color:#ff4b4b;">▲ {t.get("chg", 0):.2f}%</small></div>''', unsafe_allow_html=True)
            if "hist" in t: st.plotly_chart(draw_chart(t["hist"]), use_container_width=True, config={'displayModeBar': False})

    st.divider()
    st.markdown("### 🔥 섹터 주도주 (실시간 9격자)")
    for s_name in ["반도체", "로봇", "바이오"]:
        with st.expander(f"📂 {s_name} | 실시간 수급 포착", expanded=True):
            cols = st.columns(3)
            if not live_df.empty:
                s_stocks = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
                for i in range(len(s_stocks)):
                    with cols[i % 3]:
                        row = s_stocks.iloc[i]
                        amt = f"{int(row.get('Amount', 0)/1e8)}억"
                        st.markdown(f'''<div class="stock-card"><b>{row["Name"]}</b><br>
                        <span class="price-up">{int(row["Close"]):,}원</span><br>
                        <small>{row.get("Chg_Fix", 0.0):+.2f}%</small><br>
                        <span class="amt-label">대금: {amt}</span></div>''', unsafe_allow_html=True)

with tab2:
    st.markdown("### 💰 거래대금 상위 Top 9")
    if not live_df.empty:
        top_9 = live_df.sort_values('Amount', ascending=False).head(9)
        cols_9 = st.columns(3)
        for i in range(len(top_9)):
            with cols_9[i % 3]:
                s = top_9.iloc[i]
                amt = f"{int(s.get('Amount', 0)/1e8):,}억"
                st.markdown(f'''<div class="stock-card" style="border-top: 3px solid #ff4b4b;">
                    <b>{s["Name"]}</b><br><span class="price-up">{int(s["Close"]):,}원</span><br>
                    <small>{s.get("Chg_Fix", 0.0):+.2f}%</small><br>
                    <span class="amt-label">대금: {amt}</span></div>''', unsafe_allow_html=True)

time.sleep(1) # 1초 대기 후 즉시 재실행
st.rerun()
