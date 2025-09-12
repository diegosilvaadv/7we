#!/usr/bin/env python3
"""
RFID Reader Desktop Application
A Python/Tkinter application for reading RFID tags over network connection.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import socket
import threading
import time
import json
from datetime import datetime
from typing import Set, Dict, Any, Optional


class RFIDReaderApp:
    """Main application class for RFID Reader Desktop App."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Reader Desktop App")
        self.root.geometry("800x600")
        
        # Application state
        self.connected = False
        self.reading = False
        self.socket_connection: Optional[socket.socket] = None
        self.reader_thread: Optional[threading.Thread] = None
        self.unique_epcs: Set[str] = set()
        self.start_time: Optional[datetime] = None
        self.antenna_power = 30  # Default power level (dBm)
        
        # Network settings
        self.reader_host = tk.StringVar(value="192.168.1.100")
        self.reader_port = tk.IntVar(value=8080)
        
        # Timer variables
        self.elapsed_time = tk.StringVar(value="00:00:00")
        
        self.setup_ui()
        self.update_timer()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection Settings", padding="10")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(conn_frame, text="Host:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(conn_frame, textvariable=self.reader_host, width=20).grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky=tk.W)
        ttk.Entry(conn_frame, textvariable=self.reader_port, width=10).grid(row=0, column=3, padx=(5, 10))
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.toggle_connection)
        self.connect_btn.grid(row=0, column=4, padx=(10, 0))
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Reader Controls", padding="10")
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Antenna power control
        ttk.Label(control_frame, text="Antenna Power (dBm):").grid(row=0, column=0, sticky=tk.W)
        self.power_scale = ttk.Scale(control_frame, from_=10, to=30, value=self.antenna_power,
                                   orient=tk.HORIZONTAL, length=200, command=self.update_power)
        self.power_scale.grid(row=0, column=1, padx=(5, 10))
        
        self.power_label = ttk.Label(control_frame, text=f"{self.antenna_power} dBm")
        self.power_label.grid(row=0, column=2)
        
        # Start/Stop buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=(10, 0))
        
        self.start_btn = ttk.Button(button_frame, text="Start Reading", command=self.start_reading)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Reading", command=self.stop_reading, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        ttk.Label(status_frame, text="Timer:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(status_frame, textvariable=self.elapsed_time, font=("Arial", 12, "bold")).grid(row=0, column=1, sticky=tk.W)
        
        ttk.Label(status_frame, text="Unique EPCs:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.epc_count_label = ttk.Label(status_frame, text="0", font=("Arial", 12, "bold"))
        self.epc_count_label.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
        # EPC display frame
        epc_frame = ttk.LabelFrame(main_frame, text="Detected EPCs", padding="10")
        epc_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.epc_text = scrolledtext.ScrolledText(epc_frame, width=40, height=20)
        self.epc_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def update_power(self, value):
        """Update antenna power setting."""
        self.antenna_power = int(float(value))
        self.power_label.config(text=f"{self.antenna_power} dBm")
        
        if self.connected:
            self.send_command({"command": "set_power", "power": self.antenna_power})
    
    def toggle_connection(self):
        """Toggle connection to RFID reader."""
        if self.connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        """Connect to RFID reader."""
        try:
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.settimeout(5)
            
            host = self.reader_host.get()
            port = self.reader_port.get()
            
            self.socket_connection.connect((host, port))
            
            # Send initial configuration
            self.send_command({"command": "set_power", "power": self.antenna_power})
            
            self.connected = True
            self.connect_btn.config(text="Disconnect")
            self.status_label.config(text="Connected", foreground="green")
            
            messagebox.showinfo("Success", f"Connected to RFID reader at {host}:{port}")
            
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {str(e)}")
            if self.socket_connection:
                self.socket_connection.close()
                self.socket_connection = None
    
    def disconnect(self):
        """Disconnect from RFID reader."""
        if self.reading:
            self.stop_reading()
        
        if self.socket_connection:
            try:
                self.socket_connection.close()
            except:
                pass
            self.socket_connection = None
        
        self.connected = False
        self.connect_btn.config(text="Connect")
        self.status_label.config(text="Disconnected", foreground="red")
    
    def send_command(self, command: Dict[str, Any]):
        """Send command to RFID reader."""
        if self.socket_connection:
            try:
                message = json.dumps(command) + '\n'
                self.socket_connection.send(message.encode())
            except Exception as e:
                messagebox.showerror("Communication Error", f"Failed to send command: {str(e)}")
                self.disconnect()
    
    def start_reading(self):
        """Start RFID reading process."""
        if not self.connected:
            messagebox.showwarning("Not Connected", "Please connect to an RFID reader first.")
            return
        
        self.reading = True
        self.start_time = datetime.now()
        self.unique_epcs.clear()
        self.epc_text.delete(1.0, tk.END)
        self.update_epc_count()
        
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Send start reading command
        self.send_command({"command": "start_reading"})
        
        # Start reader thread
        self.reader_thread = threading.Thread(target=self.read_epcs, daemon=True)
        self.reader_thread.start()
    
    def stop_reading(self):
        """Stop RFID reading process."""
        self.reading = False
        
        # Send stop reading command
        if self.connected:
            self.send_command({"command": "stop_reading"})
        
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def read_epcs(self):
        """Read EPCs from RFID reader in separate thread."""
        if not self.socket_connection:
            return
        
        try:
            while self.reading and self.connected:
                # In a real implementation, this would receive data from the RFID reader
                # For demo purposes, we'll simulate receiving EPC data
                time.sleep(1)
                
                # Simulate receiving EPC data (in real app, parse from socket)
                if self.reading:
                    # This is simulation - in real app, parse actual RFID reader protocol
                    import random
                    simulated_epc = f"E200{random.randint(1000, 9999):04d}{random.randint(10000000, 99999999):08d}"
                    
                    if random.random() < 0.3:  # 30% chance of new EPC
                        self.process_epc(simulated_epc)
                        
        except Exception as e:
            if self.reading:
                self.root.after(0, lambda: messagebox.showerror("Reading Error", f"Error reading EPCs: {str(e)}"))
                self.root.after(0, self.stop_reading)
    
    def process_epc(self, epc: str):
        """Process a received EPC."""
        if epc not in self.unique_epcs:
            self.unique_epcs.add(epc)
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Update UI in main thread
            self.root.after(0, lambda: self.add_epc_to_display(epc, timestamp))
            self.root.after(0, self.update_epc_count)
    
    def add_epc_to_display(self, epc: str, timestamp: str):
        """Add EPC to display area."""
        self.epc_text.insert(tk.END, f"[{timestamp}] {epc}\n")
        self.epc_text.see(tk.END)
    
    def update_epc_count(self):
        """Update EPC count display."""
        self.epc_count_label.config(text=str(len(self.unique_epcs)))
    
    def update_timer(self):
        """Update the elapsed time timer."""
        if self.start_time and self.reading:
            elapsed = datetime.now() - self.start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.elapsed_time.set(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        elif not self.reading:
            self.elapsed_time.set("00:00:00")
        
        # Schedule next update
        self.root.after(1000, self.update_timer)
    
    def on_closing(self):
        """Handle application closing."""
        if self.reading:
            self.stop_reading()
        if self.connected:
            self.disconnect()
        self.root.destroy()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = RFIDReaderApp(root)
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()