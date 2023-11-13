import tkinter as tk
from tkinter import ttk
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from LR.LR1 import drawLab1
from LR.LR2 import drawLab2
from LR.LR3 import drawLab3
from LR.LR4 import drawLab4
from LR.LR5 import drawLab5

window = tk.Tk()
window.title("Методы поисковой оптимизации")
window.state('zoomed')

# Создаем фрейм для Matplotlib (левая панель)
matplotlib_frame = ttk.Frame(window)
matplotlib_frame.grid(row=0, column=0, sticky="nsew")

# Устанавливаем максимальные размеры для matplotlib_frame
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Создаем трехмерное поле Matplotlib
fig = plt.figure(figsize=(6, 8), dpi=100)
ax = fig.add_subplot(projection='3d')

# Устанавливаем размеры Pyplot
canvas = FigureCanvasTkAgg(fig, master=matplotlib_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Создаем фрейм с вкладками (правая панель)
notebook = ttk.Notebook(window)
notebook.grid(row=0, column=1, sticky="nsew")

# Устанавливаем ширину для правой панели
window.grid_columnconfigure(1, minsize=350)

# Вкладка для лр1
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="ЛР1")
drawLab1(tab1, window, ax, canvas)

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="ЛР2")
drawLab2(tab2, window, ax, canvas)

tab3 = ttk.Frame(notebook)
notebook.add(tab3, text="ЛР3")
drawLab3(tab3, window, ax, canvas)

tab4 = ttk.Frame(notebook)
notebook.add(tab4, text="ЛР4")
drawLab4(tab4, window, ax, canvas)

tab5 = ttk.Frame(notebook)
notebook.add(tab5, text="ЛР5")
drawLab5(tab5, window, ax, canvas)

tab6 = ttk.Frame(notebook)
notebook.add(tab6, text="ЛР6")

tab7 = ttk.Frame(notebook)
notebook.add(tab7, text="ЛР7")

tab8 = ttk.Frame(notebook)
notebook.add(tab8, text="ЛР8")


window.mainloop()
