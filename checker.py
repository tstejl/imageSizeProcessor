from tkinter import *
from tkinter import filedialog
import glob
from PIL import Image
import shutil
import os
from pathlib import Path


class PicAnalysis(object):
    def __init__(self, master):
        self.img_list = []
        self.move_list = []
        self.cwd = ""
        self.new_dir_name = "tmp"
        frame = Frame(master)
        frame.pack()

        self.button_1 = Button(frame, text="Import",
                               command=self.import_file)
        #self.button_1.pack(side=LEFT)
        self.button_1.grid(row=0, pady=2)

        self.button_2 = Button(frame, text="Analyze",
                               command=self.analyze_pic)
        #self.button_2.pack(side=LEFT)
        self.button_2.grid(row=0, column=1, pady=2)

        self.button_3 = Button(frame, text="Move",
                               command=self.move_pic)
        #self.button_3.pack(side=LEFT)
        self.button_3.grid(row=0, column=2, pady=2)

        self.button_4 = Button(frame, text="Quit",
                               command=frame.quit)
        #self.button_4.pack(side=LEFT)
        self.button_4.grid(row=0, column=3, pady=2)

        self.textbox = Text(frame, width=70, height=5)
        #self.textbox.pack(side=TOP)
        self.textbox.grid(row=1, columnspan=4, pady=2, padx=5)
        self.textbox.configure(state='disabled')

    def print_to_box(self, str):
        self.textbox.configure(state='normal')
        self.textbox.insert('end', str)
        self.textbox.configure(state='disabled')

    def import_file(self):
        self.img_list = []
        path = filedialog.askdirectory()
        files = glob.glob(path + "\\*")
        for file in files:
            if os.path.isfile(file):  # avoid dealing with subdirectories
                self.img_list.append(file)
        out_str = str(len(self.img_list)) + " Images found in " + path + "\n"
        self.cwd = path
        self.print_to_box(out_str)

    def analyze_pic(self):
        count = 0
        self.move_list = []
        for file in self.img_list:
            img = Image.open(file)
            w, h = img.size
            w = int(w)
            h = int(h)
            r = w / h
            if 1.77 <= round(r, 2) <= 1.78:  # w/h = 16/9
                c = file.rfind("\\")
                count += 1
                self.move_list.append(file)
        out_str = str(count) + " images have 16/9 ratio.\n"
        self.print_to_box(out_str)

    def move_pic(self):
        new_dir = str(Path(self.cwd).parent) + "\\" + self.new_dir_name
        if len(self.move_list) != 0:
            os.makedirs(new_dir, exist_ok=True)
            count = 0
            for file in self.move_list:
                shutil.move(file, new_dir)
                count += 1
            out_str = str(count) + " images moved to " + self.new_dir_name + "\n"
            self.print_to_box(out_str)
        else:
            self.print_to_box("Directory is not created.\n")

root = Tk()
Title = root.title("Image Size Checker")
app = PicAnalysis(root)
root.mainloop()
