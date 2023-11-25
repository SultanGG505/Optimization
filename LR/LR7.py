import tkinter as tk
from tkinter import ttk
import numpy as np
import time
from tkinter import scrolledtext
from matplotlib.colors import LinearSegmentedColormap
import random
from operator import itemgetter

from functions import target_function


class BFO:
    def __init__(self, func, num_bacteries, chemotaxis_steps, num_to_eliminate,
                 elimination_probability, x_range, y_range):
        self.func = func
        self.num_bacteries = num_bacteries
        self.chemotaxis_steps = chemotaxis_steps
        self.num_to_eliminate = num_to_eliminate
        self.elimination_probability = elimination_probability
        self.x_range = x_range
        self.y_range = y_range

        self.bacteries = [[random.uniform(self.x_range[0], self.x_range[1]),
                           random.uniform(self.y_range[0], self.y_range[1]),
                           0.0] for _ in range(self.num_bacteries)]
        for bacteria in self.bacteries:
            bacteria[2] = self.func(bacteria[0], bacteria[1])

        self.bacteria_best = min(self.bacteries, key=itemgetter(2))
        self.hp = [bacteria[2] for bacteria in self.bacteries]

    def next_iteration(self):
        for i in range(self.num_bacteries):
            # хемотаксис
            for t in range(self.chemotaxis_steps):
                step = np.random.uniform(-1, 1)
                new_x = np.clip(self.bacteries[i][0] + step, self.x_range[0], self.x_range[1])
                new_y = np.clip(self.bacteries[i][1] + step, self.y_range[0], self.y_range[1])

                new_fitness = self.func(new_x, new_y)

                if new_fitness < self.bacteries[i][2]:
                    self.bacteries[i][0] = new_x
                    self.bacteries[i][1] = new_y
                    self.bacteries[i][2] = new_fitness
                    # break

            # репродукция
            self.hp[i] += self.bacteries[i][2]

        # Сортировка бактерий в порядке возрастания состояний здоровья
        sorted_indices = np.argsort(self.hp)
        self.bacteries = [self.bacteries[i] for i in sorted_indices]
        self.hp = [self.hp[i] for i in sorted_indices]

        # Замена второй половины бактерий первой
        half_point = self.num_bacteries // 2
        self.bacteries[:half_point], self.bacteries[half_point:] = self.bacteries[half_point:], self.bacteries[
                                                                                                :half_point]
        self.hp[:half_point], self.hp[half_point:] = self.hp[half_point:], self.hp[:half_point]

        # Ликвидация и рассеивание
        indices_to_eliminate = np.random.choice(self.num_bacteries, size=self.num_to_eliminate, replace=False)
        for i in indices_to_eliminate:
            if np.random.rand() > self.elimination_probability:
                self.bacteries[i] = [random.uniform(self.x_range[0], self.x_range[1]),
                                     random.uniform(self.y_range[0], self.y_range[1]),
                                     0]
                self.bacteries[i][2] = self.func(self.bacteries[i][0], self.bacteries[i][1])

        self.bacteria_best = min(self.bacteries, key=itemgetter(2))


