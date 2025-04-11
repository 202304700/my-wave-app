import requests
import json

# 新しく取得したAPIキーを設定
api_key = "MCQvNOUV3fOKqextUsXCm20VqraSDOkW"  # 新しいAPIキー

# Windy APIのエンドポイントURL
url = "https://api.windy.com/api/point-forecast/v2"

# ヘッダーにAPIキーを指定
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# パラメータ設定 (例: 鎌倉の波情報を取得)
payload = {
    "key": api_key,  # ここでAPIキーを"key"パラメータとして送信
    "lat": 35.3193,  # 鎌倉の緯度
    "lon": 139.5503,  # 鎌倉の経度
    "model": "gfsWave",  # 使用する波モデル
    "parameters": ["waves", "windWaves", "swell1", "swell2"],  # 取得したい波パラメータ
    "levels": ["surface"]  # 解析レベル
}

# APIにPOSTリクエストを送信
response = requests.post(url, headers=headers, json=payload)

# レスポンスが正常ならデータを表示
if response.status_code == 200:
    data = response.json()
    print(json.dumps(data, indent=2))  # 返ってきたデータを整形して表示
else:
    print("Error:", response.status_code)
    print(response.text)  # エラー内容を表示
