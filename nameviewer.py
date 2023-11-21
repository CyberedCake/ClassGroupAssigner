import os
import random
from tkinter import *


class NameViewer:
    def __init__(self, gui, clazz):
        self.root = Toplevel(gui.root)
        self.gui = gui
        self.clazz = clazz

        self.name = "View Class Members: " + str(clazz.get_name())
        self.root.title(self.name)
        self.size = (450, 450)
        self.root.configure(width=self.size[0],
                            height=self.size[1],
                            bg=gui.background
                            )
        self.root.minsize(self.size[0], self.size[1])
        self.root.grab_set()

        self.header = Label(self.root,
                            bg="#17202A",
                            fg="#EAECEF",
                            text=self.name,
                            font=("Consolas", 12),
                            pady=5)
        self.header.place(relwidth=1)

        self.exit = Button(self.root,
                           bg="red",
                           fg="white",
                           text="Exit",
                           font=("Consolas", 10),
                           command=lambda: self.root.destroy()
                           )
        self.exit.place(relx=0.01, y=int(self.size[1] * 0.01))

        self.shuffle = Button(self.root,
                              bg="green",
                              fg="white",
                              text="Shuffle",
                              font=("Consolas", 12),
                              command=lambda: self.show_list(True)
                              )
        self.shuffle.place(relx=0.2, y=65, anchor=CENTER)

        self.show_list(False)

        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        gui.main.center_window(self.root)

        self.root.mainloop()

    def item_selected(self, event):
        widget = event.widget
        index = int(widget.curselection()[0])
        value = widget.get(index)
        print(f"Item {index}: {value}")

    # noinspection PyUnresolvedReferences
    def show_list(self, shuffle: bool):
        try:
            self.scrollbar.destroy()
            self.members.destroy()
            self.window_size.destroy()
        except Exception as err:
            pass

        self.scrollbar = Scrollbar(self.root)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # 0.485, 65

        self.members = Listbox(self.root,
                               yscrollcommand=self.scrollbar.set,
                               font=("Consolas", 12),
                               height=18,
                               width=30,
                               justify="center",
                               activestyle="underline",
                               highlightcolor="blue",
                               highlightthickness=1,
                               exportselection=False,
                               )
        self.members.bind('<<ListboxSelect>>', self.item_selected)

        members_list = self.clazz.get_members()
        if shuffle:
            random.shuffle(members_list)

        for member in members_list:
            self.members.insert(END, str(member))
        # self.members.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.members.pack(padx=5, pady=(100, 10), fill=BOTH, expand=True)

        self.window_size = Label(self.root,
                                 fg="blue",
                                 bg=self.gui.background,
                                 text="Members: " + str(len(members_list)),
                                 font=("Consolas", 12)
                                 )
        self.window_size.place(relx=0.75, y=65, anchor=CENTER)

        self.seed_label = Label(self.root,
                                fg="black",
                                bg=self.gui.background,
                                text="Seed: " + str(self.gui.main.seed),
                                font=("Consolas", 10)
                                )
        self.seed_label.place(relx=0.95, y=self.size[1] - (self.size[1] * 0.01), anchor="e")

        self.scrollbar.config(command=self.members.yview)


if __name__ == "__main__":
    os.system("title Group Assigner")
