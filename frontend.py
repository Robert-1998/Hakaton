import streamlit as st
import requests
import time
import os

# Настройка страницы
st.set_page_config(page_title="AI Banner Generator", page_icon="🎨", layout="wide")

st.title("🎨 AI Генератор Баннеров")
st.markdown("Система на базе FastAPI, Celery и Streamlit")

# Настройки сервера
with st.sidebar:
    st.header("⚙️ Конфигурация")
    # Если работаете локально - localhost, если через Айнура - вставьте его Ngrok ссылку
    API_URL = st.text_input("URL вашего API:", value="http://localhost:8000")
    
    st.divider()
    st.header("🖌 Настройки стиля")
    style = st.selectbox("Выберите стиль", ["Photorealistic", "Cyberpunk", "Watercolor", "Anime"])
    ratio = st.radio("Соотношение сторон", ["1:1", "16:9", "4:3"])
    n_images = st.slider("Количество вариантов", 1, 4, 1)

# Основной интерфейс
prompt = st.text_area("📝 Описание баннера", placeholder="Например: Современная кофемашина в светлом офисе, минимализм", height=100)

if st.button("🚀 Запустить генерацию", use_container_width=True):
    if not prompt:
        st.error("Ошибка: Введите описание!")
    else:
        with st.status("🛠 Работаем...", expanded=True) as status:
            try:
                # 1. Отправка запроса на генерацию
                st.write("📡 Отправка задачи в Celery...")
                payload = {
                    "prompt": prompt,
                    "style": style,
                    "aspect_ratio": ratio,
                    "n_images": n_images
                }
                
                # Используем ваш точный путь из main.py
                response = requests.post(f"{API_URL}/api/v1/generate/", json=payload)
                
                if response.status_code == 200:
                    task_id = response.json().get("task_id")
                    st.info(f"✅ Задача принята! ID: {task_id}")
                    
                    # 2. Опрос статуса (Polling)
                    completed = False
                    while not completed:
                        st.write("⏳ Ожидание завершения воркера...")
                        status_res = requests.get(f"{API_URL}/api/v1/status/{task_id}")
                        data = status_res.json()
                        
                        if data.get("status") == "SUCCESS":
                            status.update(label="✨ Генерация завершена!", state="complete")
                            result = data.get("result", {})
                            
                            st.divider()
                            col1, col2 = st.columns([1, 1])
                            
                            with col1:
                                st.subheader("📝 Сгенерированный заголовок")
                                # Проверяем, есть ли заголовок в результате
                                title = result.get("title", "Заголовок успешно создан")
                                st.success(title)
                            
                            with col2:
                                st.subheader("🖼 Результат")
                                img_path = result.get("image_path")
                                
                                if img_path:
                                    # Формируем URL для отображения через ваш StaticFiles mount
                                    # Берем только имя файла из пути 'generated_media/file.png'
                                    file_name = os.path.basename(img_path)
                                    full_img_url = f"{API_URL}/media/{file_name}"
                                    
                                    st.image(full_img_url, caption=f"Стиль: {style}", use_container_width=True)
                                    st.caption(f"Ссылка: {full_img_url}")
                                else:
                                    st.warning("Путь к изображению не найден в ответе.")
                            
                            completed = True
                        
                        elif data.get("status") in ["FAILURE", "REVOKED"]:
                            st.error("❌ Ошибка на стороне воркера.")
                            break
                        else:
                            # Статусы PENDING или STARTED
                            time.sleep(2)
                else:
                    st.error(f"❌ Сервер ответил ошибкой: {response.status_code}")
                    
            except Exception as e:
                st.error(f"🔌 Ошибка подключения к бэкенду: {e}")
