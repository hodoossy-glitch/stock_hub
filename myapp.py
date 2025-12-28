import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 테마 로직 (우측 상단 아주 작은 버튼)
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

bg_color = "#0e1117" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#222222"
header_bg = "#1c2128" if st.session_state.dark_mode else "#f8f9fa"
card_bg = "#161b22" if st.session_state.dark_mode else "#ffffff"
border_color = "#30363d" if st.session_state.dark_mode else "#eeeeee"
btn_label = "🌙" if not st.session_state.dark_mode else "☀️"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    /* 우측 상단 초소형 버튼 스타일 */
    .stButton > button {{ 
        position: fixed; top: 5px; right: 5px; z-index: 1000; 
        padding: 0px 5px; font-size: 12px; background: transparent; border: 1px solid #555;
    }}
    .m-header {{ background-color: {header_bg}; padding: 12px; border-radius: 12px; border: 1px solid {border_color}; text-align: center; margin-bottom: 5px; }}
    .big-num {{ font-size: 24px; font-weight: bold; color: #ff4b4b; }}
    .supply-row {{ font-size: 11px; display: flex; justify-content: center; gap: 10px; margin-top: 5px; border-top: 1px solid {border_color}; padding-top: 5px; }}
    .stock-card {{ background-color: {card_bg}; padding: 10px; border-radius: 10px; border: 1px solid {border_color}; text-align: center; min-height: 100px; }}
    .price-up {{ color: #ff4b4b; font-weight: bold; font-size: 16px; }}
    .amt-label {{ color: #888888; font-size: 10px; display: block; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (강제 새로고침 기능 추가)
@st.cache_data(ttl=3) # 3초 주기로 더 빠르게 갱신
def fetch_realtime_all():
    try:
        # 전체 종목 리스트 (데이터가 0일 경우 대비해 빈 값 방어)
        df = fdr.StockListing('KRX')
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns: df['Chg_Fix'] = df[col]; break
        
        # 지수 히스토리 및 현재가
        kospi = fdr.DataReader('KS11').tail(30)
        kosdaq = fdr.DataReader('KQ11').tail(30)
        nasdaq = fdr.DataReader('NQ=F').tail(30)
        
        trends = {
            "KOSPI": {"val": kospi['Close'].iloc[-1], "chg": ((kospi['Close'].iloc[-1]/kospi['Close'].iloc[-2])-1)*100, "hist": kospi['Close'], "amt": "장준비중", "p": 0, "f": 0},
            "KOSDAQ": {"val": kosdaq['Close'].iloc[-1], "chg": ((kosdaq['Close'].iloc[-1]/kosdaq['Close'].iloc[-2])-1)*100, "hist": kosdaq['Close'], "amt": "장준비중", "p": 0, "f": 0},
            "NAS": {"val": nasdaq['Close'].iloc[-1], "chg": ((nasdaq['Close'].iloc[-1]/nasdaq['Close'].iloc[-2])-1)*100, "hist": nasdaq['Close']}
        }
        return df, trends
    except:
        return pd.DataFrame(), {}

# 모드 전환 버튼
if st.button(btn_label):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

live_df, mkt_data = fetch_realtime_all()

def draw_chart(series):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color='#ff4b4b', width=2)))
    fig.update_layout(height=45, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

# 3. 탭 구성 (선생님 요청 프레임 100% 유지)
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

with tab1:
    st.markdown(f"### 📡 실시간 지표 ({now.strftime('%H:%M:%S')})")
    c1, c2, c3 = st.columns(3)
    for idx, (m_key, m_name) in enumerate([("KOSPI", "KOSPI"), ("KOSDAQ", "KOSDAQ"), ("NAS", "나스닥선물")]):
        t = mkt_data.get(m_key, {})
        with [c1, c2, c3][idx]:
            val = t.get("val", 0)
            st.markdown(f'''<div class="m-header"><b>{m_name}</b><br><span class="big-num">{val:,.2f}</span><br>
                <small style="color:#ff4b4b;">▲ {t.get("chg", 0):.2f}% ({t.get("amt")})</small></div>''', unsafe_allow_html=True)
            if "hist" in t: st.plotly_chart(draw_chart(t["hist"]), use_container_width=True, config={'displayModeBar': False})
            if "p" in t:
                st.markdown(f'<div class="supply-row"><span style="color:#0088ff">개:{t["p"]:+}</span> <span style="color:#ff4b4b">외:{t["f"]:+}</span></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔥 실시간 주도 섹터 (9개 격자)")
    for s_name in ["반도체", "로봇", "바이오"]:
        with st.expander(f"📂 {s_name} | 분석 중", expanded=True):
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
    st.markdown("### 💰 거래대금 상위 주도주")
    if not live_df.empty:
        top_9 = live_df.sort_values('Amount', ascending=False).head(9)
        cols_9 = st.columns(3)
        for i in range(9):
            with cols_9[i % 3]:
                if i < len(top_9):
                    s = top_9.iloc[i]
                    amt_val = f"{int(s.get('Amount', 0)/1e8):,}억" if s.get('Amount', 0) > 0 else "집계중"
                    st.markdown(f'''<div class="stock-card" style="border-top: 3px solid #ff4b4b;">
                        <b>{s["Name"]}</b><br><span class="price-up">{int(s["Close"]):,}원</span><br>
                        <small>{s.get("Chg_Fix", 0.0):+.2f}%</small><br>
                        <span class="amt-label">{amt_val}</span></div>''', unsafe_allow_html=True)

with tab3: st.info("📅 오늘의 주요 증시 일정입니다.")
with tab4: st.info("📢 실시간 주요 공시입니다.")

time.sleep(3)
st.rerun()
