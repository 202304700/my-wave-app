// グラフの本体を保存する変数（再描画する時に古いものを消すため）
let myWaveChart = null;

// 【追加】現在の選択レベルと、現在ホバーしている時間のインデックスを保存する変数
let currentLevel = 'beginner'; // デフォルトは初心者
let currentIndex = 0; // 初期値は0（0時）

// 【追加】データをグローバルに保持しておくための変数（レベル切り替え時に再利用するため）
let globalData = {};

// 【追加】レベル切り替えボタンが押された時の処理
function changeLevel(level) {
    currentLevel = level;

    // ボタンの見た目（Tailwindのクラス）を切り替える
    const btnBeginner = document.getElementById('btn-beginner');
    const btnExperienced = document.getElementById('btn-experienced');

    if (level === 'beginner') {
        btnBeginner.className = "px-4 py-1 rounded-md text-xs font-bold transition-all bg-blue-600 text-white";
        btnExperienced.className = "px-4 py-1 rounded-md text-xs font-bold transition-all text-slate-400 hover:bg-slate-50";
    } else {
        btnExperienced.className = "px-4 py-1 rounded-md text-xs font-bold transition-all bg-blue-600 text-white";
        btnBeginner.className = "px-4 py-1 rounded-md text-xs font-bold transition-all text-slate-400 hover:bg-slate-50";
    }

    // 現在表示している時間のまま、スコアだけを再計算してダッシュボードを更新
    // 【修正】引数に globalData.waveSizeData を追加
    updateDashboard(currentIndex, globalData.timeData, globalData.waveData, globalData.windSpeedData, globalData.windConditionData, globalData.windCardinalData, globalData.tideData, globalData.beginnerScores, globalData.experiencedScores, globalData.waveSizeData);
}

// 【重要関数1】ダッシュボードの数字や色を更新する関数
// グラフ上でホバーした「時間（index番号）」を受け取り、該当するデータをHTMLに挿入する
// 【修正】引数に beginnerScores, experiencedScores, waveSizeData を追加
function updateDashboard(index, timeData, waveData, windSpeedData, windConditionData, windCardinalData, tideData, beginnerScores, experiencedScores, waveSizeData) {
    currentIndex = index; // 【追加】現在のインデックスを更新（レベル切り替え用）

    // HTML内の id="..." の要素を探し、中身のテキスト（innerText）を書き換える
    document.getElementById('display-time').innerText = timeData[index];
    document.getElementById('display-wave-height').innerText = waveData[index].toFixed(2); // 小数点2桁に揃える
    document.getElementById('display-tide').innerText = Math.round(tideData[index]);       // 四捨五入して整数に
    document.getElementById('display-wind-speed').innerText = windSpeedData[index].toFixed(1);
    document.getElementById('display-wind-cardinal').innerText = windCardinalData[index];

    // 【追加】サーフィン用語のサイズ名を挿入
    document.getElementById('display-wave-size').innerText = waveSizeData[index];

    const conditionEl = document.getElementById('display-wind-condition');
    const condition = windConditionData[index];
    conditionEl.innerText = condition;

    // コンディションの文字列（オフショア等）に合わせて、背景色（Tailwindのクラス）を動的に変更する
    if (condition.includes('オフショア')) {
        conditionEl.className = "inline-block text-xs font-bold px-3 py-1 rounded bg-blue-600 text-white tracking-wider";
    } else if (condition.includes('オンショア')) {
        conditionEl.className = "inline-block text-xs font-bold px-3 py-1 rounded bg-red-600 text-white tracking-wider";
    } else {
        conditionEl.className = "inline-block text-xs font-bold px-3 py-1 rounded bg-slate-600 text-slate-200 tracking-wider";
    }

    // --- 【追加・修正】ここから下を追加：スコアとアドバイスの更新処理 ---
    const score = (currentLevel === 'beginner') ? beginnerScores[index] : experiencedScores[index];
    const scoreEl = document.getElementById('display-score');
    const adviceEl = document.getElementById('display-advice');

    scoreEl.innerText = score;

    // 点数に応じて色とアドバイスのテキストを変更する
    if (score === 0) {
        // 0点（足切り）の時の危険警告：シンプルな赤色に変更
        scoreEl.className = "text-5xl md:text-6xl font-black text-red-500 tracking-tighter";
        adviceEl.innerText = "危険！行くのはやめましょう。";
        adviceEl.className = "mt-2 text-[10px] md:text-xs font-bold text-red-500";
    } else if (score >= 80) {
        scoreEl.className = "text-5xl md:text-6xl font-black text-green-400 tracking-tighter";
        adviceEl.innerText = "最高！迷わず海へ行くべきコンディションです。";
        adviceEl.className = "mt-2 text-[10px] md:text-xs font-bold text-slate-300";
    } else if (score >= 50) {
        scoreEl.className = "text-5xl md:text-6xl font-black text-yellow-400 tracking-tighter";
        adviceEl.innerText = (currentLevel === 'beginner') ? "練習に最適です。パドルアウトも楽でしょう。" : "まずまずです。潮の動きに注目しましょう。";
        adviceEl.className = "mt-2 text-[10px] md:text-xs font-bold text-slate-300";
    } else if (score >= 30) {
        scoreEl.className = "text-5xl md:text-6xl font-black text-orange-400 tracking-tighter";
        adviceEl.innerText = "少し微妙。無理のない範囲で楽しみましょう。";
        adviceEl.className = "mt-2 text-[10px] md:text-xs font-bold text-slate-300";
    } else {
        // 1〜29点の時
        scoreEl.className = "text-5xl md:text-6xl font-black text-rose-500 tracking-tighter";
        adviceEl.innerText = "厳しいかも。お家でゆっくりしましょう。";
        adviceEl.className = "mt-2 text-[10px] md:text-xs font-bold text-slate-300";
    }
}

