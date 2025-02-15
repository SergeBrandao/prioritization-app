import streamlit as st
import itertools
import pandas as pd
import random

st.title("Выбор приоритетного фактора")

# Поле для ввода названия итогового файла
file_name = st.text_input("Введите название итогового Excel-файла:", "результаты.xlsx")

# Поле для ввода факторов (по одному на строку)
factors_input = st.text_area("Введите факторы (каждый на новой строке):")
factors = [f.strip() for f in factors_input.split("\n") if f.strip()]  # Убираем пустые строки и пробелы

# Проверка: нужно минимум 2 фактора
if len(factors) < 2:
    st.warning("Введите как минимум 2 фактора!")
    st.stop()

# Инициализация баллов
if "scores" not in st.session_state:
    st.session_state.scores = {factor: 0 for factor in factors}
    st.session_state.pairs = list(itertools.combinations(factors, 2))  # Генерация всех пар
    random.shuffle(st.session_state.pairs)  # Перемешиваем пары
    st.session_state.current_pair = 0  # Текущая пара

# Функция обработки выбора
def choose_winner(winner):
    f1, f2 = st.session_state.pairs[st.session_state.current_pair]
    
    if winner == "ничья":
        st.session_state.scores[f1] += 0.5
        st.session_state.scores[f2] += 0.5
    else:
        st.session_state.scores[winner] += 1

    st.session_state.current_pair += 1  # Переход к следующей паре
    if st.session_state.current_pair >= len(st.session_state.pairs):
        st.session_state.finished = True  # Завершение сравнений

# Показываем текущую пару
if "finished" not in st.session_state:
    f1, f2 = st.session_state.pairs[st.session_state.current_pair]
    st.write("Какой фактор важнее?")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f1):
            choose_winner(f1)
            st.experimental_rerun()
    with col2:
        if st.button("Ничья"):
            choose_winner("ничья")
            st.experimental_rerun()
    with col3:
        if st.button(f2):
            choose_winner(f2)
            st.experimental_rerun()
else:
    # Сортируем и показываем результаты
    st.subheader("Ранжирование факторов:")
    sorted_factors = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    for factor, score in sorted_factors:
        st.write(f"**{factor}**: {score} баллов")

    # Сохранение результатов в Excel
    df = pd.DataFrame(sorted_factors, columns=["Фактор", "Баллы"])
    df.to_excel(file_name, index=False)
    st.success(f"Файл сохранён как {file_name}!")
