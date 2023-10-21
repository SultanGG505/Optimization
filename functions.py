import numpy as np


def target_function(x, y, function_var):
    if function_var.get() == "Функция Химмельблау":
        return himmelblau(x, y), himmelblau
    elif function_var.get() == "2x^2+3y^2+4xy-6x-3y":
        return lr2_func(x, y), lr2_func
    elif function_var.get() == "Функция Розенброка":
        return rosenbrock(x, y), rosenbrock
    elif function_var.get() == "Функция Растригина":
        return rastrigin(x, y), rastrigin
    elif function_var.get() == "Функция сферы":
        return sphere(x, y), sphere
    else:
        return


def himmelblau(x, y):
    return ((x ** 2 + y - 11) ** 2) + ((x + y ** 2 - 7) ** 2)


def lr2_func(x, y):
    return 2 * x * x + 3 * y * y + 4 * x * y - 6 * x - 3 * y


def rosenbrock(x, y):
    return (1.0 - x) ** 2 + 100.0 * (y - x * x) ** 2


def rastrigin(x, y):
    return x ** 2 - 10 * np.cos(2 * np.pi * x) + y ** 2 - 10 * np.cos(2 * np.pi * y)


def sphere(x, y):
    return x ** 2 + y ** 2
