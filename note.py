from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
from functools import partial
import os
import shutil
import pickle
import socket
import _thread

# ~~~ Filesystem Setup ~~~
if not os.path.isdir("/noteApp"):
    os.mkdir("/noteApp")

# ~~~ Window organization ~~~
win = Tk()
win.title("Note Organizer")
win.geometry("820x400")

# ~~~ Menu creation ~~~
# Main menu setup
mainMenu = Menu(win)
win.config(menu=mainMenu)

# "File" sub-menu
fileMenu = Menu(mainMenu)
newMenu = Menu(fileMenu)
fileMenu.add_cascade(label="New", menu=newMenu)
newMenu.add_command(label="Class", command=lambda: newClass())
newMenu.add_command(label="Document", command=lambda: newDocument())
fileMenu.add_command(label="Save", command=lambda: saveClick())
fileMenu.add_command(label="Open", command=lambda: openClick())
fileMenu.add_command(label="Delete", command=lambda: deleteClick())
fileMenu.add_command(label="Exit", command=win.destroy)
mainMenu.add_cascade(label="File", menu=fileMenu)

# Cloud backup sub-menu
cloudMenu = Menu(mainMenu)
mainMenu.add_cascade(label="Cloud", menu=cloudMenu)
cloudMenu.add_command(label="Backup", command=lambda: backupClick())
cloudMenu.add_command(label="Import", command=lambda: importClick())

megaFrame = Frame(win)
megaFrame.pack()

# ~~~ Folder/file section ~~~
folders = Frame(megaFrame)
folders.grid(row=0, column=0)
currentDocument = None

# ~~~ Text area section ~~~
editArea = Frame(megaFrame)
editArea.grid(row=0, column=1)
textArea = Text(editArea, height=20)
textArea.grid(row=0, column=0, sticky=NSEW)
scrollbar = Scrollbar(editArea, orient="vertical", command=textArea.yview)
textArea.config(yscrollcommand=scrollbar.set)
scrollbar.grid(row=0, column=1, sticky=NS)

# ~~~ Console ~~~
consoleArea = Frame(win)
consoleArea.pack()
consoleText = Text(consoleArea, width=100, height=5)
consoleText.pack()


# ~~~ Functions ~~~
def newClass():
    name = simpledialog.askstring(
        "User Input", "Please enter the name of your new class: ")

    # Make directory if it doesn't exist
    if not os.path.isdir("/noteApp/" + name):
        os.mkdir("/noteApp/" + name)

        # Set up button with partial() as opposed to a lambda to use an object to preserve references
        # and allow for passing itself to the function
        button = Button(folders, text=name, width=20)
        button.configure(command=partial(folderClick, button))
        button.pack()
    else:
        messagebox.showerror("Oops!", "Class name is already in use!")


def newDocument():
    folder = simpledialog.askstring(
        "User Input", "Please enter the name of the folder you wish to place your new document in: ")
    filename = simpledialog.askstring(
        "User Input", "Please enter the name of your new document: ")

    if filename == None or folder == None:
        return

    path = "/noteApp/" + folder + "/" + filename

    # Make sure the final path is a text file
    if ".txt" not in path:
        path = path + ".txt"

    # Make file if it doesn't exist, otherwise show an error
    if not os.path.exists(path):
        open(path, "w")
    else:
        messagebox.showerror("Oops!", "Document name is already in use!")


def backupClick():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(("108.218.148.128", 4454))

        consoleText.insert(END, "\nConnection to server made.")
        consoleText.see("end")

        # Create a zip, pickle and send it to the server for storage
        fileName = shutil.make_archive("noteBackup", "zip", "/noteApp")
        sock.send(fileName.encode())

        file = open(fileName, "r")

        pickle.dump(file.readlines(), "/noteApp/bytes")

        consoleText.insert(END, "\nBackup sent to server.")
        consoleText.see("end")


def importClick():
    consoleText.insert(END, "\nopenClick - TO BE IMPLEMENTED")
    consoleText.see("end")


def folderClick(button):
    folderSetup(button["text"])


def fileClick(button, folderName):
    global currentDocument
    global textArea

    # Establish path of the current document so we can read from it
    currentDocument = "/noteApp/" + folderName + "/" + button['text']

    file = open(currentDocument, "r")

    textArea.delete("1.0", END)
    textArea.insert("1.0", file.read())

    file.close()


def saveClick():
    global currentDocument
    global textArea

    if currentDocument == None:
        return

    # Open the current document and overwrite
    file = open(currentDocument, "w")
    file.write(textArea.get("1.0", END))
    file.close()

    # Print confirmation in console
    consoleText.insert(END, "\nSaved changes in " +
                       currentDocument + ".")
    consoleText.see("end")


def deleteClick():
    global textArea

    dest = simpledialog.askstring(
        "User Input", "Which class would you like to delete?")

    # Continue if the directory actually exists
    if os.path.isdir("/noteApp/" + dest):
        # Make sure that the user wants to delete the directory
        if messagebox.askyesno("User Input", "Are you sure?\n(This will delete all files within that class and cannot be undone!)") == True:
            # Delete the folder recursively
            shutil.rmtree("/noteApp/" + dest)

            # Refresh the folder display with no folder preference
            folderSetup()
            consoleText.insert(END, "\nDirectory " +
                               "/noteApp/" + dest + " was deleted.")
            consoleText.see("end")
        else:
            consoleText.insert(END, "\nClass deletion cancelled successfully.")
            consoleText.see("end")
    else:
        messagebox.showerror("Oops!", "Invalid class name!")


def openClick():
    consoleText.insert(END, "\nopenClick - TO BE IMPLEMENTED")
    consoleText.see("end")


def folderSetup(specialty=None):
    global folders

    # Clear the folders tab for new setup
    for widget in folders.winfo_children():
        widget.destroy()

    # Add folder buttons for all existing folders found in the filesystem
    for folder in os.scandir("/noteApp"):
        folderName = str(folder)[str(folder).index(
            "'") + 1: str(folder).rindex("'")]

        if os.path.isdir("/noteApp/" + folderName):
            # Set up button with partial() as opposed to a lambda to use an object to preserve references
            # and allow for passing itself to the function
            button = Button(folders, text=folderName, width=20)
            button.configure(command=partial(folderClick, button))
            button.pack()

            # If given a folder name, display its contents
            if folderName == specialty:
                for file in os.scandir("/noteApp/" + folderName):
                    fileName = str(file)[str(file).index(
                        "'") + 1: str(file).rindex("'")]
                    button = Button(folders, text=fileName, width=15)
                    button.configure(command=partial(
                        fileClick, button, folderName))
                    button.pack()


# Run the window
folderSetup()
win.mainloop()
