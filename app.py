# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_data():
    path = "data/서울도서관 도서분야별성별 대출 통계_2024) .csv"
    encodings = ['cp949','utf-8','euc-kr','latin1']
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc, skiprows=1, header=0)
            break
        except:
            continue
    else:
        raise UnicodeDecodeError(f"Cannot decode {path}")
    # 컬럼명 정리
    df.columns = df.columns.str.strip()
    orig = df.columns.tolist()
    df.columns = ['성별','연령대'] + orig[2:]
    if '합계' in df.columns: df = df.drop(columns=['합계'])
    df = df.dropna(subset=['연령대'])
    return df

df = load_data()

st.title("📚 서울도서관 분야별·성별 대출 통계 (2024)")
st.markdown("탭을 클릭해 분석 결과를 전환해 보세요.")

# 필터
st.sidebar.header("필터")
genders = ['전체'] + df['성별'].unique().tolist()
sel_gender = st.sidebar.selectbox("성별 선택", genders)
ages    = ['전체'] + df['연령대'].unique().tolist()
sel_age  = st.sidebar.selectbox("연령대 선택", ages)

df_f = df.copy()
if sel_gender!='전체': df_f = df_f[df_f['성별']==sel_gender]
if sel_age!='전체':   df_f = df_f[df_f['연령대']==sel_age]

fields = [c for c in df_f.columns if c not in ['성별','연령대']]

df_long = df_f.melt(
    id_vars=['성별','연령대'],
    value_vars=fields,
    var_name='분야',
    value_name='대출건수'
).dropna()

# 탭 구성
tab1, tab2, tab3 = st.tabs(["성별별 분류 비교","연령대별 합계","분야별 순위"])

with tab1:
    st.header("1️⃣ 성별별 도서 분류 대출 비교")
    fig = px.bar(
        df_long,
        x='분야', y='대출건수', color='성별',
        title="분야별 성별 대출 건수",
        labels={'대출건수':'대출 건수','분야':'도서분야'},
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.header("2️⃣ 연령대별 전체 대출 건수")
    df_age = df_long.groupby('연령대', as_index=False)['대출건수'].sum()
    fig = px.bar(
        df_age,
        x='연령대', y='대출건수',
        title="연령대별 전체 대출 건수",
        labels={'대출건수':'총 대출 건수','연령대':'연령대'}
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.header("3️⃣ 분야별 전체 대출 건수 순위")
    df_cat = df_long.groupby('분야', as_index=False)['대출건수'].sum().sort_values('대출건수', ascending=False)
    fig = px.bar(
        df_cat,
        x='분야', y='대출건수',
        title="분야별 전체 대출 건수 순위",
        labels={'대출건수':'총 대출 건수','분야':'도서분야'}
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)
