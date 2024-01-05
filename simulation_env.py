from flask import Flask, request, jsonify
import time
import random
import threading
import json

app = Flask(__name__)

# ---------------------------------------------------------
with open('config.json', 'r') as f:
    config = json.load(f)

sim_IP = config["sim_env"]["ip"]     # 127.0.0.1
sim_PORT = config["sim_env"]["port"] # 3330
sim_INTERVAL = config["sim_env"]["interval"]
FEED_ROUTE = config["sim_env"]["route"]["FEED"]
STATUS_ROUTE = config["sim_env"]["route"]["STATUS"]
penIds = config["pen_ids"]
# ---------------------------------------------------------
pens = {pen_id: {"water": 100, "food": 100} for pen_id in penIds}
eating_thread = None
# ---------------------------------------------------------

@app.route('/'+FEED_ROUTE, methods=['POST'])
def feed():
    global pens, eating_thread
    data = request.json

    if 'pen_id' in data and data['pen_id'] in pens and 'action' in data:
        pen_id = data['pen_id']
        action = data['action']

        if action == 'add_food':
            pens[pen_id]["food"] = 100
            print(f"農舍 {pen_id} 的食物已加滿")

        if action == 'add_water':
            pens[pen_id]["water"] = 100
            print(f"農舍 {pen_id} 的水已加滿")

        # 若 eating_thread 已經停止，則重新啟動
        if eating_thread is None or not eating_thread.is_alive():
            eating_thread = threading.Thread(target=simulate_eating)
            eating_thread.start()
            
        return jsonify({"message": f"{pen_id} 的食物/水已加滿"})

    return jsonify({"message": "無效指令"})

@app.route('/'+STATUS_ROUTE, methods=['GET'])
def status():
    global pens
    return jsonify(pens)

def simulate_eating():
    global pens
    while any(pen["food"] > 0 or pen["water"] > 0 for pen in pens.values()):
        for pen_id, pen in pens.items():
            decrease_food = random.randint(1, 5)
            decrease_water = random.randint(1, 5)

            pen["food"] -= decrease_food
            pen["water"] -= decrease_water

            if pen["food"] < 0:
                pen["food"] = 0
            if pen["water"] < 0:
                pen["water"] = 0

            print(f"農舍 {pen_id} 食物剩餘量: {pen['food']}, 水剩餘量: {pen['water']}")

        time.sleep(sim_INTERVAL)

if __name__ == '__main__':
    eating_thread = threading.Thread(target=simulate_eating).start()
    app.run(host=sim_IP, port=sim_PORT, debug=True)
