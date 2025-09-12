// RFID Reader Web Application JavaScript

class RFIDWebApp {
    constructor() {
        this.isConnected = false;
        this.isReading = false;
        this.timerInterval = null;
        this.statusInterval = null;
        this.epcInterval = null;
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.startStatusUpdates();
        this.updatePowerValue();
    }
    
    bindEvents() {
        // Connection buttons
        document.getElementById('connect-btn').addEventListener('click', () => this.connect());
        document.getElementById('disconnect-btn').addEventListener('click', () => this.disconnect());
        
        // Reading control buttons
        document.getElementById('start-btn').addEventListener('click', () => this.startReading());
        document.getElementById('stop-btn').addEventListener('click', () => this.stopReading());
        document.getElementById('clear-btn').addEventListener('click', () => this.clearEPCs());
        
        // Power slider
        document.getElementById('power-slider').addEventListener('input', (e) => this.updatePower(e.target.value));
        
        // EPC controls
        document.getElementById('refresh-epcs').addEventListener('click', () => this.refreshEPCs());
        document.getElementById('export-epcs').addEventListener('click', () => this.exportEPCs());
    }
    
    async makeRequest(url, method = 'GET', data = null) {
        try {
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(url, options);
            return await response.json();
        } catch (error) {
            console.error('Request failed:', error);
            this.showToast('Network error occurred', 'error');
            throw error;
        }
    }
    
