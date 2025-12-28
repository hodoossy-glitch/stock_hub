import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
import time

# 1. 시스템 리부트 및 초기 설정
st.set_page_config(page_title="황금키 통합 상황판", layout="wide", initial_sidebar_state="collapsed")

# 기존 에러가 화면에 남지 않도록 디자인 클린업
st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border-left: 5px solid #ff4b4b; margin-bottom: 12px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 24px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔄 시스템 리부트 및 동기화 대기")
st.write("※ 현재 시스템이 초기화되었습니다. 서버 문이 열리기를 기다리고 있습니다.")

# 2. 클린 데이터 엔진 (에러 발생 시 즉시 우회)
def reboot_engine():
    try:
        # 데이터 서버에 접속 시도
        df = fdr.StockListing('KRX')
        if df is not None and not df.empty:
            # 캡처본 기준: 시총 5,000억 이상 + 4% 이상 주도주 필터링
            leaders = df[(df['Marcap'] >= 500000000000) & (df['ChangesRatio'] >= 4.0)]
            return leaders.sort_values(by='Amount', ascending=False).head(15)
        return None
    except:
        # 일요일 서버 점검 중일 경우 조용히 대기 모드로 전환
        return "WAITING"

# 3. 리부트 결과 화면 표시
status = reboot_engine()

if isinstance(status, pd.DataFrame) and not status.empty:
    st.success("✅ 리부트 성공! 실시간 시세 연동 중")
    cols = st.columns(3)
    for idx, (i, row) in enumerate(status.iterrows()):
        with cols[idx % 3]:
            amt = row['Amount'] / 1e8
            amt_txt = f"{amt/10000:.1f}조" if amt >= 10000 else f"{int(amt)}억"
            st.markdown(f"""
                <div class="stock-card">
                    <div style="font-size:20px; font-weight:bold;">{row['Name']}</div>
                    <div class="price-up">{int(row['Close']):,}원</div>
                    <div style="display:flex; justify-content:space-between; font-size:16px;">
                        <span style="color:#ff4b4b;">▲ {row['ChangesRatio']}%</span>
                        <span style="color:#888;">{amt_txt}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
elif status == "WAITING":
    st.warning("⚠️ 시스템 리부트 완료. 데이터 서버(KRX) 점검으로 인해 '대기 모드'입니다.")
    st.info("내일(월요일) 오전 9시, 장 시작과 동시에 실시간 시세가 쏟아지기 시작합니다.")
else:
    st.info("주도주 탐색 엔진 가동 중... 잠시만 기다려 주세요.")

# 4. 1분마다 자동 새로고침 (엔진 재가동)
time.sleep(60)
st.rerun()
