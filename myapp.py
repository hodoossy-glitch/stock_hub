import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
from datetime import datetime, timedelta, timezone
import time

# 1. 페이지 설정 및 한국 시간
st.set_page_config(page_title="황금키 주도주 레이더", layout="wide")
now = datetime.now(timezone(timedelta(hours=9)))

# HTS 블랙 테마 디자인
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .sector-box { background-color: #1e1e1e; padding: 10px; border-radius: 5px; border-left: 5px solid #ff4b4b; margin-bottom: 10px; }
    .stock-tag { background-color: #262730; padding: 2px 8px; border-radius: 3px; margin-right: 5px; font-size: 14px; color: #ff4b4b; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 헤더 (영상 스타일)
st.markdown(f"""
    <div style="background-color:#1e1e1e; padding:15px; border-radius:10px; border-bottom: 3px solid #ff4b4b;">
        <span style="color:#ff4b4b; font-size:24px; font-weight:bold;">🔥 주도 섹터 실시간 레이더</span>
        <span style="float:right; color:#888;">{now.strftime('%Y-%m-%d %H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ 레이더 설정")
    min_marcap = st.number_input("최소 시총(억)", value=5000)
    st.info("💡 영상처럼 불필요한 역배열 종목은 자동 제거됩니다.")

# 3. 데이터 분석 및 섹터 그룹화 엔진
try:
    with st.spinner("시장 주도주 분석 중..."):
        # 전체 종목 리스트 및 산업군 정보 가져오기
        df_krx = fdr.StockListing('KRX')
        df_base = df_krx[
            (df_krx['Marcap'] >= (min_marcap * 100000000)) & 
            (~df_krx['Name'].str.contains('우|스팩|관리'))
        ].head(100) # 상위 100개 집중 분석

        sector_map = {} # 섹터별 종목 담을 바구니

        for _, row in df_base.iterrows():
            try:
                df = fdr.DataReader(row['Code'], (now - timedelta(days=20)).strftime('%Y-%m-%d'))
                if df is None or len(df) < 5: continue
                
                last = df.iloc[-1]
                prev = df.iloc[-2]
                curr_p = int(last['Close'])
                chg = ((curr_p - prev['Close']) / prev['Close']) * 100
                ma5 = df['Close'].tail(5).mean()
                ma20 = df['Close'].tail(20).mean()

                # 영상의 핵심: 역배열은 가차없이 버림 [00:08:53]
                if ma5 < ma20: continue 

                # 산업(섹터) 분류 확인
                sector = row['Sector'] if pd.notnull(row['Sector']) else "기타 주도주"
                
                if sector not in sector_map: sector_map[sector] = []
                
                sector_map[sector].append({
                    'name': row['Name'],
                    'chg': chg,
                    'amt': int(last['Amount'] / 1e8)
                })
            except: continue

    # 4. 섹터별 전광판 출력 (8분 30초 화면 스타일)
    if sector_map:
        # 거래대금이 많이 터진 섹터 순으로 정렬
        sorted_sectors = sorted(sector_map.items(), key=lambda x: sum(item['amt'] for item in x[1]), reverse=True)

        for sector, stocks in sorted_sectors[:8]: # 상위 8개 주도 섹터만 표시
            with st.container():
                st.markdown(f"""
                    <div class="sector-box">
                        <span style="font-size:18px; font-weight:bold; color:#ffb0b0;">📂 {sector}</span>
                        <span style="float:right; font-size:12px; color:#666;">섹터 통합 거래대금 상위</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 해당 섹터의 종목들을 가로로 나열 (영상 스타일)
                cols = st.columns(4)
                for idx, stock in enumerate(sorted(stocks, key=lambda x: x['amt'], reverse=True)[:4]):
                    with cols[idx % 4]:
                        st.markdown(f"""
                            <div style="background-color:#262730; padding:10px; border-radius:5px; text-align:center;">
                                <div style="font-size:16px; font-weight:bold;">{stock['name']}</div>
                                <div style="color:#ff4b4b; font-size:14px;">{stock['chg']:+.2f}%</div>
                                <div style="color:#888; font-size:12px;">{stock['amt']}억</div>
                            </div>
                            """, unsafe_allow_html=True)
    else:
        st.info("현재 시장을 주도하는 정배열 섹터가 없습니다.")

except Exception as e:
    st.warning("데이터 동기화 대기 중...")

time.sleep(60)
st.rerun()
