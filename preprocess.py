# preprocess.py

import pandas as pd

# 1) 원본 CSV를 "헤더 없이" 읽어온다
#    → 첫 두 행이 멀티헤더이므로 header=None 으로 읽고, 
#       실제 데이터는 2행(0,1 인덱스 제외)부터 시작함
df_raw = pd.read_csv(
    "data/서울시 서북권 공공도서관 KDC 분류별 연간 대출 현황.csv",
    header=None,
    encoding="euc-kr",  # UTF-8 에러가 나면 euc-kr
)

# 2) 첫 두 행을 분리: header_rows ← 0,1행 / data_rows ← 그 아래 모든 행
header_rows = df_raw.iloc[0:2].copy()
data_rows   = df_raw.iloc[2:].reset_index(drop=True)

# 3) header_rows를 이용해 “(col_index → (year, metric))” 맵핑 생성
#    첫 2개 컬럼(예: [0]=자치구, [1]=분류)은 연도/지표 헤더에 포함되지 않는다.
#    나머지 컬럼들은 6개씩 묶여 2018~2023년 각각 “종건수, 책건수, 대출건수, 종비율, 책비율, 대출건수비율”
#    순서로 반복되어 있다.
#
#    header_rows.iloc[0] 에는 [NaN, NaN, 2018, 2018, 2018, …, 2023,2023,…]
#    header_rows.iloc[1] 에는 [자치구, 분류, 종건수, 책건수, 대출건수, …]
year_metric_map = {}  # col_idx → (year:int, metric:str)
for col_idx, year_val in enumerate(header_rows.iloc[0]):
    if pd.isna(year_val):
        continue
    year = int(year_val)
    # 이 연도 그룹이 시작하는 컬럼 위치(col_idx), 그 뒤 6개가 해당 year
    # find which metrics at header_rows.iloc[1][col_idx:col_idx+6]
    for offset in range(6):
        metric = header_rows.iloc[1, col_idx + offset]
        year_metric_map[col_idx + offset] = (year, metric)

# 4) 데이터 행(행마다) 반복하면서 레코드 생성
records = []
for _, row in data_rows.iterrows():
    gu  = row[0]  # 0번 컬럼: 자치구(마포구·서대문구·은평구)
    cls = row[1]  # 1번 컬럼: KDC 분류명(문학, 철학 등)

    # 분류명이 NaN이면 건너뛰기
    if pd.isna(cls):
        continue

    # year_metric_map 에 등록된 모든 컬럼 위치를 순회
    for col_idx, (year, metric) in year_metric_map.items():
        # 오직 “대출건수” 데이터만 추출하고 싶다면:
        if metric != "대출건수":
            continue
        raw_val = row[col_idx]
        # 천단위 콤마 제거 후 정수 변환
        try:
            cnt = int(str(raw_val).replace(",", ""))
        except:
            cnt = None
        records.append({
            "year": year,
            "gu": gu,
            "classification": cls,
            "loan_count": cnt
        })

# 5) tidy DataFrame 생성
df_tidy = pd.DataFrame.from_records(records)

# 6) (선택) 누락값 처리, 타입 변환
df_tidy = df_tidy.dropna(subset=["loan_count"])
df_tidy["loan_count"] = df_tidy["loan_count"].astype(int)

# 7) CSV로 저장
df_tidy.to_csv("data/서울시 서북권 공공도서관 KDC 분류별 연간 대출 현황.csv", index=False, encoding="utf-8")
print("data/서울시 서북권 공공도서관 KDC 분류별 연간 대출 현황.csv 생성 완료")
