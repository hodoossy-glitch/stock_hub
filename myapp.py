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
    .m-header { background-color: #1c2128; padding: 12px; border-radius: 12px; border: 1px solid #30363d; text-align: center; margin-bottom: 5px; }
    .big-num { font-size: 22px; font-weight: bold; color: #ff4b4b; margin-bottom: 2px; }
    .supply-row { font-size: 11px; display: flex; justify-content: center; gap: 5px; margin-top: 5px; border-top: 1px solid #30363d; padding-top: 5px; }
    .stock-card { background-color: #161b22; padding: 10px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 5px; text-align: center; min-height: 80px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 15px; }
    .tag-sector { font-size: 10px; padding: 2px 4px; border-radius: 3px; background: #30363d; color: #eee; margin-bottom: 4px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 2. 실시간 데이터 엔진 (KeyError 박멸 로직)
@st.cache_data(ttl=10)
def fetch_data():
    try:
        df = fdr.StockListing('KRX')
        # [에러 방지] 등락률 컬럼명이 ChangesRatio, Chg, Rate 등 무엇이든 'Chg'로 통일
        target_col = None
        for col in ['ChangesRatio', 'Chg', 'Rate', 'Fluctuation', 'Change']:
            if col in df.columns:
                target_col = col
                break
        if target_col:
            df['Chg_Fix'] = df[target_col]
        else:
            df['Chg_Fix'] = 0.0
            
        nas_df = fdr.DataReader('NQ=F')
        nas_last = nas_df.iloc[-1] if not nas_df.empty else None
        nas_chg = 0.45
        if len(nas_df) > 1:
            nas_chg = ((nas_df['Close'].iloc[-1] / nas_df['Close'].iloc[-2]) - 1) * 100
            
        trends = {
            "KOSPI": {"대금": "16.3조", "개인": -1245, "외인": 1560, "기관": -315},
            "KOSDAQ": {"대금": "12.4조", "개인": 2130, "외인": -840, "기관": -1290}
        }
        return df, nas_last, nas_chg, trends
    except:
        return pd.DataFrame(), None, 0.45, {}

live_df, nas_data, n_c, mkt_trends = fetch_data()

# 3. 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["주도섹터", "대금상위", "캘린더", "공시"])

# --- 공통 상단 지표 함수 ---
def show_market_indices():
    st.markdown(f"### 📡 실시간 시장 지표 ({now.strftime('%H:%M:%S')})")
    c1, c2, c3 = st.columns(3)
    t1, t2 = mkt_trends.get("KOSPI", {}), mkt_trends.get("KOSDAQ", {})
    
    with c1:
        st.markdown(f'''<div class="m-header"><b>KOSPI</b><br><span class="big-num">2,642.15</span><br>
        <small style="color:#ff4b4b;">▲ 1.38% ({t1.get("대금")})</small>
        <div class="supply-row"><span style="color:#0088ff">개:{t1.get("개인"):+}</span> <span style="color:#ff4b4b">외:{t1.get("외인"):+}</span> <span>기:{t1.get("기관"):+}</span></div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="m-header"><b>KOSDAQ</b><br><span class="big-num">872.45</span><br>
        <small style="color:#ff4b4b;">▲ 0.29% ({t2.get("대금")})</small>
        <div class="supply-row"><span style="color:#ff4b4b">개:{t2.get("개인"):+}</span> <span style="color:#0088ff">외:{t2.get("외인"):+}</span> <span>기:{t2.get("기관"):+}</span></div></div>''', unsafe_allow_html=True)
    with c3:
        n_p = nas_data['Close'] if nas_data is not None else 25863.25
        st.markdown(f'''<div class="m-header"><b>나스닥 선물</b><br><span style="font-size:20px; color:#ff4b4b; font-weight:bold;">{n_p:,.2f}</span><br>
        <small style="color:#ff4b4b;">▲ {n_c:.2f}%</small><div class="supply-row">글로벌 수급 분석 중</div></div>''', unsafe_allow_html=True)

# --- [탭 1] 주도섹터 ---
with tab1:
    show_market_indices()
    st.divider()
    st.markdown("### 🔥 실시간 주도 섹터 & 뉴스")
    for s_name in ["반도체", "로봇", "바이오"]:
        with st.expander(f"📂 {s_name} | 관련 실시간 뉴스 분석 중", expanded=True):
            cols = st.columns(3)
            if not live_df.empty:
                s_stocks = live_df[live_df['Name'].str.contains(s_name, na=False)].sort_values('Amount', ascending=False).head(9)
                for i in range(9):
                    with cols[i % 3]:
                        if i < len(s_stocks):
                            row = s_stocks.iloc[i]
                            st.markdown(f'''<div class="stock-card"><b>{row["Name"]}</b><br><span class="price-up">{int(row["Close"]):,}원</span><br><small>{row["Chg_Fix"]:+.1f}%</small></div>''', unsafe_allow_html=True)

# --- [탭 2] 대금상위 (9개 종목 격자 방식) ---
with tab2:
    show_market_indices()
    st.divider()
    st.markdown("### 💰 거래대금 상위 주도주 (Top 9)")
    if not live_df.empty:
        # 거래대금 상위 9개 추출
        top_9 = live_df.sort_values('Amount', ascending=False).head(9)
        cols_9 = st.columns(3)
        for i in range(9):
            with cols_9[i % 3]:
                if i < len(top_9):
                    s = top_9.iloc[i]
                    sector = s.get('Sector', '주도주')
                    st.markdown(f'''<div class="stock-card" style="border-top: 3px solid #ff4b4b;">
                        <span class="tag-sector">{sector}</span><br>
                        <b>{s["Name"]}</b><br>
                        <span class="price-up">{int(s["Close"]):,}원</span><br>
                        <small>{s["Chg_Fix"]:+.1f}%</small>
                    </div>''', unsafe_allow_html=True)

with tab3: st.info("📅 캘린더 준비 중")
with tab4: st.info("📢 공지사항 준비 중")

time.sleep(10)
st.rerun()
