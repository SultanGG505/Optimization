import tkinter as tk
from tkinter import ttk
import numpy as np
import time
from tkinter import scrolledtext
from matplotlib.colors import LinearSegmentedColormap
import random
from operator import itemgetter

from LR.LR3 import GeneticAlgorithm
from functions import target_function


class PSO:
    def __init__(self, func, pop_size, particles, position_x, position_y, fi_p, fi_g):
        self.func = func
        self.pop_size = pop_size
        self.pos_x = float(position_x)
        self.pos_y = float(position_y)

        assert fi_p + fi_g > 4, "Сумма коэффициентов должна быть > 4"
        self.fi_p = fi_p
        self.fi_g = fi_g
        # инерционный вес
        self.xi = 2 / (np.abs(2 - (fi_p + fi_g) - np.sqrt((fi_p + fi_g) ** 2 - 4 * (fi_p + fi_g))))

        self.particles = list(particles.values())
        self.nostalgia = self.particles.copy()
        self.velocity = [[0.0 for _ in range(2)] for _ in range(self.pop_size)]
        self.particle_best = min(self.particles, key=itemgetter(2))

    def update_velocity(self, velocity, particle, point_best) -> list:
        new_vel = list()
        for i in range(2):
            r_p = random.random()
            r_g = random.random()

            new_vel.append(self.xi * (velocity[i] + self.fi_p * r_p * (point_best[i] - particle[i]) + self.fi_g * r_g *
                                      (self.particle_best[i] - particle[i])))
        return new_vel

    def update_position(self, velocity, particle):
        x = particle[0] + velocity[0]
        y = particle[1] + velocity[1]

        return [x, y, self.func(x, y)]

    def next_iteration(self):
        for i in range(self.pop_size):
            if self.nostalgia[i][2] < self.particles[i][2]:
                point_best = self.nostalgia[i]
            else:
                self.nostalgia[i] = self.particles[i]
                point_best = self.particles[i]

            self.velocity[i] = PSO.update_velocity(self, self.velocity[i], self.particles[i], point_best)
            self.particles[i] = PSO.update_position(self, self.velocity[i], self.particles[i])

        self.particle_best = min(self.particles, key=itemgetter(2))


