# 📚 서울도서관 도서 대출 통계 분석

서울도서관의 2024년 성별·도서 분야별 대출 데이터를 바탕으로 시각화한 Streamlit 기반 웹 앱입니다.

![Streamlit Screenshot](https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png)

---

## 📂 데이터 개요

- **데이터 출처**: 서울도서관 공공데이터
- **분석 대상**: 도서 분야별 성별 대출 건수
- **데이터 파일명**: `서울도서관 도서분야별성별 대출 통계_2024) .csv`

---

## 🧠 주요 기능

- 도서 분야별 **성별 대출 건수 시각화**
- **남녀 대출 비교** 그래프
- 전체 대출 건수 총합 확인
- 필터 기능 (성별 선택)

---

## 🚀 설치 및 실행

```bash
# 1. 리포지토리 클론
git clone https://github.com/<your-username>/suhang.git
cd suhang

# 2. 가상환경(optional) 및 필요한 라이브러리 설치
pip install -r requirements.txt

# 3. Streamlit 앱 실행
st.write("컬럼명 확인:", df.columns.tolist())

