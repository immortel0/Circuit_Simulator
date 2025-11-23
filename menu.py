#menu.py

import tkinter as tk
import component
import webbrowser

class Menu:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.menubar = tk.Menu(root)

        self.filemenu = tk.Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label= "New", command= self.donothing)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command= root.quit)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        self.helpmenu = tk.Menu(self.menubar, tearoff=0)
        self.helpmenu.add_command(label= "About", command= self.aboutwindow)
        self.helpmenu.add_command(label= "Controls", command= self.controls_guide)
        self.menubar.add_cascade(label= "Help", menu= self.helpmenu)

        # texturemenu = tk.Menu(menubar, tearoff=0)
        # texturemenu.add_command(label= "Symbolic", command= set_texture_pack("Symbolic"))
        # texturemenu.add_command(label= "64x64", command= set_texture_pack("64x64"))
        # menubar.add_cascade(label= "Theme", menu= texturemenu)   

        self.root.config(menu=self.menubar)


    def open_link(self, url):
        webbrowser.open_new_tab(url)

    def donothing(self):
        print("Nothing happens")

    def aboutwindow(self):
        self.about = tk.Toplevel()
        self.about.title("About Circuit Simulator")
        self.about.geometry("300x200")

        self.about_this = tk.Label(self.about, text= self.about_text, justify="center")

        self.link = tk.Label(self.about, text= self.link_text, fg="blue", cursor="hand2", font=("Arial", 9, "underline"))
        self.link.bind("<Button-1>", lambda e: self.open_link(self.link_url))
        
        self.about_this.pack()
        self.link.pack()
    
    def controls_guide(self):
        self.guide = tk.Toplevel()
        self.guide.title("Controls Guide")
        self.guide.geometry("400x300")

        self.guide_text = tk.Label(self.guide, text= self.control_guide_text, justify="left")
        self.guide_text.pack()

    def set_texture_pack(self, pack_name):
        component.texture_pack = pack_name

    def config_component(self, component):
        self.value_var=tk.StringVar()
        self.config = tk.Toplevel(self.root)
        self.config.title(f"Configure {component.name}")
        self.config.geometry("300x200")
        self.config.resizable(width=False, height=False)
        self.config.focus_force()

        self.value_label = tk.Label(self.config, text = f'{component.property_name}: ', font=('calibre',10, 'bold'))
        self.value_entry = tk.Entry(self.config, textvariable = self.value_var, width= 10)
        self.value_units = tk.Label(self.config, text = f' {component.property_unit}', font=('calibre',10, 'bold'))
        self.submit = tk.Button(self.config, text= "Enter", command= self.enter_value(self.value_var, component))

        self.value_label.grid(row=0, column=0, padx= 20, pady= 20)
        self.value_entry.grid(row=0, column=1)
        self.value_units.grid(row=0, column=2)
        self.submit.grid(row= 1, column= 1)
        
        
    def enter_value(self, var, component): 
        component.property = float(var)
        



    


    about_text = """Circuit Simulator v1.0

    Project for EE205 - Circuit Theory

    Made by
    Anurag Kole, Arnab Deka
    Ankit Sinha, Baidurya Ghosh

    Semester : July - November 2025 
    (Add something useful here)
    """

    control_guide_text = """Controls Guide:

    - Left Click to place component
    - Select DELETE to delete components
    - Right Click on component to change its values
    """

    link_text = "Source Code"
    link_url = "https://github.com/immortel0/Circuit_Simulator"