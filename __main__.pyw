import logging
import traceback

import antecedent as guiClass
import functionality as func
import os
import json
import time
import threading
import urllib.request
import ctypes
import copy
from tkinter import *


def get_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__)))


class Classes:
    @staticmethod
    def get_files(directory: str) -> list:
        if directory is None:
            directory = get_path()
        else:
            directory = get_path() + directory

        names = []
        for file in os.listdir(directory):
            names.append(Classes(directory + file))

        return names

    def __init__(self, file: str):
        self.file = file
        opened_file = open(file, "r")
        self.values = json.load(opened_file)
        opened_file.close()

    def modify(self, key, value):
        read_file = open(self.file, "r")
        self.values = json.load(read_file)
        self.values[key] = value
        read_file.close()
        self.set_to_dict(self.values)

    def set_to_dict(self, dictionary: dict):
        self.values = dictionary
        json_data = json.dumps(self.values, indent=4)
        write_file = open(self.file, "w")
        write_file.writelines(json_data)
        write_file.close()


    def get_name(self):
        return self.get_values()["name"]

    def get_values(self):
        return copy.deepcopy(self.values)

    def get_members(self):
        returnedMembers = []
        for member in self.get_values()["members"]:
            returnedMembers.append(str(member))
        return returnedMembers

    def add_member(self, who):
        dictionary = self.get_values()
        members = dictionary["members"]
        members.append(str(who))
        dictionary["members"] = members
        self.set_to_dict(dictionary)

    def remove_member(self, who):
        dictionary = self.get_values()
        members = dictionary["members"]
        members.remove(str(who))
        dictionary["members"] = members
        self.set_to_dict(dictionary)

    def __str__(self):
        return f'Classes[name="' + self.get_name() + '", members="' + str(self.get_members()) + '"]'


class Updater:

    UPDATE_URL = "https://update.cga.check.noahf.net/"
    RETRIEVE_FROM = "https://update.cga.download.noahf.net/"

    def install(self):
        print("Unable to update: Not set up")
        self.root.destroy()
        returned = ctypes.windll.user32.MessageBoxW(0, "Failed to update: Exception('Unable to update: Not set up')", "Update Failed!", 0x10 | 0x00)


    def ignore(self):
        print("User declined to update")
        try:
            self.root.destroy()
        except AttributeError as err:
            print("Attempted to destroy root (impossible - does not exist)")

    def differ(self, up_to_date: str, outdated: str, unable: str):
        if self.is_up_to_date is True:
            return up_to_date
        elif self.is_up_to_date is False:
            if self.main.updater.was_successful is False:
                return unable
            return outdated

    def request_new_version(self, old_root):
        self.root = Toplevel(old_root)

        self.background = "#4d4d4d"
        self.root.title(self.differ("Up to date!", "Update Recommended!", "Update Check Failed!"))
        self.root.resizable(width=False, height=False)
        self.default_size = (250, 250)
        self.root.configure(bg=self.background)
        self.root.grab_set()


        label_test = Label(self.root,
                           text=self.differ("Up to date!", "Update Available!", "Update Failed!"),
                           font=("Consolas", 18, "bold"),
                           bg="#696969",
                           fg="white",
                           pady=15
                           )
        label_test.place(relwidth=1)

        amount_behind = Label(self.root,
                              text=self.differ("You are on the latest version!", f"You are {str(self.distance_out_of_date)} version(s) behind!", "Failed to update, it seems there was an error."),
                              font=("Consolas", self.differ(9, 9, 7), "bold", "italic"),
                              bg="#696969",
                              fg=self.differ("#7aff85", "#ffbf00", "#cfb9eb"),
                              pady=5
                              )
        amount_behind.place(rely=0.2, relwidth=1)   

        if self.is_up_to_date is False:
            install_now = Button(self.root,
                                text="Install",
                                font=("Consolas", 20, "bold"),
                                bg="#3dfc73",
                                command=lambda: self.install()
                                )
            install_now.place(relx=0.1, rely=0.6, anchor="w")

            install_later = Button(self.root,
                                   text="Later",
                                   font=("Consolas", 14),
                                   bg="#b8b8b8",
                                   command=lambda: self.ignore()
                                   )
            install_later.place(relx=0.9, rely=0.6, anchor="e")
        elif self.is_up_to_date is True:
            close = Button(self.root,
                           text="Close",
                           font=("Consolas", 20, "bold"),
                           bg="red",
                           fg="white",
                           command=lambda: self.ignore()
                           )
            close.place(relx=0.5, rely=0.6, anchor=CENTER)
            

        Main.center_window(self.root, width=self.default_size[0], height=self.default_size[1])

        self.loader.root.wait_window(self.root)

        pass

    def __init__(self, main, loader):
        self.loader = loader
        self.main = main

        with open("version-history.json", "r") as data:
            self.local_data = json.load(data)

        self.version = self.local_data["current"]

        print("Found version(s) locally: " + str(self.local_data))

        try:
            with open("fake-online-version.json", "r") as data:
                self.web_data = json.load(data)
            #with urllib.request.urlopen(self.UPDATE_URL) as data:
            #    self.web_data = json.loads(data.read().decode('utf-8'))
        except Exception as err:
            print("----------------------------------------")
            print("FAILED TO CHECK FOR UPDATES!")
            print(str(type(err)) + ": " + str(err))
            print("----------------------------------------")
            self.web_data = None
            self.latest_version = "unknown"
            self.is_up_to_date = False
            self.distance_out_of_date = -1
            self.ignore()
            self.was_successful = False
            return

        self.was_successful = True
        self.latest_version = self.web_data["current"]

        print("Found version(s) online: " + str(self.web_data))

        self.is_up_to_date = self.version == self.latest_version

        self.distance_out_of_date = -1
        if not self.is_up_to_date:
            for index, item in enumerate(self.web_data["previous"]):
                if item == self.version:
                    self.distance_out_of_date = index + 1
                    break

            print("".join("-" for i in range(0, 45)))
            print("User is out of date by " + str(self.distance_out_of_date) + " version(s).")
            print("".join("-" for i in range(0, 45)))
            self.request_new_version(self.loader.root)
            return

        print("Update check complete. Software is up-to-date.")


