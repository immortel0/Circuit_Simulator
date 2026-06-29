# laplace_solver.py

"""
Laplace domain circuit solver with time-domain trajectory generation
Handles transient analysis of RC and RL circuits
"""

import numpy as np
from scipy import signal
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve
from simple_circuit_solver import solve_circuit_simple


class LaplaceSolver:
    """
    Solves circuits in Laplace domain and converts to time domain
    """
    
    def __init__(self, components_list):
        """
        Initialize solver with components
        
        Args:
            components_list: List of component wrappers
        """
        self.components = components_list
        self.time_points = None
        self.voltage_trajectories = {}  # {component_index: voltage_array}
        self.current_trajectories = {}  # {component_index: current_array}
        
    def analyze_circuit_type(self):
        """
        Analyze circuit to determine order and type
        Returns: (order, has_capacitor, has_inductor)
        """
        has_capacitor = False
        has_inductor = False
        
        for wrapper in self.components:
            comp = wrapper.component
            comp_type = type(comp).__name__
            
            if comp_type == "Capacitor":
                has_capacitor = True
            elif comp_type == "Inductor":
                has_inductor = True
        
        # Determine circuit order
        if has_capacitor and has_inductor:
            order = 2  # RLC circuit
        elif has_capacitor or has_inductor:
            order = 1  # RC or RL circuit
        else:
            order = 0  # Purely resistive
        
        return order, has_capacitor, has_inductor
    
    def get_circuit_parameters(self):
        """
        Extract circuit parameters (R, L, C values)
        """
        params = {
            'resistors': [],
            'capacitors': [],
            'inductors': [],
            'voltage_sources': [],
            'current_sources': []
        }
        
        for wrapper in self.components:
            comp = wrapper.component
            comp_type = type(comp).__name__
            
            if comp_type == "Resistor":
                params['resistors'].append(comp.property)
            elif comp_type == "Capacitor":
                params['capacitors'].append(comp.property)
            elif comp_type == "Inductor":
                params['inductors'].append(comp.property)
            elif comp_type == "Voltage_Source":
                params['voltage_sources'].append(comp.voltage)
            elif comp_type == "Current_Source":
                params['current_sources'].append(comp.current)
        
        return params
    
    def compute_time_constant(self):
        """
        Compute time constant based on circuit type
        τ = RC for RC circuits
        τ = L/R for RL circuits
        """
        params = self.get_circuit_parameters()
        order, has_capacitor, has_inductor = self.analyze_circuit_type()
        
        if order == 0:
            return 0.001  # Default for resistive circuits
        
        # Calculate equivalent resistance
        # If no resistors, use a small internal resistance (e.g., 0.01Ω for sources)
        R_eq = sum(params['resistors']) if params['resistors'] else 0.01
        
        if has_capacitor and not has_inductor:
            # RC circuit: τ = RC
            C_eq = sum(params['capacitors']) if params['capacitors'] else 1e-6
            tau = R_eq * C_eq
        elif has_inductor and not has_capacitor:
            # RL circuit: τ = L/R
            L_eq = sum(params['inductors']) if params['inductors'] else 1e-3
            tau = L_eq / R_eq if R_eq > 0 else 0.001
        else:
            # RLC circuit: use √(LC) as characteristic time
            C_eq = sum(params['capacitors']) if params['capacitors'] else 1e-6
            L_eq = sum(params['inductors']) if params['inductors'] else 1e-3
            tau = np.sqrt(L_eq * C_eq)
        
        return max(tau, 1e-9)  # Ensure positive time constant
    
    def generate_time_domain_trajectories(self, t_max=None, num_points=500):
        """
        Generate time-domain voltage and current trajectories
        
        Args:
            t_max: Maximum time (default: 5 time constants)
            num_points: Number of time points
        """
        order, has_capacitor, has_inductor = self.analyze_circuit_type()
        tau = self.compute_time_constant()
        
        # Set simulation time based on time constant
        if t_max is None:
            t_max = 5 * tau  # 5 time constants for ~99% settling
        
        # Generate time points
        self.time_points = np.linspace(0, t_max, num_points)
        
        if order == 0:
            # Purely resistive - steady state immediately
            self._generate_resistive_trajectories()
        elif order == 1:
            # First order (RC or RL)
            self._generate_first_order_trajectories(tau, has_capacitor, has_inductor)
        else:
            # Second order (RLC)
            self._generate_second_order_trajectories(tau)
    
    def _generate_resistive_trajectories(self):
        """Generate trajectories for purely resistive circuits"""
        # Solve at steady state
        solve_circuit_simple(self.components, frequency=0, time=0)
        
        # All components have constant values
        for idx, wrapper in enumerate(self.components):
            comp = wrapper.component
            v_steady = getattr(comp, 'voltage', 0)
            i_steady = getattr(comp, 'current', 0)
            
            # Constant trajectories
            self.voltage_trajectories[idx] = np.full_like(self.time_points, v_steady)
            self.current_trajectories[idx] = np.full_like(self.time_points, i_steady)
    
    def _generate_first_order_trajectories(self, tau, has_capacitor, has_inductor):
        """
        Generate trajectories for first-order circuits (RC or RL)
        Response: x(t) = x_steady + (x_0 - x_steady) * exp(-t/τ)
        """
        # Get steady-state solution (t → ∞)
        solve_circuit_simple(self.components, frequency=0, time=float('inf'))
        
        steady_state = {}
        for idx, wrapper in enumerate(self.components):
            comp = wrapper.component
            steady_state[idx] = {
                'voltage': getattr(comp, 'voltage', 0),
                'current': getattr(comp, 'current', 0)
            }
        
        # Calculate initial current (when capacitor acts as short or inductor as open)
        params = self.get_circuit_parameters()
        # If no resistors, use small internal resistance
        R_eq = sum(params['resistors']) if params['resistors'] else 0.01
        V_source = sum(params['voltage_sources']) if params['voltage_sources'] else 0
        I_source = sum(params['current_sources']) if params['current_sources'] else 0
        
        # Initial current through circuit
        if has_capacitor:
            # Capacitor acts as short at t=0, full current flows
            i_initial = V_source / R_eq if R_eq > 0 else 0
        elif has_inductor:
            # Inductor acts as open at t=0, no current flows
            i_initial = 0
        else:
            i_initial = 0
        
        # Get initial conditions
        initial_state = {}
        
        for idx, wrapper in enumerate(self.components):
            comp = wrapper.component
            comp_type = type(comp).__name__
            
            if comp_type == "Capacitor":
                # Capacitor starts at 0V (uncharged), full initial current
                initial_state[idx] = {
                    'voltage': 0,
                    'current': i_initial
                }
            elif comp_type == "Inductor":
                # Inductor starts at 0A (no initial current), full voltage across it
                initial_state[idx] = {
                    'voltage': V_source,
                    'current': 0
                }
            elif comp_type == "Resistor":
                # Resistor: V = I*R at t=0
                if has_capacitor:
                    initial_state[idx] = {
                        'voltage': i_initial * comp.property,
                        'current': i_initial
                    }
                elif has_inductor:
                    initial_state[idx] = {
                        'voltage': 0,  # No current, no voltage
                        'current': 0
                    }
                else:
                    initial_state[idx] = {
                        'voltage': steady_state[idx]['voltage'],
                        'current': steady_state[idx]['current']
                    }
            else:
                # Voltage/current sources
                initial_state[idx] = {
                    'voltage': steady_state[idx]['voltage'],
                    'current': i_initial if has_capacitor else 0
                }
        
        # Generate exponential trajectories
        for idx, wrapper in enumerate(self.components):
            comp = wrapper.component
            comp_type = type(comp).__name__
            
            v_0 = initial_state[idx]['voltage']
            v_inf = steady_state[idx]['voltage']
            i_0 = initial_state[idx]['current']
            i_inf = steady_state[idx]['current']
            
            # Exponential response: x(t) = x_∞ + (x_0 - x_∞) * e^(-t/τ)
            exp_factor = np.exp(-self.time_points / tau)
            
            if comp_type == "Capacitor":
                # Capacitor voltage rises exponentially from 0 to V_steady
                self.voltage_trajectories[idx] = v_inf * (1 - exp_factor)
                # Capacitor current decays exponentially from I_0 to 0
                self.current_trajectories[idx] = i_0 * exp_factor
            elif comp_type == "Inductor":
                # Inductor current rises exponentially from 0 to I_steady
                self.current_trajectories[idx] = i_inf * (1 - exp_factor)
                # Inductor voltage decays exponentially from V_0 to 0
                self.voltage_trajectories[idx] = v_0 * exp_factor
            else:
                # Resistors and sources: exponential transition
                self.voltage_trajectories[idx] = v_inf + (v_0 - v_inf) * exp_factor
                self.current_trajectories[idx] = i_inf + (i_0 - i_inf) * exp_factor
    
    def _generate_second_order_trajectories(self, tau):
        """
        Generate trajectories for second-order circuits (RLC)
        Can be overdamped, critically damped, or underdamped
        """
        params = self.get_circuit_parameters()
        
        # Calculate RLC parameters
        R_eq = sum(params['resistors']) if params['resistors'] else 1.0
        L_eq = sum(params['inductors']) if params['inductors'] else 1e-3
        C_eq = sum(params['capacitors']) if params['capacitors'] else 1e-6
        
        # Natural frequency and damping
        omega_0 = 1 / np.sqrt(L_eq * C_eq)  # Natural frequency
        zeta = (R_eq / 2) * np.sqrt(C_eq / L_eq)  # Damping ratio
        
        # Get steady-state solution
        solve_circuit_simple(self.components, frequency=0, time=float('inf'))
        
        steady_state = {}
        for idx, wrapper in enumerate(self.components):
            comp = wrapper.component
            steady_state[idx] = {
                'voltage': getattr(comp, 'voltage', 0),
                'current': getattr(comp, 'current', 0)
            }
        
        # Generate response based on damping
        if zeta > 1:
            # Overdamped
            self._generate_overdamped_response(omega_0, zeta, steady_state)
        elif zeta == 1:
            # Critically damped
            self._generate_critically_damped_response(omega_0, steady_state)
        else:
            # Underdamped (oscillatory)
            self._generate_underdamped_response(omega_0, zeta, steady_state)
    
    def _generate_overdamped_response(self, omega_0, zeta, steady_state):
        """Overdamped second-order response (two real poles)"""
        s1 = -zeta * omega_0 + omega_0 * np.sqrt(zeta**2 - 1)
        s2 = -zeta * omega_0 - omega_0 * np.sqrt(zeta**2 - 1)
        
        for idx, wrapper in enumerate(self.components):
            v_inf = steady_state[idx]['voltage']
            i_inf = steady_state[idx]['current']
            
            # Response: x(t) = x_∞ + A*e^(s1*t) + B*e^(s2*t)
            # Assuming zero initial conditions for simplicity
            A = v_inf / 2
            B = v_inf / 2
            
            self.voltage_trajectories[idx] = v_inf - A * np.exp(s1 * self.time_points) - B * np.exp(s2 * self.time_points)
            self.current_trajectories[idx] = i_inf - A * np.exp(s1 * self.time_points) - B * np.exp(s2 * self.time_points)
    
    def _generate_critically_damped_response(self, omega_0, steady_state):
        """Critically damped second-order response"""
        for idx, wrapper in enumerate(self.components):
            v_inf = steady_state[idx]['voltage']
            i_inf = steady_state[idx]['current']
            
            # Response: x(t) = x_∞ + (A + Bt)*e^(-ω₀t)
            exp_factor = np.exp(-omega_0 * self.time_points)
            
            self.voltage_trajectories[idx] = v_inf * (1 - (1 + omega_0 * self.time_points) * exp_factor)
            self.current_trajectories[idx] = i_inf * (1 - (1 + omega_0 * self.time_points) * exp_factor)
    
    def _generate_underdamped_response(self, omega_0, zeta, steady_state):
        """Underdamped second-order response (oscillatory)"""
        omega_d = omega_0 * np.sqrt(1 - zeta**2)  # Damped natural frequency
        
        for idx, wrapper in enumerate(self.components):
            v_inf = steady_state[idx]['voltage']
            i_inf = steady_state[idx]['current']
            
            # Response: x(t) = x_∞ - x_∞ * e^(-ζω₀t) * cos(ωₐt)
            exp_envelope = np.exp(-zeta * omega_0 * self.time_points)
            oscillation = np.cos(omega_d * self.time_points)
            
            self.voltage_trajectories[idx] = v_inf * (1 - exp_envelope * oscillation)
            self.current_trajectories[idx] = i_inf * (1 - exp_envelope * oscillation)
    
    def get_voltage_at_time(self, component_index, time):
        """Get voltage for a component at specific time"""
        if component_index not in self.voltage_trajectories:
            return 0
        
        # Interpolate if needed
        if self.time_points is None:
            return 0
        
        voltage_array = self.voltage_trajectories[component_index]
        return np.interp(time, self.time_points, voltage_array)
    
    def get_current_at_time(self, component_index, time):
        """Get current for a component at specific time"""
        if component_index not in self.current_trajectories:
            return 0
        
        # Interpolate if needed
        if self.time_points is None:
            return 0
        
        current_array = self.current_trajectories[component_index]
        return np.interp(time, self.time_points, current_array)


def solve_circuit_transient(components_list, t_max=None, num_points=500):
    """
    Convenience function to solve circuit in time domain
    
    Args:
        components_list: List of component wrappers
        t_max: Maximum simulation time
        num_points: Number of time points
    
    Returns:
        LaplaceSolver instance with trajectories computed
    """
    solver = LaplaceSolver(components_list)
    solver.generate_time_domain_trajectories(t_max=t_max, num_points=num_points)
    return solver
