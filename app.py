# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 세팅
plt.rcParams['font.family'] = 'Malgun Gothic' if os.name=='nt' else 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_data():
    df = pd.read_csv(
        'data/서울도서관 도서분야별성별 대출 통계_2024) .csv',
        encoding='cp949',
        skiprows=1  # 1행 건너뛰기
    )
    df.dropna(inplace=True)
    # 'Unnamed: 0'을 '성별'로 바꿔주기
    if 'Unnamed: 0' in df.columns:
        df = df.rename(columns={'Unnamed: 0': '성별'})
    # 공백 제거
    df.columns = df.columns.str.strip()
    return df

# 앱 타이틀
st.title("📚 서울도서관 분야별·성별 대출 통계 (2024)")
st.markdown("서울도서관의 2024년 도서 대출 데이터를 분야별·성별로 시각화합니다.")

# 데이터 로드
df = load_data()

# (디버깅) 실제 컬럼명 확인
st.write("#### 데이터 컬럼:", df.columns.tolist())

# 원본 데이터 보기
if st.checkbox("원본 데이터 보기"):
    st.dataframe(df)

# 사이드바 필터
st.sidebar.header("필터")
genders = ['전체'] + df['성별'].unique().tolist()
sel_gender = st.sidebar.selectbox("성별 선택", genders)
ages    = ['전체'] + df['연령대'].unique().tolist()
sel_age    = st.sidebar.selectbox("연령대 선택", ages)

# 필터링
df_f = df.copy()
if sel_gender != '전체':
    df_f = df_f[df_f['성별'] == sel_gender]
if sel_age != '전체':
    df_f = df_f[df_f['연령대'] == sel_age]

# 분석할 분야 컬럼들
fields = [c for c in df_f.columns if c not in ['성별','연령대','합계']]

# long-format 변환
df_long = df_f.melt(
    id_vars=['성별','연령대'],
    value_vars=fields,
    var_name='분야',
    value_name='대출건수'
)

# 분야별 성별 대출 건수
st.subheader("🔢 분야별 대출 건수")
fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(
    data=df_long,
    x='분야',
    y='대출건수',
    hue='성별',
    estimator=sum,
    ax=ax
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
st.pyplot(fig)
