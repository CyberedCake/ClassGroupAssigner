import antecedent as guiClass
import functionality as func
import os
import json
import time
import threading
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
        return self.values

    def get_members(self):
        returnedMembers = []
        for member in self.get_values()["members"]:
            returnedMembers.append(str(member))
        return returnedMembers

    def __str__(self):
        return f'Classes[name="' + self.get_name() + '", members="' + str(self.get_members()) + '"]'


class Updater:

    UPDATE_URL = "https://update.cga.check.noahf.net/"
    RETRIEVE_FROM = "https://update.cga.download.noahf.net/"

    def __init__(self):
        version_history_file = open("version-history.json", "r")

        self.data = json.load(version_history_file)
        self.version = self.data["current"]
        self.previous = self.data["previous"]

        version_history_file.close()

        print("Found version(s): " + str(self.data))



        print("Update checked failed: Not setup")


class Main:
    def __init__(self, loader):
        loader.write_reason("Checking for updates")
        self.updater = Updater()

        loader.write_reason("Retrieving classes list")
        self.classes = Classes.get_files("//classes//")

        loader.write_reason("Generating random seed")
        self.seed = str(round(time.time()))

        loader.write_reason("Creating base GUI")
        self.gui = guiClass.AntecedentGUI(self, self.classes, loader)

    @staticmethod
    def center_window(win):
        width = win.winfo_width()
        height = win.winfo_height()
        screen_width = round(win.winfo_screenwidth() / 2) - round(width / 2)
        screen_height = round(win.winfo_screenheight() / 2) - round(height / 2) - 50

        win.geometry(str(width) + "x" + str(height) + "+" + str(screen_width) + "+" + str(screen_height))


class Loader:
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
            self.root.after(2 * 1000, lambda: self.await_request_exit(False))
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

        self.root.after(1 * 1000, lambda: threading.Thread(target=lambda: Main(self), args=()).start())
        self.root.after(1 * 1000, self.should_exit)

        self.root.mainloop()

    def should_exit(self):
        if self.request_exit is True:
            self.exit()
            return
        self.root.after(1 * 1000, self.should_exit)

    def exit(self):
        try:
            self.root.destroy()
        except TclError as err:
            print("Failed destroy: " + str(type(err))[len("<class '"):0-len("'>")] + ": " + str(err))
        self.exit_success = True


if __name__ == "__main__":
    Loader().load_menu()