def drawLab8(tab, window, ax, canvas):
    def run_optimization():
        pso_iter = pso_iterations_var.get()
        population_size = population_size_var.get()
        coef_p = coef_p_var.get()
        coef_g = coef_g_var.get()
        ga_iter = ga_iterations_var.get()
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

        genetic = GeneticAlgorithm(target_func, ga_iter, population_size, [x_interval_min.get(), x_interval_max.get()],
                                   [y_interval_min.get(), y_interval_max.get()])
        genetic.generate_start_population()

        # отрисовка стартовой популяции
        for j in range(population_size):
            ax.scatter(genetic.population[j][0], genetic.population[j][1], genetic.population[j][2], c="red", s=1,
                       marker="s")

        best_individual = genetic.get_best_individual()
        ax.scatter(best_individual[1][0], best_individual[1][1], best_individual[1][2], c="green")
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
        for i in range(ga_iter):
            for j in range(population_size):
                # отрисовка промежуточной популяции
                ax.scatter(genetic.population[j][0], genetic.population[j][1], genetic.population[j][2], c="red", s=1,
                           marker="s")

            genetic.select()
            genetic.mutation(i)

            best_individual = genetic.get_best_individual()

            ax.scatter(best_individual[1][0], best_individual[1][1], best_individual[1][2], c="green")
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
        for j in range(population_size):
            ax.scatter(genetic.population[j][0], genetic.population[j][1], genetic.population[j][2], c="red", s=1,
                       marker="s")

        best_individual = genetic.get_best_individual()
        ax.scatter(best_individual[1][0], best_individual[1][1], best_individual[1][2], c="green")

        canvas.draw()
        window.update()

        # очистка графика
        ax.cla()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha)
        canvas.draw()
        results_text.insert(tk.END, "\n********************\nНачало работы РА\n********************\n\n")
        results_text.yview_moveto(1)

        pso = PSO(target_func, population_size, genetic.population, 5, 5, coef_p, coef_g)

        # отрисовка стартовой популяции
        for particle in pso.particles:
            ax.scatter(particle[0], particle[1], particle[2], c="red", s=1, marker="s")

        ax.scatter(pso.particle_best[0], pso.particle_best[1], pso.particle_best[2], c="blue")
        canvas.draw()
        window.update()

        # очистка графика
        ax.cla()
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.plot_surface(X, Y, Z, cmap=cmap, alpha=alpha)
        canvas.draw()

        # отрисовка промежуточной популяции и эволюция
        for i in range(pso_iter):
            pso.next_iteration()
            for particle in pso.particles:
                # отрисовка промежуточной популяции
                ax.scatter(particle[0], particle[1], particle[2], c="red", s=1, marker="s")

            ax.scatter(pso.particle_best[0], pso.particle_best[1], pso.particle_best[2], c="blue")
            results_text.insert(tk.END,
                                f"Шаг {i}: Координаты ({pso.particle_best[0]:.4f}, "
                                f"{pso.particle_best[1]:.4f}),"
                                f" Значение функции: {pso.particle_best[2]:.4f}\n")
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
        for particle in pso.particles:
            ax.scatter(particle[0], particle[1], particle[2], c="red", s=1, marker="s")

        ax.scatter(pso.particle_best[0], pso.particle_best[1], pso.particle_best[2], color='black', marker='x', s=60)

        canvas.draw()
        window.update()
        results_text.insert(tk.END,
                            f"Результат:\nКоординаты ({pso.particle_best[0]:.5f}, "
                            f"{pso.particle_best[1]:.5f}),\nЗначение функции: {pso.particle_best[2]:.8f}\n")
        results_text.yview_moveto(1)
        results_text.config(state=tk.DISABLED)

    # Создаем LabelFrame для "Инициализация значений"
    init_values_frame = ttk.LabelFrame(tab, text="Инициализация значений", padding=(15, 10))
    init_values_frame.grid(row=0, column=0, padx=10, pady=3, sticky="w")

    # Параметры задачи
    ttk.Label(init_values_frame, text="Размер популяции").grid(row=0, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Количество итераций\nгенетического алгоритма"). \
        grid(row=1, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Количество итераций\nроевого алгоритма").\
        grid(row=2, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Коэффициент p").grid(row=3, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Коэффициент g").grid(row=4, column=0, padx=10, pady=3, sticky="w")
    ttk.Label(init_values_frame, text="Задержка (сек)").grid(row=5, column=0, padx=10, pady=3, sticky="w")

    population_size_var = tk.IntVar(value=20)
    ga_iterations_var = tk.IntVar(value=10)
    pso_iterations_var = tk.IntVar(value=30)
    coef_p_var = tk.DoubleVar(value=5)
    coef_g_var = tk.DoubleVar(value=5)
    delay_var = tk.DoubleVar(value=0.01)

    population_size_entry = ttk.Entry(init_values_frame, textvariable=population_size_var)
    ga_iterations_entry = ttk.Entry(init_values_frame, textvariable=ga_iterations_var)
    pso_iterations_entry = ttk.Entry(init_values_frame, textvariable=pso_iterations_var)
    coef_p_entry = ttk.Entry(init_values_frame, textvariable=coef_p_var)
    coef_g_entry = ttk.Entry(init_values_frame, textvariable=coef_g_var)
    delay_entry = ttk.Entry(init_values_frame, textvariable=delay_var)

    population_size_entry.grid(row=0, column=1)
    ga_iterations_entry.grid(row=1, column=1)
    pso_iterations_entry.grid(row=2, column=1)
    coef_p_entry.grid(row=3, column=1)
    coef_g_entry.grid(row=4, column=1)
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
    results_text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=16, width=35, padx=2, state=tk.DISABLED)
    results_text.grid(row=16, column=0, padx=10)
