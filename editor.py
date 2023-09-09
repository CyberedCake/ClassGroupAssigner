from tkinter import *
import json
import functionality
import ctypes


class Editor:
    def save_changes(self):
        for key in self.changes.keys():
            value = self.changes[key]
            self.clazz.modify(key=key, value=value)
            print("Saved new value: " + str(key) + "=" + str(value))

    def change(self, path: str, value: str):
        try:
            obj = self.changes[path]
        except KeyError as err:
            obj = value
        if type(obj) == list:
            self.changes[path] = functionality.add_to_list_in_dict(self.changes, path, value)
            return
        self.changes[path] = value

        if self.is_not_saved():
            self.changes_status.configure(fg="#ad8e03", text="! You have unsaved changes !")
        else:
            self.changes_status.configure(fg="#00a816", text="* Your changes are saved *")

    def is_not_saved(self):
        return not dict(self.changes) == dict(self.clazz.get_values())

    def callback(self, variable):
        self.change(path=str(variable), value=variable.get().strip())

    def window_close_event(self):
        if not self.is_not_saved():
            self.destroy()
            return
        text = str(
            """Do you want to save your changes?

NOTE: Pressing no will result in your changes being lost, this is strictly irreversible.
""")
        returned = ctypes.windll.user32.MessageBoxW(0,
                                                    text,
                                                    self.name + " | Unsaved Changes", 0x20 | 0x04)
        print(str(returned))

    def __init__(self, gui, clazz):
        self.root = Toplevel(gui.root)
        self.gui = gui
        self.clazz = clazz

        self.changes = clazz.get_values().copy()

        self.name = "Edit Class: " + str(clazz.get_name())
        self.root.title(self.name)
        self.size = (450, 450)
        self.root.configure(width=self.size[0],
                            height=self.size[1],
                            bg=gui.background
                            )
        self.entry_ids = {}
        self.root.minsize(self.size[0], self.size[1])

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
                           command=lambda: self.destroy()
                           )
        self.exit.place(relx=0.01, y=int(self.size[1] * 0.01))

        self.name_text = Label(self.root,
                               bg=self.gui.background,
                               text="Class Name",
                               font=("Consolas", 16),
                               pady=0)
        self.name_text.place(relx=0.2, rely=0.16, anchor="w")

        name_variable = StringVar(master=self.root, value=str(clazz.get_name()), name="name")
        name_variable_id = name_variable.trace("w", lambda name, index, mode, sv=name_variable: self.callback(sv))
        self.entry_ids[name_variable] = name_variable_id
        self.name_entry = Entry(self.root,
                                textvariable=name_variable,
                                width=20)
        self.name_entry.place(relx=1 - 0.2, rely=0.16, anchor="e")

        self.edit = Label(self.root,
                          text="✎",
                          font=("Consolas", 16))
        self.edit.place(relx=0.5, rely=0.4)

        self.changes_status = Label(self.root,
                                    bg=self.gui.background,
                                    text="* Your changes are saved *",
                                    fg="#00a816",
                                    font=("Consolas", 11),
                                    pady=0)
        self.changes_status.place(relx=0.5, rely=0.105, anchor=CENTER)

        self.root.protocol("WM_DELETE_WINDOW", self.window_close_event)

        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        gui.main.center_window(self.root)

        self.root.mainloop()

    def destroy(self):
        for key in self.entry_ids.keys():
            value = self.entry_ids[key]
            key.trace_vdelete("w", value)
        self.root.destroy()
        del self.changes
        del self.clazz
        del self.root  
