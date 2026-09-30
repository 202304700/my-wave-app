import os
import requests
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from dotenv import load_dotenv # dotenvを使って .env ファイルを読み込む
load_dotenv()

# .env ファイルから環境変数を取得（app.pyと同じ方法）
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# 万が一.envが読み込めていない時のエラーチェック
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("エラー: .env ファイルから Supabase の設定が読み込めません。キー名を確認してください。")

def fetch_data():
    endpoint = f"{SUPABASE_URL}/rest/v1/surf_logs"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    # 全データを取得（select=*）
    response = requests.get(f"{endpoint}?select=*", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("データ取得エラー:", response.text)
        return []

def train_and_save_model():
    data = fetch_data()
    if not data:
        print("データがありませんでした。")
        return

    # データをPandas（表計算ツール）に変換
    df = pd.DataFrame(data)

    # 異常値を弾く（スコアが0〜100のものだけを残す。あの884点のデータ等を除外！）
    df = df[(df['user_score'] >= 0) & (df['user_score'] <= 100)]
    
    # AIの学習に使う要素（特徴量）
    features = ['wave_h', 'wind_speed', 'wind_sin', 'wind_cos', 'tide_h']
    
    # 欠損値（空っぽのデータ）がある行はエラーになるので削除
    df = df.dropna(subset=features + ['user_score'])

    # === Beginner用モデルの学習 ===
    df_beginner = df[df['user_name'] == 'Beginner']
    if not df_beginner.empty:
        X_beg = df_beginner[features]
        y_beg = df_beginner['user_score']
        model_beg = RandomForestRegressor(n_estimators=100, random_state=42)
        model_beg.fit(X_beg, y_beg)
        # 学習したものをファイルとして保存
        joblib.dump(model_beg, 'model_beginner.pkl')
        print(f"✅ Beginner用モデルを保存しました（学習データ: {len(df_beginner)}件）")
    else:
        print("Beginnerのデータがありませんでした。")

    # === Pro用モデルの学習 ===
    df_pro = df[df['user_name'] == 'Pro']
    if not df_pro.empty:
        X_pro = df_pro[features]
        y_pro = df_pro['user_score']
        model_pro = RandomForestRegressor(n_estimators=100, random_state=42)
        model_pro.fit(X_pro, y_pro)
        # 学習したAIの脳みそをファイルとして保存
        joblib.dump(model_pro, 'model_pro.pkl')
        print(f"✅ Pro用モデルを保存しました（学習データ: {len(df_pro)}件）")
    else:
        print("Proのデータがありませんでした。")

if __name__ == "__main__":
    train_and_save_model()