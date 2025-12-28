import streamlit as st
import time

# 1. 페이지 설정
st.set_page_config(page_title="황금키 시뮬레이터", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { display: none; }
    .main { background-color: #0e1117; color: #ffffff; }
    .stock-card { background-color: #1c2128; padding: 15px; border-radius: 12px; border-left: 5px solid #ff4b4b; margin-bottom: 12px; }
    .price-up { color: #ff4b4b; font-weight: bold; font-size: 24px; }
    .sector-tag { background-color: #4b0082; color: white; font-size: 11px; padding: 2px 6px; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🧪 금요일(12/26) 시뮬레이션 모드")
st.info("현재 서버 점검 중으로, 선생님의 캡처본 데이터를 기반으로 화면을 재현했습니다.")

# 2. 캡처본 데이터 기반 리스트 (서버 호출 없음)
mock_data = [
    {"name": "삼성전자", "price": "117,000", "chg": "+5.31%", "amt": "1.25조", "sector": "반도체"},
    {"name": "SK하이닉스", "price": "599,000", "chg": "+1.87%", "amt": "9,800억", "sector": "반도체"},
    {"name": "남선알미늄", "price": "1,310", "chg": "+29.96%", "amt": "280억", "sector": "비철금속"},
    {"name": "재영솔루텍", "price": "4,160", "chg": "+21.99%", "amt": "420억", "sector": "핸드셋"},
    {"name": "조일알미늄", "price": "1,389", "chg": "+14.79%", "amt": "190억", "sector": "비철금속"},
    {"name": "셀루메드", "price": "1,896", "chg": "+29.95%", "amt": "350억", "sector": "바이오"}
]

# 3. 화면 출력
cols = st.columns(1) # 모바일 최적화 (세로로 한 줄씩)
for s in mock_data:
    st.markdown(f"""
        <div class="stock-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:20px; font-weight:bold;">{s['name']}</div>
                    <span class="sector-tag">{s['sector']}</span>
                </div>
                <div style="text-align:right;">
                    <div class="price-up">{s['price']}원</div>
                    <div style="font-size:16px; color:#ff4b4b;">{s['chg']} <span style="color:#888; font-size:13px; margin-left:5px;">{s['amt']}</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.divider()
st.warning("내일(월요일) 오전 9시, 이 화면은 실시간 라이브 데이터로 자동 전환됩니다.")
