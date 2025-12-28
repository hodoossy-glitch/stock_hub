import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import plotly.graph_objects as go
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 모바일 전문가용 스타일 (이미지 1, 2, 3 디자인 통합)
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #f8f9fa; color: #333; }
    /* 상단 탭 스타일 */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background-color: #fff; padding: 5px; border-bottom: 1px solid #eee; }
    .stTabs [data-baseweb="tab"] { height: 45px; font-weight: bold; font-size: 16px; color: #888; }
    .stTabs [aria-selected="true"] { color: #000 !important; border-bottom: 3px solid #ff4b4b !important; }
    
    /* 이미지 1: 컬러 주도주 카드 스타일 */
    .color-card { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; border-radius: 10px; margin-bottom: 8px; font-weight: bold; font-size: 14px; border: 1px solid rgba(0,0,0,0.05); }
    .tag-bio { background-color: #d1f7d1; color: #006400; }
    .tag-robot { background-color: #fff4cc; color: #856404; }
    .tag-aero { background-color: #ffdce0; color: #a94442; }
    .tag-atomic { background-color: #e8dff5; color: #4b0082; }
    
    /* 이미지 1 & 3: 지수 및 그래프 박스 스타일 */
    .m-header { background-color: #fff; padding: 15px; border-radius: 12px; border: 1px solid #eee; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .big-num { font-size: 24px; font-weight: bold; color: #ff4b4b; margin: 5px 0; }
    .supply-info { font-size: 11px; color: #666; display: flex; justify-content: center; gap: 8px; margin-top: 8px; border-top: 1px solid #f1f1f1; padding-top: 8px; }
    
    /* 이미지 2: 뉴스 결합형 섹션 스타일 */
    .stock-grid-card { background-color: #fff; padding: 10px; border-radius: 8px; border: 1px solid #eee; text-align: center; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 무적 데이터 엔진 (KeyError 및 복사 에러 방지)
@st.cache_data(ttl=10)
def fetch_all_data():
    try:
        df = fdr.StockListing('KRX')
        c = df.columns
        df['Chg_Fix'] = df['ChangesRatio'] if 'ChangesRatio' in c else (df['Chg'] if 'Chg' in c else 0.0)
        df['Amt_Fix'] = df['Amount'] if 'Amount' in c else (df['MarCap'] if 'MarCap' in c else 0)
        
        # 지수 히스토리 (이미지 속 꺾은선 그래프용)
        k_h = fdr.DataReader('KS11').tail(20)['Close']
        q_h = fdr.DataReader('KQ11').tail(20)['Close']
        
        trends = {
            "KOSPI": {"대금": "16.3조", "개인": -1245, "외인": 1560, "기관": -315, "hist": k_h, "val": 2642.15, "chg": 1.38},
            "KOSDAQ": {"대금": "12.4조", "개인": 2130, "외인": -840, "기관": -1290, "hist": q_h, "val": 872.45, "chg": 0.29}
        }
        return df, trends
    except:
        return pd.DataFrame(), {}

live_df, mkt_data = fetch_all_data()

# 3. 그래프 드로잉 함수
def draw_chart(series):
    fig = go.Figure(data=go.Scatter(y=series, mode='lines', line=dict(color='#ff4b4b', width=2)))
    fig.update_layout(height=60, margin=dict(l=0,r=0,t=0,b=0), xaxis_visible=False, yaxis_visible=False, 
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    return fig

# 4. 탭 구성 (선생님 요청 4대 메뉴)
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

# --- [탭 1] 주도섹터 (이미지 2: 뉴스+종목 격자 스타일) ---
with tab1:
    st.markdown("### 🔥 주도 섹터 & 뉴스")
    sections = [
        ("반도체", "삼성전자 HBM3E 공급 본격화... 수혜주 강세"),
        ("로봇", "K-로봇 관절 기술 세계 시장 석권... 대기업 투자 가속")
    ]
    for s_name, s_news in sections:
        with st.expander(f"📂 {s_name} | {s_news}", expanded=True):
            cols = st.columns(3)
            if not live_df.empty:
                s_stocks = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amt_Fix', ascending=False).head(9)
                for i in range(9):
                    with cols[i % 3]:
                        if i < len(s_stocks):
                            row = s_stocks.iloc[i]
                            st.markdown(f'''<div class="stock-grid-card"><b>{row["Name"]}</b><br>
                            <span style="color:#ff4b4b;">{int(row["Close"]):,}</span><br>
                            <small>{row["Chg_Fix"]:+.1f}%</small></div>''', unsafe_allow_html=True)

# --- [탭 2] 대금상위 (이미지 1: 컬러 리스트 + 지수 그래프 스타일) ---
with tab2:
    st.markdown("### 💰 거래대금 상위 4%↑ 상승종목")
    sample_top = [
        ("삼성에피스", "바이오", "661,000", "+16.17%", "1.59조", "tag-bio"),
        ("클로봇", "로봇", "65,200", "+26.85%", "9673억", "tag-robot"),
        ("한화시스템", "우주항공", "53,100", "+10.51%", "3909억", "tag-aero"),
        ("비에이치아이", "원전", "64,200", "+21.82%", "4882억", "tag-atomic")
    ]
    for name, sector, price, chg, amt, tag in sample_top:
        st.markdown(f'<div class="color-card {tag}"><div style="flex:1.5;">{name} <small style="opacity:0.7;">{sector}</small></div><div style="flex:1; text-align:center;">{price} <small>{chg}</small></div><div style="flex:1; text-align:right;">{amt}</div></div>', unsafe_allow_html=True)
    
    st.divider()
    
    st.markdown("### 📊 시장 지표 및 매매동향")
    c1, c2 = st.columns(2)
    for idx, (m_name, m_key) in enumerate([("코스피", "KOSPI"), ("코스닥", "KOSDAQ")]):
        t = mkt_data.get(m_key, {})
        with [c1, c2][idx]:
            st.markdown(f'''<div class="m-header"><b>{m_name}</b> <small>{t.get("대금")}</small><br><span class="big-num">{t.get("val")}</span> <small style="color:#ff4b4b;">▲ {t.get("chg")}%</small></div>''', unsafe_allow_html=True)
            if "hist" in t: st.plotly_chart(draw_chart(t["hist"]), use_container_width=True, config={'displayModeBar': False})
            st.markdown(f'''<div class="supply-info"><span style="color:#0088ff">개:{t.get("개인"):+}</span> <span style="color:#ff4b4b">외:{t.get("외인"):+}</span> <span>기:{t.get("기관"):+}</span></div>''', unsafe_allow_html=True)

with tab3: st.info("📅 중요 일정 및 경제 캘린더 화면입니다.")
with tab4: st.info("📢 실시간 주요 공지 및 뉴스 특보입니다.")

time.sleep(10)
st.rerun()
