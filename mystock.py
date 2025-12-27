import FinanceDataReader as fdr
import pandas as pd
from tqdm import tqdm
from datetime import datetime

# [테스트 설정] 2025년 12월 26일 금요일 기준으로 고정
TEST_DATE = '2025-12-26'
MIN_MARKET_CAP = 500000000000  # 시총 5000억 이상
MIN_VOLUME_KRW = 30000000000   # 거래대금 300억 이상

print(f"[{TEST_DATE}] 금요일 시장 주도주 복기 스캔을 시작합니다...")

# 1. 종목 리스트 가져오기
df_krx = fdr.StockListing('KRX')
df_krx = df_krx[df_krx['Marcap'] >= MIN_MARKET_CAP]

results = []

# 2. 기술적 분석 진행
for index, row in tqdm(df_krx.iterrows(), total=len(df_krx)):
    symbol, name = row['Code'], row['Name']
    try:
        # 테스트 날짜를 포함하도록 충분한 기간의 데이터 로드
        df = fdr.DataReader(symbol, '2025-10-01', TEST_DATE)
        if len(df) < 60: continue
        
        # 이동평균선 계산
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA60'] = df['Close'].rolling(window=60).mean()
        
        last = df.iloc[-1] # 이게 바로 12월 26일 데이터가 됩니다.
        prev = df.iloc[-2]
        
        # 조건 검사: 거래대금 & 20일선 위 & 5일선 사수 & 정배열
        if (last['Amount'] >= MIN_VOLUME_KRW and 
            last['Close'] > last['MA20'] and 
            last['Close'] >= last['MA5'] and 
            last['MA20'] > last['MA60']):
            
            results.append({
                '종목명': name,
                '현재가': int(last['Close']),
                '등락률': round(((last['Close'] / prev['Close']) - 1) * 100, 2),
                '거래대금(억)': int(last['Amount'] / 100000000),
                '시가총액(억)': int(row['Marcap'] / 100000000)
            })
    except: continue

# 3. 결과 저장
if results:
    final_df = pd.DataFrame(results).sort_values(by='거래대금(억)', ascending=False)
    final_df.to_html('stock_scanner_result.html', index=False)
    print(f"\n✅ 스캔 완료! 금요일 주도주 {len(results)}개를 찾았습니다.")
else:
    print(f"\n❌ {TEST_DATE} 기준 조건에 맞는 종목이 없습니다. 기준을 조금 더 낮춰보세요.")