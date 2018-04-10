from tkinter import *
from tkinter import filedialog
import glob
from PIL import Image, ImageTk
import shutil
import os
from pathlib import Path
import resizer

class PicAnalysis(object):
    def __init__(self, master):
        self.img_list = []
        self.move_list = []
        self.cwd = ""
        self.new_dir_name = "tmp"

        self.canvas = Canvas(master, background='grey')
        self.canvas.grid(row=0,column=1)

        #save a reference to avoid GC
        self.thumbnail = None
        self.img = None

        self.resizer = None

        frame = Frame(master)
        frame.grid(row=0,column=0, sticky="n")

        self.btn_import = Button(frame, text="Import", command=self.import_file)
        self.btn_import.grid(row=0, pady=2, sticky="nwe", columnspan=3)

        self.btn_analyze = Button(frame, text="Analyze",
                               command=self.analyze_pic, state='disabled')
        self.btn_analyze.grid(row=1, column=0, pady=2, sticky="we", columnspan=3)

        self.btn_move = Button(frame, text="Move",command=self.move_pic)
        self.btn_move.grid(row=2, column=0, pady=2, sticky="we", columnspan=3)


        self.btn_resize = Button(frame, text="Resize", command=self.resize_display)
        self.btn_resize.grid(row=3, column=0, pady=2, sticky="we")

        self.btn_next = Button(frame, text="Next", command=self.next_pic)
        self.btn_next.grid(row=3, column=1, pady=2, sticky="we")

        self.btn_save = Button(frame, text="Save", command=self.save_pic)
        self.btn_save.grid(row=3, column=2, pady=2, sticky="we")

        self.btn_clear = Button(frame, text="Clear All", command=self.clear_all)
        self.btn_clear.grid(row=9, column=0, pady=2, sticky='swe', columnspan=3)

        #variables associated with checkbuttons
        self.var_top = IntVar()
        self.var_right = IntVar()
        self.var_bottom = IntVar()
        self.var_left = IntVar()

        self.check_top = Checkbutton(frame, text="top", variable=self.var_top)
        self.check_top.grid(row=4, column=0, pady=2, sticky='we')
        self.check_right = Checkbutton(frame, text="right", variable=self.var_right)
        self.check_right.grid(row=4, column=1, pady=2, sticky='we')
        self.check_bottom = Checkbutton(frame, text="bottom", variable=self.var_bottom)
        self.check_bottom.grid(row=5, column=0, pady=2, sticky='we')
        self.check_left = Checkbutton(frame, text="left", variable=self.var_left)
        self.check_left.grid(row=5, column=1, pady=2, sticky='we')

        self.btn_reex = Button(frame, text="Re-modify", command=self.reex)
        self.btn_reex.grid(row=6, column=1, pady=2, sticky="we")

        self.btn_exit = Button(frame, text="Exit", command=frame.quit)
        self.btn_exit.grid(row=10, column=0, pady=2, sticky='swe', columnspan=3)

        self.text_msgbox = Text(frame, width=40, height=5)
        self.text_msgbox.grid(row=7, sticky='we', columnspan=3)

        self.disable_widget(self.text_msgbox)
        self.disable_widget(self.btn_next)
        self.disable_widget(self.btn_save)
        self.disable_widget(self.btn_resize)
        self.disable_widget(self.btn_analyze)
        self.disable_widget(self.btn_move)
        self.disable_widget(self.btn_clear)
        self.disable_widget(self.btn_reex)

    def clear_all(self):
        self.img_list = []
        self.move_list = []
        self.thumbnail = None
        self.img = None
        self.resizer = None
        self.canvas.delete("all")
        self.canvas.configure(width=378, height=265)
        self.enable_widget(self.text_msgbox)
        self.text_msgbox.delete('1.0', END)
        self.disable_widget(self.text_msgbox)
        self.disable_widget(self.btn_next)
        self.disable_widget(self.btn_save)
        self.disable_widget(self.btn_resize)
        self.disable_widget(self.btn_analyze)
        self.disable_widget(self.btn_move)
        self.disable_widget(self.btn_clear)
        self.disable_widget(self.btn_reex)
        self.enable_widget(self.btn_import)

    def print_to_box(self, str):
        self.enable_widget(self.text_msgbox)
        self.text_msgbox.insert('end', str)
        self.disable_widget(self.text_msgbox)

    def test(self):
        print('test')

    def enable_widget(self, btn):
        btn.configure(state='normal')

    def disable_widget(self, btn):
        btn.configure(state='disabled')

    def resize_display(self, sides=None):
        self.resizer = resizer.Resizer(self.img_list[0], logger=True)
        self.enable_widget(self.btn_reex)
        if sides:
            self.resizer.manually_set_edges_to_modify(sides)
        if self.resizer.expand_flag:
            self.canvas.configure(width=1440, height=810)
            try:
                self.img = self.resizer.expand_or_crop_image()
            except:
                self.canvas.delete('all')
                self.print_to_box("Error occurred.\n")


            img_thumbnail = self.img.resize((1440, 810))
        else:
            ratio = self.resizer.old_width/self.resizer.old_height
            self.canvas.configure(width=1440,
                                height=int(1440/ratio))
            self.img = Image.open(self.img_list[0])
            img_thumbnail = self.img.resize(
            (1440, int(1440/ratio)))

        self.thumbnail = ImageTk.PhotoImage(img_thumbnail)
        self.canvas.create_image(0,0, image=self.thumbnail, anchor='nw', tags='img')

        if self.resizer.expand_flag is False:
            rect = [0, int(self.resizer.modify[0]/ratio),
            1440, int(1440/ratio-self.resizer.modify[2]/ratio)]
            self.canvas.create_rectangle(
            rect[0], rect[1], rect[2], rect[3], tags='rect')

        self.enable_widget(self.btn_save)

        if len(self.img_list) > 1:
            self.enable_widget(self.btn_next)

    def next_pic(self):
        self.canvas.delete('all')
        if len(self.img_list) > 1:
            self.img_list = self.img_list[1:]
            self.resize_display()
        else:
            self.disable_widget(self.btn_next)

    def save_pic(self):
        img = self.resizer.expand_or_crop_image()
        self.resizer.save_and_overwrite_img(img)
        self.next_pic()

    def reex(self):
        self.canvas.delete('all')
        self.resize_display([self.var_top.get(), self.var_right.get(),
            self.var_bottom.get(), self.var_left.get()])

    def import_file(self):
        self.img_list = []
        path = filedialog.askdirectory()
        files = glob.glob(path + "\\*")
        for file in files:
            if os.path.isfile(file):  # avoid dealing with subdirectories
                if os.path.splitext(file)[1][1:] == 'jpg' or\
                os.path.splitext(file)[1][1:] == 'png':
                    self.img_list.append(file)
        out_str = str(len(self.img_list)) + " Images found in " + path + "\n"
        self.cwd = path
        self.print_to_box(out_str)

        self.enable_widget(self.btn_resize)
        self.enable_widget(self.btn_analyze)
        self.enable_widget(self.btn_clear)

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
        self.enable_widget(self.btn_move)

    def move_pic(self):
        new_dir = str(Path(self.cwd)) + "\\" + self.new_dir_name
        if len(self.move_list) != 0:
            os.makedirs(new_dir, exist_ok=True)
            count = 0
            for file in self.move_list:
                shutil.move(file, new_dir)
                count += 1
            out_str = str(count) + " images moved to " + new_dir + "\n"
            self.print_to_box(out_str)
        else:
            self.print_to_box("Directory not created.\n")

root = Tk()
Title = root.title("Image Size Processor")
app = PicAnalysis(root)
root.mainloop()
