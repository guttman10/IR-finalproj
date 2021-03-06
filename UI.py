try:
    from Tkinter import Entry, Frame, Label, StringVar
    from Tkconstants import *
    from nltk.stem import PorterStemmer
except ImportError:
    from tkinter import Entry, Frame, Label, StringVar, Toplevel, Button, Text, Scrollbar
    from tkinter.constants import *
    from nltk.stem import PorterStemmer

import TF_IDF


ps = PorterStemmer()
postf = TF_IDF.get_tw(TF_IDF.parseindex())
hide_list = TF_IDF.get_hidden()


def hex2rgb(str_rgb):
    try:
        rgb = str_rgb[1:]

        if len(rgb) == 6:
            r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
        elif len(rgb) == 3:
            r, g, b = rgb[0] * 2, rgb[1] * 2, rgb[2] * 2
        else:
            raise ValueError()
    except:
        raise ValueError("Invalid value %r provided for rgb color." % str_rgb)

    return tuple(int(v, 16) for v in (r, g, b))


class Placeholder_State(object):
    __slots__ = 'normal_color', 'normal_font', 'placeholder_text', 'placeholder_color', 'placeholder_font', 'contains_placeholder'


def add_placeholder_to(entry, placeholder, color="grey", font=None):
    normal_color = entry.cget("fg")
    normal_font = entry.cget("font")

    if font is None:
        font = normal_font

    state = Placeholder_State()
    state.normal_color = normal_color
    state.normal_font = normal_font
    state.placeholder_color = color
    state.placeholder_font = font
    state.placeholder_text = placeholder
    state.contains_placeholder = True

    def on_focusin(event, entry=entry, state=state):
        if state.contains_placeholder:
            entry.delete(0, "end")
            entry.config(fg=state.normal_color, font=state.normal_font)

            state.contains_placeholder = False

    def on_focusout(event, entry=entry, state=state):
        if entry.get() == '':
            entry.insert(0, state.placeholder_text)
            entry.config(fg=state.placeholder_color, font=state.placeholder_font)

            state.contains_placeholder = True

    entry.insert(0, placeholder)
    entry.config(fg=color, font=font)

    entry.bind('<FocusIn>', on_focusin, add="+")
    entry.bind('<FocusOut>', on_focusout, add="+")

    entry.placeholder_state = state

    return state


class SearchBox(Frame):
    def __init__(self, master, entry_width=30, entry_font=None, entry_background="white", entry_highlightthickness=1,
                 button_text="Search", button_ipadx=10, button_background="#009688", button_foreground="white",
                 button_font=None, opacity=0.8, placeholder=None, placeholder_font=None, placeholder_color="grey",
                 spacing=3, command=None):
        Frame.__init__(self, master)

        self._command = command

        self.entry = Entry(self, width=entry_width, background=entry_background, highlightcolor=button_background,
                           highlightthickness=entry_highlightthickness)
        self.entry.pack(side=LEFT, fill=BOTH, ipady=1, padx=(0, spacing))

        if entry_font:
            self.entry.configure(font=entry_font)

        if placeholder:
            add_placeholder_to(self.entry, placeholder, color=placeholder_color, font=placeholder_font)

        self.entry.bind("<Escape>", lambda event: self.entry.nametowidget(".").focus())
        self.entry.bind("<Return>", self._on_execute_command)

        opacity = float(opacity)

        if button_background.startswith("#"):
            r, g, b = hex2rgb(button_background)
        else:
            # Color name
            r, g, b = master.winfo_rgb(button_background)

        r = int(opacity * r)
        g = int(opacity * g)
        b = int(opacity * b)

        if r <= 255 and g <= 255 and b <= 255:
            self._button_activebackground = '#%02x%02x%02x' % (r, g, b)
        else:
            self._button_activebackground = '#%04x%04x%04x' % (r, g, b)

        self._button_background = button_background

        self.button_label = Label(self, text=button_text, background=button_background, foreground=button_foreground,
                                  font=button_font)
        if entry_font:
            self.button_label.configure(font=button_font)

        self.button_label.pack(side=LEFT, fill=Y, ipadx=button_ipadx)

        self.button_label.bind("<Enter>", self._state_active)
        self.button_label.bind("<Leave>", self._state_normal)

        self.button_label.bind("<ButtonRelease-1>", self._on_execute_command)

    def get_text(self):
        entry = self.entry
        if hasattr(entry, "placeholder_state"):
            if entry.placeholder_state.contains_placeholder:
                return ""
            else:
                return entry.get()
        else:
            return entry.get()

    def set_text(self, text):
        entry = self.entry
        if hasattr(entry, "placeholder_state"):
            entry.placeholder_state.contains_placeholder = False

        entry.delete(0, END)
        entry.insert(0, text)

    def clear(self):
        self.entry_var.set("")

    def focus(self):
        self.entry.focus()

    def _on_execute_command(self, event):
        text = self.get_text()
        res = parse_command(text)
        self._command(res)

    def _state_normal(self, event):
        self.button_label.configure(background=self._button_background)

    def _state_active(self, event):
        self.button_label.configure(background=self._button_activebackground)


