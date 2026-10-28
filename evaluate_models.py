import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from supabase import create_client, Client
from dotenv import load_dotenv

# 日本語フォントの設定（Meiryo）
plt.rcParams['font.family'] = 'Meiryo'

print("=== Supabase本番データによるレベル別AI予測精度評価 ===\n")

# 1. 環境変数の読み込み & Supabase接続
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ エラー: .env ファイルに SUPABASE_URL または SUPABASE_KEY が設定されていません。")
    exit()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. Supabaseから全ログデータを取得
try:
    response = supabase.table("surf_logs").select("*").execute()
    data = response.data
    if not data:
        print("⚠️ ログデータがまだ登録されていません。")
        exit()
    df = pd.DataFrame(data)
    print(f"✅ Supabaseから {len(df)} 件のログデータを取得しました。")
except Exception as e:
    print(f"❌ データ取得失敗: {e}")
    exit()

# データ型の変換（数値化）
df['user_score'] = pd.to_numeric(df['user_score'], errors='coerce')
df['ai_score'] = pd.to_numeric(df['ai_score'], errors='coerce')

# 欠損値の除去
df = df.dropna(subset=['user_score', 'ai_score'])

if len(df) == 0:
    print("⚠️ 評価可能な有効データがありませんでした。")
    exit()

# レベル判定用のカラムを探す（level または user_level など）
level_col = 'user_name'

# --------------------------------------------------
# 3. グラフ描画の設定
# --------------------------------------------------
plt.figure(figsize=(8, 8))

# 理想線 (y = x)
plt.plot([0, 100], [0, 100], '--', color='red', linewidth=2, label='完全一致 (理想)')

if level_col:
    # 「ビギナー」と「プロ・経験者」のデータを振り分け
    is_beginner = df[level_col].astype(str).str.lower().isin(['beginner', 'ビギナー', 'ビギナー（初心者）'])
    
    df_beg = df[is_beginner]
    df_pro = df[~is_beginner]
    
    # それぞれのMAEを計算
    mae_beg = mean_absolute_error(df_beg['user_score'], df_beg['ai_score']) if len(df_beg) > 0 else None
    mae_pro = mean_absolute_error(df_pro['user_score'], df_pro['ai_score']) if len(df_pro) > 0 else None
    
    print("-" * 50)
    if mae_beg is not None:
        print(f"🏄 ビギナーモデル MAE: 約 {mae_beg:.2f} 点 (データ数: {len(df_beg)}件)")
    if mae_pro is not None:
        print(f"🏄‍♂️ プロ・経験者モデル MAE: 約 {mae_pro:.2f} 点 (データ数: {len(df_pro)}件)")
    print("-" * 50)

    # ビギナーのプロット（青色の丸）
    if len(df_beg) > 0:
        plt.scatter(
            df_beg['user_score'], df_beg['ai_score'], 
            alpha=0.7, color='#1f77b4', edgecolors='k', s=80, marker='o',
            label=f'ビギナー (MAE: {mae_beg:.1f}点)'
        )
        
    # プロ・経験者のプロット（緑色の四角）
    if len(df_pro) > 0:
        plt.scatter(
            df_pro['user_score'], df_pro['ai_score'], 
            alpha=0.7, color='#2ca02c', edgecolors='k', s=80, marker='s',
            label=f'プロ・経験者 (MAE: {mae_pro:.1f}点)'
        )
else:
    # カラムが見つからない場合のフォールバック
    mae_all = mean_absolute_error(df['user_score'], df['ai_score'])
    plt.scatter(
        df['user_score'], df['ai_score'], 
        alpha=0.7, color='#1f77b4', edgecolors='k', s=70, 
        label=f'全体 (MAE: {mae_all:.1f}点)'
    )

plt.xlim(0, 100)
plt.ylim(0, 100)
plt.xlabel('ユーザーが入力した体感スコア (正解)', fontsize=12)
plt.ylabel('AIの予測スコア', fontsize=12)
plt.title('【レベル別】AI波予測スコアの精度評価', fontsize=14, fontweight='bold')
plt.legend(fontsize=11, loc='upper left')
plt.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()
filename = 'ai_vs_user_by_level.png'
plt.savefig(filename, dpi=300)
print(f"✅ レベル別散布図を '{filename}' として保存しました！")