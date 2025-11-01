#menu.py

import tkinter as tk
import component
import webbrowser

def open_link(url):
    webbrowser.open_new_tab(url)

def donothing():
    print("Nothing happens")

def aboutwindow():
    about = tk.Toplevel()
    about.title("About Circuit Simulator")
    about.geometry("300x200")

    about_this = tk.Label(about, text= about_text, justify="center")

    link = tk.Label(about, text=link_text, fg="blue", cursor="hand2", font=("Arial", 9, "underline"))
    link.bind("<Button-1>", lambda e: open_link(link_url))
    
    about_this.pack()
    link.pack()
 
def controls_guide():
    guide = tk.Toplevel()
    guide.title("Controls Guide")
    guide.geometry("400x300")

    guide_text = tk.Label(guide, text= control_guide_text, justify="left")
    guide_text.pack()

def set_texture_pack(pack_name):
    component.texture_pack = pack_name




def initialize_menu(root: tk.Tk):
    menubar = tk.Menu(root)

    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label= "New", command= donothing)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command= root.quit)
    menubar.add_cascade(label="File", menu=filemenu)

    helpmenu = tk.Menu(menubar, tearoff=0)
    helpmenu.add_command(label= "About", command= aboutwindow)
    helpmenu.add_command(label= "Controls", command= controls_guide)
    menubar.add_cascade(label= "Help", menu= helpmenu)

    # texturemenu = tk.Menu(menubar, tearoff=0)
    # texturemenu.add_command(label= "Symbolic", command= set_texture_pack("Symbolic"))
    # texturemenu.add_command(label= "64x64", command= set_texture_pack("64x64"))
    # menubar.add_cascade(label= "Theme", menu= texturemenu)   


    root.config(menu=menubar)



about_text = """Circuit Simulator v1.0

Project for EE205 - Circuit Theory

Made by
Anurag Kole, Arnab Deka
Ankit Sinha, Baidurya Ghosh

July - November 2025 
(Add something useful here)
"""

control_guide_text = """Controls Guide:

- Left Click to place component
- Right Click on component to delete it
"""

link_text = "Source Code"
link_url = "https://github.com/immortel0/Circuit_Simulator"