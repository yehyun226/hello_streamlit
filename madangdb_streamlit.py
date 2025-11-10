import streamlit as st        
import pandas as pd          
import time 
import duckdb

conn = duckdb.connect(database='madang.db')
conn.sql("CREATE TABLE IF NOT EXISTS Customer AS SELECT * FROM 'Customer_madang.csv'")
conn.sql("CREATE TABLE IF NOT EXISTS Book AS SELECT * FROM 'Book_madang.csv'")
conn.sql("CREATE TABLE IF NOT EXISTS Orders AS SELECT * FROM 'Orders_madang.csv'")

def query(sql, returnType='df'):
    if returnType == 'df':
        return conn.execute(sql).df()  # 실행, 판다스 변환
    else:
        return conn.execute(sql).fetchall()  # 리스트 변환

books = [None] 
result = query("SELECT CONCAT(bookid, ',', bookname) AS info FROM Book") 
for res in result['info']:
    books.append(res)

tab1, tab2 = st.tabs(["고객조회", "거래 입력"])
# tab1: 고객 거래내역 조회
# tab2: 거래(구매) 입력

name = ""                
custid = 999           
result = pd.DataFrame() 
name = tab1.text_input("고객명")
select_book = "" 

if len(name) > 0:
    sql = f"""
        SELECT c.custid, c.name, b.bookname, o.orderdate, o.saleprice FROM Customer c, Book b, Orders o
        WHERE c.custid = o.custid AND o.bookid = b.bookid AND c.name = '{name}'; """
    result = query(sql)
    tab1.write(result)

    if not result.empty:
        custid = result['custid'][0]
        tab2.write("고객번호: " + str(custid))
        tab2.write("고객명: " + name)
        select_book = tab2.selectbox("구매 서적:", books)

        if select_book is not None:
            bookid = select_book.split(",")[0]
            dt = time.strftime('%Y-%m-%d', time.localtime())
            orderid = query("SELECT COALESCE(MAX(orderid), 0) + 1 AS nextid FROM Orders", "df")['nextid'][0]
            price = tab2.text_input("금액")

            if tab2.button("거래 입력"):
                sql = f"""
                    INSERT INTO Orders (orderid, custid, bookid, saleprice, orderdate)
                    VALUES ({orderid}, {custid}, {bookid}, {price}, '{dt}');
                """
                conn.execute(sql)
                tab2.success("거래가 입력되었습니다.")
    else:
        tab1.warning("해당 고객의 거래내역이 없습니다.")

conn.close()