    async connect() {
        this.showLoading(true);
        try {
            const result = await this.makeRequest('/api/connect', 'POST');
            if (result.success) {
                this.isConnected = true;
                this.updateConnectionUI();
                this.showMessage('connection-message', result.message, 'success');
                this.showToast('Connected successfully', 'success');
            } else {
                this.showMessage('connection-message', result.message, 'error');
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            this.showMessage('connection-message', 'Connection failed', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async disconnect() {
        this.showLoading(true);
        try {
            const result = await this.makeRequest('/api/disconnect', 'POST');
            if (result.success) {
                this.isConnected = false;
                this.isReading = false;
                this.updateConnectionUI();
                this.updateReadingUI();
                this.showMessage('connection-message', result.message, 'success');
                this.showToast('Disconnected successfully', 'success');
            } else {
                this.showMessage('connection-message', result.message, 'error');
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            this.showMessage('connection-message', 'Disconnection failed', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async updatePower(value) {
        document.getElementById('power-value').textContent = value;
        
        if (this.isConnected) {
            try {
                const result = await this.makeRequest('/api/power', 'POST', { power: parseInt(value) });
                if (!result.success) {
                    this.showToast(result.message, 'error');
                }
            } catch (error) {
                console.error('Power update failed:', error);
            }
        }
    }
    
    updatePowerValue() {
        const slider = document.getElementById('power-slider');
        document.getElementById('power-value').textContent = slider.value;
    }
    
    async startReading() {
        this.showLoading(true);
        try {
            const result = await this.makeRequest('/api/start', 'POST');
            if (result.success) {
                this.isReading = true;
                this.updateReadingUI();
                this.showMessage('reading-message', result.message, 'success');
                this.showToast('Reading started', 'success');
                this.startEPCUpdates();
            } else {
                this.showMessage('reading-message', result.message, 'error');
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            this.showMessage('reading-message', 'Failed to start reading', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async stopReading() {
        this.showLoading(true);
        try {
            const result = await this.makeRequest('/api/stop', 'POST');
            if (result.success) {
                this.isReading = false;
                this.updateReadingUI();
                this.showMessage('reading-message', result.message, 'success');
                this.showToast('Reading stopped', 'warning');
                this.stopEPCUpdates();
            } else {
                this.showMessage('reading-message', result.message, 'error');
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            this.showMessage('reading-message', 'Failed to stop reading', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async clearEPCs() {
        if (!confirm('Are you sure you want to clear all EPCs?')) {
            return;
        }
        
        this.showLoading(true);
        try {
            const result = await this.makeRequest('/api/clear', 'POST');
            if (result.success) {
                this.updateEPCList([]);
                document.getElementById('epc-count').textContent = '0';
                this.showToast('EPCs cleared', 'success');
            } else {
                this.showToast(result.message, 'error');
            }
        } catch (error) {
            this.showToast('Failed to clear EPCs', 'error');
        } finally {
            this.showLoading(false);
        }
    }
    
    async refreshEPCs() {
        try {
            const result = await this.makeRequest('/api/epcs');
            this.updateEPCList(result.epcs);
            this.showToast('EPCs refreshed', 'success');
        } catch (error) {
            this.showToast('Failed to refresh EPCs', 'error');
        }
    }
    
    exportEPCs() {
        const epcItems = document.querySelectorAll('.epc-item');
        if (epcItems.length === 0) {
            this.showToast('No EPCs to export', 'warning');
            return;
        }
        
        let csvContent = 'Timestamp,EPC\n';
        epcItems.forEach(item => {
            const timestamp = item.querySelector('.epc-timestamp').textContent;
            const epc = item.querySelector('.epc-code').textContent;
            csvContent += `${timestamp},${epc}\n`;
        });
        
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `rfid_epcs_${new Date().toISOString().slice(0, 10)}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        
        this.showToast('EPCs exported successfully', 'success');
    }
    
    updateConnectionUI() {
        const connectBtn = document.getElementById('connect-btn');
        const disconnectBtn = document.getElementById('disconnect-btn');
        const startBtn = document.getElementById('start-btn');
        const statusElement = document.getElementById('connection-status');
        
        if (this.isConnected) {
            connectBtn.disabled = true;
            disconnectBtn.disabled = false;
            startBtn.disabled = false;
            statusElement.className = 'status connected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Connected';
        } else {
            connectBtn.disabled = false;
            disconnectBtn.disabled = true;
            startBtn.disabled = true;
            statusElement.className = 'status disconnected';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Disconnected';
        }
    }
    
    updateReadingUI() {
        const startBtn = document.getElementById('start-btn');
        const stopBtn = document.getElementById('stop-btn');
        const statusElement = document.getElementById('connection-status');
        
        if (this.isReading) {
            startBtn.disabled = true;
            stopBtn.disabled = false;
            statusElement.className = 'status reading';
            statusElement.innerHTML = '<i class="fas fa-circle"></i> Reading...';
        } else {
            startBtn.disabled = !this.isConnected;
            stopBtn.disabled = true;
            if (this.isConnected) {
                statusElement.className = 'status connected';
                statusElement.innerHTML = '<i class="fas fa-circle"></i> Connected';
            }
        }
    }
    
    updateEPCList(epcs) {
        const epcList = document.getElementById('epc-list');
        
        if (epcs.length === 0) {
            epcList.innerHTML = '<div class="no-epcs">No EPCs detected yet. Start reading to see results.</div>';
            return;
        }
        
        const epcHTML = epcs.map(epc => `
            <div class="epc-item">
                <div class="epc-code">${epc.epc}</div>
                <div class="epc-timestamp">${epc.timestamp}</div>
            </div>
        `).join('');
        
        epcList.innerHTML = epcHTML;
    }
    
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    
    async updateStatus() {
        try {
            const status = await this.makeRequest('/api/status');
            
            // Update timer
            if (status.timer_running) {
                document.getElementById('timer-display').textContent = this.formatTime(status.elapsed_time);
            } else if (!this.isReading) {
                document.getElementById('timer-display').textContent = '00:00:00';
            }
            
            // Update EPC count
            document.getElementById('epc-count').textContent = status.epc_count.toString();
            
            // Update connection state if it changed
            if (this.isConnected !== status.reader_status.connected) {
                this.isConnected = status.reader_status.connected;
                this.updateConnectionUI();
            }
            
            // Update reading state if it changed
            if (this.isReading !== status.reader_status.reading) {
                this.isReading = status.reader_status.reading;
                this.updateReadingUI();
                
                if (this.isReading) {
                    this.startEPCUpdates();
                } else {
                    this.stopEPCUpdates();
                }
            }
            
        } catch (error) {
            console.error('Status update failed:', error);
        }
    }
    
    async updateEPCs() {
        try {
            const result = await this.makeRequest('/api/epcs');
            this.updateEPCList(result.epcs);
        } catch (error) {
            console.error('EPC update failed:', error);
        }
    }
    
    startStatusUpdates() {
        this.updateStatus(); // Initial update
        this.statusInterval = setInterval(() => this.updateStatus(), 1000);
    }
    
    startEPCUpdates() {
        if (this.epcInterval) return; // Already running
        this.epcInterval = setInterval(() => this.updateEPCs(), 1000);
    }
    
    stopEPCUpdates() {
        if (this.epcInterval) {
            clearInterval(this.epcInterval);
            this.epcInterval = null;
        }
    }
    
    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        if (show) {
            overlay.classList.remove('hidden');
        } else {
            overlay.classList.add('hidden');
        }
    }
    
    showMessage(elementId, message, type) {
        const element = document.getElementById(elementId);
        element.textContent = message;
        element.className = `message ${type}`;
        element.style.display = 'block';
        
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
    
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        }[type] || 'fas fa-info-circle';
        
        toast.innerHTML = `
            <i class="${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
        
        // Allow manual removal by clicking
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new RFIDWebApp();
});