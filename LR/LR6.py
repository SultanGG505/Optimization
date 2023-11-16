import tkinter as tk
from tkinter import ttk
import numpy as np
import time
from tkinter import scrolledtext
from matplotlib.colors import LinearSegmentedColormap
import random
from operator import itemgetter

from functions import target_function


class AIS:
    def __init__(self, func, iter_number, num_antibodies, num_best, num_random, num_clones, mutation_rate, x_range,
                 y_range):
        self.func = func
        self.iter_number = iter_number
        self.num_antibodies = num_antibodies
        self.num_best = num_best
        self.num_random = num_random
        self.num_clones = num_clones
        self.mutation_rate = mutation_rate
        self.x_range = x_range
        self.y_range = y_range

        self.antibodies = [[random.uniform(self.x_range[0], self.x_range[1]),
                            random.uniform(self.y_range[0], self.y_range[1]),
                            0.0] for _ in range(self.num_antibodies)]
        for antibody in self.antibodies:
            antibody[2] = self.func(antibody[0], antibody[1])

        self.antibody_best = min(self.antibodies, key=itemgetter(2))

    def sort_antibodies(self):
        self.antibodies.sort(key=lambda x: x[2])

    def mutate(self, antibody):
        new_x_val = np.clip(antibody[0] + self.mutation_rate * np.random.randn(), self.x_range[0], self.x_range[1])
        new_y_val = np.clip(antibody[1] + self.mutation_rate * np.random.randn(), self.y_range[0], self.y_range[1])
        return [new_x_val, new_y_val, self.func(new_x_val, new_y_val)]

    def next_iteration(self):
        for iteration in range(self.iter_number):
            self.sort_antibodies()

            for i in range(self.num_best, self.num_antibodies):
                if i < self.num_best + self.num_random:
                    self.antibodies[i] = [random.uniform(self.x_range[0], self.x_range[1]),
                                          random.uniform(self.y_range[0], self.y_range[1]),
                                          0.0]
                    self.antibodies[i][2] = self.func(self.antibodies[i][0], self.antibodies[i][1])
                else:
                    self.antibodies[i] = self.mutate(self.antibodies[i - self.num_random])
                    self.antibodies[i][2] = self.func(self.antibodies[i][0], self.antibodies[i][1])

            self.antibody_best = min(self.antibodies, key=itemgetter(2))