class Main:
    def __init__(self, loader):
        loader.write_reason("Checking for updates")
        self.updater = Updater(self, loader)

        loader.write_reason("Retrieving classes list")
        self.classes = Classes.get_files("//classes//")

        loader.write_reason("Generating random seed")
        self.seed = str(round(time.time()))

        loader.write_reason("Creating base GUI")
        self.gui = guiClass.AntecedentGUI(self, self.classes, loader)

    def handle_exception(self, *args):
        error = traceback.format_exception(*args)
        logging.error("".join(error).strip())
        returned = ctypes.windll.user32.MessageBoxW(0,
                                                    "An error occurred while executing the program:\n\n" + str(''.join(error)),
                                                    "An Error Occurred", 0x10 | 0x40000)

    @staticmethod
    def center_window(win, width=0, height=0):
        width = win.winfo_width() if width == 0 else width
        height = win.winfo_height() if height == 0 else height
        screen_width = round(win.winfo_screenwidth() / 2) - round(width / 2)
        screen_height = round(win.winfo_screenheight() / 2) - round(height / 2) - 50

        print("Setting window geometry of " + str(win.winfo_id()) + " to " + str(width) + "x" + str(height) + "+" + str(screen_width) + "+" + str(screen_height))
        win.geometry(str(width) + "x" + str(height) + "+" + str(screen_width) + "+" + str(screen_height))


class Loader:
    WAIT_TIME = 1 # seconds
    
    def __init__(self):
        self.request_exit = False
        self.exit_success = False

    def write_reason(self, reason):
        self.root.title("Class Group Assigner - " + str(reason))
        self.exact.config(text=str(reason))
        print(reason)

    def await_request_exit(self, first=True):
        self.request_exit = True
        if first:
            self.write_reason("Complete")

        print("Awaiting exit...")
        if self.exit_success is False:
            self.root.after(round((self.WAIT_TIME + 1) * 1000), lambda: self.await_request_exit(False))
            return False
        return True

    def load_menu(self):
        self.root = Tk()
        self.background = "#4d4d4d"
        self.root.title("Class Group Assigner")
        self.root.resizable(width=False, height=False)
        self.root.configure(width=400, height=100, bg=self.background)

        label = Label(self.root,
                          bg=self.background,
                          fg="white",
                          text="Loading program",
                          font=("Consolas", 15),
                          pady=0)
        label.place(relx=0.5, rely=0.3, anchor=CENTER)

        self.new_stage = "Starting program"
        self.stage = "Starting program"
        self.exact = Label(self.root,
                           bg=self.background,
                           fg="#9e9e9e",
                           text=self.stage,
                           font=("Consolas italic", 12),
                           pady=0)
        self.exact.place(relx=0.5, rely=0.7, anchor=CENTER)

        secondary = threading.Thread(target=self.should_exit, args=())
        secondary.start()

        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)
        Main.center_window(self.root)

        self.root.after(round(self.WAIT_TIME * 1000), lambda: threading.Thread(target=lambda: Main(self), args=()).start())
        self.root.after(round(self.WAIT_TIME * 1000), self.should_exit)

        self.root.mainloop()

    def should_exit(self):
        if self.request_exit is True:
            self.exit()
            return
        self.root.after(round(self.WAIT_TIME * 1000), self.should_exit)

    def exit(self):
        try:
            self.root.destroy()
        except TclError as err:
            print("Failed destroy: " + str(type(err))[len("<class '"):0-len("'>")] + ": " + str(err))
        self.exit_success = True


if __name__ == "__main__":
    try:
        Loader().load_menu()
    except Exception as err:
        print("Found exception: " + str(err))