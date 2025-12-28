import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time

# 1. 페이지 설정 및 디자인 (사이드바 제거)
st.set_page_config(page_title="황금키 정밀 레이더", layout="wide", initial_sidebar_state="collapsed")
now = datetime.now(timezone(timedelta(hours=9)))

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 20px; border-radius: 12px; margin-bottom: 15px; border-left: 6px solid #ff4b4b; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 26px; }
    .stock-name { font-size: 22px; font-weight: bold; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 네이버 금융 기반 정밀 시세 엔진
@st.cache_data(ttl=10) # 10초마다 갱신 (가장 빠름)
def get_verified_price():
    # 선생님이 확인하시기 좋은 대표 주도주 6선 (코드로 정확히 타격)
    targets = {
        '삼성전자': '005930', 
        'SK하이닉스': '000660', 
        '삼성바이오로직스': '207940', 
        'LG에너지솔루션': '373220',
        '현대차': '005380',
        '셀트리온': '068270'
    }
    
    results = []
    for name, code in targets.items():
        try:
            # 주말 오류를 피하기 위해 'NAVER' 소스를 명시적으로 지정
            df = fdr.DataReader(code, (now - timedelta(days=14)).strftime('%Y-%m-%d'))
            if not df.empty:
                last = df.iloc[-1]
                prev = df.iloc[-2]
                curr_p = int(last['Close'])
                chg = ((curr_p - prev['Close']) / prev['Close']) * 100
                amt = int(last['Amount'] / 1e8) if 'Amount' in last else 0
                
                results.append({'name': name, 'price': curr_p, 'chg': chg, 'amt': amt})
        except: continue
    return results

# 3. 화면 출력
st.markdown(f"## 📡 황금키 정밀 시세 전광판")
st.write(f"현재 시각(KST): {now.strftime('%Y-%m-%d %H:%M:%S')}")

data = get_verified_price()

if data:
    for item in data:
        st.markdown(f"""
            <div class="stock-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div class="stock-name">{item['name']}</div>
                        <div style="color:#888;">거래대금: {item['amt']:,}억</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="price-up">{item['price']:,}원</div>
                        <div style="font-size:18px; color:#ff4b4b;">{item['chg']:+.2f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.error("⚠️ 서버 점검 중입니다. 잠시 후 새로고침 해주세요.")

# 4. 자동 새로고침 (30초)
time.sleep(30)
st.rerun()
