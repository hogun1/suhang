import streamlit as st
import pandas as pd

st.title("서울시 서북권 도서관 KDC 분류별 대출 현황 분석")

# 데이터 불러오기
@st.cache_data
def load_data():
    df_raw = pd.read_csv("서울시 서북권 공공도서관 KDC 분류별 연간 대출 현황.csv", header=[0, 1], encoding='utf-8')
    df_raw.columns = df_raw.columns.map(lambda x: f"{x[0]}_{x[1]}" if 'Unnamed' not in x[0] else x[1])
    df = pd.concat([df_raw.iloc[:, :2],  # 자치구, 분류
                    df_raw.iloc[:, 2:]], axis=1)

    # 연도별 tidy format 만들기
    tidy_df = pd.DataFrame()
    years = ['2018', '2019', '2020', '2021', '2022', '2023']
    for year in years:
        temp = df[['자치구', '분류',
                   f'{year}_종건수', f'{year}_책건수', f'{year}_대출건수']]
        temp = temp.rename(columns={
            f'{year}_종건수': 'title_count',
            f'{year}_책건수': 'book_count',
            f'{year}_대출건수': 'loan_count'
        })
        temp['year'] = int(year)
        tidy_df = pd.concat([tidy_df, temp])

    return tidy_df

df = load_data()

# 디버깅용 컬럼 출력
st.write("📌 데이터 컬럼:", df.columns.tolist())

# 연도 선택
selected_year = st.selectbox(
    "연도를 선택하세요:",
    sorted(df['year'].dropna().astype(int).unique(), reverse=True)
)

# 선택된 연도 필터링
filtered_df = df[df['year'] == selected_year]

# 시각화
st.subheader(f"{selected_year}년 KDC 분류별 대출 건수")
st.bar_chart(filtered_df.groupby("분류")["loan_count"].sum())
