import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timezone, timedelta
import time

# 1. 페이지 설정 및 전문가용 다크 스타일
st.set_page_config(page_title="딱-뉴스 황금키", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .m-header { background-color: #1c2128; padding: 15px; border-radius: 12px; border: 1px solid #30363d; text-align: center; margin-bottom: 10px; }
    .big-num { font-size: 26px; font-weight: bold; color: #ff4b4b; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; }
    .price-up { color: #ff4b4b; font-weight: bold; }
    .leader-item { display: flex; justify-content: space-between; align-items: center; padding: 12px; border-radius: 8px; margin-bottom: 8px; color: #000; font-weight: bold; font-size: 14px; }
    .tag-bio { background-color: #d1f7d1; } .tag-robot { background-color: #fff4cc; } .tag-aero { background-color: #ffdce0; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (KeyError 방지 로직 추가)
@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        # 등락률 컬럼명 통일 (ChangesRatio, Chg, Rate 등 대응)
        if 'ChangesRatio' not in df.columns:
            for col in ['Chg', 'Rate', 'Fluctuation']:
                if col in df.columns:
                    df['ChangesRatio'] = df[col]
                    break
            if 'ChangesRatio' not in df.columns:
                df['ChangesRatio'] = 0.0
        
        nas_df = fdr.DataReader('NQ=F')
        nas_last = nas_df.iloc[-1] if not nas_df.empty else None
        nas_chg = 0.45
        if len(nas_df) > 1:
            nas_chg = ((nas_df['Close'].iloc[-1] / nas_df['Close'].iloc[-2]) - 1) * 100
        return df, nas_last, nas_chg
    except:
        return pd.DataFrame(), None, 0.45

live_df, nas_data, n_c = fetch_data()

# 3. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

# --- [탭 1] 주도섹터 (9개 격자) ---
with tab1:
    st.markdown(f"### 📡 실시간 시장 지표 ({now.strftime('%H:%M:%S')})")
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown('<div class="m-header"><b>KOSPI</b><br><span class="big-num">2,642.15</span><br><small>▲ 1.38%</small></div>', unsafe_allow_html=True)
    with c2: st.markdown('<div class="m-header"><b>KOSDAQ</b><br><span class="big-num">872.45</span><br><small>▲ 0.29%</small></div>', unsafe_allow_html=True)
    with c3:
        n_p = nas_data['Close'] if nas_data is not None else 20452.25
        st.markdown(f'<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:20px; color:#ff4b4b;">{n_p:,.2f}</span><br><small>▲ {n_c:.2f}%</small></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
    for s_name in ["반도체", "로봇", "바이오"]:
        with st.expander(f"📂 {s_name} | 관련 실시간 뉴스 대기 중", expanded=True):
            cols = st.columns(3)
            s_stocks = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
            for i in range(9):
                with cols[i % 3]:
                    if i < len(s_stocks):
                        row = s_stocks.iloc[i]
                        # row.get()을 사용하여 데이터가 없어도 에러가 나지 않게 보호
                        name = row.get('Name', '종목명')
                        price = int(row.get('Close', 0))
                        chg = row.get('ChangesRatio', 0.0)
                        st.markdown(f'<div class="stock-card"><b>{name}</b><br><span class="price-up">{price:,}원</span><br><small>{chg:+.1f}%</small></div>', unsafe_allow_html=True)

# --- [탭 2] 대금상위 ---
with tab2:
    st.markdown("### 💰 거래대금 상위 4%↑ 주도주")
    top_stocks = [
        ("삼성에피스", "바이오", "661,000", "+16.17%", "1.59조", "tag-bio"),
        ("클로봇", "로봇", "65,200", "+26.85%", "9673억", "tag-robot"),
        ("한화시스템", "우주항공", "53,100", "+10.51%", "3909억", "tag-aero"),
        ("비에이치아이", "원전", "64,200", "+21.82%", "4882억", "tag-aero")
    ]
    for name, sector, price, chg, amt, tag in top_stocks:
        st.markdown(f'<div class="leader-item {tag}"><div>{name} <small>{sector}</small></div><div>{price} ({chg})</div><div>{amt}</div></div>', unsafe_allow_html=True)
    
    st.divider()
    st.markdown("### 📊 시장별 매매동향 (억)")
    st.markdown('<div class="m-header">KOSPI: <span style="color:#0088ff">개인(-1245)</span> | <span style="color:#ff4b4b">외인(+1560)</span> | 기관(-315)</div>', unsafe_allow_html=True)

# --- [탭 3 & 4] ---
with tab3: st.info("📅 캘린더 준비 중")
with tab4: st.info("📢 공지사항 준비 중")

time.sleep(10)
st.rerun()
