import os
from flask import Flask, render_template
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

app = Flask(__name__)

# 鎌倉の緯度経度
lat = 35.3193
lon = 139.5503

# APIキーを環境変数から取得
api_key = os.environ.get("STORMGLASS_API_KEY")
url = "https://api.stormglass.io/v2/weather/point"

# 風向きの角度からコンディション（オン/オフ）を判定する関数
def get_wind_condition(deg):
    if deg is None:
        return "データなし"
    if 315 <= deg or deg <= 45:
        return "オフショア (良好)"
    elif 135 <= deg <= 225:
        return "オンショア (乱れ)"
    else:
        return "サイドショア"

# 追加：角度(0~360度)を16方位（北、南東など）に変換する関数
def get_cardinal_direction(deg):
    if deg is None:
        return "--"
    dirs = ["北", "北北東", "北東", "東北東", "東", "東南東", "南東", "南南東", 
            "南", "南南西", "南西", "西南西", "西", "西北西", "北西", "北北西"]
    ix = int((deg + 11.25) / 22.5)
    return dirs[ix % 16]

@app.route('/')
def index():
    today = datetime.today()
    dates = [today + timedelta(days=i) for i in range(7)]
    date_strings = [date.strftime('%Y-%m-%d') for date in dates]
    return render_template('index.html', dates=date_strings)

@app.route('/<date>')
def show_wave_info(date):
    # favicon.ico の自動リクエストを無視してエラーを防ぐ
    if date == 'favicon.ico':
        return "", 204

    params = {
        "lat": lat,
        "lng": lon,
        "params": "waveHeight,swellHeight,windSpeed,windDirection", 
        "start": f"{date}T00:00:00Z",
        "end": f"{date}T23:59:59Z"
    }
    
    headers = {
        "Authorization": api_key
    }

    response = requests.get(url, params=params, headers=headers)

    wave_data = []
    time_data = []
    wind_condition_data = []
    wind_speed_data = []
    wind_cardinal_data = [] # 方位データのリストを追加

    if response.status_code == 200:
        data = response.json()
        
        if "hours" in data:
            for hour_data in data["hours"]:
                wave_data.append(hour_data.get('waveHeight', {}).get('sg', 0))
                time_data.append(hour_data['time'])
                
                wind_deg = hour_data.get('windDirection', {}).get('sg')
                wind_speed = hour_data.get('windSpeed', {}).get('sg', 0)
                
                wind_condition_data.append(get_wind_condition(wind_deg))
                wind_speed_data.append(wind_speed)
                wind_cardinal_data.append(get_cardinal_direction(wind_deg)) # 方位を追加
                
            # タイムスタンプのフォーマット修正
            time_data = [datetime.strptime(hour, "%Y-%m-%dT%H:%M:%S%z").strftime("%H:%M") for hour in time_data]

    else:
        print(f"APIリクエスト失敗: {response.status_code}")
        print(response.text)

    return render_template(
        'wave_info.html', 
        wave_data=wave_data, 
        time_data=time_data, 
        wind_condition_data=wind_condition_data,
        wind_speed_data=wind_speed_data,
        wind_cardinal_data=wind_cardinal_data, # HTMLに渡す
        date=date
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)