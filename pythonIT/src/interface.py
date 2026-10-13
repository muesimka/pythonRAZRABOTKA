import tkinter as tk

score = 0

def start():
    global score
    score += 1
    label.config(text=str(score))

root = tk.Tk()

root.geometry("500x500")
root.iconbitmap("../assets/icon.ico")

header = tk.Frame(root, bg="black", height=100, width=400)
header.pack(side="top", fill="x",)

footer = tk.Frame(root, bg="black", height=100, width=400)
footer.pack(side="bottom", fill="x")

main = tk.Frame(root, bg="light blue", height=400, width=400)
main.pack(side="bottom", fill="x",)

button_start = tk.Button(main, text="Start", command=start)
button_start.pack(expand=1)

label = tk.Label(header, text= '0' , height=2, width=10)
label.pack()

entry = tk.Entry(header)
entry.pack()

root.mainloop()

