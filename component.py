# component.py

"""

use component_list to map component names to indices

"""

import tkinter as tk
from network import *
import os
import sys

# texture_pack = "Symbolic"

# Get the directory where assets are located
# If running as PyInstaller bundle, use sys._MEIPASS
# Otherwise, use the script directory
if getattr(sys, 'frozen', False):
    # Running as PyInstaller executable
    SCRIPT_DIR = sys._MEIPASS
else:
    # Running as normal Python script
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class BasicComponent:
    pass
   


class Resistor:
    def __init__(self, resistance = 1):
        self.property = resistance
        # self.image_symbolic = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_symbolic/resistor_symbol.png"))
        self.image_64x64 = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_64x64/resistor64x64.png"))
        self.voltage = 0
        self.current = 0

    name = "Resistor"
    property_name = "resistance"
    property_unit = "\u2126"

class Capacitor:
    def __init__(self, capacitance = 1):
        self.property = capacitance
        # self.image_symbolic = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_symbolic/capacitor_symbol.png"))
        self.image_64x64 = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_64x64/capacitor64x64.png"))
        self.voltage = 0
        self.current = 0
         

    name = "Capacitor"
    property_name = "capacitance"
    property_unit = "F"


class Inductor:
    def __init__(self, inductance = 1):
        self.property = inductance
        # self.image_symbolic = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_symbolic/inductor_symbol.png"))
        self.image_64x64 = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_64x64/inductor64x64.png"))
        self.voltage = 0
        self.current = 0
 
    name = "Inductor"
    property_name = "inductance"
    property_unit = "H"


class Voltage_Source:
    def __init__(self, voltage = 1):
        self.voltage = voltage
        # self.image_symbolic = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_symbolic/voltage_symbol.png"))
        self.image_64x64 = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_64x64/voltage64x64.png"))
        self.current = 0   

    name = "Voltage Source"
    property_name = "voltage"
    property_unit = "V"

class Current_Source:
    def __init__(self, current = 1):
        self.current = current
        # Use voltage source image as placeholder
        self.image_64x64 = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_64x64/voltage64x64.png"))
        self.voltage = 0   

    name = "Current Source"
    property_name = "current"
    property_unit = "A"

class Wire:
    def __init__(self):
        self.resistance = 0

    name = "Wire"

class Ground:
    def __init__(self):
        # self.image_symbolic = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_symbolic/ground_symbol.png"))
        # self.image_64x64 = tk.PhotoImage(file = os.path.join(SCRIPT_DIR, "Assets/texture_64x64/ground64x64.png"))
        self.voltage = 0
        pass

    name = "Ground"

class Delete:
    def __init__(self):
        pass

    name = "DELETE"

component_list = {
    0: Resistor,
    1: Capacitor,
    2: Inductor,
    3: Voltage_Source,
    4: Current_Source,
    10: Delete
}


texture_height = {
    "Symbolic": 22,
    "64x64": 64
}

class Connection:
    def __init__(self, node_from: Node, node_to: Node):
        self.node_from = node_from
        self.node_to = node_to
        node_from.add_connection(node_to)

    
