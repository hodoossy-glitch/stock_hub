import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time
import plotly.graph_objects as go

# 1. 페이지 설정 및 디자인 복구
st.set_page_config(page_title="황금키 통합 전광판", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #161b22; padding: 12px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 8px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 16px; }
    .info-box { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; font-size: 13px; text-align: center; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (최적화)
@st.cache_data(ttl=10)
def fetch_realtime():
    try:
        df = fdr.StockListing('KRX')
        return df if df is not None and not df.empty else None
    except:
        return None

live_data = fetch_realtime()

# --- [상단] 주도 섹터 레이더 (선생님이 극찬하신 그 디자인) ---
st.markdown(f"### 🔥 주도 섹터 실시간 레이더 ({now.strftime('%H:%M:%S')})")

sectors = {
    "반도체": "HBM 5세대 공급 부족 및 실시간 수급 폭발",
    "비철금속": "알루미늄 가격 급등에 따른 섹터 강세",
    "바이오": "신약 임상 결과 발표 임박 소식",
    "핸드셋": "온디바이스 AI 채택 기기 확대 전망"
}

for s_name, s_news in sectors.items():
    with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
        cols = st.columns(3) # 요청하신 대로 3열 구성 (총 9개 종목용)
        
        # 실제 데이터에서 해당 섹터 종목 추출
        if live_data is not None:
            # 섹터명이 포함된 상위 9개 종목 추출
            s_df = live_data[live_data['Sector'].str.contains(s_name, na=False)].head(9)
            
            for idx in range(9):
                with cols[idx % 3]:
                    if idx < len(s_df):
                        row = s_df.iloc[idx]
                        amt = f"{int(row['Amount']/1e8)}억"
                        st.markdown(f"""
                            <div class="stock-card">
                                <div style="font-size:14px; font-weight:bold;">{row['Name']}</div>
                                <div class="price-up">{int(row['Close']):,}원 (+{row['ChangesRatio']}%)</div>
                                <div style="font-size:11px; color:#888;">{amt}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        # 데이터 대기 중일 때 빈 칸 채우기
                        st.markdown("<div class='stock-card' style='color:#444;'>데이터 대기 중</div>", unsafe_allow_html=True)
        else:
            st.write("실시간 시세 연결 대기 중...")

st.divider()

# --- [하단] 시장 지표 (요청하신 좌우 배치) ---
c_left, c_right = st.columns(2)

with c_left:
    st.markdown("#### 📉 국내 수급 현황")
    m1, m2 = st.columns(2)
    with m1:
        st.write("KOSPI (조)")
        fig1 = go.Figure(go.Indicator(mode="number", value=8.4, number={'suffix':"조", 'font':{'color':'#ff4b4b'}}))
        fig1.update_layout(height=120, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="#0e1117")
        st.plotly_chart(fig1, use_container_width=True)
    with m2:
        st.write("KOSDAQ (조)")
        fig2 = go.Figure(go.Indicator(mode="number", value=6.8, number={'suffix':"조", 'font':{'color':'#ff4b4b'}}))
        fig2.update_layout(height=120, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="#0e1117")
        st.plotly_chart(fig2, use_container_width=True)
    st.markdown("<div class='info-box'><b>매매동향:</b> 외인(+1500억) 기관(-300억) 개인(-1200억)</div>", unsafe_allow_html=True)

with c_right:
    st.markdown("#### 🌐 글로벌 지표")
    st.markdown(f"""
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px;'>
            <div class='info-box'><b>미국 USD</b><br><span style='color:#0088ff;'>1,445.00 (▼5.0)</span></div>
            <div class='info-box'><b>나스닥 선물</b><br><span class='price-up'>20,452.25 (+0.45%)</span></div>
            <div class='info-box'><b>WTI 유가</b><br><span style='color:#0088ff;'>56.74 (▼1.6)</span></div>
            <div class='info-box'><b>국제 금</b><br><span class='price-up'>4,552.70 (▲49.9)</span></div>
        </div>
        """, unsafe_allow_html=True)

# 자동 리로드
time.sleep(10)
st.rerun()
