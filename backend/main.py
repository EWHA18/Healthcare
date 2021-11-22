from flask      import Flask, request, jsonify, current_app, g, flash, json, send_file
from flask_cors import CORS
from sqlalchemy import create_engine, text
from werkzeug.exceptions import HTTPException, NotFound
import datetime as dt
import os
from werkzeug.utils import secure_filename
import pandas as pd
import csv


app = Flask(__name__)
database = create_engine("mysql+mysqlconnector://'root':1234@localhost:3306/healthcare?charset=utf8", encoding = 'cp949', max_overflow = 0)
app.database = database

# 각 중금속 별 인체 노출 안전 기준(ug/kg b.w./day)
limit = {
  "납": 0.000264,
  "카드뮴": 0.000833,
  "총 비소": 0.001285,
  "총 수은": 0.000528
}

cors = CORS(app, resources = {
    r"/v1/*": {"origin": "*"},
    r"/api/*": {"origin": "*"}
  })

# HTTP Exception Handler
@app.errorhandler(HTTPException)
def error_handler(e):
    response = e.get_response()

    response.data = json.dumps({
        'status': e.code,
        'success': False,
        'message': e.description,
    })
    response.content_type = 'application/json'

    return response

# 섭취량 계산 함수
def calculate(medicine_name, num, intake):
  # 제품명을 통한 제품의 성분 함유랑 DB 검색
  product = database.execute(text("""
   SELECT
      ingredient
    FROM Medicine
      WHERE product = :medicine_name
  """), {'medicine_name': medicine_name}).fetchone()
  
  # 등록되지 않은 제품인 경우 종료
  if product is None:
        return medicine_name
 
  # 1-2_다량영양소_단백질_g_20:2-1_무기질_칼슘_mg_300:2-3_무기질_마그네슘_mg_100:2-7_무기질_아연_mg_8.5 형태의 데이터
  ingredients = product[0].split(":")
  ingredients.pop()
  
  # 각 영양소 별 섭취량 계산
  for ingredient in ingredients:
    field = ingredient.split("_")
    word_id = field[0] # 성분 ID
    classification = field[1] # 대분류
    word_name = field[2] # 성분 이름
    unit = field[3] # 단위
    volume = float(field[4]) # 함유량
    isHeavyMetal = False # 중금속 여부
    if(classification=="중금속"): 
      isHeavyMetal = True
    prev=False
    
    # 기존에 섭취한 성분인 경우
    for i in range(0,len(intake)):
      if intake[i]['word_id'] == word_id:
        intake[i]['volume'] += volume*float(num)
        prev=True
        
    # 기존에 섭취하지 않은 성분인 경우
    if(prev==False):
      data={
        "word_id": word_id,
        "word_name":word_name,
        "volume":volume*float(num),
        "unit":unit,
        "isHeavyMetal": isHeavyMetal,
        "percentage": 0
      }
      intake.append(data)
  

  for i in range(0, len(intake)):
    intake[i]['volume'] = intake[i]['volume']
    
  return None
        
  
# 단일 사용자 섭취량 계산 후 return
@app.route("/api/sendintake", methods=['POST'])
def func():
  # intake(섭취량), name(제품 이름), weight(몸무게)
  req=request.json
  intake=[]
  weight = float(0) # 몸무게
  
  # 섭취 제품 별 
  for medicine in req['data']:
        calculate(medicine['name'].strip(), medicine['intake'], intake)
        weight = medicine['weight']

  # 중금속 섭취 퍼센티지 계산
  for ingredient in intake:
      if ingredient['word_name'] in limit:
           ingredient['percentage'] = ingredient['volume']/(limit[ingredient['word_name'].strip()]*float(weight))
           # 0.264/1000 *A 
           # 10/(0.000264*A) *100%
           # volume/(limit['성분']*몸무게)*100

  data={}
  data["intake"]=intake
  return jsonify({
            "status": 200,
            "success": True,
            "data": data
        })

# DB에 등록되지 않은 제품 기록
def add_debug(personalID, product_name):
    debugFile = open(".\\debugFile.csv", mode="a", newline='', encoding='UTF-8')
    writer = csv.writer(debugFile)
    rowInfo = []
    rowInfo.append(personalID)
    rowInfo.append(product_name)
    writer.writerow(rowInfo)      
    debugFile.flush()
    debugFile.close() 

