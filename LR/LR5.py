import tkinter as tk
from tkinter import ttk
import numpy as np
import time
from tkinter import scrolledtext
from matplotlib.colors import LinearSegmentedColormap
import random
from operator import itemgetter

from functions import target_function

# Инициализация:
#
# Создание объекта BeesAlgo с параметрами, такими как количество пчел, количество элитных и перспективных участков, количество пчел в элитных и перспективных участках, размер участков, и диапазоны для X и Y.
# Отображение начальной популяции:
#
# Генерация и отображение начальной популяции пчел на графике.
# Итерационный процесс оптимизации:
#
# Итерации, в каждой из которых:
# Запоминается предыдущее лучшее решение.
# Вызывается метод next_iteration для обновления популяции и выбора нового лучшего решения.
# Обновление популяции:
#
# Объединение элитных, перспективных и оставшихся пчел для обновления популяции.
# Выбор нового лучшего решения.
# Отображение элитных и перспективных пчел:
#
# Отображение на графике элитных и перспективных пчел в текущей популяции.
# Критерий останова:
#
# Проверка наличия стагнации в оптимизации (15 итераций без изменений).
# Итоговая популяция и результаты:
#
# Отображение итоговых элитных и перспективных пчел, а также лучшего найденного решения.

class BeesAlgo:
    def __init__(self, func, sn, pan, ean, ebn, pbn, a_s, x_range, y_range):
        self.func = func
        self.sn = sn  # bees_num
        self.pan = pan  # promising_areas_num
        self.ean = ean  # elite_areas_num
        self.ebn = ebn  # elite_bees_num
        self.pbn = pbn  # promising_bees_num
        self.a_s = a_s  # area_size

        self.x_range = x_range
        self.y_range = y_range

        self.bees = self.make_rand_points__calc_fitness(self.sn, self.x_range, self.y_range)
        self.elite_bees = None
        self.promising_bees = None
        self.rem_bees = None
        self.bee_best = min(self.bees, key=itemgetter(2))

    # рандом точек и вычисление фитнес функции для них
    def make_rand_points__calc_fitness(self, cnt, x_range, y_range):
        tmp = [[random.uniform(x_range[0], x_range[1]), random.uniform(y_range[0], y_range[1]), 0.0]
               for _ in range(cnt)]
        for i in tmp:
            i[2] = self.func(i[0], i[1])

        return tmp

    def recruitment(self, elite_areas_centres, promising_areas_centres):
        fitness_of_recruits = []
        for area_centre in elite_areas_centres:
            fitness_of_recruits.append(self.min_fitness_of_recruits(area_centre, self.ebn))
        for area_centre in promising_areas_centres:
            fitness_of_recruits.append(self.min_fitness_of_recruits(area_centre, self.pbn))
        return fitness_of_recruits

    def min_fitness_of_recruits(self, area, number_of_recruits):
        recruits = self.make_rand_points__calc_fitness(number_of_recruits,
                                                       [area[0] - self.a_s, area[0] + self.a_s],
                                                       [area[1] - self.a_s, area[1] + self.a_s])
        recruits.append(area)
        return min(recruits, key=itemgetter(2))

    def remaining_bees(self):
        return self.make_rand_points__calc_fitness(self.sn - self.pan - self.ean, self.x_range, self.y_range)

    def next_iteration(self):
        sorted_bees = sorted(self.bees, reverse=False, key=lambda x: x[2])

        elite = sorted_bees[:self.ean]
        promising = sorted_bees[self.ean: self.pan + self.ean]
        self.elite_bees = self.recruitment(elite, promising)[:self.ean]
        self.promising_bees = self.recruitment(elite, promising)[self.ean: self.pan + self.ean]
        self.rem_bees = self.remaining_bees()

        self.bees = self.elite_bees + self.promising_bees + self.rem_bees
        self.bee_best = min(self.bees, key=itemgetter(2))


