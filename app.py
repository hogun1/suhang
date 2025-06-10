import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from urllib.parse import quote

st.set_page_config(page_title="서북권 공공도서관 KDC 대출 현황", layout="wide")

@st.cache_data
def load_and_preprocess():
    # 1) GitHub raw URL (퍼센트 인코딩)
    base = "https://raw.githubusercontent.com/hogun1/suhang/main/data/"
    fname = "서울시 서북권 공공도서관 KDC 분류별 연간 대출 현황.csv"
    url = base + quote(fname)

    # 2) CSV 읽기 (utf-8 우선, 실패 시 euc-kr)
    for enc in ("utf-8", "euc-kr"):
        try:
            df_raw = pd.read_csv(url, header=None, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise UnicodeDecodeError(f"Cannot decode CSV at {url}")

    # 3) 헤더 분리
    header_rows = df_raw.iloc[0:2]
    data_rows   = df_raw.iloc[2:].reset_index(drop=True)

    # 4) 연도·지표 맵핑 생성
    year_metric_map = {}
    for col_idx, year_val in enumerate(header_rows.iloc[0]):
        # NaN 건너뛰기
        if pd.isna(year_val):
            continue
        # "2018 " 처럼 불필요 문자 제거하고 4자리 숫자만 추출
        m = re.search(r"\d{4}", str(year_val))
        if not m:
            continue
        year = int(m.group())
        # 연도별 6개 지표
        for offset in range(6):
            metric = header_rows.iloc[1, col_idx + offset]
            year_metric_map[col_idx + offset] = (year, metric)

    # 5) "대출건수" 레코드만 추출
    records = []
    for _, row in data_rows.iterrows():
        gu  = row[0]
        cls = row[1]
        if pd.isna(gu) or pd.isna(cls):
            continue
        for col_idx, (year, metric) in year_metric_map.items():
            if metric != "대출건수":
                continue
            raw_val = row[col_idx]
            try:
                cnt = int(str(raw_val).replace(",", ""))
            except:
                cnt = None
            records.append({"연도": year, "자치구": gu, "분류": cls, "대출건수": cnt})

    # 6) tidy DataFrame 생성
    df = pd.DataFrame.from_records(records)
    df = df.dropna(subset=["대출건수"])
    df["대출건수"] = df["대출건수"].astype(int)
    return df

# 데이터 로드·전처리
df = load_and_preprocess()

# 앱 타이틀
st.title("서북권 공공도서관 KDC 분류별 연간 대출 현황")

# 컬럼 디버깅 (필요 시 주석 처리)
st.write("데이터 컬럼:", df.columns.tolist())

# 사이드바 필터
st.sidebar.header("필터")
years = sorted(df["연도"].unique(), reverse=True)
selected_year = st.sidebar.selectbox("연도 선택", years)
gis    = ["전체"] + sorted(df["자치구"].unique())
selected_gu = st.sidebar.selectbox("자치구 선택", gis)
class_list = ["전체"] + sorted(df["분류"].unique())
selected_cls = st.sidebar.selectbox("KDC 분류 선택", class_list)

# 필터링 적용
filtered = df[df["연도"] == selected_year]
if selected_gu != "전체":
    filtered = filtered[filtered["자치구"] == selected_gu]
if selected_cls != "전체":
    filtered = filtered[filtered["분류"] == selected_cls]

# 메인 시각화: 분류별 대출건수
st.subheader(f"{selected_year}년 대출건수 분포")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=filtered, x="분류", y="대출건수", hue="자치구", dodge=True, ax=ax)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# 연도별 추세
st.subheader("연도별 대출건수 추세")
trend = df.copy()
if selected_gu != "전체":
    trend = trend[trend["자치구"] == selected_gu]
if selected_cls != "전체":
    trend = trend[trend["분류"] == selected_cls]
trend_summary = trend.groupby("연도")["대출건수"].sum().reset_index()
fig2, ax2 = plt.subplots(figsize=(8, 4))
sns.lineplot(data=trend_summary, x="연도", y="대출건수", marker="o", ax=ax2)
ax2.set_xticks(years)
ax2.set_xlabel("연도")
ax2.set_ylabel("대출건수")
st.pyplot(fig2)
