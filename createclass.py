from tkinter import *
from tkinter import simpledialog
import random
import string
import ctypes
import converter
import re
import editor

class CreateClass:

    def show_error(self, message):
        ctypes.windll.user32.MessageBoxW(0,
                                         message,
                                         "Invalid text!", 0x40000 | 0x10)

    def __init__(self, parent, status):
        self.parent = parent
        self.status = status

        self.class_name = simpledialog.askstring(
            "New Class from " + ("Text" if status == 1 else "Scratch"),
         "Write the name for the new class you are creating below.",
         initialvalue="Class #" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5)),
            parent=self.parent.root
            )

        if self.class_name == None:
            return

        allowed_chars = "A-Za-z0-9\.,-; #"
        pattern = re.compile(r"(?!(["+allowed_chars+"]))", re.IGNORECASE)
        final = pattern.findall(self.class_name)

        if len(final) > 1 or not string:
            self.show_error("You must enter text with only the following characters:\n\n" + allowed_chars)
            CreateClass(parent, status)
            return

        lengths = [1, 16]
        if len(self.class_name) > lengths[1] or len(self.class_name) < lengths[0]:
            self.show_error(f"That name is too long or too short. Try to keep names between {str(lengths[0])} and {str(lengths[1])} characters.")
            CreateClass(parent, status)
            return

        if status == 0:
            self.from_scratch()
        elif status == 1:
            self.FromText(self)
            
    def from_scratch(self):
        ctypes.windll.user32.MessageBoxW(0,
                                         "Exception: Unable to produce GUI (RuntimeError).\n\nSupplimented Message: THIS FEATURE IS UNDER CONSTRUCTION. Try again later or update your software.",
                                         "Unable to produce GUI", 0x40000 | 0x10)

    class FromText:
        def set_window_to_size(self, size):
            self.root.geometry(str(size[0]) + "x" + str(size[1]))
        
        def __init__(self, creator):
            self.creator = creator

            self.root = Toplevel(self.creator.parent.root)
            self.name = "New Class from Text: " + str(self.creator.class_name)
            self.root.title(self.name)
            self.size = (450, 450)
            self.root.configure(width=self.size[0],
                                height=self.size[1],
                                bg=self.creator.parent.background
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
                               command=self.exit_button
                               )
            self.exit.place(relx=0.01, y=int(self.size[1] * 0.01))

            self.save = Button(self.root,
                                   bg="green",
                                   fg="white",
                                   text="Save",
                                   font=("Consolas", 10),
                                   command=self.save_button
                                   )
            self.save.place(relx=1 - 0.01, y=int(self.size[1] * 0.01), anchor="ne")

            self.instructions = Label(self.root,
                                      text="Include each name on a separate line",
                                      bg=self.creator.parent.background,
                                      fg="green",
                                      font=("Consolas", 14),
                                      justify=CENTER)
            self.instructions.place(relx=0.5, y=self.size[1]*0.13, anchor="center")

            self.text = Text(self.root,
                             bg="white",
                             fg="black",
                             font=("Consolas", 14),
                             pady=0,
                             padx=0,
                             wrap="word"
                             )
            self.text.tag_configure("center", justify='center')
            self.text.pack(expand=YES, side=BOTTOM, fill=BOTH, pady=((self.size[1] * 0.2), ((self.size[1] * 0.1))), padx=50)
            self.text.insert(INSERT, "Lorem\nIpsum\nDolor\nSit\nAmet")

            self.center_text()

            self.set_window_to_size(self.size)

            self.root.protocol("WM_DELETE_WINDOW", self.exit_button)
            
            self.root.attributes('-topmost', True)
            self.root.update()
            self.root.attributes('-topmost', False)
            self.creator.parent.main.center_window(self.root)

            self.root.mainloop()

        def center_text(self):
            self.text.tag_add("center", 1.0, "end")
            self.root.after(1500, self.center_text)

        def save_button(self):
            self.members = self.text.get(1.0, "end").strip().split("\n")
            convert = converter.Convert(self.creator.class_name, self.members)
            convert.write("text-" + str(self.creator.class_name).lower().replace(" ", "-"))
            self.destroy()
            self.creator.parent.main.refresh_classes()
            self.creator.parent.which_class_text()

        def exit_button(self):
            returned = ctypes.windll.user32.MessageBoxW(0,
                                                    "These changes will not be saved. Are you sure you want to exit? Any information about this class, including the name and its members, will be lost!\n\nPress 'YES' to close and 'NO' to cancel.",
                                                    "Are you sure you want to exit?",
                                                        0x20 | 0x04 | 0x40000 | 0x100)
            if returned == 6: # user pressed yes
                self.destroy()

        def destroy(self):
            self.root.destroy()
