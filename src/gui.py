from tkinter import Tk, Canvas, Frame, BOTH, Button, Toplevel, Entry, Label, END, DISABLED, NORMAL, Listbox, PhotoImage
from opcodes import *
from plugin import *
from math import sin
import emulator
import sys
import threading
import time

class Main():
    def __init__(self, parent, CPU_object):

        # Set up the basic variables and the frame
        self.cpu        = CPU_object
        self.parent     = parent
        self.parent.title("Main")
        self.frame      = Frame(parent)
        self.frame.config(pady = 10)
        self.running    = True

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
        self.stop_button    = Button(self.frame, text = "Stop program", width = 25, command = self.stop_program)

        # Pack the buttons
        self.monitor_button.grid(row = 12, columnspan = 2)
        self.watcher_button.grid(row = 13, columnspan = 2)
        self.run_button.grid(row = 14, columnspan = 2)
        self.step_button.grid(row = 15, columnspan = 2)
        self.stop_button.grid(row = 16, columnspan = 2)

        # Pack the frame
        self.frame.pack()

    def step_program(self):

        # Step through the program and update the registers
        self.cpu.step()
        self.update_regs()
        time.sleep(0.1)

        # Disable the buttons for step/run 
        if len(self.cpu.text) == self.cpu.PC:
            self.step_button.config(state = DISABLED)
            self.run_button.config(state = DISABLED)

    def run(self):

        while(len(self.cpu.text) != self.cpu.PC and self.running):
            self.step_program()

    def stop_program(self):
        self.running = False

    def run_program(self):
        self.running = True
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
        
        self.parent.geometry("378x288")
        self.frame              = Frame(parent)
        self.memory_listener    = MemoryListener(self.action)
        self.width              = 378
        self.height             = 288
        self.img                = PhotoImage(width=self.width, height=self.height)
        self.canvas             = None
        self.number_of_chars    = 0
        self.initUI()

    def draw_text(self, x, y, char):
        #Height of each letter is around 10 pixels, so start there. Then their width is 7 pixels-ish, so increase by that much. So yeah. 
        self.canvas.create_text(x + 10 + (7 * self.number_of_chars), y + 10, text=char, fill="white") 
        self.number_of_chars += 1

    def action(self, data):
        address = data[0]

        # Video mem starts at 0x8000, and since the monitor is 120x90, and (120*90) = 0x2A30, so 0x8000 + 0x2A30 = 0xAA30
        if(address >= 0x8000 and address <= 0xAA30):
            pixel = address - 0x8000
            color = data[1]

            # I don't think I'm getting the RGB values correctly...
            # rrrrrrgggggbbbbb
            r = (color >> 10) & 0b111111
            g = (color >> 5)  & 0b11111
            b = color & 0b11111

            print("[VIDEO]: Pixel,", hex(pixel), "set to,", hex(data[1]), "(#%02x%02x%02x)" % (r,g,b))

            #Calculate the x and y. Offset the y by 3, because the border takes up 3 pixels.
            x = (pixel%126)*3
            y = ((pixel//126) + 3)*3
            print("********************Y = ", y)

            #Update the image with a static pink
            #self.img.put("#FF00FF", (x,y))

            #Update the image with the given RGB, upscale dat stuff.
            #Row 1
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x, y)) 
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x + 1, y)) 
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x + 2, y)) 

            #Row 2
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x, y + 1)) 
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x + 1, y + 1)) 
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x + 2, y + 1)) 

            #Row 3
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x, y + 2)) 
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x + 1, y + 2)) 
            self.img.put("#%02x%02x%02x" % (r*4,g*8,b*8), (x + 2, y + 2)) 

    def initUI(self):
     
        # Deal with the UI
        self.parent.title("Monitor")        
        self.frame.pack(fill=BOTH, expand=1)

        # Now less placeholder-y 
        self.canvas = Canvas(self.frame, width=self.width, height=self.height, bg="#000")
        self.canvas.pack(fill=BOTH, expand=1)

        # Need to create an image so we can place individual pixels 
        self.canvas.create_image((self.width/2, self.height/2), image=self.img, state="normal")

        #Test drawing characters. 
        """
        self.draw_text(0, 0, "H")
        self.draw_text(1, 0, "e")
        self.draw_text(2, 0, "l")
        self.draw_text(3, 0, "l")
        self.draw_text(4, 0, "o")
        self.draw_text(5, 0, "!")
        """

class MemoryWatcher():
    
    def __init__(self, parent):

        # Window stuff
        self.parent = parent
        self.parent.geometry("200x300")
        self.frame = Frame(parent)

        # List box stuff
        self.index = 2
        self.memory_listener = MemoryListener(self.action)
        self.listbox = Listbox(self.frame)

        # Initialize the UI
        self.initUI()

    def action(self, data):
        print("MemoryWatcher GUI call with data, ", data, "!")
        mem = data[0]
        val = data[1]
        self.listbox.insert(hex(self.index), ("[" + hex(mem) + "]: " + hex(val)))
        self.index += 1

    def handle_close(self):
        self.memory_listener.unregister()
        self.parent.quit()

    def initUI(self):

        # Deal with the UI
        self.parent.title("Memory Watcher")
        self.frame.pack(fill=BOTH, expand=1)

        self.listbox.insert(1, "Memory changed: ") 
        self.listbox.pack(fill=BOTH, expand=1)

        # Handle the closing event (unregister the event listener)
        self.parent.protocol("WM_DELETE_WINDOW", self.handle_close)

def main(program):
    
    # Create object and load contents
    cpu = emulator.CPU(program)
    cpu.load(cpu.text)

    # Create basic TK loop
    root = Tk()
    ex = Main(root, cpu)
    root.geometry("300x480")
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
