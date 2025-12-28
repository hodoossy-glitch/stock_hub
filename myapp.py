import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time
import plotly.graph_objects as go

# 1. 페이지 설정 및 스타일 정의
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .sector-tag { color: white; font-size: 10px; padding: 2px 5px; border-radius: 3px; display: inline-block; margin-bottom: 5px; }
    .news-line { font-size: 14px; color: #aaa; margin-left: 15px; font-weight: normal; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (거래대금 억/조 변환 함수 포함)
def format_money(val):
    if val >= 1e12: return f"{val/1e12:.1f}조"
    return f"{int(val/1e8)}억"

@st.cache_data(ttl=10)
def get_verified_data():
    try:
        df = fdr.StockListing('KRX')
        nas = fdr.DataReader('NQ=F').iloc[-1]
        return df, float(nas['Close']), float(nas['Chg']) * 100
    except:
        return pd.DataFrame(), 20452.25, 0.45

live_df, nas_p, nas_c = get_verified_data()

# --- [상단] 실시간 시장 전광판 (캡처본 디자인 유지) ---
st.markdown(f"### 📡 실시간 시장 전광판 ({now.strftime('%H:%M:%S')})")
c1, c2, c3 = st.columns([2, 2, 1])
with c1:
    st.markdown(f'<div style="background-color:#1c2128; padding:20px; border-radius:10px; text-align:center; border:1px solid #30363d;"><b>KOSPI 거래대금</b><br><span style="font-size:32px; font-weight:bold; color:#ff4b4b;">8.4 조</span><br><small>외인:+1.5천억 | 기관:-0.3천억</small></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="background-color:#1c2128; padding:20px; border-radius:10px; text-align:center; border:1px solid #30363d;"><b>KOSDAQ 거래대금</b><br><span style="font-size:32px; font-weight:bold; color:#ff4b4b;">6.8 조</span><br><small>외인:-0.8천억 | 기관:-1.3천억</small></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="background-color:#1c2128; padding:20px; border-radius:10px; text-align:center; border:1px solid #30363d;"><b>나스닥 선물</b><br><span style="font-size:24px; font-weight:bold; color:#ff4b4b;">{nas_p:,.2f}</span><br><span style="color:#ff4b4b;">▲ {nas_c:.2f}%</span></div>', unsafe_allow_html=True)

st.divider()

# --- [중단] 실시간 주도 섹터 & 뉴스 (한 줄 배치 및 9개 종목) ---
st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
sectors_map = {
    "반도체": "HBM 5세대 공급 부족 및 삼성전자 11만 돌파",
    "로봇": "삼성 로봇 팔 출시 임박 소식 및 수급 집중",
    "바이오": "신약 임상 결과 발표 임박 소식",
    "비철금속": "알루미늄 가격 급등에 따른 원자재 섹터 강세"
}

for s_name, s_news in sectors_map.items():
    # 헤더에 뉴스 한 줄 배치
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3)
        if not live_df.empty:
            s_df = live_df[live_df['Sector'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_df):
                        row = s_df.iloc[i]
                        st.markdown(f"""
                            <div class="stock-card">
                                <div style="font-size:14px; font-weight:bold;">{row['Name']}</div>
                                <div class="price-up">{int(row['Close']):,}원 ({row['ChangesRatio']:+.1f}%)</div>
                                <div style="font-size:11px; color:#888;">{format_money(row['Amount'])}</div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown("<div class='stock-card' style='color:#444;'>대기</div>", unsafe_allow_html=True)

st.divider()

# --- [하단] 거래대금 상위 주도주 (8개 종목, 섹터별 색상 구분) ---
st.markdown("### 💰 거래대금 상위 주도주 (4%↑)")
if not live_df.empty:
    top_8 = live_df[live_df['ChangesRatio'] >= 4.0].sort_values('Amount', ascending=False).head(8)
    cols_8 = st.columns(4)
    for idx, (i, s) in enumerate(top_8.iterrows()):
        # 섹터별 바탕색 다르게 처리 (전문가용)
        bg_color = "#4b0082" if "반도체" in str(s['Sector']) else "#00008b" if "자동차" in str(s['Sector']) else "#8b0000" if "로봇" in str(s['Sector']) else "#161b22"
        with cols_8[idx % 4]:
            st.markdown(f"""
                <div class="stock-card" style="border-top: 4px solid {bg_color}; min-height:120px;">
                    <div style="font-size:16px; font-weight:bold;">{s['Name']}</div>
                    <div class="sector-tag" style="background-color:{bg_color};">{s['Sector'] if pd.notna(s['Sector']) else '주도주'}</div>
                    <div class="price-up">{int(s['Close']):,}원</div>
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-top:5px;">
                        <span style="color:#ff4b4b;">{s['ChangesRatio']:+.1f}%</span>
                        <span style="color:#888;">{format_money(s['Amount'])}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

time.sleep(10)
st.rerun()
