import itertools
import pandas as pd
import random
import os
import tkinter as tk
from tkinter import messagebox

# Ввод названия файла
file_name = input("Введите название итогового Excel-файла (без .xlsx): ") + ".xlsx"

# Ввод факторов
print("Введите факторы (по одному на строку). Когда закончите, просто нажмите Enter:")
factors = []
while True:
    factor = input()
    if factor == "":
        break
    factors.append(factor)

# Проверка, что введено хотя бы 2 фактора
if len(factors) < 2:
    print("Ошибка: нужно ввести хотя бы 2 фактора!")
    exit()

# Создаём словарь для подсчёта баллов
scores = {factor: 0 for factor in factors}

# Генерируем все возможные пары и перемешиваем их
pairs = list(itertools.combinations(factors, 2))
random.shuffle(pairs)

# Создаём окно с Tkinter
root = tk.Tk()
root.title("Выбор приоритетного фактора")
root.geometry("400x250")

# Переменная для отслеживания текущей пары
pair_index = 0

# Функция обработки нажатия кнопки
def choose_winner(winner):
    global pair_index
    f1, f2 = pairs[pair_index]

    if winner == f1:
        scores[f1] += 1
    elif winner == f2:
        scores[f2] += 1
    else:  # Ничья
        scores[f1] += 0.5
        scores[f2] += 0.5

    pair_index += 1  # Переход к следующей паре

    if pair_index < len(pairs):
        update_buttons()  # Обновляем кнопки для следующей пары
    else:
        save_results()  # Сохраняем результаты и закрываем окно

# Функция обновления кнопок
def update_buttons():
    f1, f2 = pairs[pair_index]
    button1.config(text=f1, command=lambda: choose_winner(f1))
    button2.config(text=f2, command=lambda: choose_winner(f2))
    button3.config(text="Ничья", command=lambda: choose_winner("draw"))

# Функция сохранения результатов
def save_results():
    df = pd.DataFrame(sorted(scores.items(), key=lambda x: x[1], reverse=True), columns=["Фактор", "Баллы"])
    df.to_excel(file_name, index=False)
    
    # Выводим сообщение об успешном сохранении
    messagebox.showinfo("Готово!", f"Ранжирование сохранено в:\n{os.path.abspath(file_name)}")
    root.destroy()  # Закрываем окно

# Создаём три кнопки
button1 = tk.Button(root, text="", font=("Arial", 14), width=20, height=2)
button2 = tk.Button(root, text="", font=("Arial", 14), width=20, height=2)
button3 = tk.Button(root, text="Ничья", font=("Arial", 14), width=20, height=2)

# Размещаем кнопки
button1.pack(pady=10)
button2.pack(pady=10)
button3.pack(pady=10)

# Запускаем первый раунд
update_buttons()

# Запускаем Tkinter
root.mainloop()
