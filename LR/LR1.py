import tkinter as tk
from tkinter import ttk
import time
import numdifftools as nd
from tkinter import scrolledtext
from functions import *
from matplotlib.colors import LinearSegmentedColormap


def drawLab1(tab, window, ax, canvas):
    # Функция для градиента
    def gradient(function, input):
        ret = np.empty(len(input))
        for i in range(len(input)):
            fg = lambda x: partial_function(function, input, i, x)
            ret[i] = nd.Derivative(fg)(input[i])
        return ret

    # Функция для частной производной
    def partial_function(f___, input, pos, value):
        tmp = input[pos]
        input[pos] = value
        ret = f___(*input)
        input[pos] = tmp
        return ret

    # Функция, которая будет выполнена при нажатии кнопки "Выполнить"
    def run_optimization():
        x0 = x_var.get()
        y0 = y_var.get()
        step = step_var.get()
        max_iterations = iterations_var.get()
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
        ax.plot_surface(X, Y, Z, cmap=cmap, alpha=0.7)

        target_func = target_function(X, Y, function_var)[1]
        results = []
        results_text.config(state=tk.NORMAL)
        results_text.delete(1.0, tk.END)
        for k in range(max_iterations):
            (gx, gy) = gradient(target_func, [x0, y0])

            if np.linalg.norm((gx, gy)) < 0.0001:
                break

            x1, y1 = x0 - step * gx, y0 - step * gy
            f1 = target_func(x1, y1)
            f0 = target_func(x0, y0)

            while not f1 < f0:
                step = step / 2
                x1, y1 = x0 - step * gx, y0 - step * gy
                f1 = target_func(x1, y1)
                f0 = target_func(x0, y0)

            if np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2) < 0.0001 and abs(f1 - f0) < 0.0001:
                x0, y0 = x1, y1
                break
            else:
                x0, y0 = x1, y1

            results.append((x0, y0, k, f1))
            ax.scatter([x0], [y0], [f1], color='red', s=10)
            results_text.insert(tk.END,
                                f"Шаг {k}: Координаты ({x0:.2f}, {y0:.2f}), Значение функции: {f1:.7f}\n")
            results_text.yview_moveto(1)
            canvas.draw()
            window.update()
            time.sleep(delay)

        length = len(results) - 1
        ax.scatter(results[length][0], results[length][1], results[length][3], color='black', marker='x', s=60)
        results_text.insert(tk.END,
                            f"Результат:\nКоординаты ({results[length][0]:.5f}, "
                            f"{results[length][1]:.5f}),\nЗначение функции: {results[length][3]:.8f}\n")
        results_text.yview_moveto(1)
        results_text.config(state=tk.DISABLED)

    # Создаем LabelFrame для "Инициализация значений"
    init_values_frame = ttk.LabelFrame(tab, text="Инициализация значений", padding=(15, 10))
    init_values_frame.grid(row=0, column=0, padx=10, pady=3, sticky="w")

    # Параметры задачи
    ttk.Label(init_values_frame, text="X начальное").grid(row=0, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Y начальное").grid(row=1, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Шаг").grid(row=2, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Число итераций").grid(row=3, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Задержка (сек)").grid(row=4, column=0, padx=10, pady=3, sticky="w")

    x_var = tk.DoubleVar(value=-1)
    y_var = tk.DoubleVar(value=-1)
    step_var = tk.DoubleVar(value=0.5)
    iterations_var = tk.IntVar(value=100)
    delay_var = tk.DoubleVar(value=0.5)

    x_entry = ttk.Entry(init_values_frame, textvariable=x_var)
    y_entry = ttk.Entry(init_values_frame, textvariable=y_var)
    step_entry = ttk.Entry(init_values_frame, textvariable=step_var)
    iterations_entry = ttk.Entry(init_values_frame, textvariable=iterations_var)
    delay_entry = ttk.Entry(init_values_frame, textvariable=delay_var)

    x_entry.grid(row=0, column=1)
    y_entry.grid(row=1, column=1)
    step_entry.grid(row=2, column=1)
    iterations_entry.grid(row=3, column=1)
    delay_entry.grid(row=4, column=1)

    # ------------------------------------------------------------------

    func_values_frame = ttk.LabelFrame(tab, text="Функция и отображение ее графика", padding=(15, 10))
    func_values_frame.grid(row=5, column=0, padx=10, pady=3, sticky="w")

    ttk.Label(func_values_frame, text="Выберите функцию").grid(row=6, column=0)
    function_choices = ["...", "Функция Химмельблау", "2x^2+3y^2+4xy-6x-3y", "Функция Розенброка",
                        "Функция Растригина", "Функция сферы"]
    function_var = tk.StringVar(value=function_choices[0])
    function_menu = ttk.Combobox(func_values_frame, textvariable=function_var, values=function_choices,
                                 width=22, state="readonly")
    function_menu.grid(row=6, column=1, pady=3, sticky="w")

    ttk.Label(func_values_frame, text="X интервал (min)").grid(row=8, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="X интервал (max)").grid(row=9, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Y интервал (min)").grid(row=10, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Y интервал (max)").grid(row=11, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Ось X интервал").grid(row=12, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Ось Y интервал").grid(row=13, column=0, padx=10, pady=3, sticky="w")

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

    x_interval_min_entry.grid(row=8, column=1)
    x_interval_max_entry.grid(row=9, column=1)
    y_interval_min_entry.grid(row=10, column=1)
    y_interval_max_entry.grid(row=11, column=1)
    x_axis_interval_entry.grid(row=12, column=1)
    y_axis_interval_entry.grid(row=13, column=1)

    # Создание стиля для кнопки
    button_style = ttk.Style()
    button_style.configure("Gold.TButton", foreground="black", background="gold", bordercolor="black")

    # Создание кнопки Выполнить
    apply_settings_button = tk.Button(tab, text="Выполнить", command=run_optimization,
                                      background="gold", borderwidth=1, relief="solid")
    apply_settings_button.grid(row=14, column=0, padx=10, pady=3)

    ttk.Label(tab, text="Выполнение и результаты").grid(row=15, column=0, pady=10)
    results_text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=19, width=35, padx=2, state=tk.DISABLED)
    results_text.grid(row=16, column=0, padx=10)
