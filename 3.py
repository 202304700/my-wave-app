import requests
import json
import matplotlib.pyplot as plt

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
    print("レスポンスデータ (整形):")
    print(json.dumps(data, indent=2))  # 返ってきたデータを整形して表示
    
    # 波に関連するフィールドを調べて表示する
    print("\nデータ全体:")
    for key, value in data.items():
        print(f"{key}: {value}")
    
    # 波情報を取り出して、波の高さに関連するデータを抽出
    if "data" in data:
        wave_data = []
        for entry in data["data"]:
            if "waves" in entry:
                wave_data.append(entry['waves'])  # 波の高さデータをリストに追加

        # グラフの作成
        if wave_data:
            time_stamps = list(range(1, len(wave_data) + 1))  # 例: 時間のインデックス（1, 2, 3,...）
            
            plt.plot(time_stamps, wave_data, marker='o', linestyle='-', color='b')
            plt.title('鎌倉の波の高さ')
            plt.xlabel('時間')
            plt.ylabel('波の高さ (m)')
            plt.grid(True)
            
            # グラフを表示
            plt.show()
        else:
            print("波のデータがありません。")
else:
    print("Error:", response.status_code)
    print(response.text)  # エラー内容を表示
