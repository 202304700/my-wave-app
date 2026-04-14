let myWaveChart = null;

/**
 * 波の高さグラフを描画する関数
 * @param {Array} timeData - 時刻の配列
 * @param {Array} waveData - 波の高さの配列
 * @param {Array} windSpeedData - 風速の配列 (今回追加)
 * @param {Array} windConditionData - 風の状態の配列 (今回追加)
 */
function updateDashboard(index, timeData, windSpeedData, windConditionData, windCardinalData) {
    document.getElementById('display-time').innerText = timeData[index];
    document.getElementById('display-wind-speed').innerText = windSpeedData[index];
    document.getElementById('display-wind-cardinal').innerText = windCardinalData[index];

    const conditionEl = document.getElementById('display-wind-condition');
    const condition = windConditionData[index];
    conditionEl.innerText = condition;

    // コンディションによって文字色と背景色を変える
    if (condition.includes('オフショア')) {
        conditionEl.className = "inline-block text-sm font-bold px-3 py-1 rounded bg-blue-900 text-blue-300";
    } else if (condition.includes('オンショア')) {
        conditionEl.className = "inline-block text-sm font-bold px-3 py-1 rounded bg-red-900 text-red-300";
    } else {
        conditionEl.className = "inline-block text-sm font-bold px-3 py-1 rounded bg-gray-700 text-gray-300";
    }
}

/**
 * 波の高さグラフを描画する関数
 */
function renderWaveChart(timeData, waveData, windSpeedData, windConditionData, windCardinalData) {
    const ctx = document.getElementById('waveChart').getContext('2d');

    // 再描画時のバグ防止
    if (myWaveChart) {
        myWaveChart.destroy();
    }

    // 画面を開いた時、最初のデータ(朝0時のデータなど)をパネルに表示しておく
    if (timeData.length > 0) {
        updateDashboard(0, timeData, windSpeedData, windConditionData, windCardinalData);
    }

    // グラデーション設定（元のデザインを維持）
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(54, 162, 235, 0.8)');
    gradient.addColorStop(1, 'rgba(54, 162, 235, 0.1)');

    myWaveChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: timeData,
            datasets: [{
                label: '波の高さ (m)',
                data: waveData,
                backgroundColor: gradient,
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                borderRadius: 5,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            // グラフをなぞった時の処理（パネルを更新）
            onHover: (event, activeElements) => {
                if (activeElements.length > 0) {
                    const index = activeElements[0].index;
                    updateDashboard(index, timeData, windSpeedData, windConditionData, windCardinalData);
                }
            },
            plugins: {
                legend: { display: false },
                // 吹き出し（ツールチップ）は非表示にする
                tooltip: { enabled: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: '波高 (m)' }
                },
                x: {
                    title: { display: true, text: '時刻' }
                }
            }
        }
    });
}