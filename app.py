import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic' if os.name == 'nt' else 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv('data/서울도서관 도서분야별성별 대출 통계_2024) .csv', encoding='cp949')
    df.dropna(inplace=True)
    
    # 컬럼 이름 확인용 로그 출력
    st.write("데이터 컬럼:", df.columns.tolist())

    # 컬럼명 정리 (공백 제거)
    df.columns = df.columns.str.strip()

    # 숫자형 컬럼이 제대로 변환되지 않았을 경우 대비
    df['남성'] = pd.to_numeric(df['남성'], errors='coerce')
    df['여성'] = pd.to_numeric(df['여성'], errors='coerce')

    df.dropna(inplace=True)  # 숫자로 변환 못 한 행 제거
    return df

# Streamlit 앱 구성
st.title("📚 서울도서관 도서 분야별 성별 대출 통계 (2024)")
st.markdown("이 대시보드는 서울도서관의 2024년 도서 대출 데이터를 분석합니다.")

# 데이터 로드
df = load_data()

# 원시 데이터 보기 옵션
if st.checkbox("데이터프레임 보기"):
    st.dataframe(df)

# 성별 선택
gender_option = st.radio("성별을 선택하세요:", ('남성', '여성'))

# 성별에 따라 컬럼 선택
gender_column = '남성' if gender_option == '남성' else '여성'

# 시각화용 X축 이름 (컬럼명 직접 확인)
x_column = '도서분야' if '도서분야' in df.columns else df.columns[0]  # 첫 번째 컬럼 fallback

# 분야별 성별 대출 건수 시각화
st.subheader(f"📊 분야별 {gender_option} 대출 건수")
fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(data=df, x=x_column, y=gender_column, ax=ax, palette='Set2')
plt.xticks(rotation=45)
st.pyplot(fig)

# 성별 비교 시각화
st.subheader("👥 성별 대출 비교")
df_melted = df.melt(id_vars=x_column, value_vars=['남성', '여성'], var_name='성별', value_name='대출건수')
fig2, ax2 = plt.subplots(figsize=(10, 6))
sns.barplot(data=df_melted, x=x_column, y='대출건수', hue='성별', ax=ax2, palette='pastel')
plt.xticks(rotation=45)
st.pyplot(fig2)

# 총합 출력
st.subheader("📈 전체 성별 대출 건수 총합")
total_male = df['남성'].sum()
total_female = df['여성'].sum()
st.write(f"**남성 대출 총합:** {total_male:,.0f}권")
st.write(f"**여성 대출 총합:** {total_female:,.0f}권")

# 출처 정보
st.markdown("---")
st.info("데이터 출처: 서울도서관 공공 데이터")
