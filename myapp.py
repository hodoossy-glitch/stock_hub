import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 디자인 (선생님의 다크 프레임 100% 보존)
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# 테마 색상 변수 설정
bg_color = "#0e1117" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#222222"
header_bg = "#1c2128" if st.session_state.dark_mode else "#f8f9fa"
card_bg = "#161b22" if st.session_state.dark_mode else "#ffffff"
border_color = "#30363d" if st.session_state.dark_mode else "#eeeeee"

st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    /* 우측 상단 모드 전환 버튼 (작고 심플하게) */
    .stButton > button {{ 
        position: fixed; top: 5px; right: 5px; z-index: 1000; 
        padding: 0px 5px; font-size: 10px; background: transparent; color: #888; border: 1px solid #444;
    }}
    .m-header {{ background-color: {header_bg}; padding: 10px; border-radius: 12px; border: 1px solid {border_color}; text-align: center; margin-bottom: 5px; }}
    .big-num {{ font-size: 24px; font-weight: bold; color: #ff4b4b; }}
    .stock-card {{ background-color: {card_bg}; padding: 10px; border-radius: 10px; border: 1px solid {border_color}; text-align: center; min-height: 100px; }}
    .price-up {{ color: #ff4b4b; font-weight: bold; font-size: 16px; }}
    .amt-label {{ color: #888888; font-size: 10px; display: block; margin-top: 4px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 수집 엔진 (3초 갱신 + 중괄호 에러 해결)
@st.cache_data(ttl=3)
def fetch_market_realtime():
    try:
        # KRX 종목 리스트 실시간 수집
        df = fdr.StockListing('KRX')
        target_col = None
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Change']:
            if col in df.columns:
                target_col = col
                break
        df['Chg_Fix'] = df[target_col] if target_col else 0.0
        
        # 지수 실시간 데이터
        ks = fdr.DataReader('KS11').tail(20)
        kq = fdr.DataReader('KQ11').tail(20)
        
        # [에러 해결] m_data 중괄호 및 내부 짝을 정확하게 닫았습니다.
        m_data = {
            "KOSPI": {
                "val": ks['Close'].iloc[-1], 
                "chg": ((ks['Close'].iloc[-1]/ks['Close'].iloc[-2])-1)*100, 
                "hist": ks['Close']
            },
            "KOSDAQ": {
                "val": kq['Close'].iloc[-1], 
                "chg": ((kq['Close'].iloc[-1]/kq['Close'].iloc[-2])-1)*100, 
                "hist": kq['Close']
            }
        }
        return df, m_data
    except:
        return pd.DataFrame(), {}

# 모드 전환 버튼
btn_label = "🌙" if not st.session_state.dark_mode else "☀️"
if st.button(btn_label):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()
