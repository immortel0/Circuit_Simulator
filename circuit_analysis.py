# circuit_analysis.py

"""
Circuit Analysis Module using Graph Theory
Implements KCL and KVL equations using Cutset and Tieset matrices
"""

import numpy as np
from scipy.linalg import solve, lstsq
from network import Node


class Graph:
    """
    Represents the circuit as a graph for topology analysis
    """
    
    def __init__(self):
        self.nodes = []
        self.branches = []
        self.reference_node = None
        
    def add_node(self, node):
        """Add a node to the graph"""
        if node not in self.nodes:
            self.nodes.append(node)
    
    def add_branch(self, component, from_node, to_node):
        """Add a branch (component) between two nodes"""
        branch = {
            'component': component,
            'from_node': from_node,
            'to_node': to_node,
            'id': len(self.branches)
        }
        self.branches.append(branch)
        self.add_node(from_node)
        self.add_node(to_node)
        return branch['id']
    
    def set_reference_node(self, node):
        """Set the reference (ground) node"""
        self.reference_node = node
    
    def get_num_nodes(self):
        """Get number of nodes excluding reference"""
        if self.reference_node in self.nodes:
            return len(self.nodes) - 1
        return len(self.nodes)
    
    def get_num_branches(self):
        """Get number of branches"""
        return len(self.branches)


class IncidenceMatrix:

    def __init__(self, graph):
        self.graph = graph
        self.matrix = None
        self.build_matrix()
    
    def build_matrix(self):

        n = self.graph.get_num_nodes()
        b = self.graph.get_num_branches()
        
        self.matrix = np.zeros((n, b))
        
        # Get nodes excluding reference
        nodes = [node for node in self.graph.nodes if node != self.graph.reference_node]
        
        for branch in self.graph.branches:
            branch_id = branch['id']
            from_node = branch['from_node']
            to_node = branch['to_node']
            
            # Skip branches connected to reference node on both ends
            if from_node == self.graph.reference_node and to_node == self.graph.reference_node:
                continue
            
            # Branch leaves from_node
            if from_node != self.graph.reference_node:
                node_idx = nodes.index(from_node)
                self.matrix[node_idx, branch_id] = 1
            
            # Branch enters to_node
            if to_node != self.graph.reference_node:
                node_idx = nodes.index(to_node)
                self.matrix[node_idx, branch_id] = -1
        
        return self.matrix
    
    def get_matrix(self):
        return self.matrix


class CutsetMatrix:
 
    def __init__(self, incidence_matrix, tree_branches=None):
        self.A = incidence_matrix.matrix
        self.graph = incidence_matrix.graph
        self.tree_branches = tree_branches if tree_branches else self._select_tree_branches()
        self.matrix = None
        self.build_matrix()
    
    def _select_tree_branches(self):
  
        n = self.graph.get_num_nodes()
        return list(range(n))
    
    def build_matrix(self):
     
        n = self.graph.get_num_nodes()
        b = self.graph.get_num_branches()
        
        # Number of tree branches
        n_tree = len(self.tree_branches)
        # Number of link branches (cotree)
        n_link = b - n_tree
        
        # Initialize cutset matrix
        self.matrix = np.zeros((n_tree, b))
        
        # For each tree branch, create a cutset
        for i, tree_branch in enumerate(self.tree_branches):
            # Identity matrix part for tree branches
            self.matrix[i, tree_branch] = 1
            
            # Find link branches in the same cutset
            # Using simple heuristic based on incidence matrix
            for link_branch in range(b):
                if link_branch not in self.tree_branches:
                    # Check if link branch is in cutset with tree branch
                    # Simplified: use incidence matrix relationship
                    self.matrix[i, link_branch] = self._compute_cutset_entry(tree_branch, link_branch)
        
        return self.matrix
    
    def _compute_cutset_entry(self, tree_branch, link_branch):
        
        # Simplified heuristic using incidence matrix
        # Real implementation would use graph algorithms
        return 0
    
    def get_matrix(self):
        
        return self.matrix
    
    def formulate_kcl(self, branch_currents):
   
        return np.dot(self.matrix, branch_currents)


