# simple_circuit_solver.py

"""
Simplified circuit solver using Modified Nodal Analysis (MNA)
Supports resistors, capacitors, inductors, voltage sources, and current sources
Ground is automatically assigned - no manual ground connection needed
"""

import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve


def solve_circuit_simple(components_list, frequency=0, time=0):
    """
    Solve circuit using Modified Nodal Analysis
    
    Parameters:
    - components_list: List of component wrappers from wiremanager
    - frequency: AC frequency in Hz (0 for DC)
    - time: Current time (for transient analysis)
    
    Returns:
    - dict with voltage and current for each component
    """
    
    if not components_list:
        return {}
    
    # Step 1: Build node connectivity using Union-Find
    parent = {}
    
    def find(x):
        if x not in parent:
            parent[x] = x
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    
    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py
    
    # Initialize all ports
    all_ports = []
    for comp in components_list:
        all_ports.extend([comp.port1, comp.port2])
    
    for port in all_ports:
        parent[id(port)] = id(port)
    
    # Union ports connected by wires
    for comp in components_list:
        for port in [comp.port1, comp.port2]:
            for wire in port.wires:
                other = wire.port2 if wire.port1 == port else wire.port1
                union(id(port), id(other))
    
    # Assign node numbers - find the node with most connections as ground
    # This ensures ground is automatically chosen
    node_connections = {}
    for port in all_ports:
        root = find(id(port))
        node_connections[root] = node_connections.get(root, 0) + 1
    
    # Ground is the node with most connections (or first node if tied)
    ground_root = max(node_connections.keys(), key=lambda k: node_connections[k])
    
    unique_nodes = {}
    unique_nodes[ground_root] = 0  # Ground is node 0
    node_count = 1
    for port in all_ports:
        root = find(id(port))
        if root not in unique_nodes:
            unique_nodes[root] = node_count
            node_count += 1
    
    def get_node(port):
        return unique_nodes[find(id(port))]
    
    # Step 2: Build component list with node info
    components = []
    voltage_sources = []
    current_sources = []
    
    for comp_wrapper in components_list:
        comp_obj = comp_wrapper.component
        comp_type = comp_obj.__class__.__name__
        
        node_p = get_node(comp_wrapper.port1)
        node_n = get_node(comp_wrapper.port2)
        
        comp_info = {
            'type': comp_type,
            'object': comp_obj,
            'wrapper': comp_wrapper,
            'node_p': node_p,
            'node_n': node_n
        }
        
        components.append(comp_info)
        
        if comp_type == 'Voltage_Source':
            voltage_sources.append(comp_info)
        elif comp_type == 'Current_Source':
            current_sources.append(comp_info)
    
    # Step 3: Set up MNA system
    # Variables: [V1, V2, ..., Vn, I_vs1, I_vs2, ...]
    # Ground is node 0
    n_nodes = node_count
    n_vs = len(voltage_sources)
    n_vars = (n_nodes - 1) + n_vs  # Node voltages (except ground) + VS currents
    
    if n_vars == 0:
        return {}
    
    G = lil_matrix((n_vars, n_vars), dtype=complex)
    b = np.zeros(n_vars, dtype=complex)
    
    omega = 2 * np.pi * frequency
    
    # Step 4: Fill matrix with component stamps
    for comp in components:
        comp_type = comp['type']
        node_p = comp['node_p']
        node_n = comp['node_n']
        obj = comp['object']
        
        # Skip if both nodes are ground
        if node_p == 0 and node_n == 0:
            continue
        
        # Calculate admittance based on component type
        if comp_type == 'Resistor':
            R = max(obj.property, 1e-12)
            Y = 1.0 / R
            
        elif comp_type == 'Capacitor':
            C = max(obj.property, 1e-15)
            if frequency == 0:
                Y = 0  # Open circuit in DC
            else:
                Y = 1j * omega * C
                
        elif comp_type == 'Inductor':
            L = max(obj.property, 1e-12)
            if frequency == 0:
                Y = 1e6  # Short circuit in DC (very large admittance)
            else:
                Y = 1.0 / (1j * omega * L)
                
        elif comp_type == 'Voltage_Source' or comp_type == 'Current_Source':
            # Voltage and current sources handled separately
            continue
        else:
            continue
        
        # Add admittance stamp (only for non-ground nodes)
        if Y != 0:
            if node_p != 0:
                row = node_p - 1
                G[row, row] += Y
                if node_n != 0:
                    G[row, node_n - 1] -= Y
            
            if node_n != 0:
                row = node_n - 1
                G[row, row] += Y
                if node_p != 0:
                    G[row, node_p - 1] -= Y
    
    # Step 5: Add current source stamps (current flows from + to -)
    for cs in current_sources:
        node_p = cs['node_p']
        node_n = cs['node_n']
        current = cs['object'].current  # Positive current flows from node_p to node_n
        
        # Add current to RHS (KCL: current leaving positive node, entering negative node)
        if node_p != 0:
            row = node_p - 1
            b[row] -= current  # Current leaving node
        
        if node_n != 0:
            row = node_n - 1
            b[row] += current  # Current entering node
    
    # Step 6: Add voltage source stamps
    for idx, vs in enumerate(voltage_sources):
        node_p = vs['node_p']
        node_n = vs['node_n']
        voltage = vs['object'].voltage
        current_var = (n_nodes - 1) + idx
        
        # Add current to KCL equations
        if node_p != 0:
            row = node_p - 1
            G[row, current_var] = 1
        
        if node_n != 0:
            row = node_n - 1
            G[row, current_var] = -1
        
        # Add voltage constraint equation: V_p - V_n = V_s
        row = current_var
        if node_p != 0:
            G[row, node_p - 1] = 1
        if node_n != 0:
            G[row, node_n - 1] = -1
        b[row] = voltage
    
    # Step 7: Handle floating nodes (add tiny conductance to ground)
    for node in range(1, n_nodes):
        row = node - 1
        if row < len(G.data) and abs(sum(abs(G[row, col]) for col in range(n_vars))) < 1e-15:
            G[row, row] = 1e-12  # Tiny conductance to ground
    
    # Step 8: Solve system
    try:
        x = spsolve(G.tocsr(), b)
        
        # Extract node voltages
        node_voltages = [0.0]  # Ground is 0V
        for i in range(n_nodes - 1):
            node_voltages.append(x[i])
        
        # Extract VS currents
        vs_currents = []
        for i in range(n_vs):
            vs_currents.append(x[(n_nodes - 1) + i])
        
        # Step 8: Calculate component voltages and currents
        for idx, comp in enumerate(components):
            node_p = comp['node_p']
            node_n = comp['node_n']
            obj = comp['object']
            comp_type = comp['type']
            
            V_p = node_voltages[node_p]
            V_n = node_voltages[node_n]
            V = V_p - V_n
            
            # Calculate current
            if comp_type == 'Resistor':
                R = max(obj.property, 1e-12)
                I = V / R
                
            elif comp_type == 'Capacitor':
                C = max(obj.property, 1e-15)
                if frequency == 0:
                    I = 0
                else:
                    Z = 1.0 / (1j * omega * C)
                    I = V / Z
                    
            elif comp_type == 'Inductor':
                L = max(obj.property, 1e-12)
                if frequency == 0:
                    Z = 1e-6
                else:
                    Z = 1j * omega * L
                I = V / Z
                
            elif comp_type == 'Voltage_Source':
                # Find which voltage source this is
                vs_idx = [i for i, vs in enumerate(voltage_sources) if vs == comp][0]
                I = vs_currents[vs_idx]
                
            elif comp_type == 'Current_Source':
                # For current source, current is defined by the source
                # Voltage across it is calculated from node voltages
                I = obj.current  # Current is set by the source
            else:
                I = 0
            
            # Convert to real values for display
            if frequency == 0:
                obj.voltage = float(np.real(V))
                obj.current = float(np.real(I))
            else:
                obj.voltage = float(abs(V) / np.sqrt(2))  # RMS
                obj.current = float(abs(I) / np.sqrt(2))  # RMS
        
        return {}
        
    except Exception as e:
        print(f"Solver error: {e}")
        import traceback
        traceback.print_exc()
        return {}
