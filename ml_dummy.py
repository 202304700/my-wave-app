import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Meiryo'
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

print("=== 機械学習（現実のDB同期版）テスト開始 ===\n")
# ==================================================
# 準備：app.pyのスコア計算関数をそのまま定義
# ==================================================
def calculate_surf_score(wave_h, wind_cond, wind_speed, tide_phase, level):
    if wind_speed > 12.0 or (level == "beginner" and wave_h > 1.6): return 0

    base_score = 0
    if level == "beginner":
        if 0.4 <= wave_h < 0.8: base_score = 60
        elif 0.2 <= wave_h < 0.4: base_score = 30
        else: base_score = 15
    else: 
        if 0.8 <= wave_h < 1.6: base_score = 60
        else: base_score = 30

    multiplier = 1.0
    if "オフショア" in wind_cond:
        if wind_speed <= 3.0: multiplier = 1.5
        elif wind_speed <= 5.0: multiplier = 1.3
        elif wind_speed <= 7.0: multiplier = 1.0
        else: multiplier = 0.6
    elif "サイドショア" in wind_cond:
        if wind_speed <= 2.0: multiplier = 0.8
        elif wind_speed <= 4.0: multiplier = 0.6
        elif wind_speed <= 6.0: multiplier = 0.3
        else: multiplier = 0.1
    else: 
        if wind_speed <= 2.0: multiplier = 0.7
        elif wind_speed <= 4.0: multiplier = 0.4
        elif wind_speed <= 6.0: multiplier = 0.2
        else: multiplier = 0.1

    tide_bonus = 10 if tide_phase in ["大潮", "中潮"] else 5
    final_score = (base_score * multiplier) + tide_bonus

    rounded_score = round(final_score / 5.0) * 5
    return min(100, int(rounded_score))

# ==================================================
# 1. 現実のDBに合わせたダミーデータの作成
# ==================================================
n_samples = 100

wave_h = np.random.uniform(0.2, 1.8, n_samples)      # 波高 (m)
wind_speed = np.random.uniform(0.0, 12.0, n_samples) # 風速 (m/s) 爆風も少し混ぜる
wind_cos = np.random.uniform(-1, 1, n_samples)       # 風向き (1に近いほどオフショア)
tide_h = np.random.uniform(-50, 150, n_samples)      # 潮位 (cm)

# スコア計算用の一時データ（AIには入れない）
tide_phases = np.random.choice(["大潮", "中潮", "小潮", "長潮", "若潮"], n_samples)

scores = []
for i in range(n_samples):
    # AI用の数値(wind_cos)を、計算用の文字(wind_cond)に変換
    if wind_cos[i] >= 0.5:
        wind_cond = "オフショア"
    elif wind_cos[i] <= -0.5:
        wind_cond = "オンショア"
    else:
        wind_cond = "サイドショア"

    # app.pyのロジックで点数化（レベルは「ビギナー」で固定）
    base_s = calculate_surf_score(
        wave_h[i], wind_cond, wind_speed[i], tide_phases[i], "beginner"
    )

    # 完全に計算式通りだとAIが100%暗記してしまうため、人間の感覚のブレ（ノイズ）を少し足す
    noise = np.random.normal(0, 5) 
    final_s = np.clip(base_s + noise, 0, 100)
    scores.append(final_s)

# データフレーム作成
df = pd.DataFrame({
    'wave_h': wave_h,
    'wind_speed': wind_speed,
    'wind_cos': wind_cos,
    'tide_h': tide_h,
    'user_score': scores
})

print(f"✅ 1. app.pyのルールベースでダミーデータを{n_samples}件作成しました")
print(df.head(), "\n")

# --------------------------------------------------
# 2. データの切り分け（学習用とテスト用に分割）
# --------------------------------------------------
# AIに与えるヒント（特徴量）を現在のアプリの実装に合わせる
features = ['wave_h', 'wind_speed', 'wind_cos', 'tide_h']
X = df[features]
y = df['user_score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --------------------------------------------------
# 3. AIモデルの学習（トレーニング）
# --------------------------------------------------
model = RandomForestRegressor(n_estimators=100)
model.fit(X_train, y_train)

print("✅ 3. AIが波の条件を学習しました！\n")

# --------------------------------------------------
# 4. テストデータで予測 ＆ 答え合わせ
# --------------------------------------------------
print("=== 🎯 AIの予測結果（テスト用20%の答え合わせ） ===")
predictions = model.predict(X_test)

for i in range(len(predictions)):
    actual = y_test.iloc[i]
    predicted = predictions[i]
    diff = abs(actual - predicted)
    print(f"実際の点数: {actual:4.1f}点 | AIの予測: {predicted:4.1f}点 (誤差: {diff:4.1f}点)")

mae = mean_absolute_error(y_test, predictions)
print("-" * 50)
print(f"★ 今回のAIの平均誤差: 約 {mae:.1f} 点")
print("-" * 50)


# ==================================================
# 5. 【追加】論文用のグラフ画像を生成・保存
# ==================================================

# ① 散布図の作成
plt.figure(figsize=(6, 6))
plt.scatter(y_test, predictions, alpha=0.7, color='blue')
plt.plot([0, 100], [0, 100], '--', color='red', label='完璧な予測') # 斜めの線
plt.xlabel('疑似的な主観的スコア')
plt.ylabel('AIの予測スコア')
plt.title(f'モデルの予測精度 (MAE: {mae:.1f})')
plt.legend()
plt.grid(True)
plt.savefig('scatter_plot.png')
print("✅ 散布図を 'scatter_plot.png' として保存しました。")

# ② 特徴量重要度のグラフ作成
importances = model.feature_importances_
feature_names = ['波高(wave_h)', '風速(wind_speed)', '風向き(wind_cos)', '潮位(tide_h)']

plt.figure(figsize=(8, 5))
plt.barh(feature_names, importances, color='green')
plt.xlabel('重要度（AIがどれくらい重視したか）')
plt.title('気象データの特徴量重要度')
plt.gca().invert_yaxis() # 上から重要順にするため反転
plt.tight_layout() # レイアウトを自動調整
plt.savefig('feature_importance.png')
print("✅ 特徴量重要度グラフを 'feature_importance.png' として保存しました。")