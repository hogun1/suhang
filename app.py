# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic' if os.name == 'nt' else 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_data():
    # Excel로 읽되, 2행(0-based idx=1)을 컬럼 헤더로
    df = pd.read_excel(
        'data/서울도서관 도서분야별성별 대출 통계_2024) .csv'.replace('.csv','.xlsx'),
        header=1,
        engine='openpyxl'
    )
    # 컬럼명 깨끗하게
    df.columns = df.columns.str.strip()
    # A열 '도서분류'는 실제로 '성별' 데이터가 들어있으니 이름 교체
    if '도서분류' in df.columns:
        df = df.rename(columns={'도서분류': '성별'})
    # 성별 누락 행 채우기
    df['성별'] = df['성별'].ffill()
    # 합계 컬럼은 분석 대상이 아니므로 제거
    if '합계' in df.columns:
        df = df.drop(columns=['합계'])
    # 연령대가 없는 행 제거
    df = df.dropna(subset=['연령대'])
    return df

# 앱 타이틀
st.title("📚 서울도서관 분야별·성별 대출 통계 (2024)")

# 데이터 로드
df = load_data()

# 컬럼명 및 샘플 확인 (디버깅용)
st.write("#### 컬럼명:", df.columns.tolist())
#st.dataframe(df.head())

# 원본 데이터 보기
if st.checkbox("원본 데이터 보기"):
    st.dataframe(df)

# 사이드바: 성별/연령대 필터
st.sidebar.header("필터")
genders = ['전체'] + df['성별'].unique().tolist()
sel_gender = st.sidebar.selectbox("성별 선택", genders)
ages    = ['전체'] + df['연령대'].unique().tolist()
sel_age = st.sidebar.selectbox("연령대 선택", ages)

# 필터 적용
df_f = df.copy()
if sel_gender!='전체':
    df_f = df_f[df_f['성별']==sel_gender]
if sel_age!='전체':
    df_f = df_f[df_f['연령대']==sel_age]

# 분석할 분야(컬럼) 목록
fields = [c for c in df_f.columns if c not in ['성별','연령대']]

# 분야별 건수 long-form 변환
df_long = df_f.melt(
    id_vars=['성별','연령대'],
    value_vars=fields,
    var_name='분야',
    value_name='대출건수'
)

# 분야별 성별 대출 건수
st.subheader("🔢 분야별 대출 건수")
fig, ax = plt.subplots(figsize=(10,5))
sns.barplot(data=df_long, x='분야', y='대출건수', hue='성별', estimator=sum, ax=ax)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
st.pyplot(fig)