def drawLab5(tab, window, ax, canvas):
    def run_optimization():
        iter_number = iterations_var.get()
        sn = bees_number_var.get()  # bees_num
        ean = elite_areas_num_var.get()  # elite_areas_num
        pan = promising_areas_num_var.get()  # promising_areas_num
        ebn = bees_in_elite_areas_num_var.get()  # elite_bees_num
        pbn = bees_in_promising_areas_num_var.get()  # promising_bees_num
        a_s = area_size_var.get()  # area_size
        delay = delay_var.get()  # area_size

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

        beeA = BeesAlgo(target_func, sn, pan, ean, ebn, pbn, a_s,
                        [x_interval_min.get(), x_interval_max.get()],
                        [y_interval_min.get(), y_interval_max.get()])

        # отрисовка стартовой популяции
        for bee in beeA.bees:
            ax.scatter(bee[0], bee[1], bee[2], c="red", s=1, marker="s")

        ax.scatter(beeA.bee_best[0], beeA.bee_best[1], beeA.bee_best[2], c="blue")

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
            prev_best_bee = beeA.bee_best
            beeA.next_iteration()

            # подсчет продолжительности стагнации
            if abs(prev_best_bee[2] - beeA.bee_best[2]) < 0.0001:
                cnt += 1
            else:
                cnt = 0

            if cnt == 15:
                break

            # отрисовка элитных пчел
            for bee in beeA.elite_bees:
                ax.scatter(bee[0], bee[1], bee[2], c="green", s=1, marker="s")

            # отрисовка элитных пчел
            for bee in beeA.promising_bees:
                ax.scatter(bee[0], bee[1], bee[2], c="cyan", s=1, marker="s")

            ax.scatter(beeA.bee_best[0], beeA.bee_best[1], beeA.bee_best[2], c="blue")
            results_text.insert(tk.END,
                                f"Шаг {i}: Координаты ({beeA.bee_best[0]:.4f}, "
                                f"{beeA.bee_best[1]:.4f}),"
                                f" Значение функции: {beeA.bee_best[2]:.4f}\n")
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
        # отрисовка элитных пчел
        for bee in beeA.elite_bees:
            ax.scatter(bee[0], bee[1], bee[2], c="green", s=1, marker="s")

        # отрисовка элитных пчел
        for bee in beeA.promising_bees:
            ax.scatter(bee[0], bee[1], bee[2], c="cyan", s=1, marker="s")

        ax.scatter(beeA.bee_best[0], beeA.bee_best[1], beeA.bee_best[2], c='black', marker='x', s=60)
        ax.scatter(beeA.bee_best[0], beeA.bee_best[1], beeA.bee_best[2], c='blue', marker='s')

        canvas.draw()
        window.update()
        results_text.insert(tk.END,
                            f"Результат:\nКоординаты ({beeA.bee_best[0]:.5f}, "
                            f"{beeA.bee_best[1]:.5f}),\nЗначение функции: {beeA.bee_best[2]:.8f}\n")
        results_text.yview_moveto(1)
        results_text.config(state=tk.DISABLED)

    # Создаем LabelFrame для "Инициализация значений"
    init_values_frame = ttk.LabelFrame(tab, text="Инициализация значений", padding=(15, 10))
    init_values_frame.grid(row=0, column=0, padx=10, pady=3, sticky="w")

    # Параметры задачи
    ttk.Label(init_values_frame, text="Число итераций").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    ttk.Label(init_values_frame, text="Кол-во разведчиков").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    ttk.Label(init_values_frame, text="Кол-во элитных участков").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    ttk.Label(init_values_frame, text="Кол-во перспективных участков").grid(row=3, column=0, padx=10, pady=5,
                                                                            sticky="w")
    ttk.Label(init_values_frame, text="Кол-во пчел в элитных участках").grid(row=4, column=0, padx=10, pady=5,
                                                                             sticky="w")
    ttk.Label(init_values_frame, text="Кол-во пчел в \nперспективных участках").grid(row=5, column=0, padx=10,
                                                                                     sticky="w")
    ttk.Label(init_values_frame, text="Размер участков").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    ttk.Label(init_values_frame, text="Задержка (сек)").grid(row=7, column=0, padx=10, pady=5, sticky="w")

    iterations_var = tk.IntVar(value=100)
    bees_number_var = tk.IntVar(value=50)
    elite_areas_num_var = tk.IntVar(value=3)
    promising_areas_num_var = tk.IntVar(value=15)
    bees_in_elite_areas_num_var = tk.IntVar(value=12)
    bees_in_promising_areas_num_var = tk.IntVar(value=8)
    area_size_var = tk.DoubleVar(value=0.5)
    delay_var = tk.DoubleVar(value=0.01)

    iterations_entry = ttk.Entry(init_values_frame, textvariable=iterations_var, width=10)
    bees_number_entry = ttk.Entry(init_values_frame, textvariable=bees_number_var, width=10)
    elite_areas_num_entry = ttk.Entry(init_values_frame, textvariable=elite_areas_num_var, width=10)
    promising_areas_num_entry = ttk.Entry(init_values_frame, textvariable=promising_areas_num_var, width=10)
    bees_in_elite_areas_num_entry = ttk.Entry(init_values_frame, textvariable=bees_in_elite_areas_num_var, width=10)
    bees_in_promising_areas_num_entry = ttk.Entry(init_values_frame, textvariable=bees_in_promising_areas_num_var,
                                                  width=10)
    area_size_entry = ttk.Entry(init_values_frame, textvariable=area_size_var, width=10)
    delay_entry = ttk.Entry(init_values_frame, textvariable=delay_var, width=10)

    iterations_entry.grid(row=0, column=1)
    bees_number_entry.grid(row=1, column=1)
    elite_areas_num_entry.grid(row=2, column=1)
    promising_areas_num_entry.grid(row=3, column=1)
    bees_in_elite_areas_num_entry.grid(row=4, column=1)
    bees_in_promising_areas_num_entry.grid(row=5, column=1)
    area_size_entry.grid(row=6, column=1)
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
    results_text = scrolledtext.ScrolledText(tab, wrap=tk.WORD, height=12, width=38, padx=2, state=tk.DISABLED)
    results_text.grid(row=18, column=0, padx=10)
