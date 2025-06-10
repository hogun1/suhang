import streamlit as st
import pandas as pd

df = pd.read_csv("data/library_loans_tidy.csv")

# 컬럼명 확인 (디버깅용)
st.write("🔍 DataFrame 컬럼:", df.columns.tolist())

# 연도 선택 박스 (오류 없는 방식)
selected_year = st.selectbox(
    "연도를 선택하세요:",
    sorted(df['year'].dropna().astype(int).unique(), reverse=True)
)
