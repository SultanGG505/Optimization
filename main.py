import numpy as np
import matplotlib.pyplot as plt

# Задаем функцию, которую мы хотим оптимизировать
def target_function(x):
    return x**2

# Задаем производную функции (градиент)
def gradient(x):
    return 2 * x

# Начальное значение x
x = 6

# Задаем параметры градиентного спуска
learning_rate = 0.1
num_iterations = 10

<<<<<<< Updated upstream
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('sd')
=======
# Создаем списки для хранения значений x и y (значения функции) на каждой итерации
x_history = [x]
y_history = [target_function(x)]
>>>>>>> Stashed changes

# Итерируемся по методу градиентного спуска и сохраняем значения x и y на каждой итерации
for _ in range(num_iterations):
    x -= learning_rate * gradient(x)
    x_history.append(x)
    y_history.append(target_function(x))

# Создаем график для визуализации
plt.figure(figsize=(10, 5))
plt.plot(x_history, y_history, marker='o', linestyle='-')
plt.title('Градиентный спуск с постоянным шагом')
plt.xlabel('x')
plt.ylabel('Значение функции')
plt.grid(True)
plt.show()