def drawLab6(tab, window, ax, canvas):
    def run_optimization():
        iter_number = iterations_var.get()
        antibodies_num = antibodies_number_var.get()
        best_num = best_number_var.get()
        random_num = random_number_var.get()
        clones_num = clones_number_var.get()
        mutation_coef = mutation_rate_var.get()
        delay = delay_var.get()

        x_range = np.linspace(x_interval_min.get(), x_interval_max.get(), 100)
        y_range = np.linspace(y_interval_min.get(), y_interval_max.get(), 100)
        X, Y = np.meshgrid(x_range, y_range)

        if function_var.get() != "...":
            Z = target_function(X, Y, function_var)[0]
            target_func = target_function(X, Y, function_var)[1]
        else:
            return

        ax.cla()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xticks(np.arange(x_interval_min.get(), x_interval_max.get() + 1, x_axis_interval.get()))
        ax.set_yticks(np.arange(y_interval_min.get(), y_interval_max.get() + 1, y_axis_interval.get()))
        # Создадим colormap с тремя цветами
        colors = [(0, 0, 0), (1, 0.843, 0), (1, 0.698, 0)]  # Черный, золотой, близкий к золотому
        cmap = LinearSegmentedColormap.from_list("DX:HR", colors, N=256)
        alpha = 0.3
        ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha)

        ais = AIS(target_func, iter_number, antibodies_num, best_num, random_num, clones_num, mutation_coef,
                  [x_interval_min.get(), x_interval_max.get()], [y_interval_min.get(), y_interval_max.get()])

        # отрисовка стартовой популяции
        for antibody in ais.antibodies:
            ax.scatter(antibody[0], antibody[1], antibody[2], c="red", s=1, marker="s")

        ax.scatter(ais.antibody_best[0], ais.antibody_best[1], ais.antibody_best[2], c="blue")
        canvas.draw()
        window.update()

        # очистка графика
        ax.cla()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha)
        canvas.draw()

        cnt = 0
        results_text.config(state=tk.NORMAL)
        results_text.delete(1.0, tk.END)
        # отрисовка промежуточной популяции и эволюция
        for i in range(iter_number):
            prev_antibody_best = ais.antibody_best
            ais.next_iteration()

            # подсчет продолжительности стагнации
            if abs(prev_antibody_best[2] - ais.antibody_best[2]) < 0.0001:
                cnt += 1
            else:
                cnt = 0

            if cnt == 15:
                break

            # отрисовка промежуточной популяции
            for antibody in ais.antibodies:
                ax.scatter(antibody[0], antibody[1], antibody[2], c="red", s=1, marker="s")

            ax.scatter(ais.antibody_best[0], ais.antibody_best[1], ais.antibody_best[2], c="blue")
            results_text.insert(tk.END,
                                f"Шаг {i}: Координаты ({ais.antibody_best[0]:.4f}, "
                                f"{ais.antibody_best[1]:.4f}),"
                                f" Значение функции: {ais.antibody_best[2]:.4f}\n")
            results_text.yview_moveto(1)

            canvas.draw()
            window.update()
            time.sleep(delay)

            # очистка графика
            ax.cla()
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha)
            canvas.draw()

        # отрисовка результирующей популяции
        for antibody in ais.antibodies:
            ax.scatter(antibody[0], antibody[1], antibody[2], c="red", s=1, marker="s")

        ax.scatter(ais.antibody_best[0], ais.antibody_best[1], ais.antibody_best[2], c='black', marker='x', s=60)

        canvas.draw()
        window.update()
        results_text.insert(tk.END,
                            f"Результат:\nКоординаты ({ais.antibody_best[0]:.5f}, "
                            f"{ais.antibody_best[1]:.5f}),\nЗначение функции: {ais.antibody_best[2]:.8f}\n")
        results_text.yview_moveto(1)
        results_text.config(state=tk.DISABLED)

    # Создаем LabelFrame для "Инициализация значений"
    init_values_frame = ttk.LabelFrame(tab, text="Инициализация значений", padding=(15, 10))
    init_values_frame.grid(row=0, column=0, padx=10, pady=3, sticky="w")

    # Параметры задачи
    ttk.Label(init_values_frame, text="Число итераций").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    ttk.Label(init_values_frame, text="Кол-во антител").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    ttk.Label(init_values_frame, text="Кол-во лучших антител").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    ttk.Label(init_values_frame, text="Кол-во случайных антител").grid(row=3, column=0, padx=10, pady=5,
                                                                       sticky="w")
    ttk.Label(init_values_frame, text="Кол-во клонов").grid(row=4, column=0, padx=10, pady=5,
                                                                             sticky="w")
    ttk.Label(init_values_frame, text="Коэффициент мутации").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    ttk.Label(init_values_frame, text="Задержка (сек)").grid(row=7, column=0, padx=10, pady=5, sticky="w")

    iterations_var = tk.IntVar(value=200)
    antibodies_number_var = tk.IntVar(value=200)
    best_number_var = tk.IntVar(value=10)
    random_number_var = tk.IntVar(value=20)
    clones_number_var = tk.IntVar(value=20)
    mutation_rate_var = tk.DoubleVar(value=0.2)
    delay_var = tk.DoubleVar(value=0.01)

    iterations_entry = ttk.Entry(init_values_frame, textvariable=iterations_var)
    antibodies_number_entry = ttk.Entry(init_values_frame, textvariable=antibodies_number_var)
    best_number_entry = ttk.Entry(init_values_frame, textvariable=best_number_var)
    random_number_entry = ttk.Entry(init_values_frame, textvariable=random_number_var)
    clones_number_entry = ttk.Entry(init_values_frame, textvariable=clones_number_var)
    mutation_rate_entry = ttk.Entry(init_values_frame, textvariable=mutation_rate_var)
    delay_entry = ttk.Entry(init_values_frame, textvariable=delay_var)

    iterations_entry.grid(row=0, column=1)
    antibodies_number_entry.grid(row=1, column=1)
    best_number_entry.grid(row=2, column=1)
    random_number_entry.grid(row=3, column=1)
    clones_number_entry.grid(row=4, column=1)
    mutation_rate_entry.grid(row=6, column=1)
    delay_entry.grid(row=7, column=1)

    # ------------------------------------------------------------------

    func_values_frame = ttk.LabelFrame(tab, text="Функция и отображение ее графика", padding=(15, 10))
    func_values_frame.grid(row=8, column=0, padx=10, pady=3, sticky="w")

    ttk.Label(func_values_frame, text="Выберите функцию").grid(row=9, column=0)
    function_choices = ["...", "Функция Химмельблау", "2x^2+3y^2+4xy-6x-3y", "Функция Розенброка",
                        "Функция Растригина", "Функция сферы"]
    function_var = tk.StringVar(value=function_choices[0])
    function_menu = ttk.Combobox(func_values_frame, textvariable=function_var, values=function_choices,
                                 width=22, state="readonly")
    function_menu.grid(row=9, column=1, pady=3, sticky="w")

    ttk.Label(func_values_frame, text="X интервал (min)").grid(row=10, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="X интервал (max)").grid(row=11, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Y интервал (min)").grid(row=12, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Y интервал (max)").grid(row=13, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Ось X интервал").grid(row=14, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(func_values_frame, text="Ось Y интервал").grid(row=15, column=0, padx=10, pady=3, sticky="w")

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

    x_interval_min_entry.grid(row=10, column=1)
    x_interval_max_entry.grid(row=11, column=1)
    y_interval_min_entry.grid(row=12, column=1)
    y_interval_max_entry.grid(row=13, column=1)
    x_axis_interval_entry.grid(row=14, column=1)
    y_axis_interval_entry.grid(row=15, column=1)

    # Создание стиля для кнопки
    button_style = ttk.Style()
    button_style.configure("Gold.TButton", foreground="black", background="gold", bordercolor="black")

    # Создание кнопки Выполнить
    apply_settings_button = tk.Button(tab, text="Выполнить", command=run_optimization,
                                      background="gold", borderwidth=1, relief="solid")
    apply_settings_button.grid(row=16, column=0, padx=10, pady=3)

    ttk.Label(tab, text="Выполнение и результаты").grid(row=17, column=0, pady=10)
    results_text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=14, width=38, padx=2, state=tk.DISABLED)
    results_text.grid(row=18, column=0, padx=10)
