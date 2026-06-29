# component_monitor.py

"""
Interactive component monitoring window with current vs time plotting
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from datetime import datetime
import threading
import time
from simple_circuit_solver import solve_circuit_simple


class ComponentMonitor:
    """
    Monitoring window for all components
    Shows current vs time for each component
    """
    
    def __init__(self, parent, components_list):
        self.window = tk.Toplevel(parent)
        self.window.title("Component Monitor - Current vs Time")
        self.window.geometry("1200x700")
        
        self.components = components_list
        self.monitoring = False
        
        # Data storage for plotting - one entry per component
        self.time_data = []
        self.component_data = {}  # {component_index: [currents]}
        self.max_points = 200
        self.start_time = time.time()
        
        # Initialize data structures for each component
        for i in range(len(self.components)):
            self.component_data[i] = []
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Top control panel
        control_frame = tk.Frame(self.window, bg="#f0f0f0", pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        tk.Label(control_frame, text="Circuit Current Monitor", 
                font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        
        # Frequency control
        tk.Label(control_frame, text="Frequency (Hz):", 
                font=("Arial", 10), bg="#f0f0f0").pack(side=tk.LEFT, padx=5)
        
        self.freq_var = tk.StringVar(value="0")
        self.freq_entry = tk.Entry(control_frame, textvariable=self.freq_var, width=10)
        self.freq_entry.pack(side=tk.LEFT, padx=5)
        
        # Monitor button
        self.monitor_btn = tk.Button(
            control_frame,
            text="Start Monitoring",
            command=self.toggle_monitoring,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20
        )
        self.monitor_btn.pack(side=tk.LEFT, padx=10)
        
        # Clear button
        tk.Button(
            control_frame,
            text="Clear Data",
            command=self.clear_data,
            font=("Arial", 10),
            padx=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Status: Idle | Mode: DC", 
                                     font=("Arial", 10), bg="#f0f0f0", fg="#666")
        self.status_label.pack(side=tk.LEFT, padx=20)
        
        # Matplotlib figure
        plot_frame = tk.Frame(self.window)
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.fig = Figure(figsize=(12, 6), dpi=100)
        self.fig.patch.set_facecolor('#f8f8f8')
        
        # Create single plot
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Current vs Time for All Components", fontsize=13, fontweight='bold')
        self.ax.set_xlabel("Time (s)", fontsize=11)
        self.ax.set_ylabel("Current (A)", fontsize=11)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_facecolor('#ffffff')
        
        self.fig.tight_layout(pad=2.0)
        
        # Canvas for matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Legend frame
        legend_frame = tk.LabelFrame(self.window, text="Components", 
                                     font=("Arial", 10, "bold"))
        legend_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        self.legend_text = tk.Text(legend_frame, height=4, font=("Courier", 9))
        self.legend_text.pack(fill=tk.BOTH, padx=5, pady=5)
        self.update_legend()
        
    def update_legend(self):
        """Update the legend showing component information"""
        self.legend_text.delete(1.0, tk.END)
        legend_info = []
        
        for i, comp_wrapper in enumerate(self.components):
            comp = comp_wrapper.component
            comp_type = comp.__class__.__name__
            
            if comp_type == 'Resistor':
                info = f"C{i}: {comp_type} ({comp.property}Ω)"
            elif comp_type == 'Voltage_Source':
                info = f"C{i}: {comp_type} ({comp.voltage}V)"
            elif comp_type == 'Current_Source':
                info = f"C{i}: {comp_type} ({comp.current}A)"
            elif comp_type == 'Capacitor':
                info = f"C{i}: {comp_type} ({comp.property}F)"
            elif comp_type == 'Inductor':
                info = f"C{i}: {comp_type} ({comp.property}H)"
            else:
                info = f"C{i}: {comp_type}"
            
            legend_info.append(info)
        
        self.legend_text.insert(1.0, "  |  ".join(legend_info))
    
    def toggle_monitoring(self):
        """Start/Stop monitoring"""
        self.monitoring = not self.monitoring
        
        if self.monitoring:
            try:
                self.frequency = float(self.freq_var.get())
            except ValueError:
                self.frequency = 0
                self.freq_var.set("0")
            
            mode = "DC" if self.frequency == 0 else f"AC ({self.frequency} Hz)"
            
            self.monitor_btn.config(text="Stop Monitoring", bg="#f44336")
            self.status_label.config(text=f"Status: Monitoring... | Mode: {mode}", fg="#4CAF50")
            self.start_time = time.time()
            self.clear_data()
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
        else:
            self.monitor_btn.config(text="Start Monitoring", bg="#4CAF50")
            self.status_label.config(text="Status: Stopped", fg="#f44336")
    
    def monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                self.update_data()
                time.sleep(0.5)  # Update every 0.5 seconds
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def update_data(self):
        """Update data and plots"""
        if not self.monitoring:
            return
        
        current_time = time.time() - self.start_time
        
        # Solve the circuit with frequency parameter
        try:
            solve_circuit_simple(self.components, frequency=self.frequency, time=current_time)
        except Exception as e:
            print(f"Circuit solve error: {e}")
            import traceback
            traceback.print_exc()
            return
        
        self.time_data.append(current_time)
        
        # Collect current for each component
        for i, comp_wrapper in enumerate(self.components):
            comp = comp_wrapper.component
            current = getattr(comp, 'current', 0)
            self.component_data[i].append(current)
        
        # Limit data points
        if len(self.time_data) > self.max_points:
            self.time_data.pop(0)
            for i in range(len(self.components)):
                if len(self.component_data[i]) > self.max_points:
                    self.component_data[i].pop(0)
        
        # Update plots (must be done in main thread)
        self.window.after(0, self.update_plots)
    
    def update_plots(self):
        """Update the matplotlib plot"""
        if not self.time_data:
            return
        
        # Clear previous plot
        self.ax.clear()
        
        # Plot data for each component with different colors
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                  '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        for i, comp_wrapper in enumerate(self.components):
            if i < len(self.component_data) and self.component_data[i]:
                comp = comp_wrapper.component
                comp_type = comp.__class__.__name__
                
                # Create label
                if comp_type == 'Resistor':
                    label = f"C{i}: {comp_type} ({comp.property}Ω)"
                elif comp_type == 'Voltage_Source':
                    label = f"C{i}: {comp_type} ({comp.voltage}V)"
                elif comp_type == 'Current_Source':
                    label = f"C{i}: {comp_type} ({comp.current}A)"
                elif comp_type == 'Capacitor':
                    label = f"C{i}: {comp_type} ({comp.property}F)"
                elif comp_type == 'Inductor':
                    label = f"C{i}: {comp_type} ({comp.property}H)"
                else:
                    label = f"C{i}: {comp_type}"
                
                color = colors[i % len(colors)]
                self.ax.plot(self.time_data, self.component_data[i], 
                           color=color, linewidth=2, marker='o', markersize=4,
                           label=label, alpha=0.8)
        
        # Restore styling
        self.ax.set_title("Current vs Time for All Components", fontsize=13, fontweight='bold')
        self.ax.set_xlabel("Time (s)", fontsize=11)
        self.ax.set_ylabel("Current (A)", fontsize=11)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_facecolor('#ffffff')
        self.ax.legend(loc='best', fontsize=9, framealpha=0.9)
        
        self.fig.tight_layout(pad=2.0)
        self.canvas.draw()
    
    def clear_data(self):
        """Clear all recorded data"""
        self.time_data = []
        for i in range(len(self.components)):
            self.component_data[i] = []
        self.start_time = time.time()
        
        # Clear plot
        self.ax.clear()
        self.ax.set_title("Current vs Time for All Components", fontsize=13, fontweight='bold')
        self.ax.set_xlabel("Time (s)", fontsize=11)
        self.ax.set_ylabel("Current (A)", fontsize=11)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_facecolor('#ffffff')
        
        self.canvas.draw()


def open_component_monitor(parent, components_list):
    """Open the component monitor window"""
    if not components_list:
        messagebox.showwarning("No Components", 
                              "Please add components to the circuit first!")
        return
    
    monitor = ComponentMonitor(parent, components_list)
