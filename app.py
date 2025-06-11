# app.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

st.set_page_config(page_title="서울도서관 분야별·성별 대출 분석", layout="wide")

@st.cache_data
def load_data():
    # 1) 엑셀 읽기 (skiprows=1 해서 두 번째 행을 헤더로 사용)
    df = pd.read_excel(
        "data/2b279523-9118-463e-a125-7ee8e4055776.xlsx",
        sheet_name="Sheet1",
        skiprows=1,
        engine="openpyxl"
    )
    # 2) 컬럼명 정리
    df = df.rename(columns={"Unnamed: 0": "성별"})
    # 3) 첫 행(남성/여성 분리)에서 성별이 NaN인 경우 앞 성별 채움
    df["성별"] = df["성별"].ffill()
    # 4) 불필요한 빈 행 제거
    df = df.dropna(subset=["연령대"])
    return df

df = load_data()

st.title("📚 서울도서관 분야별·성별 대출 통계 (2024년)")

# — 사이드바 필터
st.sidebar.header("필터")
genders = ["전체"] + df["성별"].unique().tolist()
sel_gender = st.sidebar.selectbox("성별 선택", genders)
ages    = ["전체"] + df["연령대"].unique().tolist()
sel_age    = st.sidebar.selectbox("연령대 선택", ages)

# 1) 데이터 필터링
df_filtered = df.copy()
if sel_gender != "전체":
    df_filtered = df_filtered[df_filtered["성별"] == sel_gender]
if sel_age != "전체":
    df_filtered = df_filtered[df_filtered["연령대"] == sel_age]

# 2) Melt to long for classification visualization
class_cols = [c for c in df_filtered.columns if c not in ["성별", "연령대", "합계"]]
df_long = df_filtered.melt(
    id_vars=["성별", "연령대"],
    value_vars=class_cols,
    var_name="분야",
    value_name="대출권수"
)

# 3) 분야별 대출 건수 바차트
st.subheader("🔢 분야별 대출 건수")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(
    data=df_long,
    x="분야",
    y="대출권수",
    hue="성별",
    estimator=sum,
    ax=ax
)
plt.xticks(rotation=45)
st.pyplot(fig)

# 4) 데이터 테이블 보기
with st.expander("원본 데이터 보기"):
    st.dataframe(df_filtered.reset_index(drop=True))

# 5) 머신러닝: KMeans 클러스터링 (옵션)
if st.checkbox("클러스터링 결과 보기 (KMeans)"):
    st.subheader("🤖 연령·성별 그룹 클러스터링")
    # 피쳐로 분야별 대출권수 사용
    X = df_filtered[class_cols].fillna(0)
    # 클러스터 개수 입력
    k = st.slider("클러스터 수 (k)", min_value=2, max_value=6, value=3)
    model = KMeans(n_clusters=k, random_state=42)
    labels = model.fit_predict(X)
    df_clustered = df_filtered.copy()
    df_clustered["cluster"] = labels.astype(str)

    # 클러스터별 그룹 요약
    st.write("### 클러스터별 연령대·성별 조합")
    st.dataframe(df_clustered.groupby("cluster")[["성별","연령대"]]
                 .agg(lambda x: ", ".join(sorted(x.unique()))).reset_index())

    # 클러스터 분포 시각화
    st.write("### 클러스터별 대출 분포(평균)")
    cluster_means = df_clustered.groupby("cluster")[class_cols].mean().reset_index().melt(
        id_vars="cluster", var_name="분야", value_name="평균대출권수"
    )
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.lineplot(
        data=cluster_means,
        x="분야",
        y="평균대출권수",
        hue="cluster",
        marker="o",
        ax=ax2
    )
    plt.xticks(rotation=45)
    st.pyplot(fig2)
