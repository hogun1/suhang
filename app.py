import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="서북권 공공도서관 KDC 대출 현황", layout="wide")

@st.cache_data
def load_and_preprocess():
    # 1) GitHub raw URL 에서 CSV 직접 읽기 (멀티헤더)
    url = (
        "https://raw.githubusercontent.com/"
        "hogun1/suhang/main/data/"
        "%EC%84%9C%EC%9A%B8%EC%8B%9C%20%EC%84%9C%EB%B6%81%EA%B6%8C%20"
        "%EA%B3%B5%EA%B3%B5%EB%8F%84%EC%84%9C%EA%B4%80%20"
        "KDC%20%EB%B6%84%EB%A5%98%EB%B3%84%20%EC%97%B0%EA%B0%84%20"
        "%EB%8C%80%EC%B6%9C%20%ED%98%84%ED%99%A9.csv"
    )
    # header=None 으로 멀티헤더 포함해서 읽기
    df_raw = pd.read_csv(url, header=None, encoding="euc-kr")

    # 2) 멀티헤더 분리
    header_rows = df_raw.iloc[0:2]
    data_rows   = df_raw.iloc[2:].reset_index(drop=True)

    # 3) 연도-지표 맵핑 생성
    year_metric_map = {}
    for col_idx, year_val in enumerate(header_rows.iloc[0]):
        if pd.isna(year_val):
            continue
        year = int(year_val)
        # 해당 연도 위치부터 6개 지표(종건수,책건수,대출건수,종비율,책비율,대출건수비율)
        for offset in range(6):
            metric = header_rows.iloc[1, col_idx + offset]
            year_metric_map[col_idx + offset] = (year, metric)

    # 4) 레코드 생성 (오직 "대출건수"만)
    records = []
    for _, row in data_rows.iterrows():
        gu  = row[0]  # 0번 컬럼: 자치구
        cls = row[1]  # 1번 컬럼: 분류명
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
            records.append({
                "연도": year,
                "자치구": gu,
                "분류": cls,
                "대출건수": cnt
            })

    # 5) tidy DataFrame
    df = pd.DataFrame.from_records(records)
    df = df.dropna(subset=["대출건수"])
    df["대출건수"] = df["대출건수"].astype(int)
    return df

# 데이터 로드·전처리
df = load_and_preprocess()

# 페이지 타이틀
st.title("서북권 공공도서관 KDC 분류별 연간 대출 현황")

# (디버깅용) 컬럼 확인
st.write("#### 컬럼:", df.columns.tolist())

# 사이드바: 필터
st.sidebar.header("필터")
years = sorted(df["연도"].unique(), reverse=True)
selected_year = st.sidebar.selectbox("연도 선택", years)
gis    = ["전체"] + sorted(df["자치구"].unique())
selected_gu = st.sidebar.selectbox("자치구 선택", gis)
class_list = ["전체"] + sorted(df["분류"].unique())
selected_cls = st.sidebar.selectbox("KDC 분류 선택", class_list)

# 필터링
filtered = df[df["연도"] == selected_year]
if selected_gu != "전체":
    filtered = filtered[filtered["자치구"] == selected_gu]
if selected_cls != "전체":
    filtered = filtered[filtered["분류"] == selected_cls]

# 메인: 전체 막대차트
st.subheader(f"{selected_year}년 대출건수 분포")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(
    data=filtered,
    x="분류",
    y="대출건수",
    hue="자치구",
    dodge=True,
    ax=ax
)
plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)

# 연도별 추세 (선택된 조건 기반)
st.subheader("연도별 대출건수 추세")
trend = df.copy()
# 추세 필터링: 자치구/분류
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
