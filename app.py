import streamlit as st
import itertools
import pandas as pd
import random
import io

st.title("Выбор приоритетного фактора")

# Поле для ввода названия файла
file_name = st.text_input("Введите название файла:", "результаты.xlsx")

# Поле для ввода факторов (по одному на строку)
factors_input = st.text_area("Введите факторы (каждый на новой строке):")
factors = [f.strip() for f in factors_input.split("\n") if f.strip()]

# Проверка: нужно минимум 2 фактора
if len(factors) < 2:
    st.warning("Введите как минимум 2 фактора!")
    st.stop()

# Инициализация переменных
if "scores" not in st.session_state:
    st.session_state.scores = {factor: 0 for factor in factors}
    st.session_state.pairs = list(itertools.combinations(factors, 2))
    random.shuffle(st.session_state.pairs)
    st.session_state.current_pair = 0
    st.session_state.finished = False

# Функция обработки выбора
def choose_winner(winner):
    if st.session_state.current_pair < len(st.session_state.pairs):
        f1, f2 = st.session_state.pairs[st.session_state.current_pair]

        if winner == "ничья":
            st.session_state.scores[f1] += 0.5
            st.session_state.scores[f2] += 0.5
        else:
            st.session_state.scores[winner] += 1

        st.session_state.current_pair += 1

    if st.session_state.current_pair >= len(st.session_state.pairs):
        st.session_state.finished = True

    st.rerun()

# Показываем текущую пару
if not st.session_state.finished and st.session_state.current_pair < len(st.session_state.pairs):
    f1, f2 = st.session_state.pairs[st.session_state.current_pair]
    st.write("Какой фактор важнее?")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f1, key=f"btn_{f1}_{f2}"):
            choose_winner(f1)
    with col2:
        if st.button("Ничья", key=f"btn_draw_{f1}_{f2}"):
            choose_winner("ничья")
    with col3:
        if st.button(f2, key=f"btn_{f2}_{f1}"):
            choose_winner(f2)

else:
    # Сортируем и показываем результаты
    st.subheader("Ранжирование факторов:")
    sorted_factors = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    for factor, score in sorted_factors:
        st.write(f"**{factor}**: {score} баллов")

    # Создание Excel-файла в памяти (без сохранения на диск)
    df = pd.DataFrame(sorted_factors, columns=["Фактор", "Баллы"])
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    output.seek(0)

    # Кнопка для скачивания
    st.download_button(
        label="📥 Скачать результаты в Excel",
        data=output,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
