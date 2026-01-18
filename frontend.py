import streamlit as st
import requests
import json
import time

# --- Конфигурация страницы ---
st.set_page_config(
    page_title="Banner AI Generator",
    page_icon="🎨",
    layout="wide"
)

# Адрес вашего API (измените, если хостинг отличается)
API_URL = "http://localhost:8000"

# --- Стилизация интерфейса ---
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stImage > img {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
    .variant-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Боковая панель (Настройки) ---
st.sidebar.header("⚙️ Настройки генерации")
user_input = st.sidebar.text_area(
    "Тема объявления:",
    placeholder="Например: Курсы фехтования со скидкой 50%",
    help="Введите краткое описание вашего продукта или услуги"
)

selected_style = st.sidebar.selectbox(
    "Визуальный стиль:",
    ["Photorealistic", "Cyberpunk", "Watercolor", "Anime", "Default"]
)

n_variants = st.sidebar.slider("Количество вариантов:", min_value=3, max_value=5, value=3)
st.sidebar.caption("Согласно ТЗ генерируется минимум 3 варианта")

# --- Главный экран ---
st.title("🚀 Генератор рекламных баннеров")
st.markdown("Система создает комплексное решение: **фон + текст + композиция**.")

if st.sidebar.button("Сгенерировать баннеры", type="primary"):
    if not user_input:
        st.error("Пожалуйста, введите тему объявления!")
    else:
        with st.status("🤖 Работаем...", expanded=True) as status:
            st.write("Генерируем рекламные тексты и идеи для фона...")
            
            payload = {
                "prompt": user_input,
                "style": selected_style,
                "aspect_ratio": "16:9",
                "n_images": n_variants
            }
            
            try:
                # Отправка запроса к FastAPI
                response = requests.post(f"{API_URL}/api/v1/generate", json=payload)
                
                if response.status_code == 200:
                    task_id = response.json().get("task_id")
                    st.write(f"Задача запущена (ID: {task_id}). Ожидаем отрисовку 1920x1080...")
                    
                    # Опрос состояния задачи (Polling)
                    while True:
                        res = requests.get(f"{API_URL}/api/v1/result/{task_id}")
                        result = res.json()
                        
                        if result.get("status") == "SUCCESS":
                            status.update(label="✅ Генерация завершена!", state="complete", expanded=False)
                            variants = result.get("variants", [])
                            break
                        elif result.get("status") == "FAILURE":
                            st.error("Ошибка при генерации.")
                            break
                        
                        time.sleep(2)
                    
                    # --- Отображение результатов ---
                    st.divider()
                    st.header("🎯 Готовые варианты")
                    
                    for var in variants:
                        with st.container():
                            st.markdown(f"### Вариант №{var['variant_num']}")
                            
                            # Колонка с текстом и колонка с изображением
                            col_img, col_info = st.columns([3, 1])
                            
                            marketing = var.get("text")
                            # Обработка случая, если JSON пришел строкой
                            if isinstance(marketing, str):
                                try: marketing = json.loads(marketing)
                                except: marketing = {"title": "Ошибка парсинга", "subtitle": marketing}

                            with col_img:
                                # Формируем URL картинки (через эндпоинт статики FastAPI)
                                img_filename = var['image_path'].split('/')[-1]
                                st.image(
                                    f"{API_URL}/media/{img_filename}",
                                    use_container_width=True,
                                    caption=f"Разрешение: 1920x1080 | Формат: 16:9"
                                )
                            
                            with col_info:
                                st.success(f"**Заголовок:**\n{marketing.get('title', '—')}")
                                st.info(f"**Оффер:**\n{marketing.get('subtitle', '—')}")
                                st.button(
                                    marketing.get('cta', 'Узнать цену'),
                                    key=f"btn_{var['variant_num']}",
                                    use_container_width=True
                                )
                            st.divider()
                            
                else:
                    st.error(f"Ошибка API: {response.text}")
            except Exception as e:
                st.error(f"Не удалось связаться с сервером: {e}")

else:
    # Состояние покоя
    st.info("Введите данные в левой панели и нажмите 'Сгенерировать', чтобы получить минимум 3 варианта баннера.")
