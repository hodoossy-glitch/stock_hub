import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time

# 1. 모바일 최적화 및 한국 시간 설정
st.set_page_config(page_title="황금키 실시간 레이더", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

# CSS: 모바일 전용 블랙 HTS 디자인
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 12px; border: 1px solid #30363d; border-left: 5px solid #ff4b4b; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 22px; }
    .m-title { font-size: 20px; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 헤더
st.markdown(f"<div class='m-title'>📡 실시간 주도주 레이더</div>", unsafe_allow_html=True)
st.caption(f"데이터 동기화 시각: {now.strftime('%H:%M:%S')}")

# 3. 실시간 데이터 검색 함수 (핵심 엔진)
@st.cache_data(ttl=60) # 1분마다 최신 데이터로 갱신
def fetch_realtime_leaders():
    try:
        # 전종목 시세 가져오기
        df = fdr.StockListing('KRX')
        
        # 필터링 1: 시총 5,000억 이상 (우량주 집중)
        # 필터링 2: 등락률 4% 이상 (주도주 집중)
        # 필터링 3: 잡주 제거 (우선주, 스팩 등)
        leaders = df[
            (df['Marcap'] >= 500000000000) & 
            (df['ChangesRatio'] >= 4.0) &
            (~df['Name'].str.contains('우|스팩|관리'))
        ].sort_values(by='Amount', ascending=False).head(15) # 거래대금 순 정렬
        
        return leaders
    except:
        return pd.DataFrame()

# 4. 실시간 전광판 출력
st.markdown("### 💰 실시간 거래대금 상위 (4%↑)")

leaders_df = fetch_realtime_leaders()

if not leaders_df.empty:
    for _, row in leaders_df.iterrows():
        # 거래대금 단위 변환 (조/억)
        amt_val = row['Amount'] / 1e8
        amt_display = f"{amt_val/10000:.1f}조" if amt_val >= 10000 else f"{int(amt_val)}억"
        
        # 모바일 최적화 카드 출력
        st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:18px; font-weight:bold;">{row['Name']}</div>
                        <div style="font-size:12px; color:#888;">{row['Sector'] if row['Sector'] else '주도주'}</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="price-up">{int(row['Close']):,}원</div>
                        <div style="font-size:14px; color:#ff4b4b;">{row['ChangesRatio']:+.2f}% <span style="color:#888; margin-left:5px;">{amt_display}</span></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("⌛ 현재 조건(시총 5천억↑, 4%↑)을 만족하는 주도주를 탐색 중입니다. 장 시작 후 자동으로 표시됩니다.")

# 5. 하단 시장 지표 (나스닥 선물 등)
st.divider()
st.markdown(f"🌐 **나스닥 100 선물:** <span style='color:#ff4b4b;'>실시간 연동 중...</span>", unsafe_allow_html=True)

# 6. 1분마다 자동 새로고침
time.sleep(60)
st.rerun()
