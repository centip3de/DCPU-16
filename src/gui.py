from tkinter import Tk, Canvas, Frame, BOTH, Button, Toplevel, Entry, Label, END, DISABLED, NORMAL
from opcodes import *
import emulator
import sys

#FIXME: Freezes on infinite loop. :(

class Main():
    def __init__(self, parent, CPU_object):

        # Set up the basic variables and the fram
        self.cpu = CPU_object
        self.parent = parent
        self.parent.title("Main")
        self.frame = Frame(parent)
        self.frame.config(pady = 10)

        # Set up the label at the top
        self.label = Label(self.frame, text = "Registers: ")
        self.label.grid(row = 0, columnspan = 2)

        # Set up the labels and text-boxes for the registers
        self.register_text = []
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
        self.run_button     = Button(self.frame, text = "Run program", width = 25, command = self.run_program)
        self.step_button    = Button(self.frame, text = "Step program", width = 25, command = self.step_program)

        # Pack the buttons
        self.monitor_button.grid(row = 12, columnspan = 2)
        self.run_button.grid(row = 13, columnspan = 2)
        self.step_button.grid(row = 14, columnspan = 2)

        # Pack the frame
        self.frame.pack()

    def step_program(self):

        # Step through the program and update the registers
        self.cpu.step()
        self.update_regs()

        # Disable the buttons for step/run 
        if len(self.cpu.text) == self.cpu.PC:
            self.step_button.config(state = DISABLED)
            self.run_button.config(state = DISABLED)

    def run_program(self):

        # While we're not at the end of the program, step
        while(len(self.cpu.text) != self.cpu.PC):
            self.step_program()

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

    def open_monitor(self):

        # Open the monitor
        self.monitor_window = Toplevel(self.parent)
        self.app = Monitor(self.monitor_window)

class Monitor():
  
    def __init__(self, parent):
        
        # Set up the initial variables/frame stuff
        self.parent = parent        
        self.parent.geometry("640x480")
        self.frame = Frame(parent)
        self.initUI()

    def initUI(self):
     
        # Deal with the UI
        self.parent.title("Monitor")        
        self.frame.pack(fill=BOTH, expand=1)

        # Place holder stuff
        canvas = Canvas(self.frame)
        canvas.create_rectangle(0, 0, 640, 480, outline="#000", fill="#000")
        canvas.create_text(20, 30, anchor="w", font="Purisa", text="Output window... place... thing.", fill="#fff")
        canvas.pack(fill=BOTH, expand=1)


def main(program):
    
    # Create object and load contents
    cpu = emulator.CPU(program)
    cpu.load(cpu.text)

    # Create basic TK loop
    root = Tk()
    ex = Main(root, cpu)
    root.geometry("300x450")
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