class TiesetMatrix:

    
    def __init__(self, incidence_matrix, tree_branches=None):
        self.A = incidence_matrix.matrix
        self.graph = incidence_matrix.graph
        self.tree_branches = tree_branches if tree_branches else self._select_tree_branches()
        self.matrix = None
        self.build_matrix()
    
    def _select_tree_branches(self):
     
        n = self.graph.get_num_nodes()
        return list(range(n))
    
    def build_matrix(self):
     
        n = self.graph.get_num_nodes()
        b = self.graph.get_num_branches()
        
        # Number of tree branches
        n_tree = len(self.tree_branches)
        # Number of link branches (fundamental loops)
        n_link = b - n_tree
        
        if n_link <= 0:
            # No loops, just tree
            self.matrix = np.zeros((0, b))
            return self.matrix
        
        # Initialize tieset matrix
        self.matrix = np.zeros((n_link, b))
        
        # Get link branches
        link_branches = [i for i in range(b) if i not in self.tree_branches]
        
        # For each link branch, create a fundamental loop
        for i, link_branch in enumerate(link_branches):
            # Identity matrix part for link branches
            self.matrix[i, link_branch] = 1
            
            # Find tree branches in the same loop
            # Using simple heuristic based on circuit topology
            for tree_branch in self.tree_branches:
                self.matrix[i, tree_branch] = self._compute_tieset_entry(link_branch, tree_branch)
        
        return self.matrix
    
    def _compute_tieset_entry(self, link_branch, tree_branch):
        
        # Simplified heuristic - real implementation uses graph traversal
        # to find the unique path in tree between link branch endpoints
        link = self.graph.branches[link_branch]
        tree = self.graph.branches[tree_branch]
        
        # Check if tree branch connects nodes in link branch path
        # Simplified logic
        if (tree['from_node'] == link['from_node'] or 
            tree['to_node'] == link['to_node'] or
            tree['from_node'] == link['to_node'] or
            tree['to_node'] == link['from_node']):
            return 1
        return 0
    
    def get_matrix(self):
      
        return self.matrix
    
    def formulate_kvl(self, branch_voltages):

        return np.dot(self.matrix, branch_voltages)


