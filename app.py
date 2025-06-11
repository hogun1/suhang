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
    path = "data/서울도서관 도서분야별성별 대출 통계_2024) .csv"
    # 1행 건너뛰고(제목), 2행을 컬럼명으로
    df = pd.read_csv(path, encoding='cp949', skiprows=1, header=0)
    df.dropna(inplace=True)
    # 컬럼명 깨끗하게
    df.columns = df.columns.str.strip()
    # Unnamed:0 → 성별, Unnamed:1 → 연령대
    if 'Unnamed: 0' in df.columns:
        df = df.rename(columns={'Unnamed: 0': '성별'})
    if 'Unnamed: 1' in df.columns:
        df = df.rename(columns={'Unnamed: 1': '연령대'})
    # '합계' 컬럼 제거
    if '합계' in df.columns:
        df = df.drop(columns=['합계'])
    return df

# 앱 제목
st.title("📚 서울도서관 분야별·성별 대출 통계 (2024)")
st.markdown("서울도서관의 2024년 도서 대출 데이터를 분야별·성별로 시각화합니다.")

# 데이터 로드
df = load_data()

# (디버깅) 컬럼명 확인
st.write("#### 로드된 컬럼명:", df.columns.tolist())

# 원본 데이터 보기
if st.checkbox("원본 데이터 보기"):
    st.dataframe(df)

# 사이드바: 필터
st.sidebar.header("필터")
genders = ['전체'] + df['성별'].unique().tolist()
sel_gender = st.sidebar.selectbox("성별 선택", genders)
ages    = ['전체'] + df['연령대'].unique().tolist()
sel_age = st.sidebar.selectbox("연령대 선택", ages)

# 필터링 적용
df_f = df.copy()
if sel_gender!='전체':
    df_f = df_f[df_f['성별']==sel_gender]
if sel_age!='전체':
    df_f = df_f[df_f['연령대']==sel_age]

# 분석 대상 컬럼 (분야들)
fields = [c for c in df_f.columns if c not in ['성별','연령대']]

# long-format 변환
df_long = df_f.melt(
    id_vars=['성별','연령대'],
    value_vars=fields,
    var_name='분야',
    value_name='대출건수'
)

# 시각화: 분야별 대출 건수
st.subheader("🔢 분야별 대출 건수")
fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(
    data=df_long, x='분야', y='대출건수', hue='성별',
    estimator=sum, ax=ax, palette='Set2'
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
st.pyplot(fig)
