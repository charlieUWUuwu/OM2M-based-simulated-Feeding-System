from requests.auth import HTTPBasicAuth
from flask import Flask, request, Response, jsonify, render_template
from flask_cors import CORS
import requests
import configparser, json
import xml.etree.ElementTree as ET
import mylibs.in_API as in_API

api = Flask(__name__)
CORS(api)

# ---------------------------------------------------------
config = configparser.ConfigParser()
with open('config.json', 'r') as f:
    config = json.load(f)

in_IP = config["in_cse"]["ip"] # 127.0.0.1
in_PORT = config["in_cse"]["port"] # 3000
WEB_DATA_ROUTE = config["in_cse"]["route"]["WEB_DATA"] 
WEB_CONTROL_ROUTE = config["in_cse"]["route"]["WEB_CONTROL"]
WATER_THRESHOLD = int(config["water_threshold"])
FOOD_THRESHOLD = int(config["food_threshold"])
penIds = config["pen_ids"]
# ---------------------------------------------------------
data_show = {pen_id: {"water": 100, "food": 100, "warning": ""} for pen_id in penIds}
# ---------------------------------------------------------


# 解析出 penId、water、food
def _parseData(raw_data, format="xml"):
    if (format=="xml"):
        root = ET.fromstring(raw_data)
        con_content = root.find('.//con').text
        con_root = ET.fromstring(con_content) # 再次解析
        penId = con_root.find('.//str[@name="penId"]').attrib['val']
        water_value = con_root.find('.//int[@name="water"]').attrib['val']
        food_value = con_root.find('.//int[@name="food"]').attrib['val']
    elif(format=="json"):
        print("raw_data\n", raw_data)
        data = raw_data['m2m:sgn']['m2m:nev']['m2m:rep']['m2m:cin']['con']
        penId = data.split('name="penId" val="')[1].split('"')[0]
        water_value = int(data.split('name="water" val="')[1].split('"')[0])
        food_value = int(data.split('name="food" val="')[1].split('"')[0])
    return penId, water_value, food_value

# 更新 data_show 內容
def _update2LatestData():
    global data_show
    for id, data in data_show.items():
        url = 'http://127.0.0.1:8080/~/in-cse/in-name/WEB_DATA/{0}/la'.format(id)
        response = requests.get(
            url,
            auth = HTTPBasicAuth('admin', 'admin')
        )
        if (response.status_code == 200 or response.status_code == 201):
            penId, water_value, food_value = _parseData(response.text, "xml")
        else:
            penId, water_value, food_value = id, 100, 100
            
        data_show[penId]["water"] = water_value
        data_show[penId]["food"] = food_value
    print("data_show : \n", data_show)
    

@api.route("/home")
def home():
    global data_show
    _update2LatestData()
    return render_template("home.html", data_show=data_show)

# 與前端約定的route，會定時自動觸發更新
@api.route('/getDisplayData', methods=['GET'])
def getDisplayData():
    global data_show
    _update2LatestData()
    print("觸發自動刷新")
    return jsonify(data_show)

@api.route('/button_click', methods=['POST'])
def button_click():
    penId, action = request.form['penId'], request.form['action']
    in_API.create_CIN_action(WEB_CONTROL_ROUTE, penId, "DATA", action)
    return "按鈕點擊成功"

# ADN : 解析OM2M格式，並根據 penId 傳送至前端更新顯示
@api.route('/'+WEB_DATA_ROUTE, methods=['POST'])
def processSensorData():
    penId, water_value, food_value = _parseData(request.json, 'json')
    print("penId: ", penId, "; food: ", food_value, "; water: ", water_value)
    
    # 添加一筆資料到 IN 的 WEB_DATA 
    res = in_API.create_CIN_data(WEB_DATA_ROUTE, penId, penId, water_value, food_value)

    # 更新顯示資料
    _update2LatestData()

    # response
    response = Response('') # 創建一個空的HTTP響應對象
    response.headers["X-M2M-RSC"] = 2000
    cseRelease = '3'
    response.headers["X-M2M-RVI"] = cseRelease
    return response

# ASN : 解析OM2M格式，檢查新增的資料, 看是否顯示警告以及觸發自動餵食
@api.route('/'+WEB_CONTROL_ROUTE, methods=['POST'])
def checkData():
    global data_show, WATER_THRESHOLD, FOOD_THRESHOLD

    # get data from any AE (PEN)
    penId, water_value, food_value = _parseData(request.json, 'json')

    warning = ""
    if(water_value <= WATER_THRESHOLD):
        warning += "水太少  "
        in_API.create_CIN_action(WEB_CONTROL_ROUTE, penId, "DATA", "add_water")
    if(food_value <= FOOD_THRESHOLD):
        warning += "食物太少"
        in_API.create_CIN_action(WEB_CONTROL_ROUTE, penId, "DATA", "add_food")

    data_show[penId]["warning"] = warning
    print(data_show[penId]["warning"])

    response = Response('')
    response.headers["X-M2M-RSC"] = 2000
    cseRelease = '3'
    response.headers["X-M2M-RVI"] = cseRelease
    return response
    
if __name__ == '__main__':
    api.run(host=in_IP, port=in_PORT, debug=True)
    
    