import scipy.io
import csv
import pymysql
import math
import pandas as pd
import datetime

#user, password, db를 각각 로컬 환경에 맞게 변경
conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='hj', charset='utf8')
curs = conn.cursor()
conn.commit()

f = open("word_input_name.csv",'r',encoding = 'utf8') #파일 읽기
csvReader = csv.reader(f)
next(f)

for row in csvReader: #파일의 각 줄을 word 테이블의 name 칼럼에 삽입
    sql = """insert into word (name) values (%s)"""
    curs.execute(sql, (row))
conn.commit()

f.close() #파일 닫기