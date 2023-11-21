import __main__
import os
from tkinter import *

import antecedent
import functionality


class ShowResults:
    def add_page(self, what):
        self.previous_menu.page.append(what)

    def zoom_in(self, event=None):
        self.change_font_size(self.font_size + 1)

    def zoom_out(self, event=None):
        if event is not None and isinstance(event, Event) and event.keycode != 189:
            return
        self.change_font_size(self.font_size - 1)

    def mouse_zoom(self, event):
        delta = event.delta
        if delta > 0:
            self.zoom_in("through_scroll")
        if delta < 0:   
            self.zoom_out("through_scroll")

    size_limits = (0, 100)

    def change_font_size(self, new_size: int):
        if new_size >= self.size_limits[1]:
            self.zoom_in_button["state"] = "disabled"
            self.zoom_in_button.configure(bg="#0c5c00")
            return
        if new_size <= self.size_limits[0]:
            self.zoom_out_button["state"] = "disabled"
            self.zoom_out_button.configure(bg="#420000")
            return

        self.zoom_in_button["state"] = "normal"
        self.zoom_in_button.configure(bg="green")

        self.zoom_out_button["state"] = "normal"
        self.zoom_out_button.configure(bg="red")

        self.font_size = new_size
        size_before_transformation = self.previous_menu.size
        self.text.configure(font=("Consolas", self.font_size))
        self.set_window_to_size(size_before_transformation)
        self.zoom_level.configure(text="Zoom: " + str(new_size) + "px")
        print("New zoom level: " + str(new_size))

    def set_window_to_size(self, size):
        self.root.geometry(str(size[0]) + "x" + str(size[1]))

    def __init__(self, previous_menu, clazz, groups=-1, per_group=-1, round_method="UP"):
        self.previous_menu: antecedent.AntecedentGUI = previous_menu
        self.root: Tk = self.previous_menu.root
        self.clazz: __main__.Classes = clazz

        class_header = Label(self.root,
                             bg="#17202A",
                             fg="#EAECEF",
                             text="Class: " + clazz.get_name(),
                             font=("Consolas", 15),
                             pady=5)
        class_header.place(relx=0.5, y=(self.previous_menu.default_size[1] * 0.12), relwidth=1, anchor=CENTER)
        self.add_page(class_header)

        results = functionality.randomize(self.clazz, per_group, groups, True if round_method == "UP" else False)

        settings = Label(self.root,
                         bg=self.previous_menu.background,
                         fg="black",
                         text="Groups: " + str(
                             groups if groups != -1 else len(results.keys())) + "\nPer Group: " + str(per_group),
                         font=("Consolas", 13),
                         justify="left",
                         pady=0
                         )
        settings.place(relx=0.01, y=(self.previous_menu.default_size[1] * 0.20), anchor="w")
        self.add_page(settings)

        self.zoom_in_button = Button(self.root,
                                     bg="green",
                                     fg="black",
                                     text="+",
                                     font=("Consolas", 13),
                                     pady=0,
                                     command=self.zoom_in
                                     )
        self.zoom_in_button.place(relx=(1 - 0.01), y=(self.previous_menu.default_size[1] * 0.20), anchor="e")
        self.add_page(self.zoom_in_button)

        self.zoom_out_button = Button(self.root,
                                      bg="red",
                                      fg="black",
                                      text="-",
                                      font=("Consolas", 13),
                                      pady=0,
                                      command=self.zoom_out
                                      )
        self.zoom_out_button.place(relx=1 - 0.06, y=(self.previous_menu.default_size[1] * 0.20), anchor="e")
        self.add_page(self.zoom_out_button)

        self.zoom_level = Label(self.root,
                                bg=self.previous_menu.background,
                                fg="black",
                                text="Zoom: 16px",
                                font=("Consolas", 13),
                                pady=0
                                 )
        self.zoom_level.place(relx=1 - 0.12, y=(self.previous_menu.default_size[1] * 0.20), anchor="e")
        self.add_page(self.zoom_level)

        self.font_size = 16
        self.text = Text(self.root,
                         bg=self.previous_menu.background,
                         font=("Consolas", self.font_size),
                         pady=0,
                         padx=0,
                         width=50,
                         wrap="word"
                         )
        self.text.pack(expand=YES, side=BOTTOM, fill=BOTH, pady=((self.previous_menu.default_size[1] * 0.25), 0))
        # text.place(relx=0.05, rely=0.25, anchor="nw")
        self.text.tag_configure("secondary", foreground="black")
        self.text.tag_configure("primary", foreground="#5c5c5c")
        self.add_page(self.text)

        self.root.bind("<Control-Key-=>", self.zoom_in)
        self.root.bind("<Control-Key-->", self.zoom_out)
        self.root.bind("<Control-MouseWheel>", self.mouse_zoom)

        y = 0.2
        v = True
        for key in results.keys():
            value = results[key]

            v = not v

            self.text.insert(INSERT, ("" if key == 0 else "\n") +
                             "Group " + str(key + 1) + ": " + str(", ".join(value)),
                             ("secondary" if v == True else "primary")
                             )

            y += 0.05

        self.set_window_to_size(self.previous_menu.size)
        print(str(results))


if __name__ == "__main__":
    os.system("title Group Assigner")
