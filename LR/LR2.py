import tkinter as tk
from tkinter import ttk
import numpy as np
import time
from tkinter import scrolledtext

from matplotlib.colors import LinearSegmentedColormap
from scipy.optimize import minimize

from functions import target_function


def drawLab2(tab, window, ax, canvas):
    def simplex_method(x, y):
        #   global points
        points = []

        def fun(x_i):  # Функция
            x1 = x_i[0]
            x2 = x_i[1]
            return 2 * x1 * x1 + 3 * x2 * x2 + 4 * x1 * x2 - 6 * x1 - 3 * x2

        def callback(x_w):
            g_list = np.ndarray.tolist(x_w)
            g_list.append(fun(x_w))
            points.append(g_list)

        b = (0, float("inf"))  # диапазон поиска
        bounds = (b, b)
        x0 = (x, y)  # начальная точка
        con = {'type': 'eq', 'fun': fun}

        # основной вызов
        res = minimize(fun, x0, method="SLSQP", bounds=bounds,
                       constraints=con, callback=callback)

        gList = np.ndarray.tolist(res.x)
        gList.append(res.fun)
        points.append(gList)

        for iteration, point in enumerate(points):
            yield iteration, point

    def run_optimization():
        res_x = x_var.get()
        res_y = y_var.get()
        delay = delay_var.get()

        ax.cla()
        x_range = np.linspace(x_interval_min.get(), x_interval_max.get(), 100)
        y_range = np.linspace(y_interval_min.get(), y_interval_max.get(), 100)
        X, Y = np.meshgrid(x_range, y_range)

        if function_var.get() != "...":
            Z = target_function(X, Y, function_var)[0]
        else:
            return

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xticks(np.arange(x_interval_min.get(), x_interval_max.get() + 1, x_axis_interval.get()))
        ax.set_yticks(np.arange(y_interval_min.get(), y_interval_max.get() + 1, y_axis_interval.get()))
        # Создадим colormap с тремя цветами
        colors = [(0, 0, 0), (1, 0.843, 0), (1, 0.698, 0)]  # Черный, золотой, близкий к золотому
        cmap = LinearSegmentedColormap.from_list("DX:HR", colors, N=256)
        ax.plot_surface(X, Y, Z, cmap=cmap)

        results = []
        results_text.config(state=tk.NORMAL)
        results_text.delete(1.0, tk.END)

        for i, point in simplex_method(res_x, res_y):
            # Сохранение результатов и обновление графика
            results.append((point[0], point[1], i, point[2]))
            ax.scatter(point[0], point[1], point[2], color='red', s=10)
            results_text.insert(tk.END,
                                f"Шаг {i}: Координаты ({point[0]:.2f}, {point[1]:.2f}), "
                                f"Значение функции: {point[2]:.7f}\n")
            results_text.yview_moveto(1)
            canvas.draw()
            window.update()
            time.sleep(delay)

        # Вывод окончательного результата
        length = len(results) - 1
        ax.scatter(results[length][0], results[length][1], results[length][3], color='black', marker='x', s=60)
        results_text.insert(tk.END,
                            f"Результат:\nКоординаты ({results[length][0]:.8f}, {results[length][1]:.8f})\n"
                            f"Значение функции: {results[length][3]:.8f}\n")
        results_text.yview_moveto(1)
        results_text.config(state=tk.DISABLED)

    # Создаем LabelFrame для "Инициализация значений"
    init_values_frame = ttk.LabelFrame(tab, text="Инициализация значений", padding=(15, 10))
    init_values_frame.grid(row=0, column=0, padx=10, pady=3, sticky="w")

    # Параметры задачи
    ttk.Label(init_values_frame, text="X начальное").grid(row=0, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Y начальное").grid(row=1, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Задержка (сек)").grid(row=2, column=0, padx=10, pady=3, sticky="w")

    x_var = tk.DoubleVar(value=10)
    y_var = tk.DoubleVar(value=10)
    delay_var = tk.DoubleVar(value=0.5)

    x_entry = ttk.Entry(init_values_frame, textvariable=x_var)
    y_entry = ttk.Entry(init_values_frame, textvariable=y_var)
    delay_entry = ttk.Entry(init_values_frame, textvariable=delay_var)

    x_entry.grid(row=0, column=1)
    y_entry.grid(row=1, column=1)
    delay_entry.grid(row=2, column=1)

    # ------------------------------------------------------------------

    func_values_frame = ttk.LabelFrame(tab, text="Функция и отображение ее графика", padding=(15, 10))
    func_values_frame.grid(row=3, column=0, padx=10, pady=3, sticky="w")

    ttk.Label(func_values_frame, text="Выберите функцию").grid(row=3, column=0)
    function_choices = ["2x^2+3y^2+4xy-6x-3y"]
    function_var = tk.StringVar(value=function_choices[0])
    function_menu = ttk.Combobox(func_values_frame, textvariable=function_var, values=function_choices,
                                 width=22, state="readonly")
    function_menu.grid(row=3, column=1, pady=3, sticky="w")

    ttk.Label(func_values_frame, text="X интервал (min)").grid(row=5, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="X интервал (max)").grid(row=6, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Y интервал (min)").grid(row=7, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Y интервал (max)").grid(row=8, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Ось X интервал").grid(row=9, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Ось Y интервал").grid(row=10, column=0, padx=10, pady=3, sticky="w")

    x_interval_min = tk.DoubleVar(value=-5)
    x_interval_max = tk.DoubleVar(value=5)
    y_interval_min = tk.DoubleVar(value=-5)
    y_interval_max = tk.DoubleVar(value=5)
    x_axis_interval = tk.IntVar(value=2)
    y_axis_interval = tk.IntVar(value=2)

    x_interval_min_entry = ttk.Entry(func_values_frame, textvariable=x_interval_min)
    x_interval_max_entry = ttk.Entry(func_values_frame, textvariable=x_interval_max)
    y_interval_min_entry = ttk.Entry(func_values_frame, textvariable=y_interval_min)
    y_interval_max_entry = ttk.Entry(func_values_frame, textvariable=y_interval_max)
    x_axis_interval_entry = ttk.Entry(func_values_frame, textvariable=x_axis_interval)
    y_axis_interval_entry = ttk.Entry(func_values_frame, textvariable=y_axis_interval)

    x_interval_min_entry.grid(row=5, column=1)
    x_interval_max_entry.grid(row=6, column=1)
    y_interval_min_entry.grid(row=7, column=1)
    y_interval_max_entry.grid(row=8, column=1)
    x_axis_interval_entry.grid(row=9, column=1)
    y_axis_interval_entry.grid(row=10, column=1)

    # Создание стиля для кнопки
    button_style = ttk.Style()
    button_style.configure("Gold.TButton", foreground="black", background="gold", bordercolor="black")

    # Создание кнопки Выполнить
    apply_settings_button = tk.Button(tab, text="Выполнить", command=run_optimization,
                                      background="gold", borderwidth=1, relief="solid")
    apply_settings_button.grid(row=11, column=0, padx=10, pady=3)

    ttk.Label(tab, text="Выполнение и результаты").grid(row=12, column=0, pady=10)
    results_text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=19, width=35, padx=2, state=tk.DISABLED)
    results_text.grid(row=13, column=0, padx=10)