# 다중 사용자인 경우 파일 읽고 처리하기
def csv_process(filename):
  file = pd.read_csv("./csv/"+filename, engine='python', encoding='cp949')
  data = []
  weights = {}

  for i in range(0, len(file)):
      name = str(file.loc[i]['개인ID'])
      weight = file.loc[i]['추정체중(Kg)']
      medicine_name = str(file.loc[i]['데이터베이스 제품명']).strip()
      num = file.loc[i]['1일 건기식 섭취량 (제품의 1일 권장섭취량 대비)']
      flag = False
      
      # 기존에 기록된 사용자인 경우 
      for person in data:
            if person['name'] == name:
                  product_name = calculate(medicine_name, num, person['intake'])
                  if product_name is not None:
                        add_debug(name, product_name)
                  flag = True
                  break
      
      # 기존에 기록되지 않은 사용자인 경우          
      if(flag == False):
            dt = {}
            dt['name'] = name
            dt['intake'] = [] 
            product_name = calculate(medicine_name, num, dt['intake'])
            if product_name is not None:
                  add_debug(name, product_name) # 디버그 파일에 추가
            weights[name] = weight
            data.append(dt)
            # person name, intake를 가지고 있는 dict 를 data 에 삽입
  # 중금속 섭취 퍼센티지 계산           
  for person in data:
        for ingredient in person['intake']:
              if ingredient['word_name'].strip() in limit:
                ingredient['percentage'] = ingredient['volume']/(limit[ingredient['word_name'].strip()]*weights[person['name']])


  return data
          
# CSV 파일 입력       
@app.route("/api/sendfile", methods=['POST'])
def file():
  if request.method == 'POST':
        
    # 별도로 파일 저장 후 읽어서 처리
    csv_file = request.files['file']
    filename = secure_filename(str(dt.datetime.now()).replace(" ", "").replace("-","_").replace(":", "_").replace(".", "_") + ".csv")

    if not os.path.exists('csv'):
            os.makedirs('csv')

    csv_file.save('./csv/{0}'.format(filename))
    
    data = csv_process(filename)
    os.remove("./csv/"+filename)
    
    return jsonify({
          "status": 200,
          "success": True,
          "data": data
    })
    
# CSV 파일로 결과 작성    
@app.route("/api/exportFile", methods=['POST'])
def exportFile():      
      ingredients = []
      ingredients.append("이름")
      ingredientsName = []
      
      # DB에서 각 성분 정보를 모두 Search
      ingredientInfo = database.execute(text("""
        SELECT
          name
        FROM Word
      """), ).fetchall()

      # 성분 명 추출
      for ingredient in ingredientInfo:
            ingredients.append(ingredient[0])
            ingredientsName.append(ingredient[0].split("_")[0]+ingredient[0].split("_")[2])
      
      # 별도로 섭취 비율을 계산해야 하는 네 가지 중금속 처리를 위함     
      ingredients.append("납")
      ingredients.append("총 수은")
      ingredients.append("카드뮴")
      ingredients.append("총 비소")
      
      req=request.json
      filename = secure_filename(str(dt.datetime.now()).replace(" ", "").replace("-","_").replace(":", "_").replace(".", "_") + ".csv")
      
      exportFile = open(f".\\{filename}", mode="w", newline='', encoding='UTF-8')
      writer = csv.writer(exportFile)
      writer.writerow(ingredients)
      
      # 사용자 별 성분 섭취량 CSV 파일에 Write
      for userInfo in req['data']:
          rowInfo = [] # CSV 파일에 적을 정보
          heavyMetalPercentage = [] # 중금속 섭취 비율
          rowInfo.append(userInfo['name'])
          for ingredientName in ingredientsName:
              isAppended = False
              # 섭취한 성분인 경우
              for ingredients in userInfo['intake']:
                    if ingredientName == ingredients['word_id']+ingredients['word_name']:
                          rowInfo.append(ingredients['volume'])
                          isAppended = True
                          # 중금속 섭취 비율 추가
                          if ingredients['word_name'] == "납" and ingredients['word_id'] == "8-13":
                                heavyMetalPercentage.append(ingredients['percentage'])
                          elif ingredients['word_name'] == "총 수은" and ingredients['word_id'] == "8-14":
                                heavyMetalPercentage.append(ingredients['percentage'])
                          elif ingredients['word_name'] == "카드뮴" and ingredients['word_id'] == "8-15":
                                heavyMetalPercentage.append(ingredients['percentage'])    
                          elif ingredients['word_name'] == "총 비소" and ingredients['word_id'] == "8-16":
                                heavyMetalPercentage.append(ingredients['percentage'])  
                          break
                    
              # 섭취하지 않은 성분인 경우
              if isAppended == False:
                    rowInfo.append(0)
                    # 각 중금속 섭취 비율에 대해서도 0 저장
                    if ingredientName == "8-16총 비소":
                          heavyMetalPercentage.append(0)
                    elif ingredientName == "8-14총 수은":
                          heavyMetalPercentage.append(0)
                    elif ingredientName == "8-13납":
                          heavyMetalPercentage.append(0)  
                    elif ingredientName == "8-15카드뮴":
                          heavyMetalPercentage.append(0) 
                    
          for percentage in heavyMetalPercentage:
                rowInfo.append(percentage)
          
          writer.writerow(rowInfo)
      
      exportFile.flush()
      exportFile.close()
      
      return send_file(
        filename,
        mimetype='text/csv',
        as_attachment=True,
        attachment_filename="medicineIntake.csv"
      )
      
      
      

if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000", debug=True)