# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정 (Windows / macOS-Linux 대응)
plt.rcParams['font.family'] = 'Malgun Gothic' if os.name == 'nt' else 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_data():
    path = "data/서울도서관 도서분야별성별 대출 통계_2024) .csv"
    # 첫 두 행(타이틀, 컬럼 헤더 설명)을 건너뛰고 3행부터 data, header=None으로
    cols = ['성별','연령대','총류','철학','종교','사회','순수','기술','예술','언어','문학','역사','기타','합계']
    df = pd.read_csv(path, encoding='cp949', skiprows=2, header=None, names=cols)
    # 빈 연령대 행 제거
    df = df.dropna(subset=['연령대'])
    return df

# 앱 제목
st.title("📚 서울도서관 분야별·성별 대출 통계 (2024)")
st.markdown("본 대시보드는 **성별**, **연령대**, 그리고 **전체 도서 분류** 관점에서 대출 통계를 시각화합니다.")

# 데이터 로드
df = load_data()

# (디버깅) 컬럼명 확인
st.write("#### 데이터 컬럼:", df.columns.tolist())

# 원본 데이터 보기
if st.checkbox("원본 데이터 보기"):
    st.dataframe(df)

# 분석1: 성별별 분야 대출 비교
st.header("1️⃣ 성별별 도서 분류 대출 비교")
# melt long-form
fields = cols[2:-1]  # '총류'부터 '기타'까지
df_long = df.melt(id_vars=['성별','연령대'], value_vars=fields,
                  var_name='분야', value_name='대출권수')

fig1, ax1 = plt.subplots(figsize=(10,5))
sns.barplot(data=df_long, x='분야', y='대출권수', hue='성별',
            estimator=sum, ax=ax1, palette='Set2')
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
st.pyplot(fig1)

# 분석2: 연령대별 전체 대출 건수
st.header("2️⃣ 연령대별 전체 대출 건수")
df_age = df.groupby('연령대')['합계'].sum().reindex(df['연령대'].unique()).reset_index()
fig2, ax2 = plt.subplots(figsize=(8,4))
sns.barplot(data=df_age, x='연령대', y='합계', ax=ax2, palette='Blues_d')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
ax2.set_ylabel('총 대출 건수')
st.pyplot(fig2)

# 분석3: 전체 분류별 총 대출 건수
st.header("3️⃣ 분야별 전체 대출 건수 순위")
df_cat = df_long.groupby('분야')['대출권수'].sum().reset_index().sort_values('대출권수', ascending=False)
fig3, ax3 = plt.subplots(figsize=(10,5))
sns.barplot(data=df_cat, x='분야', y='대출권수', ax=ax3, palette='rocket')
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45)
ax3.set_ylabel('총 대출 건수')
st.pyplot(fig3)
