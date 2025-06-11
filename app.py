# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic' if os.name=='nt' else 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False

@st.cache_data
def load_data():
    path = "data/서울도서관 도서분야별성별 대출 통계_2024) .csv"
    # 시도할 인코딩 리스트
    encodings = ['cp949', 'utf-8', 'euc-kr', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc, skiprows=2, header=None)
            break
        except Exception:
            continue
    else:
        raise UnicodeDecodeError(f"Cannot decode {path} with {encodings}")

    # 컬럼명 수동 할당 (2행 이후부터 데이터)
    cols = ['성별','연령대','총류','철학','종교','사회','순수','기술','예술','언어','문학','역사','기타','합계']
    df.columns = cols
    df.dropna(subset=['연령대'], inplace=True)
    # 컬럼트림
    df.columns = df.columns.str.strip()
    return df

# 앱 제목
st.title("📚 서울도서관 분야별·성별 대출 통계 (2024)")
st.markdown("서울도서관의 2024년 도서 대출 데이터를 분야별·성별로 시각화합니다.")

# 데이터 로드
df = load_data()

# 컬럼명 확인 (디버깅용)
st.write("#### 데이터 컬럼:", df.columns.tolist())

# 원본 데이터 보기
if st.checkbox("원본 데이터 보기"):
    st.dataframe(df)

# 사이드바 필터
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

# 분석할 분야 컬럼
fields = [c for c in df_f.columns if c not in ['성별','연령대','합계']]

# long-form 변환
df_long = df_f.melt(
    id_vars=['성별','연령대'],
    value_vars=fields,
    var_name='분야',
    value_name='대출건수'
)

# 분석1: 성별별 분류 대출
st.header("1️⃣ 성별별 도서 분류 대출 비교")
fig1, ax1 = plt.subplots(figsize=(10,5))
sns.barplot(data=df_long, x='분야', y='대출건수', hue='성별',
            estimator=sum, ax=ax1, palette='Set2')
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
st.pyplot(fig1)

# 분석2: 연령대별 전체 합계
st.header("2️⃣ 연령대별 전체 대출 건수")
df_age = df.groupby('연령대')['합계'].sum().reset_index()
fig2, ax2 = plt.subplots(figsize=(8,4))
sns.barplot(data=df_age, x='연령대', y='합계', ax=ax2, palette='Blues_d')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
ax2.set_ylabel('총 대출 건수')
st.pyplot(fig2)

# 분석3: 분야별 전체 대출 순위
st.header("3️⃣ 분야별 전체 대출 건수 순위")
df_cat = df_long.groupby('분야')['대출건수'].sum().reset_index().sort_values('대출건수', ascending=False)
fig3, ax3 = plt.subplots(figsize=(10,5))
sns.barplot(data=df_cat, x='분야', y='대출건수', ax=ax3, palette='rocket')
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=45)
ax3.set_ylabel('총 대출 건수')
st.pyplot(fig3)
