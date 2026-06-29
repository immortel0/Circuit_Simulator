#   Yp - Passive Admittance Matrix
#   Vn - Node Voltages
#   Vb - Branch Voltages


import numpy as np
import sympy as sym
from component import *

node_list = []
branch_list = []
passive_branch_list = []

class Node:
    def __init__(self):
        self.index = len(node_list)
        node_list.append(self)
        self.node_to = []
        self.node_from = []
    
    def connect(self, node_target = None):
        for node in node_target:    
            self.node_to.append(node)
            Branch(self, node)
            node.node_from.append(self)

    def delete(self):
        node_list.remove(self)
        for node in self.node_from:
            node.node_to.remove(self)
        for node in self.node_to:
            node.node_from.remove(self)
                
        
class Branch:
    def __init__(self, node_from: Node , node_to: Node, component = None):
        self.index = len(branch_list)
        branch_list.append(self)
        self.node_from = node_from
        self.node_to = node_to
        self.component = component

        if type(component) in passive_component_list:
            passive_branch_list.append(self)

    def delete(self):
        branch_list.remove(self)
        self.node_from.delete()
        self.node_to.delete()
        


def generate_incedence_matrix(node_list: list, branch_list: list):
    IncMatrix = np.zeros((len(node_list), len(branch_list)))
    
    for node in node_list:
        for branch in branch_list:
            if node == branch.node_from:
                IncMatrix[node.index, branch.index] = 1
            elif node == branch.node_to:
                IncMatrix[node.index, branch.index] = -1
            else:
                IncMatrix[node.index, branch.index] = 0

    return IncMatrix

def generate_Yp_matrix(branch_list):
    n = len(branch_list)
    Yp = np.zeros(n,n)

    for branch in branch_list:
        Yp[branch.index, [branch.index]] = branch.component.impedence

    return Yp

def matrix_to_equations(A, symbols, rhs=None):
    A = np.array(A)
    n = A.shape[0]
    m = A.shape[1]
    
    if rhs is None:
        rhs = [0]*n
    
    eqns = []
    for i in range(n):
        lhs = sum(A[i, j] * symbols[j] for j in range(m))
        eqns.append(sym.Eq(lhs, rhs[i]))
    
    return eqns

def depth_first_search(start_node:Node, previous_node:Node = None, visited = None, spanning_tree = None):

    if visited == None:
        visited = set()
    
    if spanning_tree == None:
        spanning_tree = set()
    
    visited.add(start_node)
    
    for node in start_node.node_to:
        print(f"Node at {start_node.index}, Node to {node.index}")

        if node not in visited:
            print(f"Visiting node {node.index}")
            depth_first_search(node, start_node, visited, spanning_tree)
        
        elif node in visited:
            print(f"Creating spanning_tree:{node.index}")
            spanning_tree.add((start_node.index, node.index))

    return spanning_tree, visited





I = sym.symbols(f'i0:{len(branch_list)}')
Vn = sym.symbols(f'Vn0:{len(node_list)}')
Vb = sym.symbols(f'Vb0:{len(branch_list)}')

Ap = generate_incedence_matrix(node_list, passive_branch_list)

def cc_update():
    global I, Vn, Vb, Ap

    I = sym.symbols(f'i0:{len(branch_list)}')
    Vn = sym.symbols(f'Vn0:{len(node_list)}')
    Vb = sym.symbols(f'Vb0:{len(branch_list)}')
    Ap = generate_incedence_matrix(node_list, passive_branch_list)


if __name__ == "__main__":
    n0 = Node()
    n1 = Node()
    n2 = Node()
    n3 = Node()
    # n3 = Node()
    # n4 = Node()
    # n5 = Node()

    n0.connect([n1, n1])
    n1.connect([n0, n0])
    n2.connect([n3])
    n3.connect([n2])

    # n3.connect([n4])
    # n4.connect([n5]) 
    # n5.connect([n3])


    visited = []


    generate_incedence_matrix(node_list, branch_list)

    for node in node_list:
        if node not in visited:
            spanning_tree, visited = depth_first_search(node)
            print(spanning_tree)

    A = generate_incedence_matrix(node_list, branch_list)

    print(A)

    KCL = matrix_to_equations(A, I)

    Atranspose = A.transpose()

    KVL = matrix_to_equations(Atranspose, Vn, Vb)

    # print(matrix_to_equations(A, I))
    # print(matrix_to_equations(Atranspose, Vn, Vb))

    KCL_sol = sym.solve(KCL, I)

    # print(KCL_sol)

    # spanning_tree, visited = depth_first_search(node_list[0])


