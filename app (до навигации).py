import streamlit as st
import itertools
import pandas as pd
import random
import io

st.title("Выбор приоритетного фактора")

# Поле для ввода названия файла
file_name = st.text_input("Введите название файла:", "результаты.xlsx")

# Поле для ввода факторов (по одному на строке)
factors_input = st.text_area("Введите факторы (каждый на новой строке):")

# Кнопка для подтверждения ввода факторов
if st.button("✅ Подтвердить ввод факторов"):
    st.session_state.factors = [f.strip() for f in factors_input.split("\n") if f.strip()]
    st.session_state.scores = {factor: 0 for factor in st.session_state.factors}
    st.session_state.pairs = list(itertools.combinations(st.session_state.factors, 2))
    random.shuffle(st.session_state.pairs)
    st.session_state.current_pair = 0
    st.session_state.total_pairs = len(st.session_state.pairs)  # Общее кол-во пар
    st.session_state.finished = False
    st.session_state.comparison_history = []  # История всех сравнений
    st.rerun()

# Проверяем, есть ли уже введённые факторы
if "factors" not in st.session_state or len(st.session_state.factors) < 2:
    st.warning("Введите как минимум 2 фактора и нажмите '✅ Подтвердить ввод факторов'!")
    st.stop()

# Функция обработки выбора
def choose_winner(winner):
    if st.session_state.current_pair < st.session_state.total_pairs:
        f1, f2 = st.session_state.pairs[st.session_state.current_pair]

        # Записываем результат сравнения в историю
        if winner == "ничья":
            st.session_state.scores[f1] += 0.5
            st.session_state.scores[f2] += 0.5
            st.session_state.comparison_history.append([st.session_state.current_pair + 1, f1, 0.5, f2, 0.5])
        else:
            st.session_state.scores[winner] += 1
            loser = f1 if winner == f2 else f2
            st.session_state.comparison_history.append([st.session_state.current_pair + 1, winner, 1, loser, 0])

        st.session_state.current_pair += 1

    if st.session_state.current_pair >= st.session_state.total_pairs:
        st.session_state.finished = True

    st.rerun()

# Показываем счётчик сравнения пар
st.subheader(f"Прогресс: {st.session_state.current_pair} / {st.session_state.total_pairs} пар")

# Показываем текущую пару
if not st.session_state.finished and st.session_state.current_pair < st.session_state.total_pairs:
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

    # Создание первого Excel-файла (ранжирование)
    df_ranking = pd.DataFrame(sorted_factors, columns=["Фактор", "Баллы"])
    output_ranking = io.BytesIO()
    with pd.ExcelWriter(output_ranking, engine="openpyxl") as writer:
        df_ranking.to_excel(writer, index=False)
    output_ranking.seek(0)

    # Создание второго Excel-файла (история сравнений)
    df_history = pd.DataFrame(st.session_state.comparison_history, columns=["№ пары", "Фактор 1", "Балл 1", "Фактор 2", "Балл 2"])
    output_history = io.BytesIO()
    with pd.ExcelWriter(output_history, engine="openpyxl") as writer:
        df_history.to_excel(writer, index=False)
    output_history.seek(0)

    # Кнопка для скачивания итогового файла с ранжированием
    st.download_button(
        label="📥 Скачать результаты в Excel",
        data=output_ranking,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Кнопка для скачивания файла с историей сравнений
    st.download_button(
        label="📥 Скачать историю сравнений в Excel",
        data=output_history,
        file_name=f"история_{file_name}",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
