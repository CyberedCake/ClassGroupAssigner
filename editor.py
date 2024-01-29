import ctypes
import functools
import re
from tkinter import *
from tkinter import simpledialog
from typing import Optional


class SanitationError:

    def __init__(self, integer_representation: int, obj=None):
        self.integer_representation = integer_representation
        self.obj = obj

    def get_integer_representation(self):
        return self.integer_representation

    def get_stored_object(self):
        return self.obj


SUCCESS = SanitationError(0)
INVALID_CHARACTERS = SanitationError(1)
MEMBER_ALREADY_EXISTS = SanitationError(2)
NAME_TOO_LONG_OR_TOO_SHORT = SanitationError(3, [2, 32]) # object is min and max length of string



class Editor:
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
        self.original = self.clazz.get_values()
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
                           command=lambda: self.window_close_event()
                           )
        self.exit.place(relx=0.01, y=int(self.size[1] * 0.01))

        self.save = None

        self.name_text = Label(self.root,
                               bg=self.gui.background,
                               text="Class Name",
                               font=("Consolas", 16),
                               pady=0)
        self.name_text.place(relx=0.2, rely=0.16, anchor="w")

        self.name_entry = Entry(self.root,
                                textvariable=self.new_variable(
                                    StringVar(master=self.root, value=str(clazz.get_name()), name="name")),
                                width=20)
        self.name_entry.place(relx=1 - 0.2, rely=0.16, anchor="e")

        self.changes_status = Label(self.root,
                                    bg=self.gui.background,
                                    text="* Your changes are saved *",
                                    fg="#00a816",
                                    font=("Consolas", 11),
                                    pady=0)
        self.changes_status.place(relx=0.5, rely=0.105, anchor=CENTER)

        self.root.protocol("WM_DELETE_WINDOW", self.window_close_event)
        self.root.bind("<Control-s>", lambda e: self.save_changes())

        self.outer_frame = Frame(self.root)
        self.canvas = Canvas(self.outer_frame)
        self.inner_frame = Frame(self.canvas)

        self.scrollbar = Scrollbar(self.outer_frame, orient="vertical", command=self.canvas.yview)

        self.canvas.create_window((0, 0), window=self.inner_frame, anchor='nw')
        self.canvas.bind("<MouseWheel>", self.use_mousewheel)

        self.add_member = Button(self.canvas,
                                 bg="#208f14",
                                 fg="white",
                                 text="+",
                                 font=("Consolas", 20),
                                 padx=5,
                                 command=self.add
                                 )
        self.add_member.place(relx=0.9, rely=0.87, anchor="center")

        self.refresh_list(True)

        self.inner_frame.update()
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=LEFT, expand=True, fill=BOTH, pady=5)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.outer_frame.pack(padx=5, pady=(100, 20), fill=BOTH, expand=True)

        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        gui.main.center_window(self.root)

        self.root.mainloop()


    def callback(self, variable):
        self.change(path=str(variable), value=variable.get().strip())

    def new_variable(self, var: StringVar):
        var_id = var.trace_add("write", lambda name, index, mode, sv=var: self.callback(sv))
        self.entry_ids[str(var)] = {'variable': var, 'trace_id': str(var_id)}
        return var

    def find_differences(self):
        return list(set(self.changes["members"]) - set(self.clazz.get_members()))

    def change(self, path: str, value: Optional[str], old_if_listed: str = None):
        if path == "members":
            if value is not None:
                self.changes[path].append(f"+{value}")
            if old_if_listed is not None:
                for member in self.find_differences():
                    if f"+{old_if_listed}" in member and old_if_listed != value:
                        self.changes["members"].remove(member)
                if old_if_listed in self.changes["members"] and old_if_listed != value:
                    self.changes["members"].remove(old_if_listed)
            self.changes[path].append(f"-{old_if_listed}")
            self.refresh_list()
        else:
            self.changes[path] = value
            

        print(f"Changed path={str(path)}, is_saved={str(self.is_saved())}, new=" + str(value))
        print("Changes: " + str(self.changes))
        self.update_save_status()

    # noinspection PyMethodMayBeStatic
    def show_invalid(self, reason: str):
        ctypes.windll.user32.MessageBoxW(0,
                                         reason,
                                         "Invalid text!", 0x40000 | 0x10)

    def request_input(self, dialog_title, dialog_text, dialog_initial_value: str | None, return_function):
        new_value = simpledialog.askstring(dialog_title, dialog_text,
                                           initialvalue=dialog_initial_value, parent=self.root)
        if new_value is None:
            return None

        sanitation = self.is_sanitary(new_value)
        error = sanitation[0]
        if error == INVALID_CHARACTERS:
            self.show_invalid("You must enter text with only the following characters:\n\nA-Za-z0-9.,-'")
            return_function(preset_value=sanitation[1])
            return None

        if error == MEMBER_ALREADY_EXISTS:
            self.show_invalid(
                "That member is already a person in your class. Try a different name or a variation of that name.")
            return_function(preset_value=sanitation[1])
            return None

        if error == NAME_TOO_LONG_OR_TOO_SHORT:
            lengths = NAME_TOO_LONG_OR_TOO_SHORT.get_stored_object()
            self.show_invalid(
                f"That name is too long or too short. Try to keep names between {str(lengths[0])} and {str(lengths[1])} characters.")
            return_function(preset_value=sanitation[1])
            return None

        return new_value



    def edit(self, value, preset_value=None):
        inputted = self.request_input("Edit Student", "Please enter the new value for '" + value + "'", preset_value if preset_value is not None else str(value), functools.partial(self.edit, value))
        if inputted is None:
            return
        self.change("members", inputted, value)

    def remove(self, value):
        self.change("members", None, value)

    def add(self, preset_value=None):
        inputted = self.request_input("Add Student", "Please enter a name for a student to add to the list.\n\nRestrictions: A-Za-z0-9.,-'", preset_value, self.add)
        if inputted is None:
            return
        self.change("members", inputted, None)

    def is_sanitary(self, string: str):
        if string is None:
            return
        pattern = re.compile(r"(?!([A-Za-z0-9\.,-; ]))", re.IGNORECASE)
        final = pattern.findall(string)
        if len(final) > 1 or not string:
            return [INVALID_CHARACTERS, string]
        if string in self.changes["members"] or f"+{string}" in self.changes["members"]:
            return [MEMBER_ALREADY_EXISTS, string]
        lengths = NAME_TOO_LONG_OR_TOO_SHORT.get_stored_object()
        if len(string) > lengths[1] or len(string) < lengths[0]:
            return [NAME_TOO_LONG_OR_TOO_SHORT, string]
        return [SUCCESS, string]

    def refresh_list(self, first=False):
        for widgets in self.inner_frame.winfo_children():
            widgets.destroy()

        members_list = self.clazz.get_members() if first == True else self.changes["members"]
        for index, member in enumerate(members_list):
            possible_action = str(member)[0:1]
            if possible_action == "-":
                index -= 1
                continue

            if possible_action == "+":
                member = member[1:]

            edit = Button(self.inner_frame,
                          text="E",
                          bg="yellow",
                          font=("Consolas", 10),
                          command=functools.partial(self.edit, member)
                          )
            edit.grid(column=0, row=index)

            remove = Button(self.inner_frame,
                            text="R",
                            bg="red",
                            fg="white",
                            font=("Consolas", 10),
                            command=functools.partial(self.remove, member)
                            )
            remove.grid(column=1, row=index)

            display = Label(self.inner_frame,
                            text=str(member),
                            bg=self.gui.background,
                            font=("Consolas", 12)
                            )
            display.grid(column=2, row=index)

        self.inner_frame.update()

        self.canvas.configure(scrollregion=(0, 0, 0, float(self.inner_frame.winfo_height())))

    def use_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def update_save_status(self):
        if not self.is_saved():
            self.changes_status.configure(fg="#ad8e03", text="! You have unsaved changes !")
            if self.save is None:
                self.save = Button(self.root,
                                   bg="green",
                                   fg="white",
                                   text="Save",
                                   font=("Consolas", 10),
                                   command=lambda: self.save_changes()
                                   )
                self.save.place(relx=1 - 0.01, y=int(self.size[1] * 0.01), anchor="ne")
        else:
            self.changes_status.configure(fg="#00a816", text="* Your changes are saved *")
            if self.save is not None:
                self.save.destroy()
                self.save = None

    def is_saved(self):
        changes = dict(self.changes)
        original = dict(self.original)
        return (changes == original) and list(changes["members"]) == list(original["members"])

    def save_changes(self):
        if self.is_saved():
            print("*** Values are already saved. Not executing save again! ***")
            return

        print("SAVING_CHANGES...")
        for key in self.changes.keys():
            if key == "members":
                continue
            value = self.changes[key]
            self.clazz.modify(key=key, value=value)
            print("Saved new value: " + str(key) + "=" + str(value))
        for member in self.changes["members"]:
            action = member[0:1]
            member = member[1:]
            if action == "+":
                self.clazz.add_member(member)
                print(f"MEMBER_ADDED:{str(member)}")
            elif action == "-":
                if member in self.clazz.get_members():
                    self.clazz.remove_member(member)
                print(f"MEMBER_REMOVED:{str(member)}")

        self.changes = self.clazz.get_values().copy()
        self.original = self.clazz.get_values()
        self.update_save_status()

        if str(self.changes["name"]) is not self.name.replace("Edit Class: ", ""):
            self.name = "Edit Class: " + str(self.changes["name"])
            self.header.configure(text=self.name)

    def window_close_event(self):
        self.update_save_status()

        if self.is_saved():
            self.destroy()
            return
        text = str(
            """Do you want to save your changes?

NOTE: Pressing no will result in your changes being lost, this is strictly irreversible.
""")
        returned = ctypes.windll.user32.MessageBoxW(0,
                                                    text,
                                                    self.name + " | Unsaved Changes", 0x20 | 0x03)
        if returned == 6:  # user pressed yes
            self.save_changes()
            clazz = self.clazz
            self.destroy()
            self.gui.which_class_execution(clazz)
        elif returned == 7:  # user pressed no
            self.destroy()
        # user pressed cancel

    def destroy(self):
        print(str(self.entry_ids))
        for key in self.entry_ids.keys():
            value = self.entry_ids[key]
            value['variable'].trace_remove("write", value['trace_id'])
        self.root.destroy()
        del self.changes
        del self.clazz
        del self.root
