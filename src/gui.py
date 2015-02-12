from tkinter import Tk, Canvas, Frame, BOTH, Button, Toplevel, Entry, Label, END, DISABLED, NORMAL, Listbox, PhotoImage
from opcodes import *
from plugin import *
from math import sin
import emulator
import sys
import threading
import time

#FIXME: Freezes on infinite loop. :(

class Main():
    def __init__(self, parent, CPU_object):

        # Set up the basic variables and the fram
        self.cpu        = CPU_object
        self.parent     = parent
        self.parent.title("Main")
        self.frame      = Frame(parent)
        self.frame.config(pady = 10)

        # Set up the label at the top
        self.label      = Label(self.frame, text = "Registers: ")
        self.label.grid(row = 0, columnspan = 2)

        # Set up the labels and text-boxes for the registers
        self.register_text  = []
        self.register_label = []

        # A loop for setting the registers text boxes and labels
        for x in range(11):

            # Use tricky-tricks to not have to write in the values for the labels
            label_text = REV_VALUES[x] + ": "

            if x > 7:
                label_text = REV_VALUES[x + 19] + ": "

            self.register_label.append(Label(self.frame, text = label_text))
            self.register_text.append(Entry(self.frame, width = 25))

            self.register_label[x].grid(row = x + 1, column = 0)
            self.register_text[x].grid(row = x + 1, column = 1)

        #Set up the buttons into the frame
        self.monitor_button = Button(self.frame, text = "Open monitor", width = 25, command = self.open_monitor)
        self.watcher_button = Button(self.frame, text = "Open watcher", width = 25, command = self.open_watcher)
        self.run_button     = Button(self.frame, text = "Run program", width = 25, command = self.run_program)
        self.step_button    = Button(self.frame, text = "Step program", width = 25, command = self.step_program)

        # Pack the buttons
        self.monitor_button.grid(row = 12, columnspan = 2)
        self.watcher_button.grid(row = 13, columnspan = 2)
        self.run_button.grid(row = 14, columnspan = 2)
        self.step_button.grid(row = 15, columnspan = 2)

        # Pack the frame
        self.frame.pack()

    def step_program(self):

        # Step through the program and update the registers
        self.cpu.step()
        self.update_regs()
        time.sleep(1)

        # Disable the buttons for step/run 
        if len(self.cpu.text) == self.cpu.PC:
            self.step_button.config(state = DISABLED)
            self.run_button.config(state = DISABLED)

    def run(self):

        # Stupid threads. WHO NEEDS YOU ANYWAY?!
        while(len(self.cpu.text) != self.cpu.PC):
            self.step_program()

    def run_program(self):

        #Threading is hard. :(
        t = threading.Thread(target=self.run)
        t.start()

    def update_text(self, obj, text):

        # Update the text in an Entry object
        obj.delete(0, END)
        obj.insert(0, text)

    def update_regs(self):
        
        # Update the general registers
        for i, reg in enumerate(self.cpu.regs):
            self.update_text(self.register_text[i], hex(reg))

        # Update SP, PC, and O
        self.update_text(self.register_text[8], hex(self.cpu.SP))
        self.update_text(self.register_text[9], hex(self.cpu.PC))
        self.update_text(self.register_text[10], hex(self.cpu.O))

    def open_watcher(self):
        self.watcher_window = Toplevel(self.parent)
        self.app = MemoryWatcher(self.watcher_window) 

    def open_monitor(self):

        # Open the monitor
        self.monitor_window = Toplevel(self.parent)
        self.app = Monitor(self.monitor_window)

class Monitor():
  
    def __init__(self, parent):
        
        # Set up the initial variables/frame stuff
        self.parent             = parent        
        
        # We need to upscale this somehow 
        self.parent.geometry("120x90")
        self.frame              = Frame(parent)
        self.memory_listener    = MemoryListener(self.action)
        self.width              = 120
        self.height             = 90
        self.img                = PhotoImage(width=self.width, height=self.height)
        self.initUI()

    def action(self, data):
        address = data[0]

        # Video mem starts at 0x8000, and since the monitor is 120x90, and (120*90) = 0x2A30, so 0x8000 + 0x2A30 = 0xAA30
        if(address >= 0x8000 and address <= 0xAA30):
            pixel = address - 0x8000
            color = data[1]

            print("[VIDEO]: Pixel,", hex(pixel), "set to,", hex(color))

            # No idea what this shit does. self.img.put should allow me to do pixels. 
            for x in range(4 * self.width):
                y = int(self.height/2 + self.height/4 * sin(x/80.0))
                self.img.put("#ffffff", (x//4, y)) 

    def initUI(self):
     
        # Deal with the UI
        self.parent.title("Monitor")        
        self.frame.pack(fill=BOTH, expand=1)

        # Now less placeholder-y 
        canvas = Canvas(self.frame, width=self.width, height=self.height, bg="#000")
        canvas.pack(fill=BOTH, expand=1)

        # Need to create an image so we can place individual pixels 
        canvas.create_image((self.width/2, self.height/2), image=self.img, state="normal")

class MemoryWatcher():
    
    def __init__(self, parent):

        # Window stuff
        self.parent = parent
        self.parent.geometry("400x300")
        self.frame = Frame(parent)

        # List box stuff
        self.index = 2
        self.memory_listener = MemoryListener(self.action)
        self.listbox = Listbox(self.frame)

        # Initialize the UI
        self.initUI()

    def action(self, data):
        print("MemoryWatcher GUI call with data, ", data, "!")
        self.listbox.insert(self.index, data)
        self.index += 1

    def initUI(self):

        # Deal with the UI
        self.parent.title("Memory Watcher")
        self.frame.pack(fill=BOTH, expand=1)

        self.listbox.insert(1, "Memory changed: ") 
        self.listbox.pack(fill=BOTH, expand=1)

def main(program):
    
    # Create object and load contents
    cpu = emulator.CPU(program)
    cpu.load(cpu.text)

    # Create basic TK loop
    root = Tk()
    ex = Main(root, cpu)
    root.geometry("300x460")
    root.mainloop()  


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 gui.py <program.obj>")
        exit(1)
     
    # Get program contents
    program = sys.argv[1]
    fi = open(program, "r")
    program = fi.read()
    fi.close()

    main(program)
