# app.py
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="서울도서관 분야별·성별 대출 분석", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/서울도서관 도서분야별성별 대출 통계_2024) .csv",
        encoding="utf-8-sig"
    )
    df = df.rename(columns={"Unnamed: 0": "성별"})
    df["성별"] = df["성별"].ffill()
    df = df.dropna(subset=["연령대"])
    return df

df = load_data()

st.title("📚 서울도서관 분야별·성별 대출 통계 (2024년)")

# 사이드바 필터
st.sidebar.header("필터")
genders = ["전체"] + df["성별"].unique().tolist()
sel_gender = st.sidebar.selectbox("성별 선택", genders)
ages = ["전체"] + df["연령대"].unique().tolist()
sel_age = st.sidebar.selectbox("연령대 선택", ages)

# 데이터 필터링
df_filtered = df.copy()
if sel_gender != "전체":
    df_filtered = df_filtered[df_filtered["성별"] == sel_gender]
if sel_age != "전체":
    df_filtered = df_filtered[df_filtered["연령대"] == sel_age]

# 분석 대상 컬럼 추출
class_cols = [col for col in df_filtered.columns if col not in ["성별", "연령대", "합계"]]

# 데이터를 long 포맷으로 변환
df_long = df_filtered.melt(
    id_vars=["성별", "연령대"],
    value_vars=class_cols,
    var_name="분야",
    value_name="대출권수"
)

# 분야별 대출 건수 시각화
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

# 원본 데이터 보기
with st.expander("원본 데이터 보기"):
    st.dataframe(df_filtered.reset_index(drop=True))
