import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv('data/library_loans.csv', encoding='utf-8')

df = load_data()

st.title("서울시 서북권 도서관 KDC 분류별 연간 대출 분석")
st.markdown("""
이 프로젝트는 공공데이터포털에서 제공한 서울시 서북권 공공도서관 KDC 분류별 연간 대출 데이터를 활용하여,
연도별, 도서관별, KDC 주제별 대출 추세를 분석하고 시각화합니다.
""")

# 사용자 선택: 연도별
selected_year = st.selectbox("연도를 선택하세요:", sorted(df['연도'].unique(), reverse=True))
filtered = df[df['연도'] == selected_year]

# 시각화
st.subheader(f"{selected_year}년 KDC 대출 건수")
fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x='KDC분류', y='대출건수', data=filtered, ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)
import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv('data/library_loans.csv', encoding='utf-8')
    st.write("### 데이터 컬럼 목록", df.columns.tolist())
    return df

df = load_data()

