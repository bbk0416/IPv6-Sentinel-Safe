class IPv6SentinelDashboard {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.isMonitoring = false;
        this.autoScroll = true;
        this.updateInterval = null;
        this.performanceChart = null;
        this.assets = new Map();
        this.logs = [];
        this.restMode = false;
        this.init();
    }

    init() {
        this.connectSocket();
        this.setupEventListeners();
        this.setupCharts();
        this.loadSettings();
        this.startUpdateTimer();
        this.updateCurrentTime();
    }

    connectSocket() {
        try {
            if (typeof io === 'undefined') {
                this.enterRestFallbackMode('Socket.IO 클라이언트 CDN을 사용할 수 없어 REST 폴링 모드로 전환했습니다.');
                return;
            }
            this.socket = io();

            this.socket.on('connect', () => {
                this.isConnected = true;
                this.updateConnectionStatus('연결됨', 'success');
                this.log('시스템에 연결되었습니다.', 'info');
            });

            this.socket.on('disconnect', () => {
                this.isConnected = false;
                this.updateConnectionStatus('연결 끊김', 'danger');
                this.log('시스템 연결이 끊어졌습니다.', 'error');
            });

            this.socket.on('connected', (payload) => {
                if (payload.stats) this.updateStats(payload.stats);
                if (payload.assets) this.updateAssets(payload.assets);
                if (payload.settings) this.applySettings(payload.settings);
            });

            this.socket.on('stats_update', (data) => this.updateStats(data));
            this.socket.on('assets_update', (assets) => this.updateAssets(assets));
            this.socket.on('monitoring_log', (entry) => this.addLogEntry(entry));
            this.socket.on('asset_discovered', (asset) => {
                this.assets.set(asset.asset_id, asset);
                this.updateAssets(Array.from(this.assets.values()));
                this.showNotification(`새 관측 자산: ${asset.host || asset.mac}`, 'info');
            });
            this.socket.on('monitoring_status', (status) => this.handleMonitoringStatus(status));
            this.socket.on('inventory_status', (status) => this.handleInventoryStatus(status));
            this.socket.on('inventory_progress', (progress) => this.updateInventoryProgress(progress));
            this.socket.on('performance_update', (data) => this.updatePerformance(data));
            this.socket.on('settings_updated', (settings) => this.applySettings(settings));
            this.socket.on('demo_scenario_seeded', (payload) => this.handleDemoScenario(payload));
            this.socket.on('logs_cleared', () => {
                this.logs = [];
                document.getElementById('terminal').innerHTML = '';
                this.log('서버 로그가 정리되었습니다.', 'success');
            });
            this.socket.on('error', (error) => this.log(`소켓 오류: ${error}`, 'error'));
        } catch (error) {
            console.error('소켓 연결 실패:', error);
            this.enterRestFallbackMode('소켓 연결에 실패해 REST 폴링 모드로 전환했습니다.');
        }
    }

    enterRestFallbackMode(message) {
        this.restMode = true;
        this.isConnected = true;
        this.updateConnectionStatus('REST 모드', 'warning');
        this.log(message, 'warning');
        this.requestUpdates();
    }

    setupEventListeners() {
        document.getElementById('start-monitoring').addEventListener('click', () => this.startMonitoring());
        document.getElementById('stop-monitoring').addEventListener('click', () => this.stopMonitoring());
        document.getElementById('generate-assets').addEventListener('click', () => this.generateAssets());
        document.getElementById('seed-demo').addEventListener('click', () => this.seedDemoScenario());
        document.getElementById('clear-logs').addEventListener('click', () => this.clearLogs());
        document.getElementById('reset-simulation').addEventListener('click', () => this.resetSimulation());
        document.getElementById('export-logs').addEventListener('click', () => this.exportLogs());
        document.getElementById('export-snapshot').addEventListener('click', () => this.exportSnapshot());
        document.getElementById('export-report').addEventListener('click', () => this.exportPortfolioReport());
        document.getElementById('auto-scroll').addEventListener('click', () => this.toggleAutoScroll());
        document.getElementById('clear-terminal').addEventListener('click', () => this.clearTerminal());
        document.getElementById('simulation-speed').addEventListener('input', (event) => this.updateSpeed(event.target.value));
        document.getElementById('modal-speed').addEventListener('input', (event) => {
            document.getElementById('simulation-speed').value = event.target.value;
            document.getElementById('speed-value').textContent = event.target.value;
        });
        document.getElementById('save-settings').addEventListener('click', () => this.saveSettings());
    }

    setupCharts() {
        const canvas = document.getElementById('performance-chart');
        if (!canvas || typeof Chart === 'undefined') return;
        const ctx = canvas.getContext('2d');
        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: '안전 점수 (%)', data: [], borderColor: '#198754', backgroundColor: 'rgba(25,135,84,0.12)', tension: 0.35, fill: true },
                    { label: '총 이벤트', data: [], borderColor: '#0dcaf0', backgroundColor: 'rgba(13,202,240,0.10)', tension: 0.35, fill: true, yAxisID: 'y1' }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { labels: { color: '#fff' } } },
                scales: {
                    x: { ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                    y: { beginAtZero: true, max: 100, ticks: { color: '#fff' }, grid: { color: 'rgba(255,255,255,0.1)' } },
                    y1: { type: 'linear', display: true, position: 'right', beginAtZero: true, ticks: { color: '#fff' }, grid: { drawOnChartArea: false } }
                }
            }
        });
    }

    startUpdateTimer() {
        this.updateInterval = setInterval(() => {
            this.updateCurrentTime();
            this.requestUpdates();
        }, 3000);
    }

    requestUpdates() {
        if (this.socket && this.isConnected && !this.restMode) {
            this.socket.emit('request_update');
            this.socket.emit('request_stats');
            this.socket.emit('request_performance');
            return;
        }
        if (this.restMode) this.fetchRestState();
    }

    async fetchRestState() {
        try {
            const [stats, assets, performance, logs] = await Promise.all([
                fetch('/api/stats').then(r => r.json()),
                fetch('/api/assets').then(r => r.json()),
                fetch('/api/performance').then(r => r.json()).catch(() => ({})),
                fetch('/api/logs').then(r => r.json()).catch(() => [])
            ]);
            this.updateStats(stats);
            this.updateAssets(assets);
            this.updatePerformance(performance || {});
            if (Array.isArray(logs) && logs.length !== this.logs.length) {
                this.logs = logs;
                const terminal = document.getElementById('terminal');
                terminal.innerHTML = '';
                this.logs.forEach(entry => this.displayLog(entry));
            }
        } catch (error) {
            this.updateConnectionStatus('REST 오류', 'danger');
            this.log(`REST 상태 갱신 실패: ${error}`, 'error');
        }
    }

    updateCurrentTime() {
        document.getElementById('current-time').textContent = new Date().toLocaleTimeString('ko-KR');
    }

    updateConnectionStatus(status, type) {
        const statusElement = document.getElementById('connection-status');
        const indicator = document.querySelector('.navbar-text i.fas.fa-circle');
        statusElement.textContent = status;
        indicator.className = `fas fa-circle text-${type}`;
        indicator.style.animation = type === 'success' ? 'pulse 2s infinite' : 'none';
    }

    updateStats(data) {
        document.getElementById('total-events').textContent = data.total_events || 0;
        document.getElementById('dhcpv6-observations').textContent = data.dhcpv6_observations || 0;
        document.getElementById('dns-observations').textContent = data.dns_observations || 0;
        document.getElementById('safety-score').textContent = `${data.safety_score ?? 100}%`;
        const activeAssets = document.getElementById('active-assets');
        if (activeAssets) activeAssets.textContent = data.active_assets || 0;
        document.getElementById('security-score').textContent = data.safety_score ?? 100;
        document.getElementById('policy-response-events').textContent = data.policy_response_events || 0;
        document.getElementById('suspicious-events').textContent = data.suspicious_events || 0;
        if (data.memory_usage !== undefined) document.getElementById('memory-usage').textContent = `${data.memory_usage.toFixed(1)}%`;
        if (data.cpu_usage !== undefined) document.getElementById('cpu-usage').textContent = `${data.cpu_usage.toFixed(1)}%`;
        if (data.uptime !== undefined) document.getElementById('uptime').textContent = this.formatUptime(data.uptime);
        document.getElementById('last-update').textContent = new Date().toLocaleTimeString('ko-KR');
        this.updateSecurityProgress(data.safety_score ?? 100);
        this.updateChart(data);
    }

    updateSecurityProgress(score) {
        const progress = document.getElementById('security-progress');
        progress.style.width = `${score}%`;
        progress.className = 'progress-bar ' + (score >= 80 ? 'bg-success' : score >= 50 ? 'bg-warning' : 'bg-danger');
    }

    updateChart(data) {
        if (!this.performanceChart) return;
        const now = new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        this.performanceChart.data.labels.push(now);
        this.performanceChart.data.datasets[0].data.push(data.safety_score ?? 100);
        this.performanceChart.data.datasets[1].data.push(data.total_events || 0);
        if (this.performanceChart.data.labels.length > 20) {
            this.performanceChart.data.labels.shift();
            this.performanceChart.data.datasets.forEach(dataset => dataset.data.shift());
        }
        this.performanceChart.update('none');
    }

    updateAssets(assets) {
        const list = document.getElementById('asset-list');
        const count = document.getElementById('asset-count');
        assets.forEach(asset => this.assets.set(asset.asset_id || asset.mac, asset));
        const normalized = Array.from(this.assets.values());
        count.textContent = normalized.length;
        if (normalized.length === 0) {
            list.innerHTML = '<div class="text-center text-muted py-4"><i class="fas fa-magnifying-glass fa-2x mb-2"></i><p>샘플 자산 생성을 누르세요</p></div>';
            return;
        }
        list.innerHTML = '';
        normalized.sort((a, b) => (a.host || '').localeCompare(b.host || '')).forEach(asset => list.appendChild(this.createAssetElement(asset)));
    }

    createAssetElement(asset) {
        const div = document.createElement('div');
        div.className = 'target-item fade-in';
        const risk = asset.metadata?.risk_level || 'LOW';
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="target-mac">${this.escapeHtml(asset.host || asset.mac)}</div>
                    <div class="target-ip text-muted">${this.escapeHtml(asset.ipv6 || asset.ipv4 || asset.mac)}</div>
                </div>
                <div class="text-end">
                    <span class="badge ${risk === 'HIGH' ? 'bg-danger' : risk === 'MEDIUM' ? 'bg-warning text-dark' : 'bg-success'}">${risk}</span>
                    <div class="target-status online mt-2"></div>
                </div>
            </div>`;
        div.addEventListener('click', () => this.showAssetDetails(asset));
        return div;
    }

    addLogEntry(entry) {
        this.logs.push(entry);
        if (this.logs.length > 1000) this.logs = this.logs.slice(-500);
        this.displayLog(entry);
    }

    displayLog(entry) {
        const terminal = document.getElementById('terminal');
        const line = document.createElement('div');
        line.className = `terminal-line ${entry.status || 'info'}`;
        const timestamp = entry.timestamp || new Date().toLocaleTimeString('ko-KR');
        const message = entry.message || entry.details?.message || '';
        line.textContent = `${timestamp} [${entry.event_type || 'SYSTEM'}] ${entry.asset || ''} - ${message}`;
        terminal.appendChild(line);
        if (this.autoScroll) terminal.scrollTop = terminal.scrollHeight;
        while (terminal.children.length > 150) terminal.removeChild(terminal.firstChild);
    }

    log(message, type = 'info') {
        this.addLogEntry({ timestamp: new Date().toLocaleTimeString('ko-KR'), event_type: 'system', asset: 'local-dashboard', status: type, message });
    }

    async startMonitoring() {
        if (!this.isConnected) return this.showNotification('시스템에 연결되지 않았습니다.', 'error');
        if (this.socket && !this.restMode) {
            this.socket.emit('start_monitoring');
        } else {
            const response = await fetch('/api/monitoring/start', { method: 'POST' });
            const payload = await response.json();
            this.updateStats(payload.stats || {});
            this.updateAssets(payload.assets || []);
            this.handleMonitoringStatus({ status: 'started' });
        }
        this.log('모니터링 시작 명령을 전송했습니다.', 'info');
    }

    async stopMonitoring() {
        if (!this.isConnected) return this.showNotification('시스템에 연결되지 않았습니다.', 'error');
        if (this.socket && !this.restMode) {
            this.socket.emit('stop_monitoring');
        } else {
            const response = await fetch('/api/monitoring/stop', { method: 'POST' });
            const payload = await response.json();
            this.updateStats(payload.stats || {});
            this.updateAssets(payload.assets || []);
            this.handleMonitoringStatus({ status: 'stopped' });
        }
        this.log('모니터링 중지 명령을 전송했습니다.', 'info');
    }

    async generateAssets() {
        if (!this.isConnected) return this.showNotification('시스템에 연결되지 않았습니다.', 'error');
        if (this.socket && !this.restMode) {
            this.socket.emit('generate_sample_assets');
        } else {
            const response = await fetch('/api/assets/generate', { method: 'POST' });
            const payload = await response.json();
            this.updateAssets(payload.assets || []);
            this.updateStats(payload.stats || {});
            this.logs = payload.logs || this.logs;
            const terminal = document.getElementById('terminal');
            terminal.innerHTML = '';
            this.logs.forEach(entry => this.displayLog(entry));
            this.handleInventoryStatus({ status: 'completed' });
        }
        this.log('샘플 자산 생성을 시작했습니다.', 'info');
    }

    handleMonitoringStatus(status) {
        const startButton = document.getElementById('start-monitoring');
        const stopButton = document.getElementById('stop-monitoring');
        if (status.status === 'started') {
            this.isMonitoring = true;
            startButton.disabled = true;
            stopButton.disabled = false;
            this.showNotification('모니터링이 시작되었습니다.', 'success');
        } else if (status.status === 'stopped') {
            this.isMonitoring = false;
            startButton.disabled = false;
            stopButton.disabled = true;
            this.showNotification('모니터링이 중지되었습니다.', 'warning');
        }
    }

    handleInventoryStatus(status) {
        if (status.status === 'running') this.log('샘플 자산 생성 중...', 'info');
        if (status.status === 'completed') {
            this.log('샘플 자산 생성이 완료되었습니다.', 'success');
            this.showNotification('샘플 자산 생성 완료', 'success');
        }
    }

    updateInventoryProgress(progress) {
        this.log(`자산 생성 진행률: ${progress.progress.toFixed(1)}% (${progress.processed ?? 0}/${progress.total})`, 'info');
    }

    updatePerformance(data) {
        if (data.cpu_usage !== undefined) document.getElementById('cpu-usage').textContent = `${data.cpu_usage.toFixed(1)}%`;
        if (data.memory_usage !== undefined) document.getElementById('memory-usage').textContent = `${data.memory_usage.toFixed(1)}%`;
        if (data.network_throughput_mbps !== undefined) document.getElementById('network-throughput').textContent = `${data.network_throughput_mbps.toFixed(3)} Mbps`;
    }

    updateSpeed(value) {
        document.getElementById('speed-value').textContent = value;
        document.getElementById('modal-speed').value = value;
        if (this.socket && this.isConnected && !this.restMode) {
            this.socket.emit('set_simulation_speed', { speed: parseInt(value, 10) });
        } else if (this.restMode) {
            fetch('/api/simulation/speed', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ speed: parseInt(value, 10) })
            }).catch(() => this.log('시뮬레이션 속도 저장 실패', 'warning'));
        }
    }

    toggleAutoScroll() {
        this.autoScroll = !this.autoScroll;
        const button = document.getElementById('auto-scroll');
        button.innerHTML = this.autoScroll ? '<i class="fas fa-arrow-down"></i>' : '<i class="fas fa-pause"></i>';
        button.classList.toggle('btn-outline-secondary', !this.autoScroll);
        button.classList.toggle('btn-outline-light', this.autoScroll);
    }

    clearTerminal() {
        document.getElementById('terminal').innerHTML = '';
        this.log('터미널이 정리되었습니다.', 'info');
    }

    clearLogs() {
        this.logs = [];
        document.getElementById('terminal').innerHTML = '';
        if (this.socket && this.isConnected && !this.restMode) {
            this.socket.emit('clear_logs');
        } else if (this.restMode) {
            fetch('/api/logs/clear', { method: 'POST' }).catch(() => this.log('서버 로그 정리 실패', 'warning'));
        }
        this.log('로그 정리 요청을 전송했습니다.', 'info');
    }

    async resetSimulation() {
        try {
            const response = await fetch('/api/reset', { method: 'POST' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const payload = await response.json();
            this.assets.clear();
            this.updateAssets(payload.assets || []);
            this.updateStats(payload.stats || {});
            this.logs = [];
            document.getElementById('terminal').innerHTML = '';
            this.log('시뮬레이션 데이터가 초기화되었습니다.', 'success');
            this.showNotification('시뮬레이션 초기화 완료', 'success');
        } catch (error) {
            this.showNotification('초기화에 실패했습니다.', 'error');
            this.log(`초기화 실패: ${error}`, 'error');
        }
    }

    async seedDemoScenario() {
        try {
            const response = await fetch('/api/demo/scenario', { method: 'POST' });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const payload = await response.json();
            this.handleDemoScenario(payload);
        } catch (error) {
            this.showNotification('데모 시나리오 생성에 실패했습니다.', 'error');
            this.log(`데모 시나리오 실패: ${error}`, 'error');
        }
    }

    handleDemoScenario(payload) {
        if (!payload) return;
        this.updateAssets(payload.assets || []);
        this.updateStats(payload.stats || {});
        this.logs = payload.logs || [];
        const terminal = document.getElementById('terminal');
        terminal.innerHTML = '';
        this.logs.forEach(entry => this.displayLog(entry));
        this.showNotification('데모 시나리오 준비 완료', 'success');
    }

    exportLogs() {
        window.location.href = '/api/logs.csv';
    }

    exportSnapshot() {
        window.location.href = '/api/snapshot.json';
    }

    exportPortfolioReport() {
        window.location.href = '/api/report.json';
    }

    showAssetDetails(asset) {
        const body = document.getElementById('asset-detail-body');
        const metadata = asset.metadata || {};
        body.innerHTML = `
            <dl class="row mb-0">
                <dt class="col-sm-4">호스트</dt><dd class="col-sm-8">${this.escapeHtml(asset.host || '-')}</dd>
                <dt class="col-sm-4">MAC</dt><dd class="col-sm-8"><code>${this.escapeHtml(asset.mac || '-')}</code></dd>
                <dt class="col-sm-4">IPv4</dt><dd class="col-sm-8"><code>${this.escapeHtml(asset.ipv4 || '-')}</code></dd>
                <dt class="col-sm-4">IPv6</dt><dd class="col-sm-8"><code>${this.escapeHtml(asset.ipv6 || '-')}</code></dd>
                <dt class="col-sm-4">역할</dt><dd class="col-sm-8">${this.escapeHtml(metadata.role || 'Unknown')}</dd>
                <dt class="col-sm-4">위험도</dt><dd class="col-sm-8">${this.escapeHtml(metadata.risk_level || 'LOW')}</dd>
                <dt class="col-sm-4">관측 횟수</dt><dd class="col-sm-8">${asset.observation_count || 0}</dd>
                <dt class="col-sm-4">최초 관측</dt><dd class="col-sm-8">${this.escapeHtml(asset.first_seen || '-')}</dd>
                <dt class="col-sm-4">최근 관측</dt><dd class="col-sm-8">${this.escapeHtml(asset.last_seen || '-')}</dd>
            </dl>`;
        if (window.bootstrap && bootstrap.Modal) {
            new bootstrap.Modal(document.getElementById('assetModal')).show();
        } else {
            this.showNotification(`자산 상세: ${asset.host || asset.mac}`, 'info');
        }
    }

    async loadSettings() {
        try {
            const response = await fetch('/api/settings');
            if (response.ok) this.applySettings(await response.json());
        } catch (error) {
            this.log('설정 로드 실패: 기본값 사용', 'warning');
        }
    }

    async saveSettings() {
        const payload = {
            interface: document.getElementById('interface-select').value,
            simulation_speed: parseInt(document.getElementById('modal-speed').value, 10),
            policy_response_enabled: document.getElementById('policy-response-enabled').checked,
            threat_detection: document.getElementById('threat-detection').checked,
            event_retention: parseInt(document.getElementById('event-retention').value, 10)
        };
        try {
            const response = await fetch('/api/settings', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const settings = await response.json();
            this.applySettings(settings);
            this.showNotification('설정이 저장되었습니다.', 'success');
            if (window.bootstrap && bootstrap.Modal) bootstrap.Modal.getInstance(document.getElementById('settingsModal'))?.hide();
        } catch (error) {
            this.showNotification('설정 저장에 실패했습니다.', 'error');
            this.log(`설정 저장 실패: ${error}`, 'error');
        }
    }

    applySettings(settings) {
        if (!settings) return;
        if (settings.interface !== undefined) {
            document.getElementById('interface-select').value = settings.interface;
            document.getElementById('interface-name').textContent = settings.interface;
        }
        if (settings.simulation_speed !== undefined) {
            document.getElementById('simulation-speed').value = settings.simulation_speed;
            document.getElementById('modal-speed').value = settings.simulation_speed;
            document.getElementById('speed-value').textContent = settings.simulation_speed;
        }
        if (settings.policy_response_enabled !== undefined) document.getElementById('policy-response-enabled').checked = settings.policy_response_enabled;
        if (settings.threat_detection !== undefined) document.getElementById('threat-detection').checked = settings.threat_detection;
        if (settings.event_retention !== undefined) document.getElementById('event-retention').value = settings.event_retention;
    }

    showNotification(message, type = 'info') {
        const toast = document.getElementById('notification-toast');
        document.getElementById('toast-message').textContent = message;
        toast.className = `toast bg-dark text-light border-${type}`;
        if (window.bootstrap && bootstrap.Toast) {
            new bootstrap.Toast(toast).show();
        } else {
            this.log(message, type);
        }
    }

    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        if (hours > 0) return `${hours}h ${minutes}m ${secs}s`;
        if (minutes > 0) return `${minutes}m ${secs}s`;
        return `${secs}s`;
    }

    escapeHtml(value) {
        return String(value).replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
    }

    destroy() {
        if (this.updateInterval) clearInterval(this.updateInterval);
        if (this.socket) this.socket.disconnect();
        if (this.performanceChart) this.performanceChart.destroy();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new IPv6SentinelDashboard();
    window.addEventListener('beforeunload', () => window.dashboard?.destroy());
});
