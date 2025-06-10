import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 스트림릿 기본 설정
st.set_page_config(page_title="도서 대출 데이터 분석", layout="wide")

st.title("📚 서울시 서북권 공공도서관 대출 현황 분석")

# CSV 파일 GitHub raw 링크
csv_url = "https://raw.githubusercontent.com/hogun1/suhang/main/data/%EC%84%9C%EC%9A%B8%EC%8B%9C%20%EC%84%9C%EB%B6%81%EA%B6%8C%20%EA%B3%B5%EA%B3%B5%EB%8F%84%EC%84%9C%EA%B4%80%20KDC%20%EB%B6%84%EB%A5%98%EB%B3%84%20%EC%97%B0%EA%B0%84%20%EB%8C%80%EC%B6%9C%20%ED%98%84%ED%99%A9.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(csv_url)
    return df

# 데이터 불러오기
df = load_data()

# 데이터 미리 보기
st.subheader("🔍 데이터 미리 보기")
st.dataframe(df.head())

# 연도와 KDC 분류 기준으로 피벗 테이블 생성
st.subheader("📊 연도별 KDC 분류 대출량")
pivot_df = df.pivot_table(index='연도', columns='KDC', values='대출권수', aggfunc='sum')

# 시각화
fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(data=pivot_df, marker="o", ax=ax)
ax.set_title("연도별 KDC 분류 대출권수 추이", fontsize=16)
ax.set_xlabel("연도")
ax.set_ylabel("대출권수")
ax.legend(title="KDC 분류")
st.pyplot(fig)

# 특정 KDC 선택 후 연도별 변화 보기
st.subheader("📈 특정 KDC 분류 선택 시 변화")
kdc_options = df['KDC'].unique()
selected_kdc = st.selectbox("KDC 분류를 선택하세요", kdc_options)

filtered_df = df[df['KDC'] == selected_kdc]

fig2, ax2 = plt.subplots()
sns.barplot(data=filtered_df, x='연도', y='대출권수', ax=ax2)
ax2.set_title(f"{selected_kdc} 분류의 연도별 대출권수")
st.pyplot(fig2)
