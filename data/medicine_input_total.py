import scipy.io
import csv
import pymysql
import math
import pandas as pd
import datetime

#user, password, db를 각각 로컬 환경에 맞게 변경
conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='healthcare', charset='utf8')
curs = conn.cursor()
conn.commit()

f = open("DB_total_1113.csv",'r',encoding = 'utf8') #파일 읽기
csvReader = csv.reader(f)
next(f)
data = pd.read_csv("DB_total_1113.csv")
volume = data.columns[66:]
heavy = data.columns[130:141] 

for row in csvReader:
    product = row[2] #제품명
    if row[0]=="": #입력이 끝나면 종료
        break
    sub_volume = ''
    sub_heavy = ''
    for i in range(66,270): #205개의 성분중 0 이상인 값만 입력
        if(row[i]!='' and float(row[i])>0):
            sub_volume+=volume[i-66]+"_"+row[i]+':' 
    for i in range(130,141): #중금속 1일 섭취량 0 이상인 값만 입력
        if(row[i]!='' and float(row[i])>0):
            sub_heavy+=heavy[i-130]+"_"+row[i]+':'
    #DB에 입력
    sql = """insert into medicine (product,ingredient,heavy_intake) values (%s, %s, %s)"""
    curs.execute(sql, (product,sub_volume,sub_heavy))
conn.commit()

f.close()