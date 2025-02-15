import streamlit as st

# Заголовок приложения
st.title("Выбор приоритетного фактора")

# Список факторов (можно добавить свои)
factors = ["Фактор 1", "Фактор 2", "Фактор 3", "Фактор 4"]

# Инициализация состояния сессии для хранения баллов
if "scores" not in st.session_state:
    st.session_state.scores = {factor: 0 for factor in factors}

# Перебираем пары факторов
for i in range(len(factors)):
    for j in range(i + 1, len(factors)):
        f1, f2 = factors[i], factors[j]

        # Выводим название факторов
        st.write(f"Какой фактор важнее?")

        # Две кнопки для выбора
        col1, col2 = st.columns(2)
        if col1.button(f1, key=f"{f1}-{f2}"):
            st.session_state.scores[f1] += 1
        if col2.button(f2, key=f"{f2}-{f1}"):
            st.session_state.scores[f2] += 1

# Итоговый рейтинг факторов
st.subheader("Ранжирование факторов:")
sorted_factors = sorted(st.session_state.scores.items(), key=lambda x: x[1], reverse=True)
for factor, score in sorted_factors:
    st.write(f"**{factor}**: {score} баллов")
