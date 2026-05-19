// Configuration des graphiques
let cpuChart, memoryChart, networkChart, cpuDoughnutChart;
let cpuHistory = [];
let memoryHistory = [];
let networkSentHistory = [];
let networkRecvHistory = [];
const maxDataPoints = 30; // 30 secondes d'historique

// Couleurs du thème
const colors = {
    primary: 'rgba(74, 144, 226, 1)',
    primaryLight: 'rgba(74, 144, 226, 0.2)',
    success: 'rgba(40, 167, 69, 1)',
    successLight: 'rgba(40, 167, 69, 0.2)',
    danger: 'rgba(220, 53, 69, 1)',
    dangerLight: 'rgba(220, 53, 69, 0.2)',
    warning: 'rgba(255, 193, 7, 1)',
    warningLight: 'rgba(255, 193, 7, 0.2)',
    info: 'rgba(23, 162, 184, 1)',
    infoLight: 'rgba(23, 162, 184, 0.2)'
};

// Initialisation des graphiques
function initCharts() {
    // Graphique CPU ligne
    const cpuCtx = document.getElementById('cpuChart');
    if (cpuCtx) {
        cpuChart = new Chart(cpuCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Utilisation CPU (%)',
                    data: [],
                    borderColor: colors.primary,
                    backgroundColor: colors.primaryLight,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Graphique CPU Doughnut
    const cpuDoughnutCtx = document.getElementById('cpuDoughnutChart');
    if (cpuDoughnutCtx) {
        cpuDoughnutChart = new Chart(cpuDoughnutCtx, {
            type: 'doughnut',
            data: {
                labels: ['Utilisé', 'Libre'],
                datasets: [{
                    data: [0, 100],
                    backgroundColor: [colors.primary, colors.primaryLight],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Graphique Mémoire
    const memoryCtx = document.getElementById('memoryChart');
    if (memoryCtx) {
        memoryChart = new Chart(memoryCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Utilisation Mémoire (%)',
                    data: [],
                    borderColor: colors.success,
                    backgroundColor: colors.successLight,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }

    // Graphique Réseau
    const networkCtx = document.getElementById('networkChart');
    if (networkCtx) {
        networkChart = new Chart(networkCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Envoyé (MB)',
                    data: [],
                    borderColor: colors.success,
                    backgroundColor: colors.successLight,
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Reçu (MB)',
                    data: [],
                    borderColor: colors.info,
                    backgroundColor: colors.infoLight,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + ' MB';
                            }
                        }
                    }
                }
            }
        });
    }
}

// Mise à jour des graphiques
function updateCharts(timestamp) {
    const timeLabel = new Date().toLocaleTimeString('fr-FR');
    
    // Limiter le nombre de points de données
    if (cpuHistory.length > maxDataPoints) {
        cpuHistory.shift();
        memoryHistory.shift();
        networkSentHistory.shift();
        networkRecvHistory.shift();
    }
}

// Mise à jour des métriques depuis l'API
async function updateMetrics() {
    try {
        const response = await fetch('/api/metrics/');
        const data = await response.json();
        
        // Mise à jour du timestamp
        document.getElementById('last-update').textContent = data.timestamp;
        
        // Mise à jour Load Average
        updateLoadAverage(data.load);
        
        // Mise à jour CPU
        updateCPU(data.cpu);
        
        // Mise à jour Mémoire
        updateMemory(data.memory);
        
        // Mise à jour Disques
        updateDisks(data.disk);
        
        // Mise à jour Réseau
        updateNetwork(data.network);
        
        // Mise à jour Système
        updateSystem(data.system);
        
        // Mise à jour des graphiques
        const timeLabel = new Date().toLocaleTimeString('fr-FR');
        cpuHistory.push(data.cpu.percent);
        memoryHistory.push(data.memory.percent);
        networkSentHistory.push(data.network.bytes_sent);
        networkRecvHistory.push(data.network.bytes_recv);
        
        if (cpuHistory.length > maxDataPoints) {
            cpuHistory.shift();
            memoryHistory.shift();
            networkSentHistory.shift();
            networkRecvHistory.shift();
        }
        
        // CPU Chart
        if (cpuChart) {
            cpuChart.data.labels.push(timeLabel);
            cpuChart.data.datasets[0].data = cpuHistory;
            if (cpuChart.data.labels.length > maxDataPoints) {
                cpuChart.data.labels.shift();
            }
            cpuChart.update('none');
        }
        
        // CPU Doughnut
        if (cpuDoughnutChart) {
            cpuDoughnutChart.data.datasets[0].data = [data.cpu.percent, 100 - data.cpu.percent];
            cpuDoughnutChart.update('none');
        }
        
        // Memory Chart
        if (memoryChart) {
            memoryChart.data.labels.push(timeLabel);
            memoryChart.data.datasets[0].data = memoryHistory;
            if (memoryChart.data.labels.length > maxDataPoints) {
                memoryChart.data.labels.shift();
            }
            memoryChart.update('none');
        }
        
        // Network Chart
        if (networkChart) {
            networkChart.data.labels.push(timeLabel);
            networkChart.data.datasets[0].data = networkSentHistory;
            networkChart.data.datasets[1].data = networkRecvHistory;
            if (networkChart.data.labels.length > maxDataPoints) {
                networkChart.data.labels.shift();
            }
            networkChart.update('none');
        }
        
    } catch (error) {
        console.error('Erreur lors de la récupération des métriques:', error);
    }
}

// Mise à jour Load Average
function updateLoadAverage(load) {
    document.getElementById('load1-value').textContent = load.load1.toFixed(2);
    document.getElementById('load5-value').textContent = load.load5.toFixed(2);
    document.getElementById('load15-value').textContent = load.load15.toFixed(2);
}

// Mise à jour CPU
function updateCPU(cpu) {
    document.getElementById('cpu-count-value').textContent = cpu.count;
    document.getElementById('cpu-freq').textContent = cpu.freq.toFixed(0) + ' MHz';
    document.getElementById('cpu-count').textContent = cpu.count + ' cœurs';
    document.getElementById('cpu-avg').textContent = cpu.percent.toFixed(1) + '%';
    
    // Mise à jour des barres par CPU
    const perCpuContainer = document.getElementById('per-cpu-bars');
    perCpuContainer.innerHTML = '';
    
    cpu.per_cpu.forEach((percent, index) => {
        const color = percent > 80 ? 'danger' : percent > 50 ? 'warning' : 'success';
        perCpuContainer.innerHTML += `
            <div class="mb-3">
                <div class="d-flex justify-content-between mb-1">
                    <span class="text-muted">CPU ${index}</span>
                    <span class="fw-bold">${percent.toFixed(1)}%</span>
                </div>
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar bg-${color}" role="progressbar" 
                         style="width: ${percent}%;" 
                         aria-valuenow="${percent}" 
                         aria-valuemin="0" 
                         aria-valuemax="100">
                    </div>
                </div>
            </div>
        `;
    });
}

// Mise à jour Mémoire
function updateMemory(memory) {
    document.getElementById('ram-percent').textContent = memory.percent.toFixed(1) + '%';
    document.getElementById('ram-used').textContent = memory.used.toFixed(2) + ' GB utilisés';
    document.getElementById('ram-total').textContent = memory.total.toFixed(2) + ' GB total';
    
    document.getElementById('swap-percent').textContent = memory.swap_percent.toFixed(1) + '%';
    document.getElementById('swap-used').textContent = memory.swap_used.toFixed(2) + ' GB utilisés';
    document.getElementById('swap-total').textContent = memory.swap_total.toFixed(2) + ' GB total';
    
    // Mise à jour des barres de progression
    const ramBar = document.querySelector('#ram-percent').previousElementSibling.querySelector('.progress-bar');
    const swapBar = document.querySelector('#swap-percent').previousElementSibling.querySelector('.progress-bar');
    
    if (ramBar) {
        ramBar.style.width = memory.percent + '%';
        ramBar.className = `progress-bar bg-${memory.percent > 80 ? 'danger' : memory.percent > 50 ? 'warning' : 'primary'}`;
    }
    
    if (swapBar) {
        swapBar.style.width = memory.swap_percent + '%';
        swapBar.className = `progress-bar bg-${memory.swap_percent > 80 ? 'danger' : memory.swap_percent > 50 ? 'warning' : 'warning'}`;
    }
}

// Mise à jour Disques
function updateDisks(disks) {
    const tbody = document.getElementById('disk-table-body');
    tbody.innerHTML = '';
    
    disks.forEach(disk => {
        const color = disk.percent > 80 ? 'danger' : disk.percent > 50 ? 'warning' : 'success';
        tbody.innerHTML += `
            <tr>
                <td><strong>${disk.device}</strong></td>
                <td>${disk.mountpoint}</td>
                <td><span class="badge bg-secondary">${disk.fstype}</span></td>
                <td>${disk.total.toFixed(2)} GB</td>
                <td>${disk.used.toFixed(2)} GB</td>
                <td>${disk.free.toFixed(2)} GB</td>
                <td>
                    <div class="progress" style="height: 20px; min-width: 100px;">
                        <div class="progress-bar bg-${color}" role="progressbar" 
                             style="width: ${disk.percent}%;">
                            ${disk.percent.toFixed(1)}%
                        </div>
                    </div>
                </td>
            </tr>
        `;
    });
}

// Mise à jour Réseau
function updateNetwork(network) {
    document.getElementById('net-sent').textContent = network.bytes_sent.toFixed(2) + ' MB';
    document.getElementById('net-recv').textContent = network.bytes_recv.toFixed(2) + ' MB';
    document.getElementById('packets-sent').textContent = network.packets_sent.toLocaleString();
    document.getElementById('packets-recv').textContent = network.packets_recv.toLocaleString();
}

// Mise à jour Système
function updateSystem(system) {
    document.getElementById('sys-platform').textContent = system.platform;
    document.getElementById('sys-version').textContent = system.platform_release;
    document.getElementById('sys-arch').textContent = system.architecture;
    document.getElementById('sys-hostname').textContent = system.hostname;
    document.getElementById('sys-boot').textContent = system.boot_time;
    document.getElementById('sys-uptime').textContent = system.uptime;
    document.getElementById('sys-processor').textContent = system.processor || 'N/A';
}

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    updateMetrics();
    
    // Mise à jour toutes les 2 secondes
    setInterval(updateMetrics, 2000);
});
