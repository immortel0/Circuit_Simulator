# simulator_integration.py

"""
Integration module to connect the GUI circuit simulator with 
circuit analysis (KCL/KVL using cutset and tieset matrices)
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
from circuit_analysis import Graph, CircuitEquations
from network import Node
import wiremanager as wm
from simple_circuit_solver import solve_circuit_simple
from component_monitor import open_component_monitor
from transient_monitor import show_transient_analysis


class AnalysisWindow:
    """
    Window to display circuit analysis results with KCL/KVL equations
    """
    
    def __init__(self, parent, graph, circuit_equations):
        self.window = tk.Toplevel(parent)
        self.window.title("Circuit Analysis - KCL/KVL Equations")
        self.window.geometry("800x600")
        
        self.graph = graph
        self.circuit_eqs = circuit_equations
        
        self.create_widgets()
        self.display_analysis()
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Title
        title = tk.Label(self.window, text="Circuit Analysis Results", 
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)
        
        # Tabs for different views
        notebook = tk.Frame(self.window)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create text area with scrollbar
        self.text_area = scrolledtext.ScrolledText(
            notebook, 
            wrap=tk.WORD, 
            width=90, 
            height=30,
            font=("Courier New", 10)
        )
        self.text_area.pack(fill="both", expand=True)
        
        # Buttons
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)
        
        solve_btn = tk.Button(button_frame, text="Solve Circuit", 
                              command=self.solve_and_display, 
                              font=("Arial", 11, "bold"),
                              bg="#4CAF50", fg="white", padx=20)
        solve_btn.grid(row=0, column=0, padx=5)
        
        export_btn = tk.Button(button_frame, text="Export Results", 
                               command=self.export_results,
                               font=("Arial", 11),
                               padx=20)
        export_btn.grid(row=0, column=1, padx=5)
        
        close_btn = tk.Button(button_frame, text="Close", 
                             command=self.window.destroy,
                             font=("Arial", 11),
                             padx=20)
        close_btn.grid(row=0, column=2, padx=5)
    
    def display_analysis(self):
        """Display the circuit analysis"""
        self.text_area.delete(1.0, tk.END)
        
        output = []
        output.append("="*70)
        output.append("CIRCUIT ANALYSIS - KCL AND KVL EQUATIONS")
        output.append("Using Cutset and Tieset Matrix Methods")
        output.append("="*70)
        output.append("")
        
        # Circuit topology
        output.append("CIRCUIT TOPOLOGY:")
        output.append(f"  Number of Nodes: {self.graph.get_num_nodes() + 1}")
        output.append(f"  Number of Branches: {self.graph.get_num_branches()}")
        output.append(f"  Reference Node: {self.graph.reference_node}")
        output.append("")
        
        # Branches
        output.append("BRANCHES:")
        for i, branch in enumerate(self.graph.branches):
            comp = branch['component']
            comp_type = comp.__class__.__name__
            from_n = branch['from_node']
            to_n = branch['to_node']
            output.append(f"  Branch {i}: {comp_type} from {from_n} to {to_n}")
        output.append("")
        
        # Incidence Matrix
        output.append("INCIDENCE MATRIX (A):")
        output.append("  Rows = Nodes (excluding reference), Columns = Branches")
        A = self.circuit_eqs.incidence_matrix.get_matrix()
        output.append(self._format_matrix(A))
        output.append("")
        
        # Cutset Matrix
        output.append("CUTSET MATRIX (Qf) - For KCL:")
        output.append("  Each row represents a fundamental cutset")
        Qf = self.circuit_eqs.cutset_matrix.get_matrix()
        output.append(self._format_matrix(Qf))
        output.append("")
        
        # Tieset Matrix
        output.append("TIESET MATRIX (Bf) - For KVL:")
        output.append("  Each row represents a fundamental loop")
        Bf = self.circuit_eqs.tieset_matrix.get_matrix()
        if Bf.shape[0] > 0:
            output.append(self._format_matrix(Bf))
        else:
            output.append("  (No loops - tree structure only)")
        output.append("")
        
        # KCL Equations
        output.append("KIRCHHOFF'S CURRENT LAW (KCL) EQUATIONS:")
        output.append("  (Using Cutset Matrix: Qf * I = 0)")
        for i, row in enumerate(Qf):
            terms = []
            for j, coeff in enumerate(row):
                if coeff != 0:
                    sign = '+' if coeff > 0 else ''
                    terms.append(f"{sign}{int(coeff)}*I{j}")
            if terms:
                output.append(f"  Node {i}: {' '.join(terms)} = 0")
        output.append("")
        
        # KVL Equations
        output.append("KIRCHHOFF'S VOLTAGE LAW (KVL) EQUATIONS:")
        output.append("  (Using Tieset Matrix: Bf * V = 0)")
        if Bf.shape[0] > 0:
            for i, row in enumerate(Bf):
                terms = []
                for j, coeff in enumerate(row):
                    if coeff != 0:
                        sign = '+' if coeff > 0 else ''
                        terms.append(f"{sign}{int(coeff)}*V{j}")
                if terms:
                    output.append(f"  Loop {i}: {' '.join(terms)} = 0")
        else:
            output.append("  (No independent loops)")
        output.append("")
        
        # Branch Equations
        output.append("BRANCH CONSTITUTIVE EQUATIONS:")
        branch_eqs = self.circuit_eqs.formulate_branch_equations()
        for eq in branch_eqs:
            branch_id = eq['branch_id']
            if eq['type'] == 'resistor':
                output.append(f"  Branch {branch_id}: V{branch_id} = {eq['resistance']}*I{branch_id}  (Resistor, R={eq['resistance']}Ω)")
            elif eq['type'] == 'voltage_source':
                output.append(f"  Branch {branch_id}: V{branch_id} = {eq['voltage']}V  (Voltage Source)")
            elif eq['type'] == 'capacitor':
                output.append(f"  Branch {branch_id}: I{branch_id} = 0  (Capacitor, DC steady state)")
            elif eq['type'] == 'inductor':
                output.append(f"  Branch {branch_id}: V{branch_id} = 0  (Inductor, DC steady state)")
        output.append("")
        
        output.append("="*70)
        output.append("Click 'Solve Circuit' to compute voltages and currents")
        output.append("="*70)
        
        # Display in text area
        self.text_area.insert(1.0, "\n".join(output))
    
    def solve_and_display(self):
        """Solve the circuit and display results"""
        try:
            # Use simple accurate solver instead
            components = wm.components
            results = solve_circuit_simple(components)
            
            if not results:
                self.text_area.insert(tk.END, "\n\nNo valid circuit to solve or solver error.\n")
                return
            
            # Append solution to text area
            self.text_area.insert(tk.END, "\n\n")
            self.text_area.insert(tk.END, "="*70 + "\n")
            self.text_area.insert(tk.END, "CIRCUIT SOLUTION (Nodal Analysis):\n")
            self.text_area.insert(tk.END, "="*70 + "\n\n")
            
            self.text_area.insert(tk.END, "COMPONENT VOLTAGES AND CURRENTS:\n")
            self.text_area.insert(tk.END, "-"*70 + "\n")
            
            total_power = 0
            for i, comp_wrapper in enumerate(components):
                comp = comp_wrapper.component
                comp_type = comp.__class__.__name__
                
                result = results.get(id(comp_wrapper), {'voltage': 0, 'current': 0})
                v = result['voltage']
                curr = result['current']
                power = v * curr
                total_power += power
                
                self.text_area.insert(tk.END, 
                    f"Component {i} ({comp_type:15s}): V = {v:8.4f}V,  I = {curr:10.6f}A,  P = {power:10.6f}W")
                
                if power > 0.001:
                    self.text_area.insert(tk.END, " (Absorbing)\n")
                elif power < -0.001:
                    self.text_area.insert(tk.END, " (Supplying)\n")
                else:
                    self.text_area.insert(tk.END, "\n")
            
            self.text_area.insert(tk.END, f"\nTotal Power (should be ≈0): {total_power:.9f}W\n")
            self.text_area.insert(tk.END, "="*70 + "\n")
            
            # Scroll to bottom
            self.text_area.see(tk.END)
            
            messagebox.showinfo("Success", "Circuit solved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to solve circuit:\n{str(e)}")
    
    def export_results(self):
        """Export analysis results to a text file"""
        try:
            filename = "circuit_analysis_results.txt"
            content = self.text_area.get(1.0, tk.END)
            
            with open(filename, 'w') as f:
                f.write(content)
            
            messagebox.showinfo("Export Successful", 
                              f"Results exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error: {str(e)}")
    
    def _format_matrix(self, matrix):
        """Format a matrix for display"""
        if matrix.size == 0:
            return "  (Empty matrix)"
        
        lines = []
        for row in matrix:
            formatted_row = "  [" + "  ".join(f"{val:6.2f}" for val in row) + "]"
            lines.append(formatted_row)
        return "\n".join(lines)


def analyze_simulator_circuit():
    """
    Analyze the current circuit in the simulator
    Called from the GUI to perform analysis
    """
    # Get components from wiremanager
    components = wm.components
    
    if len(components) == 0:
        messagebox.showwarning("No Circuit", "Please create a circuit first!")
        return
    
    # Build graph from simulator components
    graph = Graph()
    
    # Create node mapping from ports
    node_map = {}
    node_counter = 0
    
    def get_or_create_node(port):
        """Get or create a node for a port"""
        # Use port's parent and offset as unique identifier
        port_id = (id(port.parent), port.x_offset, port.y_offset)
        
        if port_id not in node_map:
            # Check if port is connected to other ports via wires
            # For now, create unique node for each port
            node = Node(f"N{node_counter}")
            node_map[port_id] = node
            return node
        return node_map[port_id]
    
    # Set reference node (ground)
    reference_node = Node("Ground")
    graph.set_reference_node(reference_node)
    
    # Add branches for each component
    for comp_wrapper in components:
        component = comp_wrapper.component
        
        # Get nodes from ports
        if hasattr(comp_wrapper, 'port1') and hasattr(comp_wrapper, 'port2'):
            node1 = get_or_create_node(comp_wrapper.port1)
            node2 = get_or_create_node(comp_wrapper.port2)
            
            # Add branch
            graph.add_branch(component, node1, node2)
    
    # If no ground connection, use first node as reference
    if graph.get_num_branches() == 0:
        messagebox.showwarning("Invalid Circuit", 
                              "Circuit has no valid connections!")
        return
    
    try:
        # Create circuit equations
        circuit_eqs = CircuitEquations(graph)
        circuit_eqs.build_matrices()
        
        # Create and show analysis window
        root = tk._default_root
        analysis_win = AnalysisWindow(root, graph, circuit_eqs)
        
    except Exception as e:
        messagebox.showerror("Analysis Error", 
                           f"Failed to analyze circuit:\n{str(e)}")


def add_analysis_menu(menu_bar, root):
    """
    Add circuit analysis menu to the main menu bar
    Call this from menu.py to integrate with GUI
    """
    analysis_menu = tk.Menu(menu_bar, tearoff=0)
    analysis_menu.add_command(label="Show KCL/KVL Equations", 
                             command=analyze_simulator_circuit)
    analysis_menu.add_separator()
    analysis_menu.add_command(label="Transient Analysis (Time Domain)", 
                             command=open_transient_window)
    analysis_menu.add_separator()
    menu_bar.add_cascade(label="Analysis", menu=analysis_menu)


def analyze_and_solve():
    """Analyze and immediately solve the circuit"""
    analyze_simulator_circuit()
    # The solution will be displayed when user clicks "Solve" button


def run_test_cases():
    """Run the test cases in a new window"""
    import subprocess
    import sys
    
    try:
        subprocess.Popen([sys.executable, "test_circuit_analysis.py"])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to run tests:\n{str(e)}")


def open_monitor_window():
    """Open the component monitor window"""
    components = wm.components
    root = tk._default_root
    open_component_monitor(root, components)


def open_transient_window():
    """Open the transient analysis window with Laplace-based trajectories"""
    components = wm.components
    root = tk._default_root
    show_transient_analysis(root, components)
