import streamlit as st
from groq import Groq
import os

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(
    page_title="okupAi", 
    page_icon="💜", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- СТИЛИЗАЦИЯ (CSS) ---
st.markdown("""
<style>
    /* Основной фон в стиле Deep Dark */
    .stApp {
        background-color: #0b0d11;
        color: #e5e7eb;
    }
    
    /* Боковая панель */
    [data-testid="stSidebar"] {
        background-color: #161a23;
        border-right: 1px solid #2d333b;
    }

    /* Пузыри сообщений */
    .stChatMessage {
        background-color: transparent !important;
        padding: 1rem 0;
        border-bottom: 1px solid #1f2937;
    }
    
    /* Контейнер для текста ИИ */
    .stMarkdown p {
        font-size: 1.05rem;
        line-height: 1.6;
        color: #d1d5db;
    }

    /* Анимация появления  */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stChatMessage {
        animation: fadeIn 0.4s ease-out;
    }

    /* Кастомная кнопка "Очистить" */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        border: 1px solid #8B5CF6;
        background-color: #1e1b4b;
        color: white;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #8B5CF6;
        border-color: #a78bfa;
    }

    /* Убираем лишние отступы сверху */
    .block-container {
        padding-top: 2rem !important;
        max-width: 800px;
    }
</style>
""", unsafe_allow_html=True)

# --- ИНИЦИАЛИЗАЦИЯ ---
API_KEY = st.secrets.get("GROQ_API_KEY", "ТВОЙ_КЛЮЧ_ТУТ")
client = Groq(api_key=API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- БОКОВАЯ ПАНЕЛЬ (НАСТРОЙКИ) ---
with st.sidebar:
    st.title("💜 okupAi Settings")
    st.markdown("---")
    
    selected_model = st.selectbox(
        "Выбери интеллект:",
        ["llama-3.3-70b-versatile"],
        index=0
    )
    
    temp = st.slider("Креативность (Temperature):", 0.0, 1.0, 0.7)
    
    st.markdown("---")
    if st.button("🗑 Очистить историю чата"):
        st.session_state.messages = []
        st.rerun()

    st.info("okupAi v2.0 | Работает на Groq API")

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
st.title("okupAi")

# Отображение истории сообщений
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "💜"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Поле ввода (как в Gemini)
if prompt := st.chat_input("Спроси что-нибудь у okupAi..."):
    # Отображаем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Генерация ответа
    with st.chat_message("assistant", avatar="💜"):
        placeholder = st.empty()
        full_response = ""
        
        try:
            stream = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                temperature=temp,
                stream=True,
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
            full_response = "Извини, я не смог обработать запрос."

    st.session_state.messages.append({"role": "assistant", "content": full_response})
