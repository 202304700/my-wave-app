/**
 * 波の高さグラフを描画する関数
 * @param {Array} timeData - 時刻の配列
 * @param {Array} waveData - 波の高さの配列
 */
function renderWaveChart(timeData, waveData) {
    const ctx = document.getElementById('waveChart').getContext('2d');

    // グラフにグラデーションをかける（上から下へ）
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(54, 162, 235, 0.8)');
    gradient.addColorStop(1, 'rgba(54, 162, 235, 0.1)');

    new Chart(ctx, {
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
            maintainAspectRatio: false, // スマホで見やすくするために重要
            plugins: {
                legend: { display: false }
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