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

# Инициализация session_state при первом запуске
if "factors" not in st.session_state:
    st.session_state.factors = []
    st.session_state.scores = {}
    st.session_state.pairs = []
    st.session_state.current_pair = 0
    st.session_state.comparison_history = {}

# Кнопка для подтверждения ввода факторов
if st.button("✅ Подтвердить ввод факторов"):
    st.session_state.factors = [f.strip() for f in factors_input.split("\n") if f.strip()]
    st.session_state.scores = {factor: 0 for factor in st.session_state.factors}
    st.session_state.pairs = list(itertools.combinations(st.session_state.factors, 2))
    random.shuffle(st.session_state.pairs)
    st.session_state.current_pair = 0
    st.session_state.comparison_history = {}
    st.rerun()

# Проверяем, есть ли уже введённые факторы
if len(st.session_state.factors) < 2:
    st.warning("Введите как минимум 2 фактора и нажмите '✅ Подтвердить ввод факторов'!")
    st.stop()

# Функция обработки выбора
def choose_winner(winner):
    if st.session_state.current_pair < len(st.session_state.pairs):
        f1, f2 = st.session_state.pairs[st.session_state.current_pair]
        st.session_state.comparison_history[(f1, f2)] = winner
        if winner == "ничья":
            st.session_state.scores[f1] += 0.5
            st.session_state.scores[f2] += 0.5
        else:
            st.session_state.scores[winner] += 1
        st.session_state.current_pair += 1
        st.rerun()

# Функция перемещения по сравнениям
def move_to(index):
    if 0 <= index < len(st.session_state.pairs):
        st.session_state.current_pair = index
        st.rerun()

# Показываем текущую пару
if st.session_state.current_pair < len(st.session_state.pairs):
    f1, f2 = st.session_state.pairs[st.session_state.current_pair]
    st.write("Какой фактор важнее?")
    previous_winner = st.session_state.comparison_history.get((f1, f2))

    # Обновлённая функция кнопок выбора (исправлена ошибка TypeError)
    def styled_button(text, key, is_selected):
        return st.button(text, key=key, help="Выбранный вариант" if is_selected else None, 
                         on_click=lambda: choose_winner(text), use_container_width=True, disabled=is_selected)

    col1, col2, col3 = st.columns(3)
    with col1:
        styled_button(f1, f"btn_{f1}_{f2}", previous_winner == f1)
    with col2:
        styled_button("Ничья", f"btn_draw_{f1}_{f2}", previous_winner == "ничья")
    with col3:
        styled_button(f2, f"btn_{f2}_{f1}", previous_winner == f2)

    # Кнопки навигации
    col_home, col_back, col_next, col_end = st.columns(4)
    with col_home:
        st.button("⏮ В начало", on_click=lambda: move_to(0))
    with col_back:
        st.button("⬅ Назад", on_click=lambda: move_to(st.session_state.current_pair - 1))
    with col_next:
        st.button("➡ Вперёд", on_click=lambda: move_to(st.session_state.current_pair + 1))
    with col_end:
        st.button("⏭ В конец", on_click=lambda: move_to(len(st.session_state.pairs) - 1))
else:
    st.subheader("Ранжирование факторов:")
    sorted_factors = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
    for factor, score in sorted_factors:
        st.write(f"**{factor}**: {score} баллов")

    # Создание файлов Excel
    df_ranking = pd.DataFrame(sorted_factors, columns=["Фактор", "Баллы"])
    df_history = pd.DataFrame([
        [idx + 1, pair[0], 1 if winner == pair[0] else 0.5 if winner == "ничья" else 0, 
         pair[1], 1 if winner == pair[1] else 0.5 if winner == "ничья" else 0]
        for idx, (pair, winner) in enumerate(st.session_state.comparison_history.items())
    ], columns=["№ пары", "Фактор 1", "Балл 1", "Фактор 2", "Балл 2"])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_ranking.to_excel(writer, index=False, sheet_name="Ранжирование")
        df_history.to_excel(writer, index=False, sheet_name="История сравнений")
    output.seek(0)

    st.download_button("📥 Скачать Excel", data=output, file_name=file_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
