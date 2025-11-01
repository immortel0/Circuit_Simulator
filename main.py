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



root = tk.Tk()
root.title("Circuit Simulator")
root.minsize(400, 300)
root.geometry("800x600")


menu.initialize_menu(root)

components = []
component_frames = []


# Functions

def place_component(event):
    mouse_x = event.x
    mouse_y = event.y

    # so clicking the selection panel doesnt place components B)
    if mouse_y < 75:
        return

    component_id = int(var.get())
    component_class = component_list.get(component_id)
    if component_class is None:
        return

    component = component_class()

    container = tk.Frame(root, width=64, height=64, background="black")
    container.place(x=mouse_x - 32, y=mouse_y - 32)
    container.bind('<Button-3>', delete_self)
    container.bind('<B1-Motion>', on_drag)
   
    icon = tk.Label(container, image=component.image)
    icon.pack()
    icon.bind('<Button-3>', delete_self)
    icon.bind('<B1-Motion>', on_drag)

    components.append(component)
    component_frames.append(container)


def delete_self(event: tk.Event):
    widget = event.widget
    
    if isinstance(widget, tk.Label):
        container = widget.master
    elif widget in component_frames:
        container = widget
    
    container.destroy()
    components.remove(components[component_frames.index(container)])
    component_frames.remove(container)


def on_drag(event: tk.Event):
    widget = event.widget
    
    if isinstance(widget, tk.Label):
        container = widget.master
    elif widget in component_frames:
        container = widget
    
    container.place(x=event.x_root - root.winfo_rootx() - 32, y=event.y_root - root.winfo_rooty() - 32)


# Binds

root.bind('<Button-1>', place_component)



# Etc

selection_frame = tk.LabelFrame(root, text="Components")
selection_frame.pack(side= tk.TOP ,fill= "x")

var = tk.StringVar(root)
for index, component_class in component_list.items():
    component_selection = tk.Radiobutton(
        selection_frame, text= component_class.name,variable= var, value= index, indicatoron= False
        )
    component_selection.grid(row= 0, column= index)







root.mainloop()