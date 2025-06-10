import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
from urllib.parse import quote

st.set_page_config(page_title="서북권 공공도서관 KDC 대출 현황", layout="wide")

@st.cache_data
def load_and_preprocess():
    # 1) URL 인코딩된 GitHub raw 링크
    base = "https://raw.githubusercontent.com/hogun1/suhang/main/data/"
    fname = "서울시 서북권 공공도서관 KDC 분류별 연간 대출 현황.csv"
    url = base + quote(fname)

    # 2) CSV 로드 (utf-8 → euc-kr)
    for enc in ("utf-8", "euc-kr"):
        try:
            df_raw = pd.read_csv(url, header=None, encoding=enc)
            break
        except Exception:
            continue
    else:
        raise Exception(f"Cannot read CSV with utf-8 or euc-kr: {url}")

    # 3) 빈 행 제거
    df_raw = df_raw.dropna(how="all")

    # 4) 멀티헤더 분리
    header_rows = df_raw.iloc[0:2]
    data_rows   = df_raw.iloc[2:].dropna(how="all", subset=[0,1]).reset_index(drop=True)

    # 5) 연도-지표 맵핑 생성 (지표명 정규화)
    year_metric_map = {}
    available_metrics = set()
    for col_idx, year_val in enumerate(header_rows.iloc[0]):
        if pd.isna(year_val): 
            continue

        # 4자리 연도만 추출
        m = re.search(r"\d{4}", str(year_val))
        if not m: 
            continue
        year = int(m.group())

        # 같은 위치부터 6개 지표
        for off in range(6):
            raw_metric = header_rows.iloc[1, col_idx + off]
            if pd.isna(raw_metric): 
                continue
            metric = str(raw_metric).strip()  # 공백 제거
            available_metrics.add(metric)
            year_metric_map[col_idx + off] = (year, metric)

    # 6) "대출건수" 항목만 추출
    records = []
    for _, row in data_rows.iterrows():
        gu, cls = row[0], row[1]
        if pd.isna(gu) or pd.isna(cls):
            continue
        for idx, (y, metric) in year_metric_map.items():
            # "대출건수"를 포함하는 모든 지표 매칭
            if "대출건수" not in metric:
                continue
            raw = row[idx]
            try:
                cnt = int(str(raw).replace(",", ""))
            except:
                cnt = None
            records.append({"연도": y, "자치구": gu, "분류": cls, "대출건수": cnt})

    # 7) tidy DataFrame 생성
    df = pd.DataFrame.from_records(records)
    if "대출건수" not in df.columns:
        raise KeyError(f"'대출건수' 컬럼이 없습니다. 사용 가능한 지표: {sorted(available_metrics)}")
    df = df.dropna(subset=["대출건수"])
    df["대출건수"] = df["대출건수"].astype(int)

    # 디버깅용: 사용 가능한 원본 지표 목록 전달
    df.attrs["available_metrics"] = sorted(available_metrics)
    return df

# 데이터 로드·전처리
df = load_and_preprocess()

# 디버깅: 실제 수집된 지표명 확인
st.write("🛠️ 사용 가능한 원본 지표 목록:", df.attrs.get("available_metrics", []))

# 앱 UI
st.title("서북권 공공도서관 KDC 분류별 연간 대출 현황")

# 컬럼 디버깅
st.write("데이터 컬럼:", df.columns.tolist())

# 사이드바 필터
st.sidebar.header("필터")
years = sorted(df["연도"].unique(), reverse=True)
selected_year = st.sidebar.selectbox("연도 선택", years)
gis = ["전체"] + sorted(df["자치구"].unique())
selected_gu = st.sidebar.selectbox("자치구 선택", gis)
class_list = ["전체"] + sorted(df["분류"].unique())
selected_cls = st.sidebar.selectbox("KDC 분류 선택", class_list)

# 필터링
filtered = df[df["연도"] == selected_year]
if selected_gu != "전체":
    filtered = filtered[filtered["자치구"] == selected_gu]
if selected_cls != "전체":
    filtered = filtered[filtered["분류"] == selected_cls]

# 차트1: 분류별 대출건수
st.subheader(f"{selected_year}년 대출건수 분포")
fig, ax = plt.subplots(figsize=(12,6))
sns.barplot(data=filtered, x="분류", y="대출건수", hue="자치구", dodge=True, ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

# 차트2: 연도별 추세
st.subheader("연도별 대출건수 추세")
trend = df.copy()
if selected_gu != "전체":
    trend = trend[trend["자치구"] == selected_gu]
if selected_cls != "전체":
    trend = trend[trend["분류"] == selected_cls]
trend_summary = trend.groupby("연도")["대출건수"].sum().reset_index()
fig2, ax2 = plt.subplots(figsize=(8,4))
sns.lineplot(data=trend_summary, x="연도", y="대출건수", marker="o", ax=ax2)
ax2.set_xticks(years)
ax2.set_xlabel("연도")
ax2.set_ylabel("대출건수")
st.pyplot(fig2)
