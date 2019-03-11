from os import listdir
import os
from tkinter import *
import TF_IDF
master = Tk()


def add_file(fname, win):
    fin = open("Source/"+fname, "r")
    fout = open("Files/"+fname, "w")
    for line in fin:
        fout.write(line)
    fout.close()
    fin.close()
    os.remove("Source/"+fname)
    TF_IDF.index_text_file()
    win.destroy()


def hide_file(fname, win):
    f = open("hidden.txt", "a")
    f.write(fname+"\n")
    win.destroy()


def unhide_all(win):
    f = open("hidden.txt", "w")
    f.close()
    win.destroy()


def hide_files():
    win = Toplevel()
    res_text = "Select file to hide"
    Label(win, text=res_text).pack()
    hide_list = TF_IDF.get_hidden()
    for txt_filename in listdir("Files"):
        if txt_filename not in hide_list:
            Button(win, text=txt_filename, command=lambda data=txt_filename: hide_file(data, win)).pack()
    Button(win, text="Unhide all", command= lambda: unhide_all(win)).pack()


def add_files():
    win = Toplevel()
    res_text = "Select file to add"
    flag = False
    Label(win, text=res_text).pack()
    for txt_filename in listdir("Source"):
        flag = True
        Button(win, text=txt_filename, command=lambda data=txt_filename: add_file(data, win)).pack()
    if flag:
        Button(win, text="Add all Files", command=lambda: add_all_files(win)).pack()
    else:
        Label(win, text="No files found").pack()


def add_all_files(win):
    for txt_filename in listdir("Source"):
            fptr = open("Source/" + txt_filename, "r")
            pfile = open("Files/" + txt_filename, "w")
            for line in fptr:
                pfile.write(line)

            fptr.close()
            pfile.close()
            os.remove("Source/" + txt_filename)
    TF_IDF.index_text_file()
    win.destroy()


b_hide = Button(master, text="Hide Files", command=hide_files)
b_hide.pack()
b_add = Button(master, text="Add Files", command=add_files)
b_add.pack()
mainloop()
