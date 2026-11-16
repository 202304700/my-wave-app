import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, r2_score
from supabase import create_client, Client
from dotenv import load_dotenv

# 日本語フォントの設定（Meiryo）
plt.rcParams['font.family'] = 'Meiryo'

print("=== Supabase本番データによるレベル別AI予測精度・特徴量評価 ===\n")

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

# データ型の変換と欠損値除去
df['user_score'] = pd.to_numeric(df['user_score'], errors='coerce')
df['ai_score'] = pd.to_numeric(df['ai_score'], errors='coerce')
df = df.dropna(subset=['user_score', 'ai_score'])

if len(df) == 0:
    print("⚠️ 評価可能な有効データがありませんでした。")
    exit()

# 「ビギナー」と「プロ」のデータ振り分け
is_beginner = df['user_name'].astype(str).str.lower().isin(['beginner', 'ビギナー'])
df_beg = df[is_beginner]
df_pro = df[~is_beginner]

# --------------------------------------------------
# 3. 評価指標（MAE と R^2）の算出
# --------------------------------------------------
print("-" * 55)
if len(df_beg) >= 2:
    mae_beg = mean_absolute_error(df_beg['user_score'], df_beg['ai_score'])
    r2_beg = r2_score(df_beg['user_score'], df_beg['ai_score'])
    print(f"🏄 【ビギナー】 データ数: {len(df_beg)}件 | MAE: {mae_beg:.2f} 点 | R^2: {r2_beg:.3f}")
elif len(df_beg) == 1:
    mae_beg = mean_absolute_error(df_beg['user_score'], df_beg['ai_score'])
    r2_beg = None
    print(f"🏄 【ビギナー】 データ数: 1件 | MAE: {mae_beg:.2f} 点 (R^2は2件以上で算出)")
else:
    mae_beg, r2_beg = None, None

if len(df_pro) >= 2:
    mae_pro = mean_absolute_error(df_pro['user_score'], df_pro['ai_score'])
    r2_pro = r2_score(df_pro['user_score'], df_pro['ai_score'])
    print(f"🏄‍♂️ 【プロ】     データ数: {len(df_pro)}件 | MAE: {mae_pro:.2f} 点 | R^2: {r2_pro:.3f}")
elif len(df_pro) == 1:
    mae_pro = mean_absolute_error(df_pro['user_score'], df_pro['ai_score'])
    r2_pro = None
    print(f"🏄‍♂️ 【プロ】     データ数: 1件 | MAE: {mae_pro:.2f} 点 (R^2は2件以上で算出)")
else:
    mae_pro, r2_pro = None, None
print("-" * 55)

# --------------------------------------------------
# 4. グラフ①：レベル別 予測精度散布図（MAE & R^2表記）
# --------------------------------------------------
plt.figure(figsize=(8, 8))
plt.plot([0, 100], [0, 100], '--', color='red', linewidth=2, label='完全一致 (理想)')

if len(df_beg) > 0:
    r2_text_beg = f", R²: {r2_beg:.2f}" if r2_beg is not None else ""
    plt.scatter(
        df_beg['user_score'], df_beg['ai_score'],
        alpha=0.75, color='#1f77b4', edgecolors='k', s=85, marker='o',
        label=f'ビギナー (MAE: {mae_beg:.1f}点{r2_text_beg})'
    )

if len(df_pro) > 0:
    r2_text_pro = f", R²: {r2_pro:.2f}" if r2_pro is not None else ""
    plt.scatter(
        df_pro['user_score'], df_pro['ai_score'],
        alpha=0.75, color='#2ca02c', edgecolors='k', s=85, marker='s',
        label=f'プロ・経験者 (MAE: {mae_pro:.1f}点{r2_text_pro})'
    )

plt.xlim(0, 100)
plt.ylim(0, 100)
plt.xlabel('ユーザーが入力した体感スコア (正解)', fontsize=12)
plt.ylabel('AIの予測スコア', fontsize=12)
plt.title('【レベル別】AI波予測スコアの精度評価', fontsize=14, fontweight='bold')
plt.legend(fontsize=11, loc='upper left')
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()
plt.savefig('ai_vs_user_by_level.png', dpi=300)
print("✅ 散布図を 'ai_vs_user_by_level.png' として保存しました。")

# --------------------------------------------------
# 5. グラフ②：学習済みモデル（.pkl）の特徴量重要度比較（4項目統合・正規化版）
# --------------------------------------------------
try:
    model_beg = joblib.load('model_beginner.pkl')
    model_pro = joblib.load('model_pro.pkl')

    imp_beg = model_beg.feature_importances_
    imp_pro = model_pro.feature_importances_

    grouped_labels = ['波高 (wave_h)', '風速 (wind_speed)', '風向き (wind_dir)', '潮位 (tide_h)']

    # モデルにカラム名が保存されている場合
    if hasattr(model_beg, 'feature_names_in_'):
        names = list(model_beg.feature_names_in_)
        beg_dict = dict(zip(names, imp_beg))
        pro_dict = dict(zip(names, imp_pro))

        # sin と cos の平均（÷2）をとって「1変数あたりの重要度」にする
        raw_beg = [
            beg_dict.get('wave_h', 0),
            beg_dict.get('wind_speed', 0),
            (beg_dict.get('wind_sin', 0) + beg_dict.get('wind_cos', 0)) / 2,
            beg_dict.get('tide_h', 0)
        ]
        raw_pro = [
            pro_dict.get('wave_h', 0),
            pro_dict.get('wind_speed', 0),
            (pro_dict.get('wind_sin', 0) + pro_dict.get('wind_cos', 0)) / 2,
            pro_dict.get('tide_h', 0)
        ]
    else:
        # カラム名が保存されていない場合のフォールバック（train_models.pyの並び順に合わせる）
        print("⚠️ モデルにカラム名がないため、インデックス順で統合します。")
        raw_beg = [imp_beg[0], imp_beg[1], (imp_beg[2] + imp_beg[3]) / 2, imp_beg[4]]
        raw_pro = [imp_pro[0], imp_pro[1], (imp_pro[2] + imp_pro[3]) / 2, imp_pro[4]]

    # 4項目の合計がちょうど 1.0 (100%) になるように比率を再計算（正規化）
    grouped_beg = [v / sum(raw_beg) for v in raw_beg]
    grouped_pro = [v / sum(raw_pro) for v in raw_pro]

    y_pos = np.arange(len(grouped_labels))
    bar_height = 0.35

    plt.figure(figsize=(9, 5))
    plt.barh(y_pos - bar_height/2, grouped_beg, height=bar_height, color='#1f77b4', edgecolor='k', label='ビギナーモデル')
    plt.barh(y_pos + bar_height/2, grouped_pro, height=bar_height, color='#2ca02c', edgecolor='k', label='プロモデル')

    plt.yticks(y_pos, grouped_labels, fontsize=11)
    plt.xlabel('正規化重要度（AIがスコア判定時に重視した割合）', fontsize=12)
    plt.title('【レベル別】気象条件の特徴量重要度比較', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.legend(fontsize=11, loc='lower right')
    plt.grid(axis='x', linestyle=':', alpha=0.6)
    plt.tight_layout()
    plt.savefig('feature_importance_by_level.png', dpi=300)
    print("✅ 正規化した特徴量重要度グラフを 'feature_importance_by_level.png' として保存しました。")

except FileNotFoundError:
    print("⚠️ 'model_beginner.pkl' または 'model_pro.pkl' が見つからないためスキップしました。")
except Exception as e:
    print(f"⚠️ 特徴量重要度の出力中にエラーが発生しました: {e}")