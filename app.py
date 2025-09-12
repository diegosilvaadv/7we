#!/usr/bin/env python3
"""
Web-based RFID Reader Application using Flask
This replaces the desktop tkinter version with a web interface.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import time
import random
from datetime import datetime
from typing import Set, List, Dict, Optional
import json


class MockRFIDReader:
    """Mock RFID Reader to simulate hardware functionality"""
    
    def __init__(self):
        self.connected = False
        self.antenna_power = 50  # Power level 0-100
        self.reading = False
        self.epcs_found: Set[str] = set()
        self._lock = threading.Lock()
        
    def connect(self) -> bool:
        """Simulate connection to RFID reader"""
        time.sleep(1)  # Simulate connection delay
        with self._lock:
            self.connected = True
        return True
        
    def disconnect(self):
        """Disconnect from RFID reader"""
        with self._lock:
            self.connected = False
            self.reading = False
        
    def set_antenna_power(self, power: int) -> bool:
        """Set antenna power level (0-100)"""
        with self._lock:
            if not self.connected:
                return False
            self.antenna_power = max(0, min(100, power))
        return True
        
    def start_reading(self) -> bool:
        """Start RFID reading process"""
        with self._lock:
            if not self.connected:
                return False
            self.reading = True
        return True
        
    def stop_reading(self) -> bool:
        """Stop RFID reading process"""
        with self._lock:
            if not self.connected:
                return False
            self.reading = False
        return True
        
    def get_new_epcs(self) -> List[str]:
        """Simulate reading new EPCs"""
        with self._lock:
            if not self.reading:
                return []
                
        # Randomly generate new EPCs
        new_epcs = []
        if random.random() < 0.2:  # 20% chance of finding new EPC
            epc = f"E200{random.randint(1000, 9999):04d}{random.randint(1000, 9999):04d}{random.randint(1000, 9999):04d}"
            with self._lock:
                if epc not in self.epcs_found:
                    self.epcs_found.add(epc)
                    new_epcs.append(epc)
                
        return new_epcs
    
    def get_status(self) -> Dict:
        """Get current reader status"""
        with self._lock:
            return {
                'connected': self.connected,
                'reading': self.reading,
                'antenna_power': self.antenna_power,
                'epc_count': len(self.epcs_found)
            }


class RFIDWebApp:
    """Web-based RFID Reader Application"""
    
    def __init__(self):
        self.rfid_reader = MockRFIDReader()
        self.unique_epcs: List[Dict] = []  # List of {epc, timestamp} dicts
        self.start_time: Optional[float] = None
        self.timer_running = False
        self._epc_lock = threading.Lock()
        
        # Start EPC reading thread
        self.reading_thread = threading.Thread(target=self.epc_reading_loop, daemon=True)
        self.reading_thread.start()
        
    def connect_reader(self) -> Dict:
        """Connect to RFID reader"""
        try:
            success = self.rfid_reader.connect()
            return {'success': success, 'message': 'Connected successfully' if success else 'Connection failed'}
        except Exception as e:
            return {'success': False, 'message': f'Connection error: {str(e)}'}
            
    def disconnect_reader(self) -> Dict:
        """Disconnect from RFID reader"""
        try:
            self.rfid_reader.disconnect()
            self.timer_running = False
            self.start_time = None
            return {'success': True, 'message': 'Disconnected successfully'}
        except Exception as e:
            return {'success': False, 'message': f'Disconnection error: {str(e)}'}
            
    def set_antenna_power(self, power: int) -> Dict:
        """Set antenna power"""
        try:
            success = self.rfid_reader.set_antenna_power(power)
            return {'success': success, 'message': f'Power set to {power}%' if success else 'Failed to set power'}
        except Exception as e:
            return {'success': False, 'message': f'Power setting error: {str(e)}'}
            
    def start_reading(self) -> Dict:
        """Start RFID reading"""
        try:
            success = self.rfid_reader.start_reading()
            if success:
                self.start_time = time.time()
                self.timer_running = True
            return {'success': success, 'message': 'Reading started' if success else 'Failed to start reading'}
        except Exception as e:
            return {'success': False, 'message': f'Start reading error: {str(e)}'}
            
    def stop_reading(self) -> Dict:
        """Stop RFID reading"""
        try:
            success = self.rfid_reader.stop_reading()
            if success:
                self.timer_running = False
            return {'success': success, 'message': 'Reading stopped' if success else 'Failed to stop reading'}
        except Exception as e:
            return {'success': False, 'message': f'Stop reading error: {str(e)}'}
            
    def clear_epcs(self) -> Dict:
        """Clear all EPCs"""
        try:
            with self._epc_lock:
                self.unique_epcs.clear()
            self.rfid_reader.epcs_found.clear()
            return {'success': True, 'message': 'EPCs cleared'}
        except Exception as e:
            return {'success': False, 'message': f'Clear EPCs error: {str(e)}'}
            
    def get_status(self) -> Dict:
        """Get application status"""
        reader_status = self.rfid_reader.get_status()
        
        # Calculate elapsed time
        elapsed_time = 0
        if self.timer_running and self.start_time:
            elapsed_time = time.time() - self.start_time
            
        with self._epc_lock:
            epc_count = len(self.unique_epcs)
            
        return {
            'reader_status': reader_status,
            'elapsed_time': elapsed_time,
            'epc_count': epc_count,
            'timer_running': self.timer_running
        }
        
    def get_epcs(self) -> List[Dict]:
        """Get list of unique EPCs"""
        with self._epc_lock:
            return self.unique_epcs.copy()
            
    def epc_reading_loop(self):
        """Continuously check for new EPCs"""
        while True:
            try:
                new_epcs = self.rfid_reader.get_new_epcs()
                for epc in new_epcs:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    with self._epc_lock:
                        # Check if EPC already exists in our list
                        if not any(item['epc'] == epc for item in self.unique_epcs):
                            self.unique_epcs.append({
                                'epc': epc,
                                'timestamp': timestamp,
                                'datetime': datetime.now().isoformat()
                            })
                time.sleep(0.5)
            except Exception as e:
                print(f"Error in EPC reading loop: {e}")
                time.sleep(1)


# Initialize Flask app and RFID application
app = Flask(__name__)
CORS(app)
rfid_app = RFIDWebApp()


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/connect', methods=['POST'])
def api_connect():
    """API endpoint to connect to RFID reader"""
    result = rfid_app.connect_reader()
    return jsonify(result)


@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    """API endpoint to disconnect from RFID reader"""
    result = rfid_app.disconnect_reader()
    return jsonify(result)


@app.route('/api/power', methods=['POST'])
def api_set_power():
    """API endpoint to set antenna power"""
    data = request.get_json()
    power = data.get('power', 50)
    result = rfid_app.set_antenna_power(power)
    return jsonify(result)


@app.route('/api/start', methods=['POST'])
def api_start_reading():
    """API endpoint to start reading"""
    result = rfid_app.start_reading()
    return jsonify(result)


@app.route('/api/stop', methods=['POST'])
def api_stop_reading():
    """API endpoint to stop reading"""
    result = rfid_app.stop_reading()
    return jsonify(result)


@app.route('/api/clear', methods=['POST'])
def api_clear_epcs():
    """API endpoint to clear EPCs"""
    result = rfid_app.clear_epcs()
    return jsonify(result)


@app.route('/api/status', methods=['GET'])
def api_get_status():
    """API endpoint to get application status"""
    status = rfid_app.get_status()
    return jsonify(status)


@app.route('/api/epcs', methods=['GET'])
def api_get_epcs():
    """API endpoint to get EPCs"""
    epcs = rfid_app.get_epcs()
    return jsonify({'epcs': epcs})


if __name__ == '__main__':
    print("Starting RFID Web Application...")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)