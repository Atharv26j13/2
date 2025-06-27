from tkinter import *

root = Tk()
root.geometry("400x600")
root.title("Password")

pas = StringVar()
pas.set("")

ans = Label(root, textvariable=pas, fg="black", font=("Arial", 18))
ans.pack(pady=10)

correct_password = "9378#"
num = [[9, 8, 7], [6, 5, 4], [3, 2, 1], ['*', 0, '#']]

unlocked = False

def func(val):
    global unlocked
    if unlocked:
        return
    current = pas.get()
    current += str(val)
    pas.set(current)
    if current == correct_password:
        pas.set("Unlocked")
        unlocked = True

def clear():
    global unlocked
    unlocked = False
    pas.set("")

button_frame = Frame(root)
button_frame.pack()

for i in range(4):
    for j in range(3):
        value = num[i][j]
        btn = Button(button_frame, text=str(value), width=10, height=4,
                     command=lambda val=value: func(val))
        btn.grid(row=i, column=j, sticky="nsew", padx=5, pady=5)

clear_btn = Button(root, text="Clear", bg="red", fg="black", font=("Arial", 12),
                   command=clear)
clear_btn.pack(pady=10)

root.mainloop()
