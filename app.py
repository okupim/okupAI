import streamlit as st
from groq import Groq
import os

# Настройка страницы
st.set_page_config(page_title="okupAi", page_icon="💜", layout="centered")

# Кастомный CSS для фиолетово-черного дизайна
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
        animation: fadeIn 0.5s;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    /* Фиолетовый акцент для кнопок и заголовков */
    h1, .stButton>button {
        color: #8B5CF6 !important;
    }
    .stButton>button {
        border: 1px solid #8B5CF6;
        background-color: transparent;
    }
    .stButton>button:hover {
        background-color: #8B5CF6;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💜 okupAi")

# Инициализация Groq 
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "no_key"))

# Хранилище истории чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Логика ввода
if prompt := st.chat_input("Спроси у okupAi..."):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ответ ИИ
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            with st.spinner("okupAi думает..."):
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                    stream=True,
                )
                
                for chunk in completion:
                    full_response += (chunk.choices[0].delta.content or "")
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Ошибка: {e}")

    st.session_state.messages.append({"role": "assistant", "content": full_response})
