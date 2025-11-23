// Trading Bot Dashboard - Real-Time Updates

class Dashboard {
    constructor() {
        this.API_BASE = '';  // Same origin
        this.UPDATE_INTERVAL = 5000;  // 5 seconds
        this.equityChart = null;
        this.eventSource = null;

        this.init();
    }

    async init() {
        console.log('🚀 Initializing dashboard...');

        // Initialize chart
        this.initEquityChart();

        // Load initial data
        await this.loadMetrics();
        await this.loadPositions();
        await this.loadTrades();
        await this.loadEquityCurve();

        // Start Server-Sent Events for real-time updates
        this.startSSE();

        // Fallback polling if SSE fails
        setInterval(() => this.updateAll(), this.UPDATE_INTERVAL);

        // Event listeners
        this.setupEventListeners();

        console.log('✅ Dashboard initialized');
    }

    setupEventListeners() {
        // Refresh chart button
        const refreshBtn = document.getElementById('refresh-chart');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadEquityCurve());
        }

        // Trade filters
        const filterBtns = document.querySelectorAll('.filter-btn');
        filterBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                filterBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                const filter = e.target.dataset.filter;
                this.filterTrades(filter);
            });
        });
    }

    startSSE() {
        try {
            this.eventSource = new EventSource('/api/stream');

            this.eventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.updateMetrics(data);
            };

            this.eventSource.onerror = (error) => {
                console.warn('SSE error, using polling fallback');
                this.eventSource.close();
            };

            console.log('📡 SSE connection established');
        } catch (error) {
            console.warn('SSE not supported, using polling');
        }
    }

    async updateAll() {
        try {
            await this.loadMetrics();
            await this.loadPositions();
            if (Math.random() > 0.8) {  // Update trades less frequently
                await this.loadTrades();
            }
        } catch (error) {
            console.error('Update error:', error);
        }
    }

    async loadMetrics() {
        try {
            const response = await fetch(`${this.API_BASE}/api/metrics`);
            const data = await response.json();
            this.updateMetrics(data);
        } catch (error) {
            console.error('Error loading metrics:', error);
        }
    }

    updateMetrics(data) {
        // Capital
        this.updateElement('capital', this.formatCurrency(data.capital));
        this.updateElement('initial-capital', this.formatCurrency(data.initial_capital));

        // Total Return
        const returnEl = document.getElementById('total-return');
        const returnValue = data.total_return || 0;
        returnEl.textContent = this.formatPercent(returnValue);
        returnEl.className = 'metric-value ' + (returnValue >= 0 ? 'success' : 'danger');

        // Win Rate
        this.updateElement('win-rate', this.formatPercent(data.win_rate || 0));
        this.updateElement('trades-count', `${data.total_trades || 0} trades`);

        // Profit Factor
        const pfValue = data.profit_factor || 0;
        this.updateElement('profit-factor', pfValue.toFixed(2));

        // Max Drawdown
        this.updateElement('max-drawdown', this.formatPercent(data.max_drawdown || 0));

        // Open Positions
        this.updateElement('open-positions', data.open_positions || 0);
        this.updateElement('positions-badge', data.open_positions || 0);

        // Status
        const statusBadge = document.getElementById('bot-status');
        if (statusBadge) {
            const statusText = statusBadge.querySelector('.status-text');
            const statusDot = statusBadge.querySelector('.status-dot');

            if (data.status === 'running') {
                statusText.textContent = 'Live Trading';
                statusDot.style.background = '#00ff88';
            } else if (data.status === 'stopped') {
                statusText.textContent = 'Stopped';
                statusDot.style.background = '#ff3838';
            } else {
                statusText.textContent = 'Development';
                statusDot.style.background = '#ffaa00';
            }
        }

        // Last update time
        this.updateElement('last-update-time', new Date().toLocaleTimeString());
    }

    async loadPositions() {
        try {
            const response = await fetch(`${this.API_BASE}/api/positions`);
            const positions = await response.json();
            this.displayPositions(positions);
        } catch (error) {
            console.error('Error loading positions:', error);
        }
    }

    displayPositions(positions) {
        const container = document.getElementById('positions-list');

        if (!positions || positions.length === 0) {
            container.innerHTML = '<p class="no-data">No open positions</p>';
            return;
        }

        container.innerHTML = positions.map(pos => {
            const isProfitable = pos.unrealized_pnl >= 0;
            const pnlClass = isProfitable ? 'profitable' : 'losing';

            return `
                <div class="position-card ${pnlClass}">
                    <div class="position-field">
                        <span class="position-label">Symbol</span>
                        <span class="position-value">${pos.symbol}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Side</span>
                        <span class="position-value">${pos.side}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Entry</span>
                        <span class="position-value">$${pos.entry_price.toFixed(2)}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Current</span>
                        <span class="position-value">$${pos.current_price.toFixed(2)}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Amount</span>
                        <span class="position-value">${pos.amount.toFixed(4)}</span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">PnL</span>
                        <span class="position-value ${isProfitable ? 'profit' : 'loss'}">
                            $${pos.unrealized_pnl.toFixed(2)} (${pos.pnl_percent.toFixed(2)}%)
                        </span>
                    </div>
                    <div class="position-field">
                        <span class="position-label">Duration</span>
                        <span class="position-value">${this.formatDuration(pos.duration_minutes)}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    async loadTrades() {
        try {
            const response = await fetch(`${this.API_BASE}/api/trades?limit=50`);
            const trades = await response.json();
            this.displayTrades(trades);
        } catch (error) {
            console.error('Error loading trades:', error);
        }
    }

    displayTrades(trades) {
        const tbody = document.getElementById('trades-body');

        if (!trades || trades.length === 0) {
            tbody.innerHTML = '<tr><td colspan="9" class="no-data">No trades yet</td></tr>';
            return;
        }

        tbody.innerHTML = trades.map(trade => {
            const isProfitable = trade.pnl >= 0;
            const pnlClass = isProfitable ? 'profit' : 'loss';

            const time = new Date(trade.timestamp).toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });

            return `
                <tr data-pnl="${isProfitable ? 'win' : 'loss'}">
                    <td>${time}</td>
                    <td>${trade.symbol}</td>
                    <td>${trade.strategy}</td>
                    <td>${trade.side}</td>
                    <td>$${trade.entry_price.toFixed(2)}</td>
                    <td>$${trade.exit_price.toFixed(2)}</td>
                    <td class="${pnlClass}">$${trade.pnl.toFixed(2)}</td>
                    <td class="${pnlClass}">${trade.pnl_percent.toFixed(2)}%</td>
                    <td>${trade.reason}</td>
                </tr>
            `;
        }).join('');
    }

    filterTrades(filter) {
        const rows = document.querySelectorAll('#trades-body tr');
        rows.forEach(row => {
            if (filter === 'all') {
                row.style.display = '';
            } else {
                const pnl = row.dataset.pnl;
                row.style.display =
                    (filter === 'wins' && pnl === 'win') ||
                        (filter === 'losses' && pnl === 'loss') ? '' : 'none';
            }
        });
    }

    initEquityChart() {
        const ctx = document.getElementById('equityChart');
        if (!ctx) return;

        this.equityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Capital',
                    data: [],
                    borderColor: '#0066ff',
                    backgroundColor: 'rgba(0, 102, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(26, 31, 58, 0.9)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: '#0066ff',
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(45, 53, 85, 0.3)'
                        },
                        ticks: {
                            color: '#8892b0'
                        }
                    },
                    y: {
                        grid: {
                            color: 'rgba(45, 53, 85, 0.3)'
                        },
                        ticks: {
                            color: '#8892b0',
                            callback: function (value) {
                                return '$' + value.toFixed(0);
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }

    async loadEquityCurve() {
        try {
            const response = await fetch(`${this.API_BASE}/api/equity`);
            const data = await response.json();

            if (data && data.timestamps && data.values) {
                this.equityChart.data.labels = data.timestamps.map(t => {
                    const date = new Date(t);
                    return date.toLocaleString('en-US', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                });
                this.equityChart.data.datasets[0].data = data.values;
                this.equityChart.update();
            }
        } catch (error) {
            console.error('Error loading equity curve:', error);
        }
    }

    // Utility functions
    updateElement(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    }

    formatCurrency(value) {
        return '$' + (value || 0).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    formatPercent(value) {
        const sign = value >= 0 ? '+' : '';
        return sign + (value || 0).toFixed(2) + '%';
    }

    formatDuration(minutes) {
        if (minutes < 60) {
            return `${Math.floor(minutes)}m`;
        } else if (minutes < 1440) {
            return `${Math.floor(minutes / 60)}h ${Math.floor(minutes % 60)}m`;
        } else {
            return `${Math.floor(minutes / 1440)}d ${Math.floor((minutes % 1440) / 60)}h`;
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});