class CircuitEquations:
 
    
    def __init__(self, graph):
        self.graph = graph
        self.incidence_matrix = IncidenceMatrix(graph)
        self.cutset_matrix = None
        self.tieset_matrix = None
        
    def build_matrices(self, tree_branches=None):
      
        self.cutset_matrix = CutsetMatrix(self.incidence_matrix, tree_branches)
        self.tieset_matrix = TiesetMatrix(self.incidence_matrix, tree_branches)
        
    def formulate_kcl_equations(self):
        
        if self.cutset_matrix is None:
            self.build_matrices()
        
        Qf = self.cutset_matrix.get_matrix()
        b = self.graph.get_num_branches()
        zero_vector = np.zeros(Qf.shape[0])
        
        return Qf, zero_vector
    
    def formulate_kvl_equations(self):
        
        if self.tieset_matrix is None:
            self.build_matrices()
        
        Bf = self.tieset_matrix.get_matrix()
        zero_vector = np.zeros(Bf.shape[0])
        
        return Bf, zero_vector
    
    def formulate_branch_equations(self):
      
        equations = []
        
        for branch in self.graph.branches:
            component = branch['component']
            component_type = component.__class__.__name__
            
            if component_type == 'Resistor':
                # Ohm's law: V = I * R
                equations.append({
                    'type': 'resistor',
                    'branch_id': branch['id'],
                    'resistance': component.property
                })
            elif component_type == 'Voltage_Source':
                # Voltage is fixed
                equations.append({
                    'type': 'voltage_source',
                    'branch_id': branch['id'],
                    'voltage': component.voltage
                })
            elif component_type == 'Capacitor':
                # For DC: open circuit (I = 0)
                equations.append({
                    'type': 'capacitor',
                    'branch_id': branch['id'],
                    'capacitance': component.property
                })
            elif component_type == 'Inductor':
                # For DC: short circuit (V = 0)
                equations.append({
                    'type': 'inductor',
                    'branch_id': branch['id'],
                    'inductance': component.property
                })
        
        return equations
    
    def solve_dc_circuit(self):
    
        b = self.graph.get_num_branches()
        
        # Get KCL equations (Qf * I = 0)
        Qf, _ = self.formulate_kcl_equations()
        
        # Get KVL equations (Bf * V = 0)
        Bf, _ = self.formulate_kvl_equations()
        
        # Get branch equations
        branch_eqs = self.formulate_branch_equations()
        
        # Build system of equations
        # Variables: [V1, V2, ..., Vb, I1, I2, ..., Ib]
        n_vars = 2 * b  # b voltages + b currents
        
        # Initialize coefficient matrix and constant vector
        equations = []
        constants = []
        
        # Add KCL equations (current conservation)
        for row in Qf:
            # Qf applies to currents (second half of variables)
            eq_row = np.concatenate([np.zeros(b), row])
            equations.append(eq_row)
            constants.append(0)
        
        # Add KVL equations (voltage conservation)
        for row in Bf:
            # Bf applies to voltages (first half of variables)
            eq_row = np.concatenate([row, np.zeros(b)])
            equations.append(eq_row)
            constants.append(0)
        
        # Add branch constitutive equations
        for eq in branch_eqs:
            branch_id = eq['branch_id']
            eq_row = np.zeros(n_vars)
            
            if eq['type'] == 'resistor':
                # V = I * R  =>  V - I*R = 0
                eq_row[branch_id] = 1  # Voltage term
                eq_row[b + branch_id] = -eq['resistance']  # Current term
                equations.append(eq_row)
                constants.append(0)
                
            elif eq['type'] == 'voltage_source':
                # V = Vs
                eq_row[branch_id] = 1
                equations.append(eq_row)
                constants.append(eq['voltage'])
                
            elif eq['type'] == 'capacitor':
                # DC: I = 0
                eq_row[b + branch_id] = 1
                equations.append(eq_row)
                constants.append(0)
                
            elif eq['type'] == 'inductor':
                # DC: V = 0
                eq_row[branch_id] = 1
                equations.append(eq_row)
                constants.append(0)
        
        # Convert to numpy arrays
        A = np.array(equations)
        b_vec = np.array(constants)
        
        # Solve the system
        try:
            solution = lstsq(A, b_vec)[0]
            
            # Extract voltages and currents
            voltages = solution[:b]
            currents = solution[b:]
            
            return voltages, currents
            
        except Exception as e:
            print(f"Error solving circuit: {e}")
            return np.zeros(b), np.zeros(b)
    
    def print_matrices(self):
        """Print all matrices for analysis"""
        print("\n=== INCIDENCE MATRIX (A) ===")
        print(self.incidence_matrix.get_matrix())
        
        if self.cutset_matrix:
            print("\n=== CUTSET MATRIX (Qf) ===")
            print(self.cutset_matrix.get_matrix())
        
        if self.tieset_matrix:
            print("\n=== TIESET MATRIX (Bf) ===")
            print(self.tieset_matrix.get_matrix())
    
    def print_equations(self):
        """Print KCL and KVL equations in readable form"""
        print("\n=== KCL EQUATIONS (Cutset Matrix) ===")
        Qf, _ = self.formulate_kcl_equations()
        for i, row in enumerate(Qf):
            terms = []
            for j, coeff in enumerate(row):
                if coeff != 0:
                    sign = '+' if coeff > 0 else ''
                    terms.append(f"{sign}{coeff:.0f}*I{j}")
            if terms:
                print(f"Node {i}: {' '.join(terms)} = 0")
        
        print("\n=== KVL EQUATIONS (Tieset Matrix) ===")
        Bf, _ = self.formulate_kvl_equations()
        for i, row in enumerate(Bf):
            terms = []
            for j, coeff in enumerate(row):
                if coeff != 0:
                    sign = '+' if coeff > 0 else ''
                    terms.append(f"{sign}{coeff:.0f}*V{j}")
            if terms:
                print(f"Loop {i}: {' '.join(terms)} = 0")
        
        print("\n=== BRANCH EQUATIONS ===")
        branch_eqs = self.formulate_branch_equations()
        for eq in branch_eqs:
            branch_id = eq['branch_id']
            if eq['type'] == 'resistor':
                print(f"Branch {branch_id}: V{branch_id} = {eq['resistance']}*I{branch_id} (R={eq['resistance']}Ω)")
            elif eq['type'] == 'voltage_source':
                print(f"Branch {branch_id}: V{branch_id} = {eq['voltage']}V")
            elif eq['type'] == 'capacitor':
                print(f"Branch {branch_id}: I{branch_id} = 0 (Capacitor, DC)")
            elif eq['type'] == 'inductor':
                print(f"Branch {branch_id}: V{branch_id} = 0 (Inductor, DC)")


def analyze_circuit(components_with_nodes):

    # Create graph
    graph = Graph()
    
    # Add branches
    for component, from_node, to_node in components_with_nodes:
        graph.add_branch(component, from_node, to_node)
    
    # Set reference node (typically ground or first node)
    if graph.nodes:
        graph.set_reference_node(graph.nodes[0])
    
    # Create circuit equations
    circuit_eqs = CircuitEquations(graph)
    circuit_eqs.build_matrices()
    
    return circuit_eqs
