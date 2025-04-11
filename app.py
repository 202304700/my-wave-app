from flask import Flask, render_template, redirect, url_for
import requests
import json
from datetime import datetime, timedelta

app = Flask(__name__)

# 鎌倉の緯度経度
lat = 35.3193
lon = 139.5503
api_key = "67901aaa-15eb-11f0-803a-0242ac130003-67901b04-15eb-11f0-803a-0242ac130003"  # Stormglass APIキーを入力
url = "https://api.stormglass.io/v2/weather/point"

@app.route('/')
def index():
    # 今日から7日分の日付を生成
    today = datetime.today()
    dates = [today + timedelta(days=i) for i in range(7)]
    # 日付をフォーマットしてリストに保存
    date_strings = [date.strftime('%Y-%m-%d') for date in dates]
    return render_template('index.html', dates=date_strings)

@app.route('/<date>')
def show_wave_info(date):
    # Stormglass APIでデータを取得
    params = {
        "lat": lat,
        "lng": lon,
        "params": "waveHeight,swellHeight,windSpeed",
        "start": f"{date}T00:00:00Z",  # 開始時間を指定（指定された日付の00:00:00）
        "end": f"{date}T23:59:59Z"     # 終了時間を指定（指定された日付の23:59:59）
    }
    
    headers = {
        "Authorization": api_key
    }

    response = requests.get(url, params=params, headers=headers)

    wave_data = []
    time_data = []

    if response.status_code == 200:
        data = response.json()
        
        if "hours" in data:
            for hour_data in data["hours"]:
                wave_data.append(hour_data['waveHeight']['sg'])  # SG（Stormglass）モデルの波の高さ
                time_data.append(hour_data['time'])  # 時刻データ
                
            # タイムスタンプのフォーマット修正
            time_data = [datetime.strptime(hour, "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M") for hour in time_data]

    else:
        print(f"APIリクエスト失敗: {response.status_code}")

    return render_template('wave_info.html', wave_data=wave_data, time_data=time_data, date=date)

if __name__ == '__main__':
    app.run(debug=True)
