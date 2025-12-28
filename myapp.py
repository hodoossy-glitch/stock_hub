import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 디자인 모드 선택 (다크/라이트)
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

# 상단 모드 전환 버튼
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

col_mode, _ = st.columns([1, 10])
with col_mode:
    if st.button("🌓 모드전환"):
        st.session_state.dark_mode = not st.session_state.dark_mode

# 테마 색상 설정
bg_color = "#0e1117" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#333333"
card_color = "#1c2128" if st.session_state.dark_mode else "#f8f9fa"
border_color = "#30363d" if st.session_state.dark_mode else "#eeeeee"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .main {{ background-color: {bg_color}; color: {text_color}; }}
    .m-header {{ background-color: {card_color}; padding: 12px; border-radius: 12px; border: 1px solid {border_color}; text-align: center; margin-bottom: 5px; }}
    .big-num {{ font-size: 22px; font-weight: bold; color: #ff4b4b; margin-bottom: 2px; }}
    .supply-row {{ font-size: 11px; display: flex; justify-content: center; gap: 5px; margin-top: 5px; border-top: 1px solid {border_color}; padding-top: 5px; }}
    .stock-card {{ background-color: {card_color}; padding: 10px; border-radius: 8px; border: 1px solid {border_color}; margin-bottom: 5px; text-align: center; min-height: 95px; }}
    .price-up {{ color: #ff4b4b; font-weight: bold; }}
    .amt-label {{ color: #888888; font-size: 10px; display: block; margin-top: 3px; }}
    .leader-item {{ display: flex; justify-content: space-between; align-items: center; padding: 12px; border-radius: 8px; margin-bottom: 8px; color: #000; font-weight: bold; font-size: 14px; }}
    .tag-bio {{ background-color: #d1f7d1; }} .tag-robot {{ background-color: #fff4cc; }} .tag-aero {{ background-color: #ffdce0; }}
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (그래프용 데이터 포함)
@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns:
                df['ChangesRatio'] = df[col]
                break
        
        # 그래프용 지수 데이터
        kospi_h = fdr.DataReader('KS11').tail(20)['Close']
        kosdaq_h = fdr.DataReader('KQ11').tail(20)['Close']
        nas_h = fdr.DataReader('NQ=F').tail(20)['Close']
        
        nas_df = fdr.DataReader('NQ=F')
        nas_last = nas_df.iloc[-1] if not nas_df.empty else None
        nas_chg = 0.45
        if len(nas_df) > 1:
            nas_chg = ((nas_df['Close'].iloc[-1] / nas_df['Close'].iloc[-2]) - 1) * 100
            
        trends = {
            "KOSPI": {"대금": "16.3조", "개인": -1245, "외인": 1560, "기관": -315, "hist": kospi_h},
            "KOSDAQ": {"대금": "12.4조", "개인": 2130, "외인": -840, "기관": -1290, "hist": kosdaq_h},
            "NAS": {"hist": nas_h}
        }
        return df, nas_last, nas_chg, trends
    except:
        return pd.DataFrame(), None, 0.45, {}

live_df, nas_data, n_c, mkt_trends = fetch_data()

# 지수 그래프 생성 함수
def make_mini_chart(series, color):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color=color, width=2)))
    fig.update_layout(height=45, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

# 3. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

# --- [탭 1] 주도섹터 ---
with tab1:
    st.markdown(f"### 📡 실시간 시장 지표 ({now.strftime('%H:%M:%S')})")
    c1, c2, c3 = st.columns(3)
    
    t1 = mkt_trends.get("KOSPI", {})
    with c1:
        st.markdown(f'<div class="m-header"><b>KOSPI</b><br><span class="big-num">2,642.15</span><br><small style="color:#ff4b4b;">▲ 1.38% ({t1.get("대금")})</small></div>', unsafe_allow_html=True)
        if "hist" in t1: st.plotly_chart(make_mini_chart(t1["hist"], "#ff4b4b"), use_container_width=True, config={'displayModeBar': False})
        st.markdown(f'<div class="supply-row"><span style="color:#0088ff">개:{t1.get("개인"):+}</span> <span style="color:#ff4b4b">외:{t1.get("외인"):+}</span></div>', unsafe_allow_html=True)
        
    t2 = mkt_trends.get("KOSDAQ", {})
    with c2:
        st.markdown(f'<div class="m-header"><b>KOSDAQ</b><br><span class="big-num">872.45</span><br><small style="color:#ff4b4b;">▲ 0.29% ({t2.get("대금")})</small></div>', unsafe_allow_html=True)
        if "hist" in t2: st.plotly_chart(make_mini_chart(t2["hist"], "#ff4b4b"), use_container_width=True, config={'displayModeBar': False})
        st.markdown(f'<div class="supply-row"><span style="color:#ff4b4b">개:{t2.get("개인"):+}</span> <span style="color:#0088ff">외:{t2.get("외인"):+}</span></div>', unsafe_allow_html=True)
        
    t3 = mkt_trends.get("NAS", {})
    with c3:
        n_p = nas_data['Close'] if nas_data is not None else 25863.25
        st.markdown(f'<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:20px; color:#ff4b4b; font-weight:bold;">{n_p:,.2f}</span><br><small style="color:#ff4b4b;">▲ {n_c:.2f}%</small></div>', unsafe_allow_html=True)
        if "hist" in t3: st.plotly_chart(make_mini_chart(t3["hist"], "#ff4b4b"), use_container_width=True, config={'displayModeBar': False})
        st.markdown('<div class="supply-row">글로벌 지수 실시간 추적</div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
    for s_name in ["반도체", "로봇", "바이오"]:
        with st.expander(f"📂 {s_name} | 관련 실시간 뉴스 대기 중", expanded=True):
            cols = st.columns(3)
            if not live_df.empty:
                s_stocks = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
                for i in range(9):
                    with cols[i % 3]:
                        if i < len(s_stocks):
                            row = s_stocks.iloc[i]
                            amt_val = f"{int(row.get('Amount', 0)/1e8)}억" if 'Amount' in row else "분석중"
                            st.markdown(f'''<div class="stock-card"><b>{row.get("Name")}</b><br>
                            <span class="price-up">{int(row.get("Close",0)):,}원</span><br>
                            <small>{row.get("ChangesRatio",0.0):+.1f}%</small>
                            <span class="amt-label">대금: {amt_val}</span></div>''', unsafe_allow_html=True)

# --- [탭 2] 대금상위 ---
with tab2:
    st.markdown("### 💰 거래대금 상위 4%↑ 주도주")
    top_stocks = [("삼성에피스", "바이오", "661,000", "+16.17%", "1.59조", "tag-bio"),
                  ("클로봇", "로봇", "65,200", "+26.85%", "9673억", "tag-robot"),
                  ("한화시스템", "우주항공", "53,100", "+10.51%", "3909억", "tag-aero")]
    for name, sector, price, chg, amt, tag in top_stocks:
        st.markdown(f'<div class="leader-item {tag}"><div>{name} <small>{sector}</small></div><div>{price} ({chg})</div><div>{amt}</div></div>', unsafe_allow_html=True)

# --- [탭 3 & 4] ---
with tab3: st.info("📅 캘린더 준비 중")
with tab4: st.info("📢 공지사항 준비 중")

time.sleep(10)
st.rerun()
