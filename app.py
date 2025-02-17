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
    st.session_state.total_pairs = len(st.session_state.pairs)
    st.session_state.finished = False
    st.session_state.comparison_history = {}
    st.session_state.selected_winner = None  # Хранит временный выбор пользователя
    st.rerun()

# Проверяем, есть ли уже введённые факторы
if "factors" not in st.session_state or len(st.session_state.factors) < 2:
    st.warning("Введите как минимум 2 фактора и нажмите '✅ Подтвердить ввод факторов'!")
    st.stop()

# Получаем текущую пару
current_pair_index = st.session_state.current_pair
total_pairs = st.session_state.total_pairs
f1, f2 = st.session_state.pairs[current_pair_index]

# Временное сохранение выбора
if f"{f1}-{f2}" not in st.session_state.comparison_history:
    st.session_state.comparison_history[f"{f1}-{f2}"] = None  # По умолчанию нет выбора

# Функция обработки выбора
def choose_winner(winner):
    st.session_state.selected_winner = winner

# Функция подтверждения выбора
def confirm_choice():
    pair_key = f"{f1}-{f2}"
    previous_winner = st.session_state.comparison_history[pair_key]

    if previous_winner:
        # Отменяем предыдущий выбор
        if previous_winner == "ничья":
            st.session_state.scores[f1] -= 0.5
            st.session_state.scores[f2] -= 0.5
        else:
            st.session_state.scores[previous_winner] -= 1

    # Записываем новый выбор
    if st.session_state.selected_winner == "ничья":
        st.session_state.scores[f1] += 0.5
        st.session_state.scores[f2] += 0.5
    else:
        st.session_state.scores[st.session_state.selected_winner] += 1

    st.session_state.comparison_history[pair_key] = st.session_state.selected_winner
    st.session_state.selected_winner = None  # Очистка временного выбора
    st.rerun()

# Функция перемещения по парам
def move_to(index):
    if 0 <= index < total_pairs:
        st.session_state.current_pair = index
        st.session_state.selected_winner = None  # Сбрасываем временный выбор
        st.rerun()

# Показываем текущую пару и выбор пользователя
st.subheader(f"Прогресс: {current_pair_index + 1} / {total_pairs} пар")

st.write(f"Какой фактор важнее?")
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

# Кнопки подтверждения выбора
if st.session_state.selected_winner:
    st.write(f"Вы выбрали: **{st.session_state.selected_winner}**")
    st.button("✅ Подтвердить", on_click=confirm_choice)

# Кнопки навигации
col_back, col_home, col_end, col_next = st.columns(4)
with col_home:
    st.button("⏮ В начало", on_click=lambda: move_to(0))
with col_back:
    st.button("⬅ Назад", on_click=lambda: move_to(current_pair_index - 1))
with col_next:
    st.button("➡ Вперёд", on_click=lambda: move_to(current_pair_index + 1))
with col_end:
    st.button("⏭ В конец", on_click=lambda: move_to(total_pairs - 1))

# Показываем кнопки скачивания после завершения всех сравнений
if all(value is not None for value in st.session_state.comparison_history.values()):
    st.subheader("Ранжирование факторов:")
    sorted_factors = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    for factor, score in sorted_factors:
        st.write(f"**{factor}**: {score} баллов")

    # Создание файлов Excel
    df_ranking = pd.DataFrame(sorted_factors, columns=["Фактор", "Баллы"])
    output_ranking = io.BytesIO()
    with pd.ExcelWriter(output_ranking, engine="openpyxl") as writer:
        df_ranking.to_excel(writer, index=False)
    output_ranking.seek(0)

    df_history = pd.DataFrame([
        [idx + 1, pair.split("-")[0], 1 if winner == pair.split("-")[0] else 0.5 if winner == "ничья" else 0, 
         pair.split("-")[1], 1 if winner == pair.split("-")[1] else 0.5 if winner == "ничья" else 0]
        for idx, (pair, winner) in enumerate(st.session_state.comparison_history.items())
    ], columns=["№ пары", "Фактор 1", "Балл 1", "Фактор 2", "Балл 2"])
    
    output_history = io.BytesIO()
    with pd.ExcelWriter(output_history, engine="openpyxl") as writer:
        df_history.to_excel(writer, index=False)
    output_history.seek(0)

    st.download_button(
        label="📥 Скачать результаты в Excel",
        data=output_ranking,
        file_name=file_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.download_button(
        label="📥 Скачать историю сравнений в Excel",
        data=output_history,
        file_name=f"история_{file_name}",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
