#!/usr/bin/env python3
"""
Reference Desktop RFID Reader Application using Tkinter
This serves as a baseline for the functionality to be implemented in the web version.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
from datetime import datetime
from typing import Set, List


class MockRFIDReader:
    """Mock RFID Reader to simulate hardware functionality"""
    
    def __init__(self):
        self.connected = False
        self.antenna_power = 50  # Power level 0-100
        self.reading = False
        self.epcs_found: Set[str] = set()
        
    def connect(self) -> bool:
        """Simulate connection to RFID reader"""
        time.sleep(1)  # Simulate connection delay
        self.connected = True
        return True
        
    def disconnect(self):
        """Disconnect from RFID reader"""
        self.connected = False
        self.reading = False
        
    def set_antenna_power(self, power: int) -> bool:
        """Set antenna power level (0-100)"""
        if not self.connected:
            return False
        self.antenna_power = max(0, min(100, power))
        return True
        
    def start_reading(self) -> bool:
        """Start RFID reading process"""
        if not self.connected:
            return False
        self.reading = True
        return True
        
    def stop_reading(self) -> bool:
        """Stop RFID reading process"""
        if not self.connected:
            return False
        self.reading = False
        return True
        
    def get_new_epcs(self) -> List[str]:
        """Simulate reading new EPCs"""
        if not self.reading:
            return []
            
        # Randomly generate new EPCs
        new_epcs = []
        if random.random() < 0.3:  # 30% chance of finding new EPC
            epc = f"E200{random.randint(1000, 9999):04d}{random.randint(1000, 9999):04d}{random.randint(1000, 9999):04d}"
            if epc not in self.epcs_found:
                self.epcs_found.add(epc)
                new_epcs.append(epc)
                
        return new_epcs


class RFIDReaderApp:
    """Desktop RFID Reader Application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("RFID Reader Application")
        self.root.geometry("800x600")
        
        # Initialize RFID reader
        self.rfid_reader = MockRFIDReader()
        
        # Application state
        self.unique_epcs: Set[str] = set()
        self.start_time = None
        self.timer_running = False
        
        # Create GUI
        self.create_widgets()
        
        # Start timer update thread
        self.timer_thread = threading.Thread(target=self.update_timer, daemon=True)
        self.timer_thread.start()
        
        # Start EPC reading thread
        self.reading_thread = threading.Thread(target=self.epc_reading_loop, daemon=True)
        self.reading_thread.start()
        
    def create_widgets(self):
        """Create the GUI widgets"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding="5")
        conn_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.connect_btn = ttk.Button(conn_frame, text="Connect", command=self.connect_reader)
        self.connect_btn.grid(row=0, column=0, padx=5)
        
        self.disconnect_btn = ttk.Button(conn_frame, text="Disconnect", command=self.disconnect_reader, state="disabled")
        self.disconnect_btn.grid(row=0, column=1, padx=5)
        
        self.status_label = ttk.Label(conn_frame, text="Status: Disconnected")
        self.status_label.grid(row=0, column=2, padx=20)
        
        # Antenna power frame
        power_frame = ttk.LabelFrame(main_frame, text="Antenna Power", padding="5")
        power_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(power_frame, text="Power Level:").grid(row=0, column=0, padx=5)
        
        self.power_var = tk.IntVar(value=50)
        self.power_scale = ttk.Scale(power_frame, from_=0, to=100, variable=self.power_var, 
                                   orient=tk.HORIZONTAL, length=200, command=self.update_power)
        self.power_scale.grid(row=0, column=1, padx=5)
        
        self.power_label = ttk.Label(power_frame, text="50%")
        self.power_label.grid(row=0, column=2, padx=5)
        
        # Reading control frame
        read_frame = ttk.LabelFrame(main_frame, text="Reading Control", padding="5")
        read_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.start_btn = ttk.Button(read_frame, text="Start Reading", command=self.start_reading, state="disabled")
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.stop_btn = ttk.Button(read_frame, text="Stop Reading", command=self.stop_reading, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=5)
        
        self.clear_btn = ttk.Button(read_frame, text="Clear EPCs", command=self.clear_epcs)
        self.clear_btn.grid(row=0, column=2, padx=5)
        
        # Timer frame
        timer_frame = ttk.LabelFrame(main_frame, text="Timer", padding="5")
        timer_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)
        
        self.timer_label = ttk.Label(timer_frame, text="00:00:00", font=("Arial", 16))
        self.timer_label.grid(row=0, column=0)
        
        # EPC count frame
        count_frame = ttk.LabelFrame(main_frame, text="EPC Count", padding="5")
        count_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
        
        self.count_label = ttk.Label(count_frame, text="0", font=("Arial", 16))
        self.count_label.grid(row=0, column=0)
        
        # EPC display frame
        epc_frame = ttk.LabelFrame(main_frame, text="Unique EPCs", padding="5")
        epc_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.epc_text = scrolledtext.ScrolledText(epc_frame, height=15, width=70)
        self.epc_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        epc_frame.columnconfigure(0, weight=1)
        epc_frame.rowconfigure(0, weight=1)
        
    def connect_reader(self):
        """Connect to RFID reader"""
        try:
            if self.rfid_reader.connect():
                self.status_label.config(text="Status: Connected")
                self.connect_btn.config(state="disabled")
                self.disconnect_btn.config(state="normal")
                self.start_btn.config(state="normal")
                messagebox.showinfo("Success", "Connected to RFID reader")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")
            
    def disconnect_reader(self):
        """Disconnect from RFID reader"""
        self.rfid_reader.disconnect()
        self.status_label.config(text="Status: Disconnected")
        self.connect_btn.config(state="normal")
        self.disconnect_btn.config(state="disabled")
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="disabled")
        self.timer_running = False
        
    def update_power(self, value=None):
        """Update antenna power"""
        power = int(self.power_var.get())
        self.power_label.config(text=f"{power}%")
        if self.rfid_reader.connected:
            self.rfid_reader.set_antenna_power(power)
            
    def start_reading(self):
        """Start RFID reading"""
        if self.rfid_reader.start_reading():
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.start_time = time.time()
            self.timer_running = True
            
    def stop_reading(self):
        """Stop RFID reading"""
        if self.rfid_reader.stop_reading():
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.timer_running = False
            
    def clear_epcs(self):
        """Clear all EPCs"""
        self.unique_epcs.clear()
        self.rfid_reader.epcs_found.clear()
        self.epc_text.delete(1.0, tk.END)
        self.count_label.config(text="0")
        
    def update_timer(self):
        """Update timer display"""
        while True:
            if self.timer_running and self.start_time:
                elapsed = time.time() - self.start_time
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                timer_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                self.timer_label.config(text=timer_text)
            time.sleep(1)
            
    def epc_reading_loop(self):
        """Continuously check for new EPCs"""
        while True:
            if self.rfid_reader.reading:
                new_epcs = self.rfid_reader.get_new_epcs()
                for epc in new_epcs:
                    if epc not in self.unique_epcs:
                        self.unique_epcs.add(epc)
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.epc_text.insert(tk.END, f"[{timestamp}] {epc}\n")
                        self.epc_text.see(tk.END)
                        self.count_label.config(text=str(len(self.unique_epcs)))
            time.sleep(0.5)


def main():
    """Main application entry point"""
    root = tk.Tk()
    app = RFIDReaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()