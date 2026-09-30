import pandas as pd
import requests
import os
from dotenv import load_dotenv

# これが .env ファイルを読み込む魔法の呪文！
load_dotenv()

# .env からURLとキーを取得
SUPABASE_URL = os.environ.get("SUPABASE_URL") 
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}"
}

print("データを取得しています...")

# Supabaseからデータを取得
response = requests.get(f"{SUPABASE_URL}/rest/v1/surf_logs?select=*", headers=headers)

# JSONデータをPandasの「表」に変換
df = pd.DataFrame(response.json())

print("取得成功！最初の5件を表示します：\n")
print(df.head())