def drawLab7(tab, window, ax, canvas):
    def run_optimization():
        iter_number = iterations_var.get()
        bacteries_number = bacteries_number_var.get()
        steps_of_chemotaxis = chemotaxis_steps_var.get()
        eliminate_number = num_to_eliminate_var.get()
        elimination_prob = elimination_probability_var.get()
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

        bfo = BFO(target_func, bacteries_number, steps_of_chemotaxis, eliminate_number, elimination_prob,
                  [x_interval_min.get(), x_interval_max.get()], [y_interval_min.get(), y_interval_max.get()])

        # отрисовка стартовой популяции
        for bacteria in bfo.bacteries:
            ax.scatter(bacteria[0], bacteria[1], bacteria[2], c="red", s=1, marker="s")

        ax.scatter(bfo.bacteria_best[0], bfo.bacteria_best[1], bfo.bacteria_best[2], c="blue")
        canvas.draw()
        window.update()

        # очистка графика
        ax.cla()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha)
        canvas.draw()

        results_text.config(state=tk.NORMAL)
        results_text.delete(1.0, tk.END)
        # отрисовка промежуточной популяции и эволюция
        for i in range(iter_number):
            bfo.next_iteration()
            for bacteria in bfo.bacteries:
                # отрисовка промежуточной популяции
                ax.scatter(bacteria[0], bacteria[1], bacteria[2], c="red", s=1, marker="s")

            ax.scatter(bfo.bacteria_best[0], bfo.bacteria_best[1], bfo.bacteria_best[2], c="blue")
            results_text.insert(tk.END,
                                f"Шаг {i}: Координаты ({bfo.bacteria_best[0]:.4f}, "
                                f"{bfo.bacteria_best[1]:.4f}),"
                                f" Значение функции: {bfo.bacteria_best[2]:.4f}\n")
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
        for bacteria in bfo.bacteries:
            ax.scatter(bacteria[0], bacteria[1], bacteria[2], c="red", s=1, marker="s")

        ax.scatter(bfo.bacteria_best[0], bfo.bacteria_best[1], bfo.bacteria_best[2], c='black', marker='x', s=60)

        canvas.draw()
        window.update()
        results_text.insert(tk.END,
                            f"Результат:\nКоординаты ({bfo.bacteria_best[0]:.5f}, "
                            f"{bfo.bacteria_best[1]:.5f}),\nЗначение функции: {bfo.bacteria_best[2]:.8f}\n")
        results_text.yview_moveto(1)
        results_text.config(state=tk.DISABLED)

    # Создаем LabelFrame для "Инициализация значений"
    init_values_frame = ttk.LabelFrame(tab, text="Инициализация значений", padding=(15, 10))
    init_values_frame.grid(row=0, column=0, padx=10, pady=3, sticky="w")

    # Параметры задачи
    ttk.Label(init_values_frame, text="Количество итераций").grid(row=0, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Количество бактерий").grid(row=1, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Шагов хемотаксиса").grid(row=2, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Количество ликвидируемых").grid(row=3, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Вероятность ликвидации").grid(row=4, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Задержка (сек)").grid(row=5, column=0, padx=10, pady=3, sticky="w")

    iterations_var = tk.IntVar(value=50)
    bacteries_number_var = tk.IntVar(value=50)
    chemotaxis_steps_var = tk.IntVar(value=15)
    num_to_eliminate_var = tk.IntVar(value=20)
    elimination_probability_var = tk.DoubleVar(value=0.6)
    delay_var = tk.DoubleVar(value=0.01)

    iterations_entry = ttk.Entry(init_values_frame, textvariable=iterations_var)
    bacteries_number_entry = ttk.Entry(init_values_frame, textvariable=bacteries_number_var)
    chemotaxis_steps_entry = ttk.Entry(init_values_frame, textvariable=chemotaxis_steps_var)
    num_to_eliminate_entry = ttk.Entry(init_values_frame, textvariable=num_to_eliminate_var)
    elimination_probability_entry = ttk.Entry(init_values_frame, textvariable=elimination_probability_var)
    delay_entry = ttk.Entry(init_values_frame, textvariable=delay_var)

    iterations_entry.grid(row=0, column=1)
    bacteries_number_entry.grid(row=1, column=1)
    chemotaxis_steps_entry.grid(row=2, column=1)
    num_to_eliminate_entry.grid(row=3, column=1)
    elimination_probability_entry.grid(row=4, column=1)
    delay_entry.grid(row=5, column=1)

    # ------------------------------------------------------------------

    func_values_frame = ttk.LabelFrame(tab, text="Функция и отображение ее графика", padding=(15, 10))
    func_values_frame.grid(row=6, column=0, padx=10, pady=3, sticky="w")

    ttk.Label(func_values_frame, text="Выберите функцию").grid(row=7, column=0)
    function_choices = ["...", "Функция Химмельблау", "2x^2+3y^2+4xy-6x-3y", "Функция Розенброка",
                        "Функция Растригина", "Функция сферы"]
    function_var = tk.StringVar(value=function_choices[0])
    function_menu = ttk.Combobox(func_values_frame, textvariable=function_var, values=function_choices,
                                 width=22, state="readonly")
    function_menu.grid(row=7, column=1, pady=3, sticky="w")

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
