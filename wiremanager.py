# wiremanager.py

import tkinter as tk
from component import *

components = []

delete_mode = False

class Wire:
    def __init__(self, canvas, port1, port2):
        self.canvas = canvas
        self.port1 = port1
        self.port2 = port2

        x1, y1 = port1.center()
        x2, y2 = port2.center()    
        self.line = canvas.create_line(x1, y1, x2, y2, width=4)

        port1.wires.append(self)
        port2.wires.append(self)

        self.canvas.tag_bind(self.line, "<Button-3>", self.delete)

    def update(self):
        x1, y1 = self.port1.center()
        x2, y2 = self.port2.center()
        self.canvas.coords(self.line, x1, y1, x2, y2)

    def delete(self, event):
        self.canvas.delete(self.line)
        if self in self.port1.wires:
            self.port1.wires.remove(self)
        if self in self.port2.wires:
            self.port2.wires.remove(self)

class Port:
    RADIUS = 5

    def __init__(self, parent, x_offset, y_offset):
        self.parent = parent
        self.canvas = parent.canvas
        self.x_offset, self.y_offset = x_offset, y_offset
        self.wires = []
    
        x , y = self.center()

        self.circle = self.canvas.create_oval(
            x - self.RADIUS, y - self.RADIUS, 
            x + self.RADIUS, y + self.RADIUS, 
            fill= "black"
        )

        self.canvas.tag_bind(self.circle, "<Button-1>", self.on_click)
    
    def center(self):
        return (self.parent.x + self.x_offset, self.parent.y + self.y_offset)
    
    def on_click(self, event):
        global selected_port

        if selected_port is None: 
            selected_port = self
            self.highlight_port(self, True)
        else:
            if selected_port != self:
                Wire(self.canvas, selected_port, self)
            self.highlight_port(selected_port, False)
            selected_port = None

    def move(self, dx, dy):
        self.canvas.move(self.circle,dx, dy)
        for wire in self.wires:
            wire.update()
    
    def highlight_port(self, port, state):
        if state:
            colour = "red" 
        else:
            colour = "black"
        port.canvas.itemconfig(port.circle, fill=colour)

class Component:
    def __init__(self, canvas, x, y, component_id):
        self.canvas = canvas
        self.x, self.y = x, y
        self.index = len(components)
        components.append(self)

        self.component_class = component_list.get(component_id)
        self.component = self.component_class()
        self.image = self.component.image_64x64

        self.rect = canvas.create_image(x, y, image= self.image)

        # Create value label above component
        self.value_label = self.create_value_label()

        self.port1 = Port(self, -32, 0)
        self.port2 = Port(self, 32, 0)

        self.drag_offset_x = 0
        self.drag_offset_y = 0

        
        canvas.tag_bind(self.rect, "<Button-1>", self.handle_b1)
        canvas.tag_bind(self.rect, "<B1-Motion>", self.on_drag)
        canvas.tag_bind(self.rect, "<Button-3>", self.configure_component)

    def on_click(self, event):
        self.drag_offset_x = event.x - self.x
        self.drag_offset_y = event.y - self.y
    

    def on_drag(self, event):
        new_x = event.x - self.drag_offset_x
        new_y = event.y - self.drag_offset_y
        dx = new_x - self.x
        dy = new_y - self.y

        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.value_label, dx, dy)
    
        self.port1.move(dx, dy)
        self.port2.move(dx, dy)
        self.x, self.y = new_x, new_y

    def delete(self, event):
        for port in (self.port1, self.port2):
            for wire in list(port.wires):
                wire.delete(event)
            self.canvas.delete(port.circle)

        self.canvas.delete(self.rect)
        self.canvas.delete(self.value_label)
        components.remove(self)

    def handle_b1(self, event):
        global delete_mode
        if delete_mode:
            self.delete(event)
        else:
            self.on_click(event)
    
    def configure_component(self, event):
        # Import here to avoid circular import
        import menu
        import tkinter as tk
        # Get the menu instance from root
        root = tk._default_root
        if hasattr(root, 'menu_instance'):
            root.menu_instance.config_component(self.component)
            # Update the label after configuration
            self.update_value_label()
    
    def create_value_label(self):
        """Create a text label showing the component value"""
        value_text = self.get_value_text()
        label = self.canvas.create_text(
            self.x, self.y - 40,
            text=value_text,
            font=("Arial", 10, "bold"),
            fill="black",
            anchor="center"
        )
        return label
    
    def update_value_label(self):
        """Update the value label text"""
        value_text = self.get_value_text()
        self.canvas.itemconfig(self.value_label, text=value_text)
    
    def get_value_text(self):
        """Get the formatted value text for display"""
        comp_type = self.component.__class__.__name__
        
        if comp_type == 'Resistor':
            value = self.component.property
            if value >= 1000:
                return f"{value/1000:.1f}kΩ"
            else:
                return f"{value:.1f}Ω"
        elif comp_type == 'Voltage_Source':
            return f"{self.component.voltage:.1f}V"
        elif comp_type == 'Current_Source':
            current = self.component.current
            if abs(current) >= 1:
                return f"{current:.2f}A"
            elif abs(current) >= 0.001:
                return f"{current*1000:.1f}mA"
            elif abs(current) >= 0.000001:
                return f"{current*1000000:.1f}µA"
            else:
                return f"{current*1000000000:.1f}nA"
        elif comp_type == 'Capacitor':
            value = self.component.property
            if value >= 1:
                return f"{value:.1f}F"
            elif value >= 0.001:
                return f"{value*1000:.1f}mF"
            elif value >= 0.000001:
                return f"{value*1000000:.1f}µF"
            else:
                return f"{value*1000000000:.1f}nF"
        elif comp_type == 'Inductor':
            value = self.component.property
            if value >= 1:
                return f"{value:.1f}H"
            elif value >= 0.001:
                return f"{value*1000:.1f}mH"
            else:
                return f"{value*1000000:.1f}µH"
        else:
            return ""

selected_port = None