def ret_not_files(files):
    res=[]
    from os import listdir
    for txt_filename in listdir("Files"):
        txt_filename = txt_filename.strip('.txt')
        if txt_filename not in files:
            res.append(txt_filename)
    return res


def parse_command(buffer):
    templist = []
    not_flag = False
    and_flag = False
    or_flag  = False
    t_flag = True
    par_flag = False
    res = []
    buff = ""
    for word in buffer.split():
        word = word.lower()
        word = ps.stem(word)
        if word == 'not':
            not_flag = True
        elif word == 'or':
            or_flag = True
        elif word == 'and':
            and_flag = True
        if word[0] == '(':
            par_flag = True

        if par_flag:
            buff += word + " "
            if word.endswith(")"):
                for char in buff:
                    if char in "()":
                        buff = buff.replace(char, '')
                par_flag = False
                templist = parse_command(buff)

                if not_flag:
                    templist = ret_not_files(templist)
                    not_flag = False

                if and_flag:
                    res = set(res) & set(templist)
                    res = list(res)
                    and_flag = False

                if or_flag:
                    res = res + list(set(templist) - set(res))
                    or_flag = False

                if word != 'not' and t_flag:
                    res = templist
                    t_flag = False
        else:
            if word in postf:
                templist = []
                for data in postf[word]:
                    templist.append(data[0])
                if not_flag:
                    templist = ret_not_files(templist)
                    not_flag = False
                if and_flag:
                    res = set(res) & set(templist)
                    res = list(res)
                    and_flag = False

                if or_flag:
                    res = res + list(set(templist) - set(res))
                    or_flag = False

        if word != 'not' and t_flag:
            res = templist
            t_flag = False

    return res


def res_win(fname):
    win = Toplevel()
    S = Scrollbar(win)
    T = Text(win, height=25, width=50)
    S.pack(side=RIGHT, fill=Y)
    T.pack(side=LEFT, fill=Y)
    S.config(command=T.yview)
    T.config(yscrollcommand=S.set)

    fptr = open("Files/"+fname, 'r')
    buffer = ''
    for line in fptr:
        buffer += line
    fptr.close()
    T.insert(END, buffer)


def generate_summary(fname):
    f = open("Files/"+fname+".txt", "r")
    buffer = ""
    for i in range(0, 3):
        buffer += f.readline()

    return buffer


if __name__ == "__main__":
    try:
        from Tkinter import Tk
        from tkMessageBox import showinfo
    except ImportError:
        from tkinter import Tk
        from tkinter.messagebox import showinfo


    def open_search_res(res):
        # create child window
        win = Toplevel()
        # display message
        res_text = StringVar()
        Label(win, textvariable=res_text).pack()
        i = 0
        for data in res:
            if data + ".txt" not in hide_list:
                Button(win, text=data, command=lambda fname=data + ".txt": res_win(fname)).pack()

                Label(win, text=generate_summary(data)).pack()
                i += 1
                if i >= 4:
                    break
        res_text.set("Found " + str(len(res)) + " Files\n Showing " + str(i) + "\n")


    root = Tk()
    SearchBox(root, command=open_search_res, placeholder="Type and press enter", entry_highlightthickness=0).pack(
        pady=6,
        padx=3)

    root.mainloop()
