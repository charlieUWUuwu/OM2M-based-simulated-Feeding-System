# OM2M-based-simulated-Feeding-System

- 物聯網核心網路技術課程專題
- 參考論文[Design and Implementation of Intelligent Feeding System Based-on the oneM2M](https://ieeexplore.ieee.org/abstract/document/9389827)，製作基於 OM2M 架構的餵食系統

## DEMO
[![期末專題](http://img.youtube.com/vi/TLV7WGfjJN4/0.jpg)](https://www.youtube.com/watch?v=TLV7WGfjJN4 "物聯網期末專題 demo")

## 系統功能
- 資料蒐集
  - 剩餘食物量
  - 剩餘水量
- 狀態顯示
  - 網頁顯示當前剩餘食物及水量
- 邏輯控制
  - 剩餘食物、水量低於閾值，網頁顯示文字提醒
  - 低於閾值，自動加水或食物
  - 網頁含餵食按鈕，可手動添加食物、水


## 執行
0. 安裝依賴項
    ```
    pip install -r requirements.txt
    ```
1. 啟動 in-cse/mn-cse (運行 docker-compose.yml)
    ```
    docker-compose up
    ```
2. 啟動模擬環境
    ```
    python simulation_env.py
    ```
3. 啟動 in_app.py
    ```
    python in_app.py
    ```
4. 啟動 mn_app.py
    ```
    python mn_app.py
    ```
5. 開啟前端畫面 : http://localhost:3000/home

## 文件說明
- `./mylibs/in_API.py` : 對 in-cse 發送 request 的相關操作
- `./mylibs/mn_API.py` : 對 mn-cse 發送 request 的相關操作
- `./mylibs/set_OM2M.py` : 建置所需之 AE、Container、Subscription 等資源在 OM2M Resource tree 的流程
- `in_app.py` : 處理前端按鈕事件、水/食物值的範圍檢查、獲取最新的資訊給前端
- `mn_app.py` : 從模擬環境獲得資訊、接收餵食指令
- `simulation_env.py` : 模擬農舍牲畜進食，水/食物自動減少的情況

## 系統架構
![image](https://github.com/charlieUWUuwu/OM2M-based-simulated-Feeding-System/assets/111500816/c8dfccdd-e95e-400d-bc4e-a68a1853780a)
![image](https://github.com/charlieUWUuwu/OM2M-based-simulated-Feeding-System/assets/111500816/917c61b0-fd95-437a-8c33-e82ba5240200)
![image](https://github.com/charlieUWUuwu/OM2M-based-simulated-Feeding-System/assets/111500816/6d4ef3af-d2e2-4ca9-a60f-2677c1ffd257)


