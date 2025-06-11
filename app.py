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
    path = "data/서울도서관 도서분야별성별 대출 통계_2024) .csv"
    encodings = ['cp949', 'utf-8', 'euc-kr', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc, skiprows=1, header=0)
            break
        except Exception:
            continue
    else:
        raise UnicodeDecodeError(f"Cannot decode {path}")

    # 원본 컬럼명
    orig_cols = df.columns.tolist()

    # 첫 두 컬럼을 '성별', '연령대'로 재명명, 나머지 그대로 유지
    new_cols = ['성별', '연령대'] + orig_cols[2:]
    df.columns = new_cols

    # '합계' 컬럼이 있으면 제거
    if '합계' in df.columns:
        df = df.drop(columns=['합계'])

    # 빈 연령대 행 제거
    df = df.dropna(subset=['연령대'])
    return df

# 앱 타이틀
st.title("📚 서울도서관 분야별·성별 대출 통계 (2024)")
st.markdown("서울도서관의 2024년 도서 대출 데이터를 분야별·성별, 연령대별로 시각화합니다.")

# 데이터 로드
df = load_data()

# (디버깅) 실제 컬럼명 확인
st.write("#### 데이터 컬럼:", df.columns.tolist())

# 원본 데이터 보기
if st.checkbox("원본 데이터 보기"):
    st.dataframe(df)

# 사이드바: 성별/연령대 필터
st.sidebar.header("필터")
genders = ['전체'] + df['성별'].unique().tolist()
sel_gender = st.sidebar.selectbox("성별 선택", genders)
ages    = ['전체'] + df['연령대'].unique().tolist()
sel_age = st.sidebar.selectbox("연령대 선택", ages)

# 필터링
df_f = df.copy()
if sel_gender!='전체':
    df_f = df_f[df_f['성별']==sel_gender]
if sel_age!='전체':
    df_f = df_f[df_f['연령대']==sel_age]

# 분석할 분야 컬럼 목록 (성별, 연령대 제외)
fields = [c for c in df_f.columns if c not in ['성별','연령대']]

# long-format 변환
df_long = df_f.melt(
    id_vars=['성별','연령대'],
    value_vars=fields,
    var_name='분야',
    value_name='대출건수'
)

# 분석1: 성별별 분야 대출 비교
st.header("1️⃣ 성별별 도서 분류 대출 비교")
fig1, ax1 = plt.subplots(figsize=(10,5))
sns.barplot(
    data=df_long, x='분야', y='대출건수', hue='성별',
    estimator=sum, ax=ax1, palette='Set2'
)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
st.pyplot(fig1)

# 분석2: 연령대별 전체 대출 건수
st.header("2️⃣ 연령대별 전체 대출 건수")
df_age = df.groupby('연령대')[fields].sum().sum(axis=1).reset_index(name='총대출건수')
# 위는 (연령대별 각 분야 합산).sum(axis=1)

fig2, ax2 = plt.subplots(figsize=(8,4))
sns.barplot(data=df_age, x='연령대', y='총대출건수', ax=ax2, palette='Blues_d')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
ax2.set_ylabel('총 대출 건수')
st.pyplot(fig2)

# 분석3: 전체 분야별 총 대출 건수 순위
st.header("3️⃣ 분야별 전체 대출 건수 순위")
df_cat = df_long.groupby('분야')['대출건수'].sum().reset_index().sort_values('대출건수', ascending=False)

fig3, ax3 = plt.subplots(figsize=(10,5))
sns.barplot(data=df_cat, x='분야', y='대출건수', ax=ax3, palette='rocket')
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45)
ax3.set_ylabel('총 대출 건수')
st.pyplot(fig3)
