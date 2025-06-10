import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from urllib.parse import quote

st.set_page_config(page_title="서북권 공공도서관 KDC 대출 현황", layout="wide")

@st.cache_data
def load_and_preprocess():
    # GitHub raw URL 베이스
    base = "https://raw.githubusercontent.com/hogun1/suhang/main/data/"
    # 한글 파일명 부분만 quote() 로 인코딩
    fname = "서울시 서북권 공공도서관 KDC 분류별 연간 대출 현황.csv"
    url = base + quote(fname)

    # 인코딩 시도
    for enc in ("utf-8", "euc-kr"):
        try:
            df_raw = pd.read_csv(url, header=None, encoding=enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise UnicodeDecodeError(f"Cannot decode CSV at {url}")

    # (이하 기존 전처리 로직 그대로)
    header_rows = df_raw.iloc[0:2]
    data_rows   = df_raw.iloc[2:].reset_index(drop=True)

    # 연도-지표 매핑
    year_metric = {}
    for idx, year in enumerate(header_rows.iloc[0]):
        if pd.notna(year):
            y = int(year)
            for off in range(6):
                metric = header_rows.iloc[1, idx + off]
                year_metric[idx + off] = (y, metric)

    records = []
    for _, row in data_rows.iterrows():
        gu, cls = row[0], row[1]
        if pd.isna(gu) or pd.isna(cls): continue
        for idx, (y, m) in year_metric.items():
            if m != "대출건수": continue
            raw = row[idx]
            try:
                cnt = int(str(raw).replace(",", ""))
            except:
                cnt = None
            records.append({"연도": y, "자치구": gu, "분류": cls, "대출건수": cnt})

    df = pd.DataFrame.from_records(records)
    df = df.dropna(subset=["대출건수"])
    df["대출건수"] = df["대출건수"].astype(int)
    return df

df = load_and_preprocess()

st.title("서북권 공공도서관 KDC 분류별 연간 대출 현황")

# 디버깅: 컬럼 확인
st.write("컬럼:", df.columns.tolist())

# 사이드바 필터
years = sorted(df["연도"].unique(), reverse=True)
yr = st.sidebar.selectbox("연도", years)
gus = ["전체"] + sorted(df["자치구"].unique())
gu = st.sidebar.selectbox("자치구", gus)
cls = ["전체"] + sorted(df["분류"].unique())
cl = st.sidebar.selectbox("분류", cls)

# 필터 적용
f = df[df["연도"] == yr]
if gu!="전체": f = f[f["자치구"]==gu]
if cl!="전체": f = f[f["분류"]==cl]

# 시각화
st.subheader(f"{yr}년 대출건수 분포")
fig, ax = plt.subplots(figsize=(12,6))
sns.barplot(data=f, x="분류", y="대출건수", hue="자치구", ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)