// 【重要関数2】Chart.jsを使ってグラフを描画する関数
// 【修正】引数に beginnerScores, experiencedScores, waveSizeData を追加
function renderWaveChart(timeData, waveData, windSpeedData, windConditionData, windCardinalData, tideData, beginnerScores, experiencedScores, waveSizeData) {

    // 【追加】データをグローバル変数に保存（ボタンでレベルを切り替えた時に再利用するため）
    globalData = { timeData, waveData, windSpeedData, windConditionData, windCardinalData, tideData, beginnerScores, experiencedScores, waveSizeData };

    const ctx = document.getElementById('waveChart').getContext('2d');

    // 既にグラフが存在する場合は、一度破壊（リセット）する
    if (myWaveChart) myWaveChart.destroy();

    // 初期表示として、最初の時間（index = 0）のデータをダッシュボードに表示しておく
    // 【修正】スコアの配列とサイズ名の配列も渡す
    updateDashboard(0, timeData, waveData, windSpeedData, windConditionData, windCardinalData, tideData, beginnerScores, experiencedScores, waveSizeData);

    // Chart.js の設定本体
    myWaveChart = new Chart(ctx, {
        data: {
            labels: timeData, // X軸（横軸）のラベルは「時間」
            datasets: [
                // 1つ目のグラフ：波高（棒グラフ）
                {
                    type: 'bar', label: '波高 (m)', data: waveData,
                    backgroundColor: 'rgba(34, 211, 238, 0.6)',
                    borderColor: 'rgba(34, 211, 238, 1)',
                    borderWidth: 1,
                    yAxisID: 'y', // 左側のY軸を使用
                    order: 2      // 描画順序（数字が大きいほど奥に描かれる）
                },
                // 2つ目のグラフ：潮位（折れ線グラフ）
                {
                    type: 'line', label: '潮位 (cm)', data: tideData,
                    borderColor: 'rgba(251, 146, 60, 1)',
                    backgroundColor: 'rgba(251, 146, 60, 0.1)',
                    fill: true,   // 線の内側を塗りつぶす
                    borderWidth: 4, tension: 0.4, // tensionで線を滑らかなカーブにする
                    pointRadius: 0,
                    yAxisID: 'y1', // 右側のY軸を使用
                    order: 1       // 波の棒グラフより手前に描画する
                }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },

            // 【重要】グラフにマウスが乗った（ホバーした）時の処理
            onHover: (event, activeElements) => {
                if (activeElements.length > 0) {
                    // カーソルが合っている棒グラフのインデックス番号（0〜23）を取得し、ダッシュボードを更新
                    // 【修正】スコアの配列とサイズ名の配列も渡す
                    updateDashboard(activeElements[0].index, timeData, waveData, windSpeedData, windConditionData, windCardinalData, tideData, beginnerScores, experiencedScores, waveSizeData);
                }
            },
            scales: {
                // 左のY軸（波高用）の設定
                y: { type: 'linear', position: 'left', beginAtZero: true, title: { display: true, text: '波高(m)' } },
                // 右のY軸（潮位用）の設定
                y1: { type: 'linear', position: 'right', beginAtZero: false, title: { display: true, text: '潮位(cm)' }, grid: { drawOnChartArea: false } }
            },
            plugins: {
                legend: { display: true, position: 'bottom' }
            }
        }
    });
}