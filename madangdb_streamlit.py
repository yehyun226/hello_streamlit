import streamlit as st
import duckdb
import pandas as pd
import time

# ==========================
# 🔐 DuckDB 연결
# ==========================
DB_PATH = "madang.duckdb"   # 프로젝트 폴더 내 DB 파일
conn = duckdb.connect(DB_PATH)

# ==========================
# 🏗️ 초기 테이블 생성 (CSV → DuckDB)
# ==========================

conn.sql("""
CREATE TABLE IF NOT EXISTS Customer AS
SELECT * FROM read_csv_auto('Customer_madang.csv')
""")

conn.sql("""
CREATE TABLE IF NOT EXISTS Book AS
SELECT * FROM read_csv_auto('Book_madang.csv')
""")

conn.sql("""
CREATE TABLE IF NOT EXISTS Orders AS
SELECT * FROM read_csv_auto('Orders_madang.csv')
""")

# ==========================
# 🔎 SQL 실행 함수
# ==========================
def query(sql):
    return conn.sql(sql).df()

# ==========================
# 🔧 Streamlit UI
# ==========================
st.set_page_config(page_title="서점 관리시스템", layout="wide")
st.title("서점 관리 시스템")

menu = st.sidebar.radio("메뉴 선택", [
    "고객 조회",
    "도서 조회",
    "거래 입력",
    "고객 등록",
    "거래 요약"
])

# ==========================
# 🔍 고객 조회
# ==========================
if menu == "고객 조회":
    name = st.text_input("고객 이름으로 검색", "")
    if len(name) > 0:
        sql = f"""
        SELECT c.custid, c.name, c.address, c.phone,
               b.bookname, o.orderdate, o.saleprice
        FROM Customer c
        JOIN Orders o ON c.custid = o.custid
        JOIN Book b ON o.bookid = b.bookid
        WHERE c.name ILIKE '%{name}%'
        """
        result = query(sql)
        if not result.empty:
            st.success(f"총 {len(result)}건의 거래 내역이 검색되었습니다.")
            st.dataframe(result)
        else:
            st.warning("해당 고객의 거래 내역이 없습니다.")

# ==========================
# 📚 도서 조회
# ==========================
elif menu == "도서 조회":
    st.subheader("도서 목록")
    st.dataframe(query("SELECT * FROM Book"))

# ==========================
# 🧾 거래 입력
# ==========================
elif menu == "거래 입력":
    st.subheader("거래 등록")

    customers = query("SELECT custid, name FROM Customer")
    cust_map = {
        f"{row['name']} ({row['custid']})": row['custid']
        for _, row in customers.iterrows()
    }
    cust_select = st.selectbox("고객 선택", list(cust_map.keys()))

    books = query("SELECT bookid, bookname FROM Book")
    book_map = {
        f"{row['bookname']} ({row['bookid']})": row['bookid']
        for _, row in books.iterrows()
    }
    book_select = st.selectbox("구매할 도서 선택", list(book_map.keys()))

    saleprice = st.number_input("판매 금액 입력", min_value=0, step=1000)

    if st.button("거래 입력"):
        custid = cust_map[cust_select]
        bookid = book_map[book_select]
        nextid = query("SELECT IFNULL(MAX(orderid),0)+1 AS nextid FROM Orders")["nextid"][0]
        today = time.strftime('%Y-%m-%d')

        conn.sql(f"""
        INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
        VALUES ({nextid}, {custid}, {bookid}, {saleprice}, '{today}')
        """)

        st.success(f"거래가 등록되었습니다! (거래번호: {nextid})")

# ==========================
# 🧍 고객 등록
# ==========================
elif menu == "고객 등록":
    st.subheader("🧍 신규 고객 등록")
    name = st.text_input("고객 이름")
    address = st.text_input("주소")
    phone = st.text_input("전화번호")

    if st.button("등록"):
        nextid = query("SELECT IFNULL(MAX(custid),0)+1 AS nextid FROM Customer")["nextid"][0]

        conn.sql(f"""
        INSERT INTO Customer VALUES({nextid}, '{name}', '{address}', '{phone}')
        """)

        st.success(f"신규 고객 '{name}' 등록 완료! (ID: {nextid})")

# ==========================
# 📊 거래 요약
# ==========================
elif menu == "거래 요약":
    st.subheader("거래 통계")
    df = query("""
        SELECT c.name AS 고객명,
               COUNT(o.orderid) AS 거래수,
               SUM(o.saleprice) AS 총금액
        FROM Orders o
        JOIN Customer c ON o.custid = c.custid
        GROUP BY c.name
        ORDER BY 총금액 DESC
    """)
    st.dataframe(df)
