
from flask import Flask, request, Response
import requests
import configparser, json
import time
import xml.etree.ElementTree as ET
import threading
import mylibs.mn_API as mn_API
import simulation_env

api = Flask(__name__)

# -------------------------- MN ---------------------------
config = configparser.ConfigParser()
with open('config.json', 'r') as f:
    config = json.load(f)

mn_IP = config["mn_cse"]["ip"]     # 127.0.0.1
mn_PORT = config["mn_cse"]["port"] # 3300
FEED_GATEWAY_ROUTE = config["mn_cse"]["route"]["FEED_GATEWAY"] 
# ------------------------- env ---------------------------
sim_INTERVAL = config["sim_env"]["interval"]
# ---------------------------------------------------------


# 解析出 penId、action
def _parseData(raw_data, format="xml"):
    try:
        if (format=="xml"):
            root = ET.fromstring(raw_data)
            con_content = root.find('.//con').text # 使用 XPath 獲取特定元素的值
            con_root = ET.fromstring(con_content) # 再次解析
            penId = con_root.find('.//str[@name="penId"]').attrib['val']
            action = con_root.find('.//str[@name="action"]').attrib['val']
        elif(format=="json"):
            data = raw_data['m2m:sgn']['m2m:nev']['m2m:rep']['m2m:cin']['con']
            penId = data.split('name="penId" val="')[1].split('"')[0]
            action = data.split('name="action" val="')[1].split('"')[0]
        return penId, action
    except ET.ParseError:
        print("Error parsing XML data")
        return None, None
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None, None


# 獲取農舍資料,傳給 mn-AE's DATA container
def _sendSensorData2AE():
    global sim_INTERVAL
    while(True):
        url = "http://"+simulation_env.sim_IP+":"+str(simulation_env.sim_PORT)+r"/status"
        response = requests.get(url)

        if response.status_code == 200:
            pens = response.json()
            for pen_id, pen_data in pens.items():
                mn_API.create_CIN_data(pen_id, pen_id, "DATA", pen_data["water"], pen_data["food"])
        else:
            print(f"GET 請求失敗，狀態碼：{response.status_code}")
        time.sleep(sim_INTERVAL)

def _sendActionData2AE(penId, action):
    mn_API.create_CIN_action(penId, penId, "FEEDER", action)


# 收到餵食指令, 控制程式將食物或水量加滿
@api.route('/'+FEED_GATEWAY_ROUTE, methods=['POST'])
def checkData():
    # get action from IN-CSE
    json_data = request.json
    penId, action = _parseData(json_data, 'json')
    if penId is None or action is None:
        return Response(status=400)

    # send the "add" instruction
    url = "http://"+simulation_env.sim_IP+":"+str(simulation_env.sim_PORT)+r"/feed"
    json_data = {
        "pen_id": penId,
        "action": action
    }
    response = requests.post(url, json=json_data)
    
    if response.status_code == 200:
        mn_API.create_CIN_action(FEED_GATEWAY_ROUTE, penId, "DATA", action)
        
        response = Response('')
        response.headers["X-M2M-RSC"] = 2000
        cseRelease = '3'
        response.headers["X-M2M-RVI"] = cseRelease
        return response

    print(f"POST 請求失敗，狀態碼：{response.status_code}")


if __name__ == '__main__':
    import mylibs.set_OM2M as set_OM2M
    set_OM2M.setUp()
    
    sensor_data_thread = threading.Thread(target=_sendSensorData2AE)
    sensor_data_thread.start()
    api.run(host=mn_IP, port=mn_PORT, debug=True)
    