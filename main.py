# main.py

"""
functions:
    place_component places component at mouse position
    delete_self makes component commit suicide
    on_drag moves component 
    do_nothing does nothing... big surprise

frames:
    root is the main window
    container is the frame for each component
    selection_frame is frame for component selection
"""

import tkinter as tk
from tkinter import ttk

import menu
from component import *
import wiremanager as wm


root = tk.Tk()
root.title("Circuit Simulator")
root.minsize(400, 300)
root.geometry("800x600")


new_menu = menu.Menu(root)
root.menu_instance = new_menu  # Store menu instance for component configuration

components = []
selected_port = None
height_adjustment = 0

# Functions
# new_connection_handler = Connections(root)

canvas = tk.Canvas(root, bg="gray", width=800, height=400)
canvas.pack(side=tk.BOTTOM, fill= "both", expand=True)

def place_component(event: tk.Event):
    if canvas.find_withtag(tk.CURRENT):
        return

    mouse_x = event.x
    mouse_y = event.y
 
    if mouse_y < 75:
        return

    component_id = int(var.get())
    if component_id == 10: 
        return

    component_class = component_list.get(component_id)

    if component_class is None:
        return
    
    component = wm.Component(canvas, mouse_x, mouse_y, component_id)
    
    # container.bind('<Button-3>', menu.config_component(component))

    # if texture_pack == "Symbolic":
    #     icon = tk.Label(container, image=component.image_symbolic)
    # elif texture_pack == "64x64":
    #     icon = tk.Label(container, image=component.image_64x64)
    
    # icon.grid(row=0, column=1)
    
    # icon.bind('<Button-1>', handle_B1)
    # icon.bind('<B1-Motion>', on_drag)
    # icon.bind('<Button-3>', lambda e: new_menu.config_component(component=component))
    


    # components.append(component)
    # component_frames.append(container)



# def handle_B1(event: tk.Event):
#     if int(var.get()) == 10:
#         delete_self(event)
    
#     else:
#         manage_wiring(event)

# def delete_self(event: tk.Event):
#     widget = event.widget
    
#     if isinstance(widget, tk.Label):
#         container = widget.master
#     elif widget in component_frames:
#         container = widget
    
#     if int(var.get()) == 10:
#         container.destroy()
#         components.remove(components[component_frames.index(container)])
#         component_frames.remove(container)

 
# def on_drag(event: tk.Event):
#     widget = event.widget
    
#     if isinstance(widget, tk.Label):
#         container = widget.master
#     elif widget in component_frames:
#         container = widget
    
#     container.place(x=event.x_root - root.winfo_rootx() - 32, y=event.y_root - root.winfo_rooty() - texture_height[texture_pack] / 2)

# selected_port = None

# def manage_wiring(event: tk.Event):
    
#     widget = event.widget
    
#     if isinstance(widget, tk.Label):
#         container = widget.master
#     elif widget in component_frames:
#         container = widget

#     global selected_port

#     if selected_port == None:
#         selected_port = [event.x_root, event.y_root]
#         print(f"{container} selected")
#         # temp_wire = canvas.create_line(container.winfo_x, container.winfo_y, event.x, event.y, fill="blue", dash=(2, 2))
#         # canvas.bind("<Motion>", update_temp_wire)
    
#     else:
#         canvas.create_line(selected_port[0], selected_port[1], event.x_root, event.y_root)
#         selected_port = None


# Binds
    
canvas.bind('<Button-1>', place_component)



# Etc

selection_frame = tk.LabelFrame(root, text="Components")
selection_frame.pack(side= tk.TOP ,fill= "x")


var = tk.StringVar(root)
var.set("0")  # Set default to Resistor

def on_component_select():
    """Handle component selection changes"""
    selected = var.get()
    if selected == "10":  # DELETE mode
        wm.delete_mode = True
    else:
        wm.delete_mode = False

for index, component_class in component_list.items():
    component_selection = tk.Radiobutton(
        selection_frame, text= component_class.name, variable= var, 
        value= index, indicatoron= False, command= on_component_select
        )
    component_selection.grid(row= 0, column= index)




root.mainloop()