def get_reduced_incidence_matrix():
    """
    Generates the reduced incidence matrix by omitting the row 
    corresponding to the Ground node (Reference Node).
    """
    # Find the index of the node connected to Ground
    ground_node_index = None
    for b in branch_list:
        if b.component and b.component.name == "Ground":
            # Assuming ground component sets its associated node as ground reference
            ground_node_index = b.node_from.index # or b.node_to depending on connection
            break
            
    # Default to node 0 if no Ground component is placed yet
    if ground_node_index is None:
        ground_node_index = 0

    num_nodes = len(node_list)
    
    # We will build separate lists for passives and voltage sources
    passive_branches = [b for b in branch_list if type(b.component) in passive_component_list]
    voltage_branches = [b for b in branch_list if type(b.component) == Voltage_Source]
    
    # Construct maps
    num_p = len(passive_branches)
    num_v = len(voltage_branches)
    
    # Reduced rows: total nodes minus 1 (the ground reference)
    reduced_node_indices = [i for i in range(num_nodes) if i != ground_node_index]
    N = len(reduced_node_indices)
    
    # Helper to map original node index to reduced matrix row index
    node_map = {orig: new for new, orig in enumerate(reduced_node_indices)}

    # 1. Build A_p (Passive Incidence Matrix)
    A_p = sym.zeros(N, num_p)
    for j, b in enumerate(passive_branches):
        if b.node_from.index in node_map:
            A_p[node_map[b.node_from.index], j] = 1
        if b.node_to.index in node_map:
            A_p[node_map[b.node_to.index], j] = -1

    # 2. Build B matrix from Voltage Sources
    B = sym.zeros(N, num_v)
    E = sym.zeros(num_v, 1)
    for j, b in enumerate(voltage_branches):
        if b.node_from.index in node_map:
            B[node_map[b.node_from.index], j] = 1  # Assuming node_from is positive terminal
        if b.node_to.index in node_map:
            B[node_map[b.node_to.index], j] = -1 # Assuming node_to is negative terminal
        E[j, 0] = b.component.property # Voltage source value

    # 3. Build Y_p (Admittance matrix for passives)
    Y_p = sym.zeros(num_p, num_p)
    for j, b in enumerate(passive_branches):
        # Using correct spelling 'impedance'
        # Admittance Y = 1 / Impedance
        Y_p[j, j] = 1 / b.component.impedance 

    return A_p, Y_p, B, E, reduced_node_indices, voltage_branches


def solve_circuit():
    """
    Assembles the Modified Nodal Analysis (MNA) matrix and solves for unknowns.
    """
    if not branch_list:
        return "Empty Circuit"

    # Fetch partitioned matrices
    A_p, Y_p, B, E, reduced_nodes, voltage_branches = get_reduced_incidence_matrix()
    
    N = A_p.shape[0]       # Number of non-ground nodes
    M = B.shape[1]       # Number of voltage sources

    if N == 0:
        return "Circuit needs more nodes connected beyond Ground."

    # Compute G = A_p * Y_p * A_p^T
    G = A_p * Y_p * A_p.T
    
    # Assemble MNA left-hand Matrix
    MNA_LHS = sym.zeros(N + M, N + M)
    MNA_LHS[0:N, 0:N] = G
    MNA_LHS[0:N, N:N+M] = B
    MNA_LHS[N:N+M, 0:N] = B.T
    # Bottom right D block remains zeros for ideal independent voltage sources

    # Assemble MNA right-hand Vector
    MNA_RHS = sym.zeros(N + M, 1)
    # Top block (J) is zero since there are no current sources in your component list
    MNA_RHS[N:N+M, 0] = E

    # Generate symbolic Unknowns Vector tracking variables
    V_nodes = [sym.Symbol(f'V_node_{idx}') for idx in reduced_nodes]
    I_sources = [sym.Symbol(f'I_{b.component.name}') for b in voltage_branches]
    Unknowns = V_nodes + I_sources

    # Solve the system symbolically!
    try:
        solution = sym.Linsolve((MNA_LHS, MNA_RHS), Unknowns)
        return dict(zip(Unknowns, list(solution)[0]))
    except Exception as e:
        return f"Matrix is singular or structural error: {str(e)}"