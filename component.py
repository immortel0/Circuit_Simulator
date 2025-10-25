# component.py

"""

use component_list to map component names to indices

"""

import tkinter as tk


texture_pack = "Symbolic"

class Resistor:
    def __init__(self, resistance = 1):
        self.resistance = resistance
        self.image_symbolic = tk.PhotoImage(file = "Assets/texture_symbolic/resistor_symbol.png")
        self.image_64x64 = tk.PhotoImage(file = "Assets/texture_64x64/resistor64x64.png")
        self.voltage = 0
        self.current = 0

    name = "Resistor"


class Capacitor:
    def __init__(self, capacitance = 1):
        self.capacitance = capacitance
        self.image_symbolic = tk.PhotoImage(file = "Assets/texture_symbolic/capacitor_symbol.png")
        self.image_64x64 = tk.PhotoImage(file = "Assets/texture_64x64/capacitor64x64.png")
        self.voltage = 0
        self.current = 0

    name = "Capacitor"


class Inductor:
    def __init__(self, inductance = 1):
        self.inductance = inductance
        self.image_symbolic = tk.PhotoImage(file = "Assets/texture_symbolic/inductor_symbol.png")
        self.image_64x64 = tk.PhotoImage(file = "Assets/texture_64x64/inductor64x64.png")
        self.voltage = 0
        self.current = 0
 
    name = "Inductor"


class Voltage_Source:
    def __init__(self, voltage = 1):
        self.voltage = voltage
        self.image_symbolic = tk.PhotoImage(file = "Assets/texture_symbolic/voltage_symbol.png")
        self.image_64x64 = tk.PhotoImage(file = "Assets/texture_64x64/voltage64x64.png")
        self.current = 0   

    name = "Voltage Source"


class Wire:
    def __init__(self):
        self.resistance = 0

    name = "Wire"


component_list = {
    0: Resistor,
    1: Capacitor,
    2: Inductor,
    3: Voltage_Source
}


texture_height = {
    "Symbolic": 22,
    "64x64": 64
}
