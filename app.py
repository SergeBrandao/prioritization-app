import streamlit as st

# Заголовок приложения
st.title("Выбор приоритетного фактора")

# Список факторов (можно добавить свои)
factors = ["Фактор 1", "Фактор 2", "Фактор 3", "Фактор 4"]

# Создаём две колонки для выбора между факторами
col1, col2 = st.columns(2)

# Перебираем пары факторов
for i in range(len(factors)):
    for j in range(i + 1, len(factors)):
        f1, f2 = factors[i], factors[j]
        
        # Отображаем сравнение
        with col1:
            if st.button(f1):
                st.session_state[f1] = st.session_state.get(f1, 0) + 1
        
        with col2:
            if st.button(f2):
                st.session_state[f2] = st.session_state.get(f2, 0) + 1

# Итоговый рейтинг факторов
st.subheader("Ранжирование факторов:")
sorted_factors = sorted(st.session_state.items(), key=lambda x: x[1], reverse=True)
for factor, score in sorted_factors:
    st.write(f"**{factor}**: {score} баллов")
