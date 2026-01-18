import streamlit as st
import requests
import time
import os

# --- Настройки страницы ---
st.set_page_config(page_title="AI Banner Generator", layout="wide")

st.title("🚀 Генератор рекламных баннеров")

# --- Боковая панель (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Конфигурация")
    # Убедитесь, что порт совпадает с портом вашего FastAPI
    api_url = st.text_input("URL вашего API:", value="http://localhost:8000")
    
    st.header("🖌 Настройки стиля")
    style = st.selectbox("Выберите стиль", ["Photorealistic", "Cyberpunk", "Watercolor", "Anime", "Default"])
    aspect_ratio = st.radio("Соотношение сторон", ["1:1", "16:9", "9:16"], index=1)
    n_images = st.slider("Количество вариантов", min_value=1, max_value=4, value=2)

# --- Основная область ввода ---
prompt = st.text_area("Введите описание продукта или акции:",
                      placeholder="Например: Курсы фехтования со скидкой 50% до конца января",
                      height=150)

if st.button("Сгенерировать баннеры", type="primary"):
    if not prompt:
        st.warning("Пожалуйста, введите описание.")
    else:
        with st.status("🚀 Запуск процесса...") as status:
            try:
                # 1. Отправка запроса (Путь соответствует вашему Main.py)
                payload = {
                    "prompt": prompt,
                    "style": style,
                    "aspect_ratio": aspect_ratio,
                    "n_images": n_images
                }
                
                # ВАЖНО: Путь /api/v1/generate без завершающего слэша
                response = requests.post(f"{api_url}/api/v1/generate", json=payload)
                response.raise_for_status()
                task_id = response.json().get("task_id")
                
                st.write(f"✅ Задача принята! ID: `{task_id}`")
                
                # 2. Опрос состояния задачи (Polling)
                variants = []
                while True:
                    status.update(label="⏳ Ожидание завершения воркера (это может занять 10-30 сек)...")
                    # Путь соответствует вашему get_task_status
                    check_res = requests.get(f"{api_url}/api/v1/status/{task_id}")
                    check_res.raise_for_status()
                    task_data = check_res.json()
                    
                    if task_data.get("status") == "SUCCESS":
                        status.update(label="✨ Баннеры готовы!", state="complete")
                        # Извлекаем результат, который вернул Celery
                        result_content = task_data.get("result", {})
                        variants = result_content.get("variants", [])
                        break
                    elif task_data.get("status") in ["FAILURE", "REVOKED"]:
                        st.error(f"Ошибка задачи: {task_data.get('status')}")
                        break
                    
                    time.sleep(2)
                
                # 3. Отображение результата
                if variants:
                    st.divider()
                    st.subheader(f"🎨 Сгенерировано вариантов: {len(variants)}")

                    for var in variants:
                        with st.container():
                            # Создаем две колонки: текст и изображение
                            col_text, col_img = st.columns([1, 2])
                            
                            marketing = var.get("text", {})
                            
                            with col_text:
                                st.markdown(f"### Вариант №{var['variant_num']}")
                                st.success(f"**Заголовок:**\n{marketing.get('title', '—')}")
                                st.info(f"**Оффер:** {marketing.get('subtitle', '—')}")
                                
                                # Кнопка-заглушка с текстом CTA из нейросети
                                cta_label = marketing.get('cta', 'Подробнее')
                                st.button(cta_label, key=f"btn_{var['variant_num']}_{task_id}")
                            
                            with col_img:
                                # Путь к картинке: меняем папку на /media/ (как в app.mount)
                                raw_path = var.get("image_path", "")
                                if raw_path:
                                    # Если путь 'generated_media/file.png', превращаем в 'http://localhost:8000/media/file.png'
                                    file_name = os.path.basename(raw_path)
                                    full_img_url = f"{api_url}/media/{file_name}"
                                    st.image(full_img_url, use_container_width=True)
                                else:
                                    st.error("Изображение отсутствует.")
                            
                            st.divider()

            except Exception as e:
                st.error(f"🔴 Ошибка: {e}")

# --- Подвал ---
st.caption("Hakaton 2026 - Image & Text Generation System")
