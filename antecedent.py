import threading
from tkinter import *
import os
import random
import nameviewer
import resultsgui
import ctypes
import editor


def start_thread(lamb):
    thread = threading.Thread(target=lamb, args=())
    thread.start()
    thread.join()


class AntecedentGUI:
    def on_window_change(self, event):
        self.size = (self.root.winfo_width(), self.root.winfo_height())

    def clear(self):
        for element in self.page:
            element.destroy()
        self.page.clear()

    def put_back_button(self, func):
        if func is None:
            self.back = Button(self.root)
            return
        self.back = Button(self.root,
                           bg="#17202A",
                           fg="#EAECEF",
                           text="Back",
                           font=("Consolas", 15),
                           command=func
                           )
        self.back.place(relx=0.01, rely=0.01)
        self.page.append(self.back)

    def __init__(self, main, classes, loader):
        self.root = Tk()
        self.main = main
        self.classes = classes

        random.seed(main.seed)

        self.name = "Class Group Assigner"
        self.root.title(self.name)
        self.default_size = (550, 550)
        self.size = self.default_size
        self.root.resizable(width=True, height=True)
        self.background = "#cfcfcf"
        self.root.configure(width=self.size[0],
                            height=self.size[1],
                            bg=self.background)
        self.root.minsize(self.size[0], self.size[1])

        self.back = Button(self.root)

        self.header = Label(self.root,
                            bg="#17202A",
                            fg="#EAECEF",
                            text=self.name,
                            font=("Consolas", 25),
                            pady=5)
        self.header.place(relwidth=1)

        self.page = []
        self.which_class_text()

        self.root.bind("<Configure>", self.on_window_change)

        loader.await_request_exit()
        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        self.main.center_window(self.root)

        self.root.mainloop()

    def which_class_text(self):
        self.clear()

        class_question = Label(self.root,
                               text="Which class?",
                               font=("Consolas", 20),
                               bg=self.background,
                               pady=5)
        class_question.place(relx=0.05, rely=0.13)
        self.page.append(class_question)

        version = Label(self.root,
                        text="Version: " + self.main.updater.version,
                        font=("Consolas", 8),
                        bg="#b8b8b8",
                        pady=0
                        )
        version.place(relx=1, rely=0.95, anchor="e")

        is_up_to_date = self.main.updater.is_up_to_date
        distance = self.main.updater.distance_out_of_date
        is_latest = Label(self.root,
                          text=("On the latest version!" if is_up_to_date is True else f"Outdated by {str(self.main.updater.distance_out_of_date)} versions!" if distance != -1 else "Outdated software!"),
                          font=("Consolas", 8),
                          bg="#b8b8b8",
                          fg=("#38803e" if is_up_to_date is True else "#803838")
                          )
        is_latest.place(relx=1, rely=0.98, anchor="e")

        x = 0.10
        y = 0.25

        for clazz in self.classes:
            button = Button(self.root,
                            text=clazz.get_name(),
                            font=("Consolas", 14),
                            fg="black",
                            bg="orange",
                            pady=0.1,
                            command=lambda clazz1=clazz:
                            self.which_class_execution(clazz1)
                            )
            button.place(relx=x, rely=y)
            self.page.append(button)
            y += 0.08
            if y + 0.08 > 1:
                y = 0.25
                x += 0.35

    def which_class_execution(self, clazz):
        self.clear()

        class_header = Label(self.root,
                             bg="#17202A",
                             fg="#EAECEF",
                             text="Class: " + clazz.get_name(),
                             font=("Consolas", 15),
                             pady=5)
        class_header.place(relx=0.5, y=(self.default_size[1] * 0.12), relwidth=1, anchor=CENTER)
        self.page.append(class_header)

        self.selected_class = clazz

        start_text = """
It is necessary to fill out *at least*
one of the text fields above. You can
leave one blank if you wish but at least
one must have information.
"""
        start = Label(self.root,
                      bg=self.background,
                      fg="red",
                      text=start_text,
                      font=("Consolas", 11),
                      pady=5
                      )
        start.place(relx=0.5, rely=0.46, anchor=CENTER)
        self.page.append(start)

        self.groups_text = Label(self.root,
                                 bg=self.background,
                                 text="Amount of Groups",
                                 font=("Consolas", 16),
                                 pady=5)
        self.groups_text.place(relx=0.2, rely=0.22, anchor="w")
        self.page.append(self.groups_text)

        self.groups_entry = Entry(self.root, width=10)
        self.groups_entry.place(relx=1 - 0.2, rely=0.22, anchor="e")
        self.page.append(self.groups_entry)

        self.per_group_text = Label(self.root,
                                    bg=self.background,
                                    text="Amount per Group",
                                    font=("Consolas", 16),
                                    pady=5)
        self.per_group_text.place(relx=0.2, rely=0.28, anchor="w")
        self.page.append(self.per_group_text)

        self.per_group_entry = Entry(self.root, width=10)
        self.per_group_entry.place(relx=1 - 0.2, rely=0.28, anchor="e")
        self.page.append(self.per_group_entry)

        self.round_method = StringVar(self.root, "DOWN")
        round_method_text = Checkbutton(self.root,
                                   text="Round Up?",
                                        bg=self.background,
                                        font=("Consolas", 16),
                                        variable=self.round_method,
                                        onvalue="UP",
                                        offvalue="DOWN",
                                        pady=0,
                                        padx=0)
        round_method_text.place(relx=0.5, rely=0.35, anchor=CENTER)
        self.page.append(round_method_text)

        open_editor = Button(self.root,
                             bg="gray",
                             fg="white",
                             text="Open class editor",
                             font=("Consolas", 12),
                             pady=5,
                             command=lambda: editor.Editor(self, clazz))
        open_editor.place(relx=0.5, rely=0.9, anchor=CENTER)
        self.page.append(open_editor)

        view_names = Button(self.root,
                            bg="gray",
                            fg="white",
                            text="View names in class",
                            font=("Consolas", 12),
                            pady=5,
                            command=lambda: nameviewer.NameViewer(self, clazz))
        view_names.place(relx=0.5, rely=0.8, anchor=CENTER)
        self.page.append(view_names)

        generate_button = Button(self.root,
                                 bg="green",
                                 fg="white",
                                 text="Generate!",
                                 font=("Consolas", 24),
                                 pady=5,
                                 command=lambda:
                                 self.show_results(clazz)
                                 )
        generate_button.place(relx=0.5, rely=0.65, anchor=CENTER)
        self.page.append(generate_button)

        self.put_back_button(self.which_class_text)

    def show_results(self, clazz):
        groups = -1 if self.groups_entry.get() == "" else int(self.groups_entry.get())
        per_group = -1 if self.per_group_entry.get() == "" else int(self.per_group_entry.get())
        round_method = self.round_method.get()

        error = ""
        if groups == -1 and per_group == -1:
            error = "At least one option has to have a value."

        if groups > len(clazz.get_members()):
            error = "Cannot have more groups than members in the class. (" + str(groups) + " groups requested, " + str(
                len(clazz.get_members())) + " class members)"

        if per_group > len(clazz.get_members()):
            error = "Cannot have more per group than members in the class. (" + str(
                per_group) + " per group requested, " + str(len(clazz.get_members())) + " class members)"

        if not error == "":
            returned = ctypes.windll.user32.MessageBoxW(0, str(error), "An exception occurred!", 0x10 | 0x00)
            return

        self.clear()
        self.put_back_button(lambda: self.which_class_execution(clazz))
        resultsgui.ShowResults(self, clazz, groups, per_group, round_method)


if __name__ == "__main__":
    os.system("title Group Assigner")
