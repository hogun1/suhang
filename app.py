# app.py
import matplotlib.font_manager as fm

# 설치된 폰트 출력
font_list = [font.name for font in fm.fontManager.ttflist]
font_list
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트

plt.rcParams['font.family'] = 'NanumGothic'
@st.cache_data
def load_data():
    path = "data/서울도서관 도서분야별성별 대출 통계_2024) .csv"
    encodings = ['cp949', 'utf-8', 'euc-kr', 'latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc, skiprows=1, header=0)
            break
        except:
            continue
    else:
        raise UnicodeDecodeError(f"Cannot decode {path}")
    df.columns = df.columns.str.strip()
    orig = df.columns.tolist()
    df.columns = ['성별','연령대'] + orig[2:]
    if '합계' in df.columns:
        df = df.drop(columns=['합계'])
    df = df.dropna(subset=['연령대'])
    return df

df = load_data()

st.title("📚 서울도서관 대출 통계 대시보드 (2024)")
st.markdown("탭을 클릭해 분석 결과를 전환해보세요.")

# 필터
st.sidebar.header("필터")
genders = ['전체'] + df['성별'].unique().tolist()
sel_gender = st.sidebar.selectbox("성별 선택", genders)
ages    = ['전체'] + df['연령대'].unique().tolist()
sel_age = st.sidebar.selectbox("연령대 선택", ages)

df_f = df.copy()
if sel_gender!='전체':
    df_f = df_f[df_f['성별']==sel_gender]
if sel_age!='전체':
    df_f = df_f[df_f['연령대']==sel_age]

fields = [c for c in df_f.columns if c not in ['성별','연령대']]

df_long = df_f.melt(
    id_vars=['성별','연령대'],
    value_vars=fields,
    var_name='분야',
    value_name='대출건수'
)
df_long.dropna(subset=['분야','대출건수'], inplace=True)
df_long['필드'] = df_long['분야'].astype(str)
df_long['대출건수'] = pd.to_numeric(df_long['대출건수'], errors='coerce').fillna(0)

# 탭 생성
tab1, tab2, tab3 = st.tabs(["성별별 분류 비교", "연령대별 합계", "분야별 순위"])

with tab1:
    st.header("1️⃣ 성별별 도서 분류 대출 비교")
    fig1, ax1 = plt.subplots(figsize=(10,5))
    sns.barplot(
        data=df_long, x='분야', y='대출건수', hue='성별',
        estimator=sum, ax=ax1, palette='Set2'
    )
    plt.xticks(rotation=45)
    st.pyplot(fig1)

with tab2:
    st.header("2️⃣ 연령대별 전체 대출 건수")
    df_age = df_long.groupby('연령대')['대출건수'].sum().reset_index()
    fig2, ax2 = plt.subplots(figsize=(8,4))
    sns.barplot(data=df_age, x='연령대', y='대출건수', ax=ax2, palette='Blues_d')
    plt.xticks(rotation=45)
    ax2.set_ylabel('총 대출 건수')
    st.pyplot(fig2)

with tab3:
    st.header("3️⃣ 분야별 전체 대출 건수 순위")
    df_cat = df_long.groupby('분야')['대출건수'].sum().reset_index().sort_values('대출건수', ascending=False)
    fig3, ax3 = plt.subplots(figsize=(10,5))
    sns.barplot(data=df_cat, x='분야', y='대출건수', ax=ax3, palette='rocket')
    plt.xticks(rotation=45)
    ax3.set_ylabel('총 대출 건수')
    st.pyplot(fig3)
