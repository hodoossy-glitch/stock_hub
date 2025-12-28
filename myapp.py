import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 정밀 레이더", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

# CSS 디자인 (가독성 극대화)
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; margin-bottom: 12px; border-left: 5px solid #ff4b4b; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 24px; }
    .m-title { font-size: 22px; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.markdown(f"<div class='m-title'>📡 황금키 실시간 정밀 레이더</div>", unsafe_allow_html=True)
st.caption(f"조회 시각: {now.strftime('%Y-%m-%d %H:%M:%S')}")

# 2. 정밀 시세 엔진 (가장 최근 종가 직접 추출)
@st.cache_data(ttl=30) # 30초마다 갱신
def get_real_price():
    try:
        # 주요 주도주 리스트 (선생님이 보시는 종목들 중심)
        target_codes = ['005930', '000660', '207940', '373220', '005380', '068270'] 
        # 삼성전자, SK하이닉스, 삼성바이오, LG엔솔, 현대차, 셀트리온 등
        
        results = []
        for code in target_codes:
            # DataReader로 최근 5일치 시세를 직접 긁어옴
            df = fdr.DataReader(code, (now - timedelta(days=10)).strftime('%Y-%m-%d'))
            if df.empty: continue
            
            # 상장 정보에서 이름 가져오기
            stock_info = fdr.StockListing('KRX')
            name = stock_info[stock_info['Code'] == code]['Name'].values[0]
            
            last = df.iloc[-1]
            prev = df.iloc[-2]
            
            curr_p = int(last['Close'])
            chg = ((curr_p - prev['Close']) / prev['Close']) * 100
            amt = int(last['Amount'] / 1e8)

            results.append({'종목': name, '현재가': curr_p, '등락률': chg, '대금': amt})
        
        return pd.DataFrame(results)
    except:
        return pd.DataFrame()

# 3. 화면 출력
df_res = get_real_price()

if not df_res.empty:
    for _, row in df_res.iterrows():
        st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="font-size:20px; font-weight:bold;">{row['종목']}</div>
                        <div style="font-size:12px; color:#888;">거래대금: {row['대금']}억</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="price-up">{row['현재가']:,}원</div>
                        <div style="font-size:16px; color:#ff4b4b;">{row['등락률']:+.2f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.warning("데이터 서버 응답 대기 중입니다. 잠시 후 다시 시도해주세요.")

st.divider()
time.sleep(60)
st.rerun()
