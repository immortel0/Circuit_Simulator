# transient_monitor.py

"""
Transient analysis monitor with Laplace-based time-domain trajectories
Shows voltage and current vs time for all components
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from laplace_solver import solve_circuit_transient


class TransientMonitor:
    """
    Transient analysis window showing voltage/current trajectories
    Uses Laplace domain analysis to generate time-domain plots
    """
    
    def __init__(self, parent, components_list):
        self.window = tk.Toplevel(parent)
        self.window.title("Transient Analysis - Time Domain Trajectories")
        self.window.geometry("1400x800")
        
        self.components = components_list
        self.solver = None
        self.colors = plt.cm.tab10(np.linspace(0, 1, 10))  # Color palette
        
        self.create_widgets()
        self.run_analysis()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Top control panel
        control_frame = tk.Frame(self.window, bg="#2c3e50", pady=15)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        
        tk.Label(control_frame, text="⚡ Transient Analysis", 
                font=("Arial", 14, "bold"), bg="#2c3e50", fg="white").pack(side=tk.LEFT, padx=20)
        
        # Time range control
        time_frame = tk.Frame(control_frame, bg="#2c3e50")
        time_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(time_frame, text="Max Time:", 
                font=("Arial", 10), bg="#2c3e50", fg="white").pack(side=tk.LEFT, padx=5)
        
        self.time_var = tk.StringVar(value="100")
        self.time_entry = tk.Entry(time_frame, textvariable=self.time_var, width=12)
        self.time_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(time_frame, text="s", 
                font=("Arial", 9), bg="#2c3e50", fg="#bdc3c7").pack(side=tk.LEFT)
        
        # Points control
        points_frame = tk.Frame(control_frame, bg="#2c3e50")
        points_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(points_frame, text="Points:", 
                font=("Arial", 10), bg="#2c3e50", fg="white").pack(side=tk.LEFT, padx=5)
        
        self.points_var = tk.StringVar(value="500")
        self.points_entry = tk.Entry(points_frame, textvariable=self.points_var, width=8)
        self.points_entry.pack(side=tk.LEFT, padx=5)
        
        # Analyze button
        tk.Button(
            control_frame,
            text="Re-analyze",
            command=self.run_analysis,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=20)
        
        # Export button
        tk.Button(
            control_frame,
            text="Export Data",
            command=self.export_data,
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(control_frame, text="Status: Ready", 
                                     font=("Arial", 10), bg="#2c3e50", fg="#ecf0f1")
        self.status_label.pack(side=tk.RIGHT, padx=20)
        
        # Main plot area with two subplots
        plot_frame = tk.Frame(self.window, bg="white")
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.fig = Figure(figsize=(14, 7), dpi=100)
        self.fig.patch.set_facecolor('#ecf0f1')
        
        # Create two subplots: voltage and current
        self.ax_voltage = self.fig.add_subplot(211)
        self.ax_current = self.fig.add_subplot(212)
        
        # Style voltage plot
        self.ax_voltage.set_title("Voltage vs Time", fontsize=13, fontweight='bold', pad=10)
        self.ax_voltage.set_xlabel("Time (s)", fontsize=11)
        self.ax_voltage.set_ylabel("Voltage (V)", fontsize=11)
        self.ax_voltage.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
        self.ax_voltage.set_facecolor('#ffffff')
        
        # Style current plot
        self.ax_current.set_title("Current vs Time", fontsize=13, fontweight='bold', pad=10)
        self.ax_current.set_xlabel("Time (s)", fontsize=11)
        self.ax_current.set_ylabel("Current (A)", fontsize=11)
        self.ax_current.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
        self.ax_current.set_facecolor('#ffffff')
        
        self.fig.tight_layout(pad=3.0)
        
        # Canvas for matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Info panel at bottom
        info_frame = tk.LabelFrame(self.window, text="Circuit Components & Analysis Info", 
                                   font=("Arial", 10, "bold"), bg="#ecf0f1")
        info_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.info_text = tk.Text(info_frame, height=6, font=("Courier New", 9), 
                                bg="#ffffff", wrap=tk.WORD)
        scrollbar = tk.Scrollbar(info_frame, command=self.info_text.yview)
        self.info_text.config(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def run_analysis(self):
        """Run transient analysis and plot results"""
        try:
            # Update status
            self.status_label.config(text="Status: Analyzing...", fg="#f39c12")
            self.window.update()
            
            # Get parameters
            time_str = self.time_var.get()
            t_max = None if time_str.lower() == "auto" else float(time_str)
            num_points = int(self.points_var.get())
            
            # Run Laplace solver
            self.solver = solve_circuit_transient(
                self.components, 
                t_max=t_max, 
                num_points=num_points
            )
            
            # Clear previous plots
            self.ax_voltage.clear()
            self.ax_current.clear()
            
            # Plot trajectories for each component
            for idx, wrapper in enumerate(self.components):
                comp = wrapper.component
                comp_type = type(comp).__name__
                color = self.colors[idx % len(self.colors)]
                
                # Get label
                if comp_type == 'Resistor':
                    label = f"R{idx} ({comp.property}Ω)"
                elif comp_type == 'Voltage_Source':
                    label = f"VS{idx} ({comp.voltage}V)"
                elif comp_type == 'Current_Source':
                    label = f"CS{idx} ({comp.current}A)"
                elif comp_type == 'Capacitor':
                    label = f"C{idx} ({self.format_value(comp.property)}F)"
                elif comp_type == 'Inductor':
                    label = f"L{idx} ({self.format_value(comp.property)}H)"
                else:
                    label = f"{comp_type}{idx}"
                
                # Plot voltage (magnitude)
                if idx in self.solver.voltage_trajectories:
                    v_data = np.abs(self.solver.voltage_trajectories[idx])  # Use magnitude
                    self.ax_voltage.plot(
                        self.solver.time_points, v_data,
                        label=label, color=color, linewidth=2, alpha=0.8
                    )
                
                # Plot current
                if idx in self.solver.current_trajectories:
                    i_data = self.solver.current_trajectories[idx]
                    self.ax_current.plot(
                        self.solver.time_points, i_data,
                        label=label, color=color, linewidth=2, alpha=0.8
                    )
            
            # Re-apply styling
            self.ax_voltage.set_title("Voltage Magnitude vs Time", fontsize=13, fontweight='bold', pad=10)
            self.ax_voltage.set_xlabel("Time (s)", fontsize=11)
            self.ax_voltage.set_ylabel("|Voltage| (V)", fontsize=11)
            self.ax_voltage.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
            self.ax_voltage.set_facecolor('#ffffff')
            self.ax_voltage.legend(loc='best', fontsize=9, framealpha=0.9)
            
            self.ax_current.set_title("Current vs Time", fontsize=13, fontweight='bold', pad=10)
            self.ax_current.set_xlabel("Time (s)", fontsize=11)
            self.ax_current.set_ylabel("Current (A)", fontsize=11)
            self.ax_current.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
            self.ax_current.set_facecolor('#ffffff')
            self.ax_current.legend(loc='best', fontsize=9, framealpha=0.9)
            
            self.fig.tight_layout(pad=3.0)
            self.canvas.draw()
            
            # Update info panel
            self.update_info_panel()
            
            # Update status
            self.status_label.config(text="Status: Analysis Complete ✓", fg="#27ae60")
            
        except Exception as e:
            messagebox.showerror("Analysis Error", f"Failed to analyze circuit:\n{str(e)}")
            self.status_label.config(text="Status: Error ✗", fg="#e74c3c")
    
    def update_info_panel(self):
        """Update the information panel with circuit details"""
        self.info_text.delete(1.0, tk.END)
        
        if self.solver is None:
            return
        
        # Circuit analysis info
        order, has_cap, has_ind = self.solver.analyze_circuit_type()
        tau = self.solver.compute_time_constant()
        
        info = []
        info.append("=" * 80)
        info.append("TRANSIENT ANALYSIS RESULTS")
        info.append("=" * 80)
        info.append("")
        
        # Circuit type
        if order == 0:
            circuit_type = "Purely Resistive (No transient response)"
        elif order == 1:
            if has_cap:
                circuit_type = "First-Order RC Circuit"
            else:
                circuit_type = "First-Order RL Circuit"
        else:
            circuit_type = "Second-Order RLC Circuit"
        
        info.append(f"Circuit Type: {circuit_type}")
        info.append(f"Order: {order}")
        
        # Check if resistors present
        params = self.solver.get_circuit_parameters()
        has_resistors = len(params['resistors']) > 0
        
        if not has_resistors and (has_cap or has_ind):
            info.append(f"Note: No resistors detected - using internal resistance (0.01Ω)")
        
        info.append(f"Time Constant (τ): {tau:.6e} seconds")
        info.append(f"Settling Time (≈5τ): {5*tau:.6e} seconds")
        info.append(f"Simulation Time: {self.solver.time_points[-1]:.6e} seconds")
        info.append(f"Number of Points: {len(self.solver.time_points)}")
        info.append(f"Plot Display: Voltage MAGNITUDE (|V|) - all positive values")
        info.append("")
        
        # Component details
        info.append("COMPONENTS:")
        for idx, wrapper in enumerate(self.components):
            comp = wrapper.component
            comp_type = type(comp).__name__
            
            if comp_type == 'Resistor':
                info.append(f"  [{idx}] Resistor: R = {comp.property} Ω")
            elif comp_type == 'Voltage_Source':
                info.append(f"  [{idx}] Voltage Source: V = {comp.voltage} V")
            elif comp_type == 'Current_Source':
                info.append(f"  [{idx}] Current Source: I = {comp.current} A")
            elif comp_type == 'Capacitor':
                info.append(f"  [{idx}] Capacitor: C = {comp.property} F ({self.format_value(comp.property)}F)")
            elif comp_type == 'Inductor':
                info.append(f"  [{idx}] Inductor: L = {comp.property} H ({self.format_value(comp.property)}H)")
        
        info.append("")
        info.append("=" * 80)
        info.append("TIP: Use right-click on components to edit values, then re-analyze")
        info.append("=" * 80)
        
        self.info_text.insert(1.0, "\n".join(info))
    
    def format_value(self, value):
        """Format component values with appropriate units"""
        if value >= 1:
            return f"{value:.3f}"
        elif value >= 1e-3:
            return f"{value*1e3:.3f}m"
        elif value >= 1e-6:
            return f"{value*1e6:.3f}µ"
        elif value >= 1e-9:
            return f"{value*1e9:.3f}n"
        elif value >= 1e-12:
            return f"{value*1e12:.3f}p"
        else:
            return f"{value:.3e}"
    
    def export_data(self):
        """Export trajectory data to CSV file"""
        try:
            if self.solver is None:
                messagebox.showwarning("No Data", "Run analysis first before exporting.")
                return
            
            from tkinter import filedialog
            
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export Trajectory Data"
            )
            
            if not filename:
                return
            
            # Create CSV content
            with open(filename, 'w') as f:
                # Header
                headers = ["Time (s)"]
                for idx, wrapper in enumerate(self.components):
                    comp_type = type(wrapper.component).__name__
                    headers.append(f"V_{comp_type}{idx} (V)")
                    headers.append(f"I_{comp_type}{idx} (A)")
                
                f.write(",".join(headers) + "\n")
                
                # Data rows
                for t_idx, t in enumerate(self.solver.time_points):
                    row = [f"{t:.6e}"]
                    
                    for idx in range(len(self.components)):
                        if idx in self.solver.voltage_trajectories:
                            v = self.solver.voltage_trajectories[idx][t_idx]
                            row.append(f"{v:.6e}")
                        else:
                            row.append("0")
                        
                        if idx in self.solver.current_trajectories:
                            i = self.solver.current_trajectories[idx][t_idx]
                            row.append(f"{i:.6e}")
                        else:
                            row.append("0")
                    
                    f.write(",".join(row) + "\n")
            
            messagebox.showinfo("Export Success", f"Data exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export data:\n{str(e)}")


def show_transient_analysis(parent, components_list):
    """
    Convenience function to show transient analysis window
    
    Args:
        parent: Parent tkinter window
        components_list: List of component wrappers
    """
    if not components_list:
        messagebox.showwarning("No Components", 
                             "Please add components to the circuit before running transient analysis.")
        return
    
    TransientMonitor(parent, components_list)
