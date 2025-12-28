import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 테마 로직 (이미지 2, 3번 디자인 유지)
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# 색상 변수 (흰색 바탕에서도 어울리도록 세밀하게 조정)
bg_color = "#0e1117" if st.session_state.dark_mode else "#ffffff"
text_color = "#ffffff" if st.session_state.dark_mode else "#222222"
header_bg = "#1c2128" if st.session_state.dark_mode else "#f8f9fa"
card_bg = "#161b22" if st.session_state.dark_mode else "#ffffff"
border_color = "#30363d" if st.session_state.dark_mode else "#eeeeee"
btn_text = "🌙 다크모드" if not st.session_state.dark_mode else "☀️ 라이트모드"

# CSS 프레임 보존 및 모드 전환 버튼 우측 상단 고정
st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{ display: none; }}
    .stApp {{ background-color: {bg_color} !important; color: {text_color} !important; }}
    
    /* 모드 전환 버튼: 우측 상단 작게 배치 */
    .mode-btn {{ position: absolute; top: 10px; right: 10px; z-index: 1000; }}
    
    .m-header {{ background-color: {header_bg}; padding: 12px; border-radius: 12px; border: 1px solid {border_color}; text-align: center; margin-bottom: 5px; }}
    .big-num {{ font-size: 24px; font-weight: bold; color: #ff4b4b; }}
    .supply-row {{ font-size: 11px; display: flex; justify-content: center; gap: 10px; margin-top: 5px; border-top: 1px solid {border_color}; padding-top: 5px; }}
    
    .stock-card {{ background-color: {card_bg}; padding: 10px; border-radius: 10px; border: 1px solid {border_color}; text-align: center; min-height: 100px; }}
    .price-up {{ color: #ff4b4b; font-weight: bold; font-size: 16px; }}
    .amt-label {{ color: #888888; font-size: 10px; display: block; margin-top: 4px; }}
    
    .stTabs [data-baseweb="tab"] {{ color: {text_color} !important; font-weight: bold; }}
    </style>
    """, unsafe_allow_html=True)

# 모드 전환 버튼 구현
c1, c2 = st.columns(
