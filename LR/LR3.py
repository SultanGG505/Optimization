import tkinter as tk
from tkinter import ttk
import numpy as np
import time
from tkinter import scrolledtext

from matplotlib.colors import LinearSegmentedColormap
from random import uniform, random

from functions import target_function


class GeneticAlgorithm:
    def __init__(self, func, generations, pop_number, x_range, y_range, mut_chance=0.8, survive_cof=0.8):
        self.func = func
        self.population = dict()
        self.mut_chance = mut_chance
        self.survive_cof = survive_cof
        self.generations = generations
        self.pop_number = pop_number
        self.x_range = x_range
        self.y_range = y_range

    def generate_start_population(self):
        for i in range(self.pop_number):
            po_x = np.clip(uniform(self.x_range[0], self.x_range[1]), self.x_range[0], self.x_range[1])
            po_y = np.clip(uniform(self.y_range[0], self.y_range[1]), self.y_range[0], self.y_range[1])
            self.population[i] = [po_x, po_y, self.func(po_x, po_y)]

    def get_best_individual(self):
        return min(self.population.items(), key=lambda item: item[1][2])

    def select(self):
        sorted_pop = dict(sorted(self.population.items(), key=lambda item: item[1][2], reverse=True))

        cof = int(self.pop_number * (1 - self.survive_cof))
        parents1 = list(sorted_pop.items())[cof: cof * 2]
        parents2 = list(sorted_pop.items())[self.pop_number - cof: self.pop_number]

        i = 0
        for pop in sorted_pop.values():
            if random() > 0.5:
                pop[0] = parents1[i][1][0]
                pop[1] = parents2[i][1][1]
                pop[2] = self.func(parents1[i][1][0], parents2[i][1][1])
            else:
                pop[0] = parents2[i][1][0]
                pop[1] = parents1[i][1][1]
                pop[2] = self.func(parents2[i][1][0], parents1[i][1][1])
            i += 1
            if i >= cof:
                break

        self.population = sorted_pop

    def mutation(self, cur_gen):
        for pop in self.population.values():
            if random() < self.mut_chance:
                pop[0] += (random() - 0.5) * ((self.generations - cur_gen) / self.generations)
            if random() < self.mut_chance:
                pop[1] += (random() - 0.5) * ((self.generations - cur_gen) / self.generations)
            pop[2] = self.func(pop[0], pop[1])


def drawLab3(tab, window, ax, canvas):
    def run_optimization():
        pop_number = pop_number_var.get()
        survive = survive_var.get()
        mutation = mutation_var.get()
        iter_number = iterations_var.get()
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
        alpha = 0.7
        ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha)

        genetic = GeneticAlgorithm(target_func, pop_number, iter_number, [x_interval_min.get(), x_interval_max.get()],
                                   [y_interval_min.get(), y_interval_max.get()], mutation, survive)
        genetic.generate_start_population(abs(x_interval_max.get()), abs(x_interval_max.get()))

        # отрисовка стартовой популяции
        for j in range(pop_number):
            ax.scatter(genetic.population[j][0], genetic.population[j][1], genetic.population[j][2], c="red", s=1,
                       marker="s")

        best_individual = genetic.get_best_individual()
        ax.scatter(best_individual[1][0], best_individual[1][1], best_individual[1][2], c="blue")
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
            for j in range(pop_number):
                # отрисовка промежуточной популяции
                ax.scatter(genetic.population[j][0], genetic.population[j][1], genetic.population[j][2], c="red", s=1,
                           marker="s")

            genetic.select()
            genetic.mutation(i)

            best_individual = genetic.get_best_individual()

            ax.scatter(best_individual[1][0], best_individual[1][1], best_individual[1][2], c="blue")
            results_text.insert(tk.END,
                                f"Шаг {i}: Координаты ({best_individual[1][0]:.4f}, {best_individual[1][1]:.4f}),"
                                f" Значение функции: {best_individual[1][2]:.4f}\n")
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
        for j in range(pop_number):
            ax.scatter(genetic.population[j][0], genetic.population[j][1], genetic.population[j][2], c="red", s=1,
                       marker="s")

        best_individual = genetic.get_best_individual()
        ax.scatter(best_individual[1][0], best_individual[1][1], best_individual[1][2], color='black', marker='x', s=60)

        canvas.draw()
        window.update()
        results_text.insert(tk.END,
                            f"Результат:\nКоординаты ({best_individual[1][0]:.5f}, "
                            f"{best_individual[1][1]:.5f}),\nЗначение функции: {best_individual[1][2]:.8f}\n")
        results_text.yview_moveto(1)
        results_text.config(state=tk.DISABLED)

    # Создаем LabelFrame для "Инициализация значений"
    init_values_frame = ttk.LabelFrame(tab, text="Инициализация значений", padding=(15, 10))
    init_values_frame.grid(row=0, column=0, padx=10, pady=3, sticky="w")

    # Параметры задачи
    ttk.Label(init_values_frame, text="Размер популяции").grid(row=0, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Выживаемость").grid(row=1, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Шанс мутации").grid(row=2, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Число итераций").grid(row=3, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Задержка (сек)").grid(row=4, column=0, padx=10, pady=3, sticky="w")

    pop_number_var = tk.IntVar(value=20)
    survive_var = tk.DoubleVar(value=0.8)
    mutation_var = tk.DoubleVar(value=0.8)
    iterations_var = tk.IntVar(value=50)
    delay_var = tk.DoubleVar(value=0.01)

    pop_number_entry = ttk.Entry(init_values_frame, textvariable=pop_number_var)
    survive_entry = ttk.Entry(init_values_frame, textvariable=survive_var)
    mutation_entry = ttk.Entry(init_values_frame, textvariable=mutation_var)
    iterations_entry = ttk.Entry(init_values_frame, textvariable=iterations_var)
    delay_entry = ttk.Entry(init_values_frame, textvariable=delay_var)

    pop_number_entry.grid(row=0, column=1)
    survive_entry.grid(row=1, column=1)
    mutation_entry.grid(row=2, column=1)